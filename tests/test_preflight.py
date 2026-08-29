"""Tests for scripts/preflight_p1.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_p1.py"
DEMO_MANIFEST = ROOT / "examples" / "demo-manifest" / "manifest.json"


def test_demo_preflight_passes_in_demo_mode():
    if not DEMO_MANIFEST.exists():
        import pytest

        pytest.skip("demo manifest not present")
    from scripts.control_plane import is_demo_mode

    if not is_demo_mode():
        import pytest

        pytest.skip("demo preflight PASS test requires demo mode")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(DEMO_MANIFEST),
            "--allow-dirty",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "Preflight PASS" in result.stdout


def test_preflight_template_fails_on_placeholders():
    template = ROOT / "experiments" / "p1-pilot-template" / "manifest.template.json"
    if not template.exists():
        import pytest

        pytest.skip("product template not present")
    from scripts.control_plane import is_demo_mode

    if is_demo_mode():
        import pytest

        pytest.skip("product template test requires product mode")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(template),
            "--allow-missing-hd14",
            "--allow-dirty",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Preflight FAIL" in result.stdout or "FAIL" in result.stdout


def test_preflight_writes_result_json(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "experiment_id": "test",
                "phase": "pilot",
                "dataset_id": "missing-dataset",
                "rubric_version": "1.0",
                "prompt_version": "P1-A-v1.1",
                "preprocessing_policy": "test",
                "pricing_snapshot_id": "test",
                "blinding_seed": 1,
                "candidates": ["Candidate A"],
                "model_mapping_path": "local",
                "retry_policy": {
                    "max_retries": 0,
                    "retry_on_parse_failure": False,
                    "rate_limit_backoff": "none",
                },
                "inference_parameters": {
                    "temperature": "0",
                    "top_p": "1",
                    "max_output_tokens": "1000",
                },
                "prompt_freeze": {
                    "ledger_entry": "HD-13",
                    "prompt_versions": {
                        "task_a": "P1-A-v1.1",
                        "task_b": "P1-B-v1.1",
                        "framework": "P1-PHOTOGRAPHIC-CRITICAL-FRAMEWORK-v1.0",
                        "output_contract": "P1-OUTPUT-CONTRACT-v1.0",
                        "cross_model_invariants": "P1-CROSS-MODEL-INVARIANTS-v1.0",
                    },
                    "prompt_paths": {},
                    "prompt_hashes": {
                        "task_a": "f70ff0c564ca7043b86448af362d20fbeb13df64d896639fea2bd84d61eb1208"
                    },
                },
                "foundry": {
                    "deployment_type": "standard",
                    "azure_region": "eastus",
                    "deployment_name": "test",
                    "pricing_meter": "test",
                    "pricing_snapshot_date": "2026-08-29",
                    "reasoning_configuration": "default",
                    "preprocessing_configuration": "test",
                    "portal_meter_verified": False,
                },
                "evaluator": {
                    "evaluator_id": "eval-1",
                    "conflict_of_interest_notes": "none",
                },
            }
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest),
            "--allow-missing-hd14",
            "--allow-dirty",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    out = tmp_path / "preflight-result.json"
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["overall"] == "FAIL"
    assert result.returncode != 0
