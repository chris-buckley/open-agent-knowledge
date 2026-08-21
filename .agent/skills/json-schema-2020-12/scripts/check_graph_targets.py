#!/usr/bin/env python3
"""Check graph-wide target existence after structural JSON Schema validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from _common import ToolError, emit_json, json_pointer, load_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check that every relationship from/to value names a node in the same System instance. "
            "This is an example project rule, not standard JSON Schema behavior."
        )
    )
    parser.add_argument("instance", type=Path, help="System instance JSON document")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return parser


def node_ids(
    nodes: Any,
    *,
    path: tuple[object, ...] = ("nodes",),
) -> tuple[set[str], list[str]]:
    found: set[str] = set()
    errors: list[str] = []
    if not isinstance(nodes, list):
        return found, [f"{json_pointer(path)} must be an array before graph checking"]
    for index, node in enumerate(nodes):
        node_path = path + (index,)
        if not isinstance(node, dict):
            errors.append(f"{json_pointer(node_path)} must be an object")
            continue
        value = node.get("id")
        id_path = json_pointer(node_path + ("id",))
        if not isinstance(value, str) or not value:
            errors.append(f"{id_path} must be a non-empty string before graph checking")
        elif value in found:
            errors.append(f"{id_path}: duplicate node id {value!r}")
        else:
            found.add(value)
        if "children" in node:
            children, child_errors = node_ids(
                node["children"],
                path=node_path + ("children",),
            )
            overlap = found.intersection(children)
            for duplicate in sorted(overlap):
                errors.append(
                    f"{json_pointer(node_path + ('children',))}: "
                    f"duplicate node id {duplicate!r}"
                )
            found.update(children)
            errors.extend(child_errors)
    return found, errors


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = args.instance.resolve()
    try:
        instance = load_json(path)
        if not isinstance(instance, dict):
            raise ToolError(f"{path}: System instance must be an object")
        identifiers, errors = node_ids(instance.get("nodes"))
        relationships = instance.get("relationships")
        if not isinstance(relationships, list):
            errors.append("/relationships must be an array before graph checking")
        else:
            for index, relationship in enumerate(relationships):
                relationship_path = ("relationships", index)
                if not isinstance(relationship, dict):
                    errors.append(f"{json_pointer(relationship_path)} must be an object")
                    continue
                for field in ("from", "to"):
                    field_path = json_pointer(relationship_path + (field,))
                    target = relationship.get(field)
                    if not isinstance(target, str) or not target:
                        errors.append(
                            f"{field_path} must be a non-empty string before graph checking"
                        )
                    elif target not in identifiers:
                        errors.append(f"{field_path}: target {target!r} does not exist")
    except ToolError as exc:
        if args.json:
            emit_json({"error": str(exc), "valid": False})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = sorted(set(errors))
    if args.json:
        emit_json(
            {
                "errors": errors,
                "instance": str(path),
                "nodeCount": len(identifiers),
                "valid": not errors,
            }
        )
    elif errors:
        for error in errors:
            print(f"ERROR: {path} {error}", file=sys.stderr)
        print(f"INVALID GRAPH: {path}", file=sys.stderr)
    else:
        print(f"VALID GRAPH TARGETS: {path}; {len(identifiers)} node(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
