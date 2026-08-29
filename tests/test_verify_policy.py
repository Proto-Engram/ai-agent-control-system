"""Tests for scripts/verify_policy.py and hooks_status.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.hooks_status import hooks_status, is_configured
from scripts.verify_policy import verify_policy


def test_hooks_status_configured():
    assert is_configured() is True
    status = hooks_status()
    assert status["configured"] is True
    assert "installed" in status
    assert "executed" in status
    assert "passed" in status


def test_verify_policy_all_files_runs():
    result, code = verify_policy(staged=False, require_installed=False)
    assert result["configured"] is True
    assert result["executed"] is True
    assert "checks" in result
    assert any(c["id"] == "hd13_hash_verify" for c in result["checks"])
    assert code in (0, 1)


def test_verify_policy_require_installed_without_hooks():
    with patch("scripts.verify_policy.is_hooks_installed", return_value=False):
        result, code = verify_policy(staged=False, require_installed=True)
    assert code == 2
    assert result["installed"] is False


def test_verify_policy_does_not_invoke_pre_commit():
    with patch("scripts.verify_policy.subprocess.run") as mock_run:
        mock_run.return_value = type(
            "R", (), {"returncode": 0, "stdout": "HD-13 prompt hash verification: PASS", "stderr": ""}
        )()
        verify_policy(staged=True, require_installed=False)
    for call in mock_run.call_args_list:
        cmd = call[0][0]
        assert "pre-commit" not in cmd


def test_hooks_status_json_cli():
    result = subprocess.run(
        [sys.executable, "scripts/hooks_status.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["configured"] is True
