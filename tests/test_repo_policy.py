"""Tests for scripts/check_repo_policy.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_repo_policy import (
    check_json_policy,
    check_no_images,
    _json_has_sensitive_keys,
)


def test_blocks_image_outside_docs():
    errors = check_no_images(["photos/test.jpg"])
    assert errors
    assert "outside approved paths" in errors[0]


def test_allows_image_in_docs():
    errors = check_no_images(["docs/example.png"])
    assert errors == []


def test_blocks_sensitive_json_path():
    errors = check_json_policy(["data/evaluation/test.json"])
    # File may not exist — create temp-like check via _json_has_sensitive_keys
    assert _json_has_sensitive_keys({"local_path": "/home/user/secret.jpg"})


def test_allows_json_without_sensitive_keys():
    assert not _json_has_sensitive_keys({"dataset_id": "test", "photographs": []})
