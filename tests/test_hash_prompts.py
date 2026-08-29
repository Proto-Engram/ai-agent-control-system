"""Tests for scripts/hash_prompts.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hash_prompts.py"


def test_hash_prompts_verify_exits_zero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--verify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS" in result.stdout


def test_compute_all_has_expected_keys():
    sys.path.insert(0, str(ROOT))
    from scripts.hash_prompts import compute_all

    hashes = compute_all()
    assert "files_canonical" in hashes
    assert "task_a" in hashes["files_canonical"]
    assert len(hashes["files_canonical"]) == 5
