#!/usr/bin/env python3
"""Compute frozen prompt hashes (LF-normalized UTF-8 canonical form)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.control_plane import (  # noqa: E402
    frozen_files,
    get_mode,
    hash_registry_path,
    is_demo_mode,
    ledger_path,
    prompt_dir,
    task_files,
)


def normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(normalize_lf(text).encode("utf-8")).hexdigest()


def sha256_raw_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_normalized(path: Path) -> str:
    return normalize_lf(path.read_text(encoding="utf-8"))


def extract_fenced(text: str, after_heading: str | None = None) -> str:
    scope = text
    if after_heading:
        idx = text.find(after_heading)
        if idx < 0:
            raise ValueError(f"Heading not found: {after_heading!r}")
        scope = text[idx:]
    match = re.search(r"```\n(.*?)```", scope, re.DOTALL)
    if not match:
        raise ValueError(f"No fenced block found after {after_heading!r}")
    return match.group(1)


def compute_all() -> dict:
    files = frozen_files()
    pdir = prompt_dir()
    framework_text = read_normalized(files["framework"])
    fw_block = extract_fenced(framework_text, "## Semantic module")

    result: dict = {
        "mode": get_mode(),
        "integrity_spec": {
            "canonical": "sha256_lf_normalized_utf8",
            "provenance_optional": "sha256_raw_file_bytes_utf8",
        },
        "files_canonical": {},
        "files_raw_provenance": {},
        "composed_system": {},
        "user_templates": {},
        "framework_semantic_module": sha256_text(fw_block),
    }

    for key, path in files.items():
        text = read_normalized(path)
        result["files_canonical"][key] = sha256_text(text)
        result["files_raw_provenance"][key] = sha256_raw_bytes(path)

    for task_key, filename in task_files():
        text = read_normalized(pdir / filename)
        task_sys = extract_fenced(text, "## System message (semantic")
        user_tpl = extract_fenced(text, "## User message template")
        result["composed_system"][task_key] = sha256_text(task_sys + fw_block)
        result["user_templates"][task_key] = sha256_text(user_tpl)

    return result


def canonical_hash_set(hashes: dict) -> set[str]:
    values = set(hashes["files_canonical"].values())
    values.update(hashes["composed_system"].values())
    values.update(hashes["user_templates"].values())
    values.add(hashes["framework_semantic_module"])
    return values


def load_expected_from_ledger() -> set[str]:
    ledger = ledger_path()
    if ledger is None or not ledger.exists():
        return set()
    text = ledger.read_text(encoding="utf-8")
    section_match = re.search(
        r"### HD-13 — Evaluation Phase P1 Prompt Freeze(.*?)---\n\n## HUMAN DECISIONS REQUIRED",
        text,
        re.DOTALL,
    )
    if not section_match:
        section_match = re.search(
            r"### HD-13 — Evaluation Phase P1 Prompt Freeze(.*?)---\n\n### HD-",
            text,
            re.DOTALL,
        )
    if not section_match:
        return set()
    section = section_match.group(1)
    return set(re.findall(r"`([a-f0-9]{64})`", section))


def load_expected_from_demo_registry() -> set[str]:
    registry = hash_registry_path()
    if registry is None or not registry.exists():
        return set()
    data = json.loads(registry.read_text(encoding="utf-8"))
    expected = data.get("expected_hashes")
    if isinstance(expected, list):
        return set(expected)
    return canonical_hash_set(data)


def load_expected_hashes() -> set[str]:
    if is_demo_mode():
        return load_expected_from_demo_registry()
    return load_expected_from_ledger()


def verify(hashes: dict) -> list[str]:
    errors: list[str] = []
    expected = load_expected_hashes()
    if not expected:
        if is_demo_mode():
            errors.append("Demo hash registry not found: examples/demo-ledger-hashes.json")
        else:
            errors.append("HD-13 section not found in docs/07-DECISIONS.md")
        return errors

    computed = canonical_hash_set(hashes)
    for h in expected:
        if h not in computed:
            errors.append(f"Registry hash not matched by computed hashes: {h}")
    for h in computed:
        if h not in expected:
            errors.append(f"Computed hash missing from registry: {h}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Verify against ledger or demo registry")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    hashes = compute_all()
    if args.verify:
        errors = verify(hashes)
        if errors:
            for err in errors:
                print(f"VERIFY FAIL: {err}", file=sys.stderr)
            return 1
        label = "Demo prompt hash verification" if is_demo_mode() else "HD-13 prompt hash verification"
        print(f"{label}: PASS")
        return 0

    if args.json:
        print(json.dumps(hashes, indent=2))
        return 0

    print(f"=== Prompt hashes ({get_mode()} mode, LF-normalized UTF-8) ===")
    for key, value in hashes["files_canonical"].items():
        print(f"{key}: {value}")
    print("\n=== Composed runtime hashes ===")
    print(f"framework_semantic_module: {hashes['framework_semantic_module']}")
    for key, value in hashes["composed_system"].items():
        print(f"composed_system.{key}: {value}")
    for key, value in hashes["user_templates"].items():
        print(f"user_templates.{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
