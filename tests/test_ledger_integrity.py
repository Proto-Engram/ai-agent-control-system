"""Tests for scripts/check_ledger_integrity.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_ledger_integrity import check_ledger_integrity
from scripts.control_plane import is_demo_mode


pytestmark = pytest.mark.skipif(is_demo_mode(), reason="ledger integrity tests require product mode")


def test_ledger_hash_edit_fails():
    with patch(
        "scripts.check_ledger_integrity.staged_diff_paths",
        return_value=[("M", "docs/07-DECISIONS.md")],
    ), patch(
        "scripts.check_ledger_integrity.ledger_hd13_hash_lines_changed",
        return_value=["a" * 64],
    ):
        ok, errors = check_ledger_integrity()
    assert ok is False
    assert any("HD-13 hash rows" in e for e in errors)


def test_coordinated_tamper_fails():
    with patch(
        "scripts.check_ledger_integrity.staged_diff_paths",
        return_value=[
            ("M", "docs/07-DECISIONS.md"),
            ("M", "prompts/evaluation/P1-A-v1.1.md"),
        ],
    ), patch(
        "scripts.check_ledger_integrity.ledger_hd13_hash_lines_changed",
        return_value=["b" * 64],
    ):
        ok, errors = check_ledger_integrity()
    assert ok is False
    assert any("Coordinated tamper" in e for e in errors)


def test_scripts_only_passes():
    with patch(
        "scripts.check_ledger_integrity.staged_diff_paths",
        return_value=[("M", "scripts/foo.py")],
    ), patch(
        "scripts.check_ledger_integrity.ledger_hd13_hash_lines_changed",
        return_value=[],
    ):
        ok, errors = check_ledger_integrity()
    assert ok is True
    assert errors == []


def test_human_override_allows_ledger_edit():
    with patch(
        "scripts.check_ledger_integrity.staged_diff_paths",
        return_value=[("M", "docs/07-DECISIONS.md")],
    ), patch(
        "scripts.check_ledger_integrity.ledger_hd13_hash_lines_changed",
        return_value=["c" * 64],
    ):
        ok, errors = check_ledger_integrity(human_override=True)
    assert ok is True
