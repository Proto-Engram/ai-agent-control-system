#!/usr/bin/env python3
"""P1 execution preflight gate — verifies prerequisites without API calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.control_plane import is_demo_mode  # noqa: E402

LEDGER = ROOT / "docs" / "07-DECISIONS.md"
SCHEMAS = ROOT / "schemas"
PREFLIGHT_VERSION = "1.1.0"


def run_check(check_id: str, fn) -> dict:
    try:
        ok, detail = fn()
        return {"id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail}
    except Exception as exc:  # noqa: BLE001 — gate must capture all failures
        return {"id": check_id, "status": "FAIL", "detail": str(exc)}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def check_hd13_hashes() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "scripts/hash_prompts.py", "--verify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, (result.stdout or result.stderr).strip()


def ledger_has_hd(entry: str) -> bool:
    if not LEDGER.exists():
        return False
    text = LEDGER.read_text(encoding="utf-8")
    pattern = rf"### {re.escape(entry)} —"
    section = re.search(pattern, text)
    if not section:
        return False
    start = section.start()
    next_hd = re.search(r"\n### HD-", text[start + 10 :])
    block = text[start : start + 10 + next_hd.start()] if next_hd else text[start:]
    return "Approved" in block or "**Approved" in block


def check_ledger_hd09_13() -> tuple[bool, str]:
    required = [f"HD-{n:02d}" for n in range(9, 14)]
    missing = [hd for hd in required if not ledger_has_hd(hd)]
    if missing:
        return False, f"Missing or unapproved ledger entries: {', '.join(missing)}"
    return True, "HD-09 through HD-13 present and approved"


def check_hd14(require: bool) -> tuple[bool, str]:
    if not require:
        return True, "Skipped (--allow-missing-hd14)"
    if ledger_has_hd("HD-14"):
        return True, "HD-14 present in ledger"
    return False, "HD-14 P1 execution authorization not recorded in 07-DECISIONS.md"


def validate_json_schema(path: Path, schema_name: str) -> tuple[bool, str]:
    if not path.exists():
        return False, f"File not found: {path}"
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    data = json.loads(path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(data))
    if errors:
        return False, "; ".join(e.message for e in errors[:5])
    return True, f"Schema valid: {path.name}"


def check_manifest_fields(manifest_path: Path) -> tuple[bool, str]:
    ok, detail = validate_json_schema(manifest_path, "experiment-manifest.schema.json")
    if not ok:
        return ok, detail
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    if data.get("foundry", {}).get("portal_meter_verified") is not True:
        issues.append("foundry.portal_meter_verified must be true before execution")
    for placeholder in ("TBD", "TODO", "<human-defined>", "<id>"):
        blob = json.dumps(data)
        if placeholder in blob:
            issues.append(f"manifest contains placeholder: {placeholder}")
    if issues:
        return False, "; ".join(issues)
    return True, "Experiment manifest complete"


def check_dataset_manifest(dataset_path: Path) -> tuple[bool, str]:
    ok, detail = validate_json_schema(dataset_path, "dataset-manifest.schema.json")
    if not ok:
        return ok, detail
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    if data.get("photograph_count", 0) < 10 or data.get("photograph_count", 0) > 20:
        return False, f"photograph_count {data.get('photograph_count')} outside P1 range 10-20"
    if data.get("group_count", 0) < 3 or data.get("group_count", 0) > 5:
        return False, f"group_count {data.get('group_count')} outside P1 range 3-5"
    for group in data.get("comparison_groups", []):
        pref = group.get("human_reference_keep_preference", "")
        if not pref or pref.startswith("<"):
            return False, f"group {group.get('group_id')} missing human_reference_keep_preference"
    return True, "Dataset manifest valid for P1 pilot"


def check_git_state(allow_dirty: bool) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    dirty = result.stdout.strip()
    if dirty and not allow_dirty:
        lines = len(dirty.splitlines())
        return False, f"Working tree dirty ({lines} entries) — reconcile or use --allow-dirty"
    return True, "Clean" if not dirty else f"Dirty allowed ({len(dirty.splitlines())} entries)"


def run_demo_preflight(*, allow_dirty: bool = False) -> dict:
    manifest = ROOT / "examples" / "demo-manifest" / "manifest.json"
    dataset = ROOT / "examples" / "demo-manifest" / "dataset.json"
    checks = [
        run_check("git_state", lambda: check_git_state(allow_dirty)),
        run_check("demo_hash_verify", check_hd13_hashes),
        run_check("experiment_manifest_schema", lambda: validate_json_schema(manifest, "experiment-manifest.schema.json")),
        run_check("dataset_manifest_schema", lambda: validate_json_schema(dataset, "dataset-manifest.schema.json")),
    ]
    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "gate": "demo_preflight",
        "preflight_version": PREFLIGHT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": current_git_commit(),
        "manifest_path": str(manifest.relative_to(ROOT)),
        "dataset_path": str(dataset.relative_to(ROOT)),
        "checks": checks,
        "overall": overall,
    }


def run_preflight(
    manifest_path: Path,
    *,
    dataset_path: Path | None = None,
    allow_missing_hd14: bool = False,
    allow_dirty: bool = False,
) -> dict:
    manifest_path = manifest_path if manifest_path.is_absolute() else ROOT / manifest_path

    if dataset_path is None:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        dataset_id = data.get("dataset_id", "")
        dataset_path = ROOT / "data" / "evaluation" / f"{dataset_id}.json"
    elif not dataset_path.is_absolute():
        dataset_path = ROOT / dataset_path

    checks = [
        run_check("git_state", lambda: check_git_state(allow_dirty)),
        run_check("hd13_hash_verify", check_hd13_hashes),
        run_check("ledger_hd09_hd13", check_ledger_hd09_13),
        run_check("hd14_execution_approved", lambda: check_hd14(not allow_missing_hd14)),
        run_check("experiment_manifest_schema", lambda: check_manifest_fields(manifest_path)),
        run_check("dataset_manifest_schema", lambda: check_dataset_manifest(dataset_path)),
    ]

    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"

    return {
        "gate": "p1_execution",
        "preflight_version": PREFLIGHT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": current_git_commit(),
        "manifest_sha256": sha256_file(manifest_path),
        "manifest_path": str(
            manifest_path.relative_to(ROOT) if manifest_path.is_relative_to(ROOT) else manifest_path
        ),
        "dataset_path": str(
            dataset_path.relative_to(ROOT) if dataset_path.is_relative_to(ROOT) else dataset_path
        ),
        "checks": checks,
        "overall": overall,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Experiment manifest path")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Dataset manifest path (default: infer from manifest dataset_id)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Preflight result JSON (default: alongside manifest as preflight-result.json)",
    )
    parser.add_argument(
        "--allow-missing-hd14",
        action="store_true",
        help="Dry-run mode — skip HD-14 requirement",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow dirty git working tree",
    )
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    out_path = args.output or manifest_path.parent / "preflight-result.json"

    if is_demo_mode() and "demo-manifest" in manifest_path.as_posix():
        result = run_demo_preflight(allow_dirty=args.allow_dirty)
    else:
        result = run_preflight(
            manifest_path,
            dataset_path=args.dataset,
            allow_missing_hd14=args.allow_missing_hd14,
            allow_dirty=args.allow_dirty,
        )

    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Preflight {result['overall']}: {out_path}")
    for check in result["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")
    return 0 if result["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
