#!/usr/bin/env python3
"""Control plane mode: product (Photo Critic) vs demo (public portfolio)."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "control-plane.json"
MODE_ENV = "PHOTO_CRITIC_MODE"

PRODUCT_PROMPT_DIR = ROOT / "prompts" / "evaluation"
DEMO_PROMPT_DIR = ROOT / "examples" / "demo-prompt"
DEMO_HASH_REGISTRY = ROOT / "examples" / "demo-ledger-hashes.json"
PRODUCT_LEDGER = ROOT / "docs" / "07-DECISIONS.md"

PRODUCT_FROZEN_FILES = {
    "task_a": PRODUCT_PROMPT_DIR / "P1-A-v1.1.md",
    "task_b": PRODUCT_PROMPT_DIR / "P1-B-v1.1.md",
    "framework": PRODUCT_PROMPT_DIR / "P1-PHOTOGRAPHIC-CRITICAL-FRAMEWORK-v1.0.md",
    "output_contract": PRODUCT_PROMPT_DIR / "P1-OUTPUT-CONTRACT-v1.0.md",
    "cross_model_invariants": PRODUCT_PROMPT_DIR / "P1-CROSS-MODEL-INVARIANTS-v1.0.md",
}

DEMO_FROZEN_FILES = {
    "task_a": DEMO_PROMPT_DIR / "DEMO-A-v1.0.md",
    "task_b": DEMO_PROMPT_DIR / "DEMO-B-v1.0.md",
    "framework": DEMO_PROMPT_DIR / "DEMO-FRAMEWORK-v1.0.md",
    "output_contract": DEMO_PROMPT_DIR / "DEMO-OUTPUT-CONTRACT-v1.0.md",
    "cross_model_invariants": DEMO_PROMPT_DIR / "DEMO-INVARIANTS-v1.0.md",
}

PRODUCT_TASK_FILES = [("task_a", "P1-A-v1.1.md"), ("task_b", "P1-B-v1.1.md")]
DEMO_TASK_FILES = [("task_a", "DEMO-A-v1.0.md"), ("task_b", "DEMO-B-v1.0.md")]


def task_files() -> list[tuple[str, str]]:
    return DEMO_TASK_FILES if is_demo_mode() else PRODUCT_TASK_FILES


def get_mode() -> str:
    env = os.environ.get(MODE_ENV, "").strip().lower()
    if env in ("product", "demo"):
        return env
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            mode = str(data.get("mode", "product")).lower()
            if mode in ("product", "demo"):
                return mode
        except (json.JSONDecodeError, OSError):
            pass
    if DEMO_HASH_REGISTRY.exists() and not PRODUCT_LEDGER.exists():
        return "demo"
    return "product"


def is_demo_mode() -> bool:
    return get_mode() == "demo"


def frozen_files() -> dict[str, Path]:
    return DEMO_FROZEN_FILES if is_demo_mode() else PRODUCT_FROZEN_FILES


def prompt_dir() -> Path:
    return DEMO_PROMPT_DIR if is_demo_mode() else PRODUCT_PROMPT_DIR


def hash_registry_path() -> Path | None:
    return DEMO_HASH_REGISTRY if is_demo_mode() else None


def ledger_path() -> Path | None:
    return None if is_demo_mode() else PRODUCT_LEDGER


def frozen_prompt_paths() -> list[str]:
    files = frozen_files()
    return [str(p.relative_to(ROOT)).replace("\\", "/") for p in files.values()]
