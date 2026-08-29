#!/usr/bin/env python3
"""Minimal P1 experiment runner — refuses execution without live preflight PASS."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_NAME = "preflight-result.json"


def execute_live_preflight(manifest_path: Path) -> tuple[int, dict | None]:
    """Run preflight subprocess — production path never uses cached JSON as authorization."""
    cmd = [
        sys.executable,
        "scripts/preflight_p1.py",
        "--manifest",
        str(manifest_path),
    ]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    preflight_path = manifest_path.parent / PREFLIGHT_NAME
    preflight_data = None
    if preflight_path.exists():
        try:
            preflight_data = json.loads(preflight_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            preflight_data = None
    return result.returncode, preflight_data


def validate_preflight_binding(preflight: dict, manifest_path: Path) -> list[str]:
    """Reject stale or mismatched evidence JSON even if overall says PASS."""
    errors: list[str] = []
    if preflight.get("overall") != "PASS":
        errors.append("preflight overall is not PASS")
        return errors

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    current_commit = head.stdout.strip() if head.returncode == 0 else None
    if preflight.get("git_commit") != current_commit:
        errors.append("preflight git_commit does not match current HEAD")

    import hashlib

    manifest_bytes = manifest_path.read_bytes()
    current_manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    if preflight.get("manifest_sha256") != current_manifest_sha:
        errors.append("preflight manifest_sha256 does not match current manifest")

    if not preflight.get("preflight_version"):
        errors.append("preflight_version missing from result")

    hd14 = next((c for c in preflight.get("checks", []) if c.get("id") == "hd14_execution_approved"), None)
    if not hd14 or hd14.get("status") != "PASS":
        errors.append("HD-14 execution authorization check did not PASS")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify gate only — do not call external APIs (default behavior)",
    )
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    exit_code, preflight = execute_live_preflight(manifest_path)
    if exit_code != 0:
        print("ERROR: live preflight execution failed", file=sys.stderr)
        if preflight:
            for check in preflight.get("checks", []):
                if check.get("status") != "PASS":
                    print(f"  FAIL: {check.get('id')}: {check.get('detail')}", file=sys.stderr)
        else:
            print("  (no preflight result written)", file=sys.stderr)
        return 1

    if preflight is None:
        print("ERROR: preflight completed but result JSON missing", file=sys.stderr)
        return 1

    binding_errors = validate_preflight_binding(preflight, manifest_path)
    if binding_errors:
        print("ERROR: preflight binding validation failed", file=sys.stderr)
        for err in binding_errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print("Gate check: PASS (live preflight)")
    print(f"Manifest: {manifest_path}")
    print(f"Preflight evidence: {manifest_path.parent / PREFLIGHT_NAME}")

    if args.dry_run:
        print("Dry-run mode — no external API calls made.")
        print("Full runner implementation deferred until human authorizes P1 execution.")
        return 0

    print("ERROR: Live API execution not implemented. Use --dry-run.", file=sys.stderr)
    print(
        "HUMAN DECISION REQUIRED: P1 execution requires authorized runner with HD-10 scope enforcement.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
