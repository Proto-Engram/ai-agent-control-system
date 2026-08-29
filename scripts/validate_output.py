#!/usr/bin/env python3
"""Validate model output JSON against P1-OUTPUT-CONTRACT-v1.0 schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "p1-output-contract.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_data(data: object, schema: dict | None = None) -> list[str]:
    schema = schema or load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{list(e.path)}: {e.message}" for e in errors]


def validate_file(path: Path) -> tuple[object | None, list[str]]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"JSON parse error: {exc}"]
    return data, validate_data(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="JSON files or '-' for stdin")
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    args = parser.parse_args()

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    any_fail = False

    for raw in args.paths:
        if raw == "-":
            try:
                data = json.load(sys.stdin)
            except json.JSONDecodeError as exc:
                print(f"FAIL stdin: JSON parse error: {exc}", file=sys.stderr)
                any_fail = True
                continue
            errors = validate_data(data, schema)
            label = "stdin"
        else:
            path = Path(raw)
            data, errors = validate_file(path)
            label = str(path)

        if errors:
            any_fail = True
            print(f"FAIL {label}:", file=sys.stderr)
            for err in errors:
                print(f"  {err}", file=sys.stderr)
        else:
            print(f"PASS {label}")

    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
