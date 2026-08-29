#!/usr/bin/env python3
"""Canonical policy verification entrypoint — runs underlying checks directly (no pre-commit recursion)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_ENVELOPE = ROOT / "tasks" / "active-envelope"
LAST_RUN_PATH = ROOT / "artifacts" / "evidence" / "policy-checks" / "last-run.json"

CONTROL_PLANE_PREFIXES = (
    "scripts/check_",
    "scripts/preflight_",
    "scripts/verify_",
    "scripts/collect_evidence.py",
    "schemas/",
    ".pre-commit-config.yaml",
    "tasks/envelopes/",
    "tasks/active-envelope",
)

REQUIRED_VERIFIER_COMMAND_IDS = frozenset({"pytest", "hd13_hash_verify"})


def run_subprocess(cmd: list[str], *, cwd: Path = ROOT) -> dict:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "command": cmd,
        "exit_code": result.returncode,
        "stdout": (result.stdout or "")[-4000:],
        "stderr": (result.stderr or "")[-4000:],
    }


def is_hooks_installed() -> bool:
    hook = ROOT / ".git" / "hooks" / "pre-commit"
    if not hook.exists():
        return False
    try:
        content = hook.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "pre-commit" in content or "verify_policy" in content


def read_active_envelope_path(*, staged: bool = False) -> Path | None:
    rel: str | None = None
    if staged:
        result = subprocess.run(
            ["git", "show", ":tasks/active-envelope"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            rel = result.stdout.strip()
    if rel is None and ACTIVE_ENVELOPE.exists():
        rel = ACTIVE_ENVELOPE.read_text(encoding="utf-8").strip()
    if not rel:
        return None
    path = ROOT / rel
    return path if path.exists() else None


def detect_control_plane_changes(*, staged: bool) -> list[str]:
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only"]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD"]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    flagged: list[str] = []
    for raw in result.stdout.splitlines():
        path = raw.strip().replace("\\", "/")
        if not path:
            continue
        for prefix in CONTROL_PLANE_PREFIXES:
            if path == prefix or path.startswith(prefix):
                flagged.append(path)
                break
    return flagged


def run_underlying_checks(*, staged: bool) -> tuple[list[dict], bool]:
    checks: list[dict] = []
    all_pass = True

    hash_result = run_subprocess([sys.executable, "scripts/hash_prompts.py", "--verify"])
    hash_ok = hash_result["exit_code"] == 0
    checks.append({"id": "hd13_hash_verify", "passed": hash_ok, **hash_result})
    all_pass = all_pass and hash_ok

    if staged:
        repo_result = run_subprocess([sys.executable, "scripts/check_repo_policy.py"])
    else:
        repo_result = run_subprocess([sys.executable, "scripts/check_repo_policy.py"])
    repo_ok = repo_result["exit_code"] == 0
    checks.append({"id": "repo_policy", "passed": repo_ok, **repo_result})
    all_pass = all_pass and repo_ok

    ledger_result = run_subprocess([sys.executable, "scripts/check_ledger_integrity.py"])
    ledger_ok = ledger_result["exit_code"] == 0
    checks.append({"id": "ledger_integrity", "passed": ledger_ok, **ledger_result})
    all_pass = all_pass and ledger_ok

    envelope_path = read_active_envelope_path(staged=staged)
    if envelope_path is not None:
        scope_cmd = [
            sys.executable,
            "scripts/check_task_scope.py",
            "--envelope",
            str(envelope_path.relative_to(ROOT)),
        ]
        if staged:
            scope_cmd.append("--staged")
        scope_result = run_subprocess(scope_cmd)
        scope_ok = scope_result["exit_code"] == 0
        checks.append({"id": "task_scope", "passed": scope_ok, **scope_result})
        all_pass = all_pass and scope_ok

    control_plane = detect_control_plane_changes(staged=staged)
    if control_plane:
        checks.append(
            {
                "id": "control_plane_change",
                "passed": True,
                "command": ["detect_control_plane_changes"],
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
                "control_plane_paths": control_plane,
                "note": "CONTROL_PLANE_CHANGE — report in evidence and verification output",
            }
        )

    return checks, all_pass


def write_last_run(*, mode: str, passed: bool, checks: list[dict]) -> None:
    LAST_RUN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "executed": True,
        "passed": passed,
        "checks": [{"id": c["id"], "passed": c.get("passed", False)} for c in checks],
    }
    LAST_RUN_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def verify_policy(*, staged: bool, require_installed: bool) -> tuple[dict, int]:
    configured = (ROOT / ".pre-commit-config.yaml").exists()
    installed = is_hooks_installed()

    if require_installed and not installed:
        return {
            "configured": configured,
            "installed": installed,
            "executed": False,
            "passed": False,
            "error": "pre-commit hooks not installed — run scripts/bootstrap_controls.py",
        }, 2

    if not configured:
        return {
            "configured": False,
            "installed": installed,
            "executed": False,
            "passed": False,
            "error": ".pre-commit-config.yaml missing",
        }, 2

    mode = "staged" if staged else "all-files"
    checks, passed = run_underlying_checks(staged=staged)
    write_last_run(mode=mode, passed=passed, checks=checks)

    return {
        "configured": configured,
        "installed": installed,
        "executed": True,
        "passed": passed,
        "mode": mode,
        "checks": checks,
    }, (0 if passed else 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Check staged changes (commit hook mode)")
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Audit mode — run underlying checks against current repo state",
    )
    parser.add_argument(
        "--require-installed",
        action="store_true",
        help="Exit 2 if pre-commit hooks are not installed",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    staged = args.staged or not args.all_files
    result, code = verify_policy(staged=staged, require_installed=args.require_installed)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key in ("configured", "installed", "executed", "passed"):
            print(f"{key}: {result.get(key)}")
        if result.get("error"):
            print(result["error"], file=sys.stderr)
        for check in result.get("checks", []):
            status = "PASS" if check.get("passed") else "FAIL"
            print(f"  [{status}] {check['id']}")
            if check.get("control_plane_paths"):
                print(f"    CONTROL_PLANE_CHANGE: {', '.join(check['control_plane_paths'])}")

    return code


if __name__ == "__main__":
    raise SystemExit(main())
