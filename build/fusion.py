"""Fuse a capability entry with declarative knowledge, not arbitrary agent graphs.

The entry owns instructions, state, triggers, processes, and interfaces. Supporting
nodes may supply only constants and schemas. This deliberately refuses to widen
another document's policy, state, arrival, or execution scope.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import PurePosixPath
import re

from oak import Act, Call, Constant, ConstantValue, Interface, Node, Process, Schema, State, Trigger, parse, resolve
from oak.base import OakModel
from oak.node.parts.entry import Entry

_TARGET_FIELDS: dict[type[OakModel], dict[str, type[Entry]]] = {
    Constant: {"schema_id": Schema},
    State: {"schema_id": Schema},
    Interface: {"schema_id": Schema},
    Process: {"input": Schema, "output": Schema},
    Act: {"input": Schema, "output": Schema},
    Call: {"process": Process},
    Trigger: {"process": Process},
    ConstantValue: {"constant": Constant},
}


def fuse(documents: Mapping[str, str], *, entry: str) -> Node:
    """Resolve exact documents, namespace definitions, and rewrite typed targets.

    Literal JSON, schema templates, example OAK, tool names, and prose are never
    string-replaced. Every supplied knowledge document must be reachable. The
    result is freshly validated, and no relative executable target remains.
    """
    if entry not in documents:
        raise ValueError("fusion entry is missing")
    for path in documents:
        name = PurePosixPath(path)
        if name.is_absolute() or ".." in name.parts or name.as_posix() != path:
            raise ValueError(f"fusion requires normalized package-relative paths: {path}")
    nodes = {path: parse(text) for path, text in documents.items()}
    for path, node in nodes.items():
        if path != entry and any((node.instructions, node.state, node.triggers, node.processes, node.interfaces)):
            raise ValueError(f"fusion would change operational or instruction scope: {path}")
    graph = resolve(nodes[entry], source=entry, load=nodes.get)
    if set(graph.documents) != set(nodes):
        raise ValueError(f"unreferenced fusion knowledge: {sorted(set(nodes) - set(graph.documents))}")

    # Stable path ordering follows the numbered guides, independent of graph traversal.
    order = [entry, *sorted(path for path in nodes if path != entry)]
    identities: dict[tuple[str, str], str] = {}
    used: set[str] = set()
    for index, path in enumerate(order):
        for part in Node.model_fields:
            for item in getattr(nodes[path], part):
                identifier = item.id if path == entry else f"guide-{index}-{item.id}"
                if identifier in used:
                    raise ValueError(f"fused identifier collision: {identifier}")
                used.add(identifier)
                identities[path, item.id] = identifier

    def target(source: str, value: str, expected: type[Entry]) -> str:
        document, item = graph.entry(source, value, expected)
        part = {Constant: "constant", Schema: "schema", Process: "process"}[expected]
        return f"{part}.{identities[document, item.id]}"

    def encoded(value: object, source: str) -> object:
        if isinstance(value, OakModel):
            fields = type(value).model_fields
            result = {
                field.alias or name: encoded(getattr(value, name), source)
                for name, field in fields.items()
            }
            if isinstance(value, Entry):
                result["id"] = identities[source, value.id]
            for name, expected in _TARGET_FIELDS.get(type(value), {}).items():
                original = getattr(value, name)
                if original is not None:
                    result[fields[name].alias or name] = target(source, original, expected)
            return result
        if isinstance(value, list):
            return [encoded(item, source) for item in value]
        if isinstance(value, dict):
            return {key: encoded(item, source) for key, item in value.items()}
        return value

    # Host prose cannot secretly serve as a second reference syntax.
    root = nodes[entry]
    prose = [instruction.body for instruction in root.instructions]
    from oak.node.parts.processes.steps import iter_steps
    prose.extend(step.instruction for process in root.processes for step in iter_steps(process.steps) if isinstance(step, Act))
    if any(re.search(r"\.oak\.md#(?:schema|constant|process)\.", text) for text in prose):
        raise ValueError("fusion dependencies in prose must be expressed as typed target bindings")

    merged = {
        part: [encoded(item, path) for path in order for item in getattr(nodes[path], part)]
        for part in Node.model_fields
    }
    node = Node.model_validate(merged)
    resolve(node)  # A standalone result may not need a loader or a source identity.
    return node
