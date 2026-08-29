"""Tests for scripts/run_p1_experiment.py gate enforcement — live preflight required."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_p1_experiment.py"


def test_runner_refuses_without_preflight(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest", str(manifest), "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "live preflight" in result.stderr.lower() or "preflight" in result.stderr.lower()


def test_fabricated_pass_json_does_not_authorize(tmp_path):
    """Cached PASS JSON alone must not satisfy runner — live preflight must fail."""
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"experiment_id": "fake"}', encoding="utf-8")
    preflight = tmp_path / "preflight-result.json"
    preflight.write_text(
        json.dumps(
            {
                "overall": "PASS",
                "git_commit": "deadbeef",
                "manifest_sha256": "0" * 64,
                "preflight_version": "1.0.0",
                "checks": [
                    {"id": "hd14_execution_approved", "status": "PASS", "detail": "forged"}
                ],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest", str(manifest), "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Gate check: PASS" not in result.stdout


def test_runner_invokes_live_preflight_subprocess(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"experiment_id": "test"}', encoding="utf-8")

    calls: list[list[str]] = []

    def track_run(cmd, **kwargs):
        calls.append(cmd)
        return type(
            "R",
            (),
            {"returncode": 1, "stdout": "", "stderr": "preflight fail"},
        )()

    with patch("scripts.run_p1_experiment.subprocess.run", side_effect=track_run):
        sys.path.insert(0, str(ROOT))
        from scripts.run_p1_experiment import execute_live_preflight

        execute_live_preflight(manifest)
        assert any("preflight_p1.py" in str(c) for c in calls)


def test_validate_preflight_binding_rejects_stale_commit(tmp_path):
    sys.path.insert(0, str(ROOT))
    from scripts.run_p1_experiment import validate_preflight_binding

    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"experiment_id": "test"}', encoding="utf-8")

    preflight = {
        "overall": "PASS",
        "git_commit": "stale_commit_hash",
        "manifest_sha256": "wrong",
        "preflight_version": "1.1.0",
        "checks": [{"id": "hd14_execution_approved", "status": "PASS"}],
    }

    with patch("scripts.run_p1_experiment.subprocess.run") as mock_run:
        mock_run.return_value = type(
            "R", (), {"returncode": 0, "stdout": "real_head\n", "stderr": ""}
        )()
        errors = validate_preflight_binding(preflight, manifest)
    assert errors
    assert any("git_commit" in e or "manifest_sha256" in e for e in errors)
