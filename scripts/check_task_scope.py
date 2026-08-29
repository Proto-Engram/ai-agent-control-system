#!/usr/bin/env python3
"""Mechanically verify Git changes against a machine-readable task envelope."""

from __future__ import annotations

import argparse
import fnmatch
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
SCHEMA_PATH = ROOT / "schemas" / "task-envelope.schema.json"

DEPENDENCY_FILES = frozenset(
    {
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "poetry.lock",
    }
)


def normalize_path(path: str) -> str:
    path = path.replace("\\", "/")
    if path.startswith("./"):
        return path[2:]
    return path


def path_matches(path: str, pattern: str) -> bool:
    path = normalize_path(path)
    pattern = normalize_path(pattern)
    if fnmatch.fnmatch(path, pattern):
        return True
    if pattern.endswith("/") and path.startswith(pattern):
        return True
    return False


def any_pattern(path: str, patterns: list[str]) -> bool:
    return any(path_matches(path, p) for p in patterns)


def git_diff_name_status(*, staged: bool, diff_base: str | None) -> list[tuple[str, str]]:
    if staged:
        cmd = ["git", "diff", "--cached", "--name-status"]
    elif diff_base:
        cmd = ["git", "diff", "--name-status", diff_base]
    else:
        cmd = ["git", "diff", "--name-status", "HEAD"]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    entries: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0].strip()
            path = normalize_path(parts[-1].strip())
            entries.append((status, path))
    return entries


def load_envelope(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(data)
    return data


def evaluate_diff(envelope: dict, diff_entries: list[tuple[str, str]]) -> dict:
    allowed = envelope.get("allowed_paths", [])
    forbidden = envelope.get("forbidden_paths", [])
    frozen = envelope.get("frozen_paths", [])
    allow_deps = envelope.get("allowed_dependency_changes", False)

    violations: list[str] = []
    deletions: list[str] = []
    changes: list[str] = []

    for status, path in diff_entries:
        changes.append(f"{status}\t{path}")
        if status.startswith("D") or status == "D":
            deletions.append(path)

        if any_pattern(path, forbidden):
            violations.append(f"forbidden path changed: {path}")
        if any_pattern(path, frozen):
            violations.append(f"frozen path changed: {path}")
        if not any_pattern(path, allowed):
            violations.append(f"path outside allowed_paths: {path}")

        basename = Path(path).name
        if not allow_deps and basename in DEPENDENCY_FILES:
            violations.append(f"dependency file changed without authorization: {path}")

    return {
        "task_id": envelope.get("task_id"),
        "changes": changes,
        "deletions": deletions,
        "violations": violations,
        "passed": len(violations) == 0,
    }


def check_task_scope(
    envelope_path: Path,
    *,
    staged: bool = False,
    diff_base: str | None = None,
    diff_entries: list[tuple[str, str]] | None = None,
) -> dict:
    envelope = load_envelope(envelope_path)
    if diff_entries is None:
        diff_entries = git_diff_name_status(staged=staged, diff_base=diff_base)
    return evaluate_diff(envelope, diff_entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--diff-base", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    envelope_path = args.envelope if args.envelope.is_absolute() else ROOT / args.envelope
    result = check_task_scope(envelope_path, staged=args.staged, diff_base=args.diff_base)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Task scope ({result['task_id']}): {'PASS' if result['passed'] else 'FAIL'}")
        if result["deletions"]:
            print("Deletions:")
            for d in result["deletions"]:
                print(f"  D\t{d}")
        if result["violations"]:
            for v in result["violations"]:
                print(f"  VIOLATION: {v}", file=sys.stderr)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
