#!/usr/bin/env python3
"""Validate worker and verifier evidence bundles for structural binding and replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
REQUIRED_VERIFIER_IDS = frozenset({"pytest", "hd13_hash_verify"})
SESSION_NOTE = (
    "Evidence separation and command replay verified mechanically; independent AI session not proven."
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate_schema(data: dict, schema_name: str) -> list[str]:
    schema = load_schema(schema_name)
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    return [e.message for e in errors]


def current_git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def check_bundle(task_id: str, *, evidence_dir: Path | None = None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    base = evidence_dir or (ROOT / "artifacts" / "evidence" / task_id)
    worker_path = base / "worker-evidence.json"
    verifier_path = base / "verifier-evidence.json"

    if not worker_path.exists():
        return False, [f"worker evidence missing: {worker_path}"]
    if not verifier_path.exists():
        return False, [f"verifier evidence missing: {verifier_path}"]

    worker = json.loads(worker_path.read_text(encoding="utf-8"))
    verifier = json.loads(verifier_path.read_text(encoding="utf-8"))

    errors.extend(validate_schema(worker, "worker-evidence.schema.json"))
    errors.extend(validate_schema(verifier, "verifier-evidence.schema.json"))

    if worker.get("role") != "worker":
        errors.append("worker evidence role must be 'worker'")
    if verifier.get("role") != "verifier":
        errors.append("verifier evidence role must be 'verifier'")

    if worker.get("task_id") != task_id or verifier.get("task_id") != task_id:
        errors.append("task_id mismatch between worker and verifier evidence")

    actual_hash = sha256_file(worker_path)
    if verifier.get("worker_evidence_sha256") != actual_hash:
        errors.append("verifier worker_evidence_sha256 does not match worker file on disk")

    head = current_git_commit()
    if verifier.get("verified_git_commit") != head:
        errors.append("verifier verified_git_commit does not match current HEAD")

    verifier_ids = {c.get("id") for c in verifier.get("commands", [])}
    missing = REQUIRED_VERIFIER_IDS - verifier_ids
    if missing:
        errors.append(f"verifier missing required replay command IDs: {', '.join(sorted(missing))}")

    for cmd in verifier.get("commands", []):
        if cmd.get("id") in REQUIRED_VERIFIER_IDS and cmd.get("exit_code") != 0:
            errors.append(f"verifier replay {cmd.get('id')} exit_code != 0")

    if verifier.get("session_independence_note") != SESSION_NOTE:
        errors.append("verifier missing required session_independence_note disclaimer")

    if not worker.get("overall_pass"):
        errors.append("worker overall_pass is false")
    if not verifier.get("overall_pass"):
        errors.append("verifier overall_pass is false")

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--evidence-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ok, errors = check_bundle(args.task_id, evidence_dir=args.evidence_dir)
    result = {"task_id": args.task_id, "passed": ok, "errors": errors}

    if args.json:
        print(json.dumps(result, indent=2))
    elif ok:
        print(f"Verification bundle ({args.task_id}): PASS")
    else:
        print(f"Verification bundle ({args.task_id}): FAIL", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
