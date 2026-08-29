#!/usr/bin/env python3
"""Collect mechanical evidence for control-system EVIDENCE stage (worker or verifier role)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION_NOTE = (
    "Evidence separation and command replay verified mechanically; independent AI session not proven."
)


def run_command(cmd: list[str], cwd: Path = ROOT) -> dict:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "command": cmd,
        "exit_code": result.returncode,
        "stdout": result.stdout[-8000:] if result.stdout else "",
        "stderr": result.stderr[-8000:] if result.stderr else "",
    }


def git_state() -> dict:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "status_porcelain": status.stdout.strip(),
        "clean": status.stdout.strip() == "",
    }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def detect_control_plane_changes() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    prefixes = (
        "scripts/check_",
        "scripts/preflight_",
        "scripts/verify_",
        "scripts/collect_evidence.py",
        "schemas/",
        ".pre-commit-config.yaml",
    )
    flagged: list[str] = []
    for raw in result.stdout.splitlines():
        path = raw.strip().replace("\\", "/")
        if any(path == p or path.startswith(p) for p in prefixes):
            flagged.append(path)
    return flagged


def collect_worker_commands(*, skip_pytest: bool) -> list[dict]:
    commands: list[dict] = []
    hash_result = run_command([sys.executable, "scripts/hash_prompts.py", "--verify"])
    commands.append({"id": "hd13_hash_verify", **hash_result})

    if not skip_pytest:
        pytest_result = run_command([sys.executable, "-m", "pytest", "tests/", "-q"])
        commands.append({"id": "pytest", **pytest_result})

    validate_a = run_command(
        [
            sys.executable,
            "scripts/validate_output.py",
            "tests/fixtures/output/task_a_valid_minimal.json",
        ]
    )
    commands.append({"id": "validate_output_task_a", **validate_a})
    return commands


def collect_verifier_commands(*, skip_pytest: bool) -> list[dict]:
    commands: list[dict] = []
    hash_result = run_command([sys.executable, "scripts/hash_prompts.py", "--verify"])
    commands.append({"id": "hd13_hash_verify", **hash_result})

    if not skip_pytest:
        pytest_result = run_command([sys.executable, "-m", "pytest", "tests/", "-q"])
        commands.append({"id": "pytest", **pytest_result})

    policy_result = run_command([sys.executable, "scripts/verify_policy.py", "--all-files"])
    commands.append({"id": "verify_policy", **policy_result})
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True, help="Task identifier for evidence bundle")
    parser.add_argument("--role", choices=["worker", "verifier"], default="worker")
    parser.add_argument(
        "--worker-evidence",
        type=Path,
        default=None,
        help="Required for verifier role — path to worker-evidence.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: artifacts/evidence/<task-id>/<role>-evidence.json)",
    )
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip running pytest (for environments without deps installed)",
    )
    args = parser.parse_args()

    out_dir = ROOT / "artifacts" / "evidence" / args.task_id
    filename = f"{args.role}-evidence.json"
    out_path = args.output or (out_dir / filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    git = git_state()
    control_plane = detect_control_plane_changes()

    if args.role == "worker":
        commands = collect_worker_commands(skip_pytest=args.skip_pytest)
        bundle: dict = {
            "role": "worker",
            "task_id": args.task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git": git,
            "commands": commands,
            "overall_pass": all(c["exit_code"] == 0 for c in commands),
        }
        if control_plane:
            bundle["control_plane_changes"] = control_plane
    else:
        if args.worker_evidence is None:
            print("ERROR: --worker-evidence required for verifier role", file=sys.stderr)
            return 1
        worker_path = args.worker_evidence if args.worker_evidence.is_absolute() else ROOT / args.worker_evidence
        if not worker_path.exists():
            print(f"ERROR: worker evidence not found: {worker_path}", file=sys.stderr)
            return 1

        commands = collect_verifier_commands(skip_pytest=args.skip_pytest)
        bundle = {
            "role": "verifier",
            "task_id": args.task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verified_git_commit": git["commit"],
            "worker_evidence_sha256": sha256_file(worker_path),
            "commands": commands,
            "overall_pass": all(c["exit_code"] == 0 for c in commands),
            "session_independence_note": SESSION_NOTE,
        }

    out_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence written: {out_path}")
    print(f"Role: {args.role}")
    print(f"Overall: {'PASS' if bundle['overall_pass'] else 'FAIL'}")
    if control_plane and args.role == "worker":
        print(f"CONTROL_PLANE_CHANGE: {', '.join(control_plane)}")
    return 0 if bundle["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
