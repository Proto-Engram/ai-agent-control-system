"""Tests for verification evidence bundle binding."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_verification_bundle import SESSION_NOTE, check_bundle, sha256_file


def _worker_bundle(task_id: str = "bundle-test") -> dict:
    return {
        "role": "worker",
        "task_id": task_id,
        "timestamp": "2026-08-29T00:00:00+00:00",
        "git": {"commit": "abc123", "status_porcelain": "", "clean": True},
        "commands": [
            {"id": "hd13_hash_verify", "command": ["python", "scripts/hash_prompts.py"], "exit_code": 0},
            {"id": "pytest", "command": ["python", "-m", "pytest"], "exit_code": 0},
        ],
        "overall_pass": True,
    }


def _verifier_bundle(task_id: str, worker_hash: str, commit: str) -> dict:
    return {
        "role": "verifier",
        "task_id": task_id,
        "timestamp": "2026-08-29T00:00:01+00:00",
        "verified_git_commit": commit,
        "worker_evidence_sha256": worker_hash,
        "commands": [
            {"id": "hd13_hash_verify", "command": ["python", "scripts/hash_prompts.py"], "exit_code": 0},
            {"id": "pytest", "command": ["python", "-m", "pytest"], "exit_code": 0},
        ],
        "overall_pass": True,
        "session_independence_note": SESSION_NOTE,
    }


def test_valid_bundle_passes(tmp_path, monkeypatch):
    task_id = "bundle-test"
    base = tmp_path / task_id
    base.mkdir()
    worker_path = base / "worker-evidence.json"
    worker_path.write_text(json.dumps(_worker_bundle(task_id)), encoding="utf-8")
    worker_hash = sha256_file(worker_path)

    import subprocess

    def fake_rev_parse(*args, **kwargs):
        return type("R", (), {"returncode": 0, "stdout": "abc123\n", "stderr": ""})()

    monkeypatch.setattr(subprocess, "run", fake_rev_parse)

    verifier_path = base / "verifier-evidence.json"
    verifier_path.write_text(
        json.dumps(_verifier_bundle(task_id, worker_hash, "abc123")),
        encoding="utf-8",
    )

    ok, errors = check_bundle(task_id, evidence_dir=base)
    assert ok is True, errors


def test_wrong_worker_hash_fails(tmp_path, monkeypatch):
    task_id = "bundle-forged"
    base = tmp_path / task_id
    base.mkdir()
    worker_path = base / "worker-evidence.json"
    worker_path.write_text(json.dumps(_worker_bundle(task_id)), encoding="utf-8")

    import subprocess

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "abc123\n", "stderr": ""})(),
    )

    verifier_path = base / "verifier-evidence.json"
    verifier_path.write_text(
        json.dumps(_verifier_bundle(task_id, "f" * 64, "abc123")),
        encoding="utf-8",
    )

    ok, errors = check_bundle(task_id, evidence_dir=base)
    assert ok is False
    assert any("worker_evidence_sha256" in e for e in errors)


def test_missing_replay_checks_fails(tmp_path, monkeypatch):
    task_id = "bundle-missing-replay"
    base = tmp_path / task_id
    base.mkdir()
    worker_path = base / "worker-evidence.json"
    worker_path.write_text(json.dumps(_worker_bundle(task_id)), encoding="utf-8")
    worker_hash = sha256_file(worker_path)

    import subprocess

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "abc123\n", "stderr": ""})(),
    )

    bad_verifier = _verifier_bundle(task_id, worker_hash, "abc123")
    bad_verifier["commands"] = [{"id": "hd13_hash_verify", "command": [], "exit_code": 0}]
    (base / "verifier-evidence.json").write_text(json.dumps(bad_verifier), encoding="utf-8")

    ok, errors = check_bundle(task_id, evidence_dir=base)
    assert ok is False
    assert any("missing required replay" in e for e in errors)
