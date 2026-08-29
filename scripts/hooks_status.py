#!/usr/bin/env python3
"""Report pre-commit / policy hook state: configured, installed, executed, passed."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE_COMMIT_CONFIG = ROOT / ".pre-commit-config.yaml"
HOOK_PATH = ROOT / ".git" / "hooks" / "pre-commit"
LAST_RUN_PATH = ROOT / "artifacts" / "evidence" / "policy-checks" / "last-run.json"


def is_configured() -> bool:
    return PRE_COMMIT_CONFIG.exists()


def is_installed() -> bool:
    if not HOOK_PATH.exists():
        return False
    try:
        content = HOOK_PATH.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "pre-commit" in content or "verify_policy" in content


def read_last_run() -> dict | None:
    if not LAST_RUN_PATH.exists():
        return None
    try:
        return json.loads(LAST_RUN_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def hooks_status() -> dict:
    last = read_last_run()
    configured = is_configured()
    installed = is_installed()
    executed = last is not None and last.get("executed") is True
    passed = last is not None and last.get("passed") is True

    return {
        "configured": configured,
        "installed": installed,
        "executed": executed,
        "passed": passed,
        "last_run_timestamp": last.get("timestamp") if last else None,
        "last_run_mode": last.get("mode") if last else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    status = hooks_status()
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        for key in ("configured", "installed", "executed", "passed"):
            print(f"{key}: {status[key]}")
        if status["last_run_timestamp"]:
            print(f"last_run: {status['last_run_timestamp']} ({status['last_run_mode']})")

    if not status["configured"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
