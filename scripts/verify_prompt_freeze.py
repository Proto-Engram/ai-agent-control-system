#!/usr/bin/env python3
"""Pre-commit hook: verify HD-13 frozen prompt hashes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    script = ROOT / "scripts" / "hash_prompts.py"
    result = subprocess.run(
        [sys.executable, str(script), "--verify"],
        cwd=ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
