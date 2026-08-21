#!/usr/bin/env python3
"""Validate an instance under an explicit Draft 2020-12 schema, offline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from _common import (
    ToolError,
    add_registry_arguments,
    build_registry,
    catch_reference_error,
    check_schema,
    emit_json,
    format_checker_for_policy,
    iter_error_records,
    load_json,
    render_error_text,
    require_draft_2020_12,
    sorted_validation_errors,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a JSON instance with JSON Schema Draft 2020-12. "
            "References resolve only from the supplied in-memory registry; network access is never attempted."
        )
    )
    parser.add_argument("schema", type=Path, help="path to the root schema JSON document")
    parser.add_argument("instance", type=Path, help="path to the instance JSON document")
    add_registry_arguments(parser)
    parser.add_argument(
        "--format-policy",
        choices=("annotation", "assert-known"),
        default="annotation",
        help=(
            "annotation: report but do not assert format keywords (Draft 2020-12 default); "
            "assert-known: assert every format and fail if any format lacks a registered checker"
        ),
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    schema_path = args.schema.resolve()
    instance_path = args.instance.resolve()
    try:
        schema = require_draft_2020_12(load_json(schema_path), schema_path)
        check_schema(schema, schema_path)
        instance = load_json(instance_path)
        registry, resources = build_registry(
            root_schema=schema,
            root_path=schema_path,
            registry_manifest=args.registry,
            explicit_resources=args.resource,
        )
        checker, format_names = format_checker_for_policy(
            args.format_policy,
            schemas=[schema, *(resource.contents for resource in resources)],
        )
        validator = Draft202012Validator(
            schema,
            registry=registry,
            format_checker=checker,
        )
        errors = sorted_validation_errors(validator, instance)
    except ToolError as exc:
        if args.json:
            emit_json(
                {
                    "error": str(exc),
                    "instance": str(instance_path),
                    "schema": str(schema_path),
                    "valid": False,
                }
            )
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # reference failures can be wrapped by jsonschema
        reference_error = catch_reference_error(exc)
        if reference_error is None:
            raise
        if args.json:
            emit_json(
                {
                    "error": str(reference_error),
                    "instance": str(instance_path),
                    "schema": str(schema_path),
                    "valid": False,
                }
            )
        else:
            print(f"ERROR: {reference_error}", file=sys.stderr)
        return 2

    if errors:
        records = [record for error in errors for record in iter_error_records(error)]
        if args.json:
            emit_json(
                {
                    "errors": records,
                    "formatKeywords": list(format_names),
                    "formatPolicy": args.format_policy,
                    "instance": str(instance_path),
                    "schema": str(schema_path),
                    "valid": False,
                }
            )
        else:
            for error in errors:
                for line in render_error_text(error, document=instance_path):
                    print(f"ERROR: {line}", file=sys.stderr)
            print(
                f"INVALID INSTANCE: {instance_path} ({len(errors)} top-level error(s)); "
                f"format-policy={args.format_policy}",
                file=sys.stderr,
            )
        return 1

    if args.json:
        emit_json(
            {
                "formatKeywords": list(format_names),
                "formatPolicy": args.format_policy,
                "instance": str(instance_path),
                "schema": str(schema_path),
                "valid": True,
            }
        )
    else:
        format_note = (
            "none present"
            if not format_names
            else ", ".join(format_names)
        )
        print(
            f"VALID INSTANCE: {instance_path}; format-policy={args.format_policy}; "
            f"format-keywords={format_note}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
