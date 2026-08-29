"""Tests for scripts/validate_output.py against contract fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_output import load_schema, validate_data, validate_file

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "output"


def test_task_a_valid_minimal_passes():
    data = json.loads((FIXTURES / "task_a_valid_minimal.json").read_text(encoding="utf-8"))
    assert validate_data(data) == []


def test_task_b_valid_minimal_passes():
    data = json.loads((FIXTURES / "task_b_valid_minimal.json").read_text(encoding="utf-8"))
    assert validate_data(data) == []


def test_task_a_missing_required_fails():
    _, errors = validate_file(FIXTURES / "task_a_missing_required.json")
    assert errors


def test_task_a_invalid_enum_fails():
    _, errors = validate_file(FIXTURES / "task_a_invalid_enum.json")
    assert any("confidence" in e for e in errors)


def test_schema_loads():
    schema = load_schema()
    assert schema["title"] == "P1 Output Contract"
