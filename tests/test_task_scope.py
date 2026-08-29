"""Tests for scripts/check_task_scope.py — uses injected diff fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_task_scope import check_task_scope, evaluate_diff

ENVELOPE = {
    "task_id": "test-scope",
    "authority": ["test"],
    "allowed_paths": ["scripts/**", "tests/**"],
    "forbidden_paths": ["docs/07-DECISIONS.md"],
    "frozen_paths": ["prompts/evaluation/P1-A-v1.1.md"],
    "allowed_dependency_changes": False,
    "forbidden_operations": ["external_api_call"],
}


def test_in_scope_change_passes():
    result = evaluate_diff(ENVELOPE, [("M", "scripts/foo.py")])
    assert result["passed"] is True
    assert result["violations"] == []


def test_out_of_scope_change_fails():
    result = evaluate_diff(ENVELOPE, [("M", "docs/10-DEVELOPMENT-GUIDE.md")])
    assert result["passed"] is False
    assert any("outside allowed_paths" in v for v in result["violations"])


def test_forbidden_path_fails():
    result = evaluate_diff(ENVELOPE, [("M", "docs/07-DECISIONS.md")])
    assert result["passed"] is False
    assert any("forbidden path" in v for v in result["violations"])


def test_deletion_in_allowed_path_reported():
    result = evaluate_diff(ENVELOPE, [("D", "tests/fixtures/output/task_a_invalid_enum.json")])
    assert "tests/fixtures/output/task_a_invalid_enum.json" in result["deletions"]
    assert result["passed"] is True
    result = evaluate_diff(ENVELOPE, [("D", "docs/08-VALIDATION.md")])
    assert "docs/08-VALIDATION.md" in result["deletions"]
    assert result["passed"] is False
    assert any("outside allowed_paths" in v for v in result["violations"])


def test_frozen_artifact_change_fails():
    result = evaluate_diff(ENVELOPE, [("M", "prompts/evaluation/P1-A-v1.1.md")])
    assert result["passed"] is False
    assert any("frozen path" in v for v in result["violations"])


def test_dependency_modification_fails_when_disallowed():
    result = evaluate_diff(ENVELOPE, [("M", "requirements-dev.txt")])
    assert result["passed"] is False
    assert any("dependency file" in v for v in result["violations"])


def test_enforcement_closure_envelope_loads():
    path = ROOT / "tasks" / "envelopes" / "enforcement-closure.json"
    result = check_task_scope(path, diff_entries=[])
    assert result["task_id"] == "enforcement-closure"
    assert result["passed"] is True
