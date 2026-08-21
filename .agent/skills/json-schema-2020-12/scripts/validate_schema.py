#!/usr/bin/env python3
"""Validate a standalone schema as JSON Schema Draft 2020-12."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import ToolError, check_schema, emit_json, load_json, require_draft_2020_12


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one schema against the JSON Schema Draft 2020-12 meta-schema. "
            "The script rejects missing and different $schema declarations."
        )
    )
    parser.add_argument("schema", type=Path, help="path to the schema JSON document")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = args.schema.resolve()
    try:
        schema = require_draft_2020_12(load_json(path), path)
        check_schema(schema, path)
    except ToolError as exc:
        if args.json:
            emit_json({"document": str(path), "error": str(exc), "valid": False})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        emit_json(
            {
                "dialect": "https://json-schema.org/draft/2020-12/schema",
                "document": str(path),
                "valid": True,
            }
        )
    else:
        print(f"VALID SCHEMA: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
