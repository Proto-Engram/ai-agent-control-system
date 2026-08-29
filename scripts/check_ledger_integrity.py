#!/usr/bin/env python3
"""Detect unauthorized HD-13 ledger hash edits and coordinated prompt/ledger tampering."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.control_plane import frozen_prompt_paths, is_demo_mode  # noqa: E402

LEDGER = ROOT / "docs" / "07-DECISIONS.md"
HUMAN_LEDGER_ENV = "PHOTO_CRITIC_HUMAN_LEDGER"

HD13_HASH_PATTERN = re.compile(r"`([a-f0-9]{64})`")

FROZEN_PROMPT_PATHS = frozen_prompt_paths()


def normalize_path(path: str) -> str:
    path = path.replace("\\", "/")
    if path.startswith("./"):
        return path[2:]
    return path


def staged_diff_paths() -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
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


def ledger_hd13_hash_lines_changed() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "-U0", "--", str(LEDGER.relative_to(ROOT))],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout:
        return []
    changed_hashes: list[str] = []
    in_hd13 = False
    for line in result.stdout.splitlines():
        if line.startswith("@@"):
            in_hd13 = False
        if "### HD-13" in line:
            in_hd13 = True
        if not in_hd13:
            continue
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            for match in HD13_HASH_PATTERN.finditer(line):
                changed_hashes.append(match.group(1))
    return changed_hashes


def check_ledger_integrity(*, human_override: bool = False) -> tuple[bool, list[str]]:
    if is_demo_mode():
        return True, []
    if human_override or os.environ.get(HUMAN_LEDGER_ENV) == "1":
        return True, []

    errors: list[str] = []
    diff_paths = staged_diff_paths()
    changed_paths = {path for _, path in diff_paths}
    ledger_changed = normalize_path("docs/07-DECISIONS.md") in changed_paths
    frozen_changed = [p for p in FROZEN_PROMPT_PATHS if p in changed_paths]
    hash_rows_changed = ledger_hd13_hash_lines_changed()

    if ledger_changed and hash_rows_changed:
        errors.append(
            "HD-13 hash rows modified in docs/07-DECISIONS.md — human ledger edits only "
            f"(set {HUMAN_LEDGER_ENV}=1 for authorized human commit)"
        )

    if frozen_changed and ledger_changed and hash_rows_changed:
        errors.append(
            "Coordinated tamper pattern: frozen HD-13 prompt file(s) and ledger hash row(s) "
            f"changed in same staged commit: {', '.join(frozen_changed)}"
        )

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--human-override",
        action="store_true",
        help="Allow ledger hash edits (equivalent to PHOTO_CRITIC_HUMAN_LEDGER=1)",
    )
    args = parser.parse_args()

    ok, errors = check_ledger_integrity(human_override=args.human_override)
    if ok:
        print("Ledger integrity: PASS")
        return 0
    for err in errors:
        print(f"LEDGER INTEGRITY FAIL: {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
