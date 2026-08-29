#!/usr/bin/env python3
"""Photo Critic repository policy checks for pre-commit."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".heif",
    ".raw",
    ".cr2",
    ".nef",
    ".arw",
    ".dng",
    ".tif",
    ".tiff",
    ".webp",
    ".gif",
}

ALLOWED_IMAGE_PREFIXES = (
    "docs/",
)

SENSITIVE_JSON_KEYS = ("local_path", "absolute_path", "source_path")
SENSITIVE_PATH_PATTERN = re.compile(
    r'"(?:local_path|absolute_path|source_path)"\s*:\s*"[^"]+"',
    re.IGNORECASE,
)
HOME_PATH_PATTERN = re.compile(
    r'["\'](?:[A-Za-z]:\\Users\\|/home/|/Users/)[^"\']+["\']'
)


def staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_no_images(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for rel in paths:
        suffix = Path(rel).suffix.lower()
        if suffix not in IMAGE_EXTENSIONS:
            continue
        if rel.startswith(ALLOWED_IMAGE_PREFIXES):
            continue
        errors.append(f"Image file staged outside approved paths: {rel}")
    return errors


def check_json_policy(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for rel in paths:
        if not rel.endswith(".json"):
            continue
        if rel.startswith("artifacts/"):
            continue
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if SENSITIVE_PATH_PATTERN.search(text):
            errors.append(f"Sensitive path key in staged JSON: {rel}")
        if HOME_PATH_PATTERN.search(text):
            errors.append(f"Absolute home/user path in staged JSON: {rel}")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        if _json_has_sensitive_keys(data):
            errors.append(f"Sensitive path key in staged JSON object: {rel}")
    return errors


def _json_has_sensitive_keys(obj: object) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in SENSITIVE_JSON_KEYS and isinstance(value, str) and value:
                return True
            if _json_has_sensitive_keys(value):
                return True
    elif isinstance(obj, list):
        return any(_json_has_sensitive_keys(item) for item in obj)
    return False


def main() -> int:
    paths = staged_files()
    if not paths:
        return 0

    errors: list[str] = []
    errors.extend(check_no_images(paths))
    errors.extend(check_json_policy(paths))

    if errors:
        for err in errors:
            print(f"POLICY FAIL: {err}", file=sys.stderr)
        return 1

    print("Photo Critic repo policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
