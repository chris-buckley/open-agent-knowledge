#!/usr/bin/env python3
"""Inspect JSON-LD identities and graph-wide reference targets."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable
from urllib.parse import urlparse

try:
    from jsonld_common import (
        JsonLdSkillError,
        LocalDocumentRegistry,
        MAX_CONTEXT_DEPTH,
        MAX_CONTEXT_URLS,
        MAX_INPUT_BYTES,
        MAX_JSON_DEPTH,
        MAX_OUTPUT_BYTES,
        canonical_json_bytes,
        default_registry_path,
        load_json_path,
        load_processor,
        preflight_contexts,
    )
except ImportError:
    from .jsonld_common import (
        JsonLdSkillError,
        LocalDocumentRegistry,
        MAX_CONTEXT_DEPTH,
        MAX_CONTEXT_URLS,
        MAX_INPUT_BYTES,
        MAX_JSON_DEPTH,
        MAX_OUTPUT_BYTES,
        canonical_json_bytes,
        default_registry_path,
        load_json_path,
        load_processor,
        preflight_contexts,
    )

DEFAULT_REFERENCE_PROPERTIES = (
    "https://example.org/term/extends",
    "https://example.org/term/from",
    "https://example.org/term/links_to",
    "https://example.org/term/to",
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("inputs", nargs="+", help="One or more JSON-LD documents")
    p.add_argument("--engine", choices=("pyld", "profile"), default="pyld")
    p.add_argument("--registry", default=str(default_registry_path()))
    p.add_argument("--base")
    p.add_argument("--reference-property", action="append", default=[])
    p.add_argument(
        "--allow-target",
        action="append",
        default=[],
        help="Exact external target IRI or compact identifier allowed without a local definition",
    )
    p.add_argument(
        "--allow-target-prefix",
        action="append",
        default=[],
        help="External target prefix allowed without a local definition",
    )
    p.add_argument("--output")
    p.add_argument("--max-input-bytes", type=int, default=MAX_INPUT_BYTES)
    p.add_argument("--max-output-bytes", type=int, default=MAX_OUTPUT_BYTES)
    p.add_argument("--max-json-depth", type=int, default=MAX_JSON_DEPTH)
    p.add_argument("--max-context-depth", type=int, default=MAX_CONTEXT_DEPTH)
    p.add_argument("--max-context-urls", type=int, default=MAX_CONTEXT_URLS)
    return p


def _is_absolute_or_blank(identifier: str) -> bool:
    return identifier.startswith("_:") or bool(urlparse(identifier).scheme)


def _walk_refs(node: Any, properties: set[str], path: str = "$") -> Iterable[dict[str, str]]:
    if not isinstance(node, dict):
        return
    for prop, raw in node.items():
        if prop == "@reverse" and isinstance(raw, dict):
            for reverse_prop, values in raw.items():
                if reverse_prop in properties:
                    for index, value in enumerate(values if isinstance(values, list) else [values]):
                        if isinstance(value, dict) and isinstance(value.get("@id"), str):
                            yield {
                                "path": f"{path}.@reverse[{reverse_prop!r}][{index}]",
                                "property": reverse_prop,
                                "target": value["@id"],
                            }
            continue
        if prop not in properties:
            continue
        for index, value in enumerate(raw if isinstance(raw, list) else [raw]):
            if isinstance(value, dict) and isinstance(value.get("@id"), str):
                yield {
                    "path": f"{path}[{prop!r}][{index}]",
                    "property": prop,
                    "target": value["@id"],
                }


def main() -> None:
    args = parser().parse_args()
    try:
        registry = LocalDocumentRegistry(args.registry, max_document_bytes=args.max_input_bytes)
        processor = load_processor(args.engine, registry)
        properties = set(DEFAULT_REFERENCE_PROPERTIES) | set(args.reference_property)
        provenance: list[dict[str, Any]] = []
        all_nodes: list[dict[str, Any]] = []
        definition_sources: dict[str, list[str]] = {}
        issues: list[dict[str, Any]] = []
        for input_path in args.inputs:
            document, source = load_json_path(
                input_path,
                max_bytes=args.max_input_bytes,
                max_depth=args.max_json_depth,
            )
            source["context_preflight"] = preflight_contexts(
                document,
                registry,
                max_context_depth=args.max_context_depth,
                max_context_urls=args.max_context_urls,
            )
            expanded = processor.expand(document, base=args.base)
            flattened = processor.flatten(expanded, None, base=args.base)
            if isinstance(flattened, dict):
                flattened = flattened.get("@graph", [])
            for node in flattened:
                if not isinstance(node, dict) or not isinstance(node.get("@id"), str):
                    continue
                identifier = node["@id"]
                definition_sources.setdefault(identifier, []).append(source["source_path"])
                tagged = dict(node)
                tagged["__source_path"] = source["source_path"]
                all_nodes.append(tagged)
            provenance.append(source)
        definitions = set(definition_sources)
        for identifier, sources in sorted(definition_sources.items()):
            if len(sources) > 1:
                matching = [node for node in all_nodes if node.get("@id") == identifier]
                forms = {
                    json.dumps(
                        {key: value for key, value in node.items() if key != "__source_path"},
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    for node in matching
                }
                severity = "warning" if len(forms) == 1 else "error"
                issues.append(
                    {
                        "code": "duplicate_application_identity",
                        "severity": severity,
                        "identifier": identifier,
                        "sources": sorted(sources),
                        "message": "The same identifier is defined more than once"
                        + (" with different node content" if len(forms) > 1 else " with identical content"),
                    }
                )
            if identifier.startswith("_:"):
                issues.append(
                    {
                        "code": "blank_node_instability",
                        "severity": "warning",
                        "identifier": identifier,
                        "message": "Blank-node identifiers are local processing labels, not durable identities",
                    }
                )
            elif not _is_absolute_or_blank(identifier):
                issues.append(
                    {
                        "code": "relative_identifier",
                        "severity": "error",
                        "identifier": identifier,
                        "message": "Identifier did not resolve to an absolute IRI",
                    }
                )
        allowed_exact = set(args.allow_target)
        allowed_prefixes = tuple(args.allow_target_prefix)
        for node_index, node in enumerate(all_nodes):
            source_path = str(node.pop("__source_path"))
            for reference in _walk_refs(node, properties, path=f"$nodes[{node_index}]"):
                target = reference["target"]
                if not _is_absolute_or_blank(target):
                    issues.append(
                        {
                            "code": "relative_reference_target",
                            "severity": "error",
                            "identifier": node.get("@id"),
                            "path": reference["path"],
                            "target": target,
                            "source": source_path,
                            "message": "Reference target did not resolve to an absolute IRI",
                        }
                    )
                elif target not in definitions and target not in allowed_exact and not target.startswith(allowed_prefixes):
                    issues.append(
                        {
                            "code": "missing_reference_target",
                            "severity": "error",
                            "identifier": node.get("@id"),
                            "path": reference["path"],
                            "property": reference["property"],
                            "target": target,
                            "source": source_path,
                            "message": "A structurally valid node reference has no loaded target definition",
                        }
                    )
        issue_counts = Counter(issue["severity"] for issue in issues)
        result = {
            "ok": issue_counts["error"] == 0,
            "operation": "inspect_graph",
            "engine": args.engine,
            "sources": provenance,
            "summary": {
                "documents": len(args.inputs),
                "defined_nodes": len(definitions),
                "errors": issue_counts["error"],
                "warnings": issue_counts["warning"],
            },
            "issues": sorted(
                issues,
                key=lambda item: (
                    item.get("severity", ""),
                    item.get("code", ""),
                    item.get("identifier", ""),
                    item.get("path", ""),
                ),
            ),
        }
        encoded = canonical_json_bytes(result)
        if len(encoded) > args.max_output_bytes:
            raise JsonLdSkillError("output_too_large", "Inspection output exceeds configured limit")
        if args.output:
            target = Path(args.output).expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(encoded)
        else:
            sys.stdout.buffer.write(encoded)
        raise SystemExit(0 if result["ok"] else 1)
    except JsonLdSkillError as exc:
        sys.stderr.buffer.write(canonical_json_bytes({"ok": False, "error": exc.as_dict()}))
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
