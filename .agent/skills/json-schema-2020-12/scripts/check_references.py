#!/usr/bin/env python3
"""Resolve every static schema reference from an offline registry."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from referencing.exceptions import Unresolvable

from _common import (
    ToolError,
    add_registry_arguments,
    build_registry,
    check_schema,
    emit_json,
    iter_subschemas,
    json_pointer,
    load_json,
    require_draft_2020_12,
    schema_id,
)


@dataclass(frozen=True)
class Finding:
    document: str
    keyword: str
    pointer: str
    reference: str
    resolved: str
    valid: bool
    error: str | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve $ref and each $dynamicRef initial target without network access. "
            "Dynamic-scope selection is exercised by instance validation, not by this static check."
        )
    )
    parser.add_argument("schema", type=Path, help="root schema JSON document")
    add_registry_arguments(parser)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return parser


def references_in_document(
    *,
    document: Path,
    schema: Any,
    registry: Any,
) -> list[Finding]:
    initial_base = schema_id(schema) or document.resolve().as_uri()
    findings: list[Finding] = []
    for pointer_parts, subschema in iter_subschemas(schema):
        if not isinstance(subschema, dict):
            continue
        base = initial_base
        # Reconstruct base changes along the path by walking from the document root.
        current: Any = schema
        if isinstance(current, dict) and isinstance(current.get("$id"), str):
            base = urljoin(document.resolve().as_uri(), current["$id"])
        for part in pointer_parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and isinstance(part, int) and 0 <= part < len(current):
                current = current[part]
            else:
                break
            if isinstance(current, dict) and isinstance(current.get("$id"), str):
                base = urljoin(base, current["$id"])
        for keyword in ("$ref", "$dynamicRef"):
            reference = subschema.get(keyword)
            if not isinstance(reference, str):
                continue
            resolved_uri = urljoin(base, reference)
            try:
                target = registry.resolver(base).lookup(reference)
            except Unresolvable as exc:
                findings.append(
                    Finding(
                        document=str(document),
                        keyword=keyword,
                        pointer=json_pointer(pointer_parts + (keyword,)),
                        reference=reference,
                        resolved=resolved_uri,
                        valid=False,
                        error=str(exc),
                    )
                )
            else:
                target_is_schema = isinstance(target.contents, (dict, bool))
                findings.append(
                    Finding(
                        document=str(document),
                        keyword=keyword,
                        pointer=json_pointer(pointer_parts + (keyword,)),
                        reference=reference,
                        resolved=resolved_uri,
                        valid=target_is_schema,
                        error=(
                            None
                            if target_is_schema
                            else f"resolved target is {type(target.contents).__name__}, not a schema"
                        ),
                    )
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root_path = args.schema.resolve()
    try:
        root = require_draft_2020_12(load_json(root_path), root_path)
        check_schema(root, root_path)
        registry, resources = build_registry(
            root_schema=root,
            root_path=root_path,
            registry_manifest=args.registry,
            explicit_resources=args.resource,
        )
        documents: dict[Path, Any] = {root_path: root}
        for item in resources:
            documents[item.path] = item.contents
        findings: list[Finding] = []
        for path in sorted(documents, key=lambda value: str(value)):
            findings.extend(
                references_in_document(
                    document=path,
                    schema=documents[path],
                    registry=registry,
                )
            )
    except ToolError as exc:
        if args.json:
            emit_json({"error": str(exc), "valid": False})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    records = [finding.__dict__ for finding in findings]
    failed = [finding for finding in findings if not finding.valid]
    if args.json:
        emit_json(
            {
                "findings": records,
                "references": len(findings),
                "valid": not failed,
            }
        )
    else:
        for finding in findings:
            status = "OK" if finding.valid else "ERROR"
            line = (
                f"{status}: {finding.document} {finding.pointer} {finding.keyword} "
                f"{finding.reference!r} -> {finding.resolved}"
            )
            if finding.error:
                line += f" ({finding.error})"
            stream = sys.stdout if finding.valid else sys.stderr
            print(line, file=stream)
        print(
            f"REFERENCE CHECK: {len(findings)} reference(s), {len(failed)} unresolved",
            file=sys.stderr if failed else sys.stdout,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
