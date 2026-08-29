#!/usr/bin/env python3
"""Bootstrap control-system dependencies and pre-commit hooks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> int:
    print(f"+ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main() -> int:
    steps: list[tuple[str, list[str]]] = [
        ("install dev dependencies", [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"]),
        ("install pre-commit hooks", [sys.executable, "-m", "pre_commit", "install", "--install-hooks"]),
    ]

    for label, cmd in steps:
        print(f"\n== {label} ==")
        code = run(cmd)
        if code != 0:
            print(f"bootstrap failed at: {label}", file=sys.stderr)
            return code

    print("\n== verify hooks status ==")
    status_code = run([sys.executable, "scripts/hooks_status.py"])
    if status_code != 0:
        return status_code

    print("\n== run policy verification ==")
    policy_code = run([sys.executable, "scripts/verify_policy.py", "--all-files"])
    if policy_code not in (0, 1):
        return policy_code

    print("\nBootstrap complete.")
    print("Note: policy verification exit 1 means policy failures exist in the working tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
