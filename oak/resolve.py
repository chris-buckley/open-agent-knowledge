"""Explicit offline resolution for one reachable OAK document graph."""

from __future__ import annotations

import posixpath
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import TypeVar

from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node import Node
from oak.node.graph import entry_registry
from oak.node.parts import (
    Act,
    All,
    Any,
    Assert,
    Call,
    Compare,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    Foreach,
    If,
    Interface,
    Not,
    Par,
    Process,
    Schema,
    Set,
    Step,
    Trigger,
    Value,
)
from oak.node.parts.processes import (
    process_visible_bindings,
    validate_call_contract,
    validate_process_contract,
)
from oak.parse import OakParseError, parse
from oak.vocabulary.text.target_path import is_relative_target, split_target

DocumentSource = str | bytes | Node
DocumentLoader = Callable[[str], DocumentSource | None]
TargetEntry = TypeVar("TargetEntry", bound=Entry)


@dataclass(frozen=True, slots=True)
class ResolutionFailure:
    """One stable document-graph resolution failure."""

    code: str
    source: str | None
    target: str
    message: str

    def __str__(self) -> str:
        location = self.source or "<unknown>"
        return f"[{self.code}] {location} -> {self.target}: {self.message}"


class ResolutionError(ValueError):
    """One explicit document-graph resolution failure."""

    def __init__(self, failure: ResolutionFailure) -> None:
        self.failure = failure
        self.code = failure.code
        super().__init__(str(failure))


def _raise(code: str, source: str | None, target: str, message: str) -> None:
    raise ResolutionError(ResolutionFailure(code, source, target, message))


def _normalize_source(source: str) -> str:
    if "\\" in source or "\x00" in source or "?" in source or "#" in source:
        _raise("invalid_document_path", source, source, "source path must be a clean POSIX path")
    normalized = posixpath.normpath(source)
    if normalized in ("", ".", "..") or source.endswith("/"):
        _raise("invalid_document_path", source, source, "source path must identify one .oak.md document")
    if not normalized.endswith(".oak.md"):
        _raise("invalid_document_path", source, source, "source path must end in .oak.md")
    return normalized


def _resolve_document(source: str, relative: str, root: str | None) -> str:
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), relative))
    if root is not None:
        root_path = posixpath.normpath(root)
        try:
            common = posixpath.commonpath((root_path, target))
        except ValueError:
            common = ""
        if common != root_path:
            _raise("invalid_document_path", source, relative, "relative target escapes the allowed root")
    return target


def _condition_values(condition: Condition) -> Iterator[Value]:
    if isinstance(condition, Compare):
        yield condition.left
        yield condition.right
    elif isinstance(condition, (All, Any)):
        for child in condition.conditions:
            yield from _condition_values(child)
    elif isinstance(condition, Not):
        yield from _condition_values(condition.condition)


def _value_targets(values: Iterable[Value]) -> Iterator[tuple[str, type[Entry]]]:
    for value in values:
        if isinstance(value, ConstantValue):
            yield value.constant, Constant


def _step_references(step: Step) -> Iterator[tuple[str, type[Entry]]]:
    if isinstance(step, Act):
        yield from _value_targets(binding.value for binding in step.inputs)
    elif isinstance(step, Set):
        yield from _value_targets((step.value,))
    elif isinstance(step, Emit):
        yield from _value_targets(binding.value for binding in step.bindings)
    elif isinstance(step, If):
        yield from _value_targets(_condition_values(step.condition))
        for child in step.then:
            yield from _step_references(child)
        if step.otherwise is not None:
            for child in step.otherwise:
                yield from _step_references(child)
    elif isinstance(step, Assert):
        yield from _value_targets(_condition_values(step.condition))
    elif isinstance(step, Foreach):
        yield from _value_targets((step.value,))
        for child in step.steps:
            yield from _step_references(child)
    elif isinstance(step, Par):
        for child in step.steps:
            yield from _step_references(child)
    elif isinstance(step, Call):
        yield from _value_targets(binding.value for binding in step.inputs)
        yield step.process, Process


def iter_targets(node: Node) -> Iterator[tuple[str, type[Entry]]]:
    """Yield every resolvable typed target in one document."""
    for interface in node.interfaces:
        yield interface.schema_id, Schema
    for process in node.processes:
        if process.input is not None:
            yield process.input, Schema
        if process.output is not None:
            yield process.output, Schema
    for trigger in node.triggers:
        yield trigger.then, Process
        if trigger.given is not True:
            yield from _value_targets(_condition_values(trigger.given))
    for process in node.processes:
        for step in process.steps:
            yield from _step_references(step)


def _steps_targets_in_process(steps: list[Step]) -> Iterator[tuple[str, type[Entry]]]:
    for step in steps:
        yield from _step_references(step)


@dataclass(frozen=True, slots=True)
class ResolvedGraph:
    """One explicitly loaded and type-checked OAK document graph."""

    root: str
    documents: Mapping[str, Node]
    registries: Mapping[str, Mapping[str, Entry]]

    def target_document(self, source: str, target: str) -> str:
        """Return the normalized document selected by one target."""
        relative, _part, _identifier = split_target(target)
        return source if relative is None else posixpath.normpath(posixpath.join(posixpath.dirname(source), relative))

    def entry(self, source: str, target: str, expected: type[TargetEntry]) -> tuple[str, TargetEntry]:
        """Return one resolved typed entry and its document."""
        document = self.target_document(source, target)
        _relative, _part, identifier = split_target(target)
        entry = self.registries.get(document, {}).get(identifier)
        if entry is None:
            _raise("external_entry_missing" if document != source else "missing_reference_target", source, target, "target entry does not exist")
        if not isinstance(entry, expected):
            _raise("wrong_reference_target_type", source, target, f"target is not a {expected.__name__.lower()}")
        return document, entry

    def display_target(self, document: str, part: str, identifier: str) -> str:
        """Return one root-relative public target."""
        if document == self.root:
            return f"{part}.{identifier}"
        relative = posixpath.relpath(document, posixpath.dirname(self.root))
        return f"{relative}#{part}.{identifier}"


def _load_document(path: str, loader: DocumentLoader, source: str) -> Node:
    loaded = loader(path)
    if loaded is None:
        _raise("external_document_missing", source, path, "explicit loader returned no document")
    if isinstance(loaded, Node):
        return loaded
    try:
        return parse(loaded)
    except OakParseError as error:
        _raise("external_document_invalid", source, path, str(error))


def _validate_targets(graph: ResolvedGraph) -> None:
    for source, node in graph.documents.items():
        for target, expected in iter_targets(node):
            graph.entry(source, target, expected)


def _schema_names(graph: ResolvedGraph, document: str, target: str | None) -> set[str]:
    if target is None:
        return set()
    _schema_document, schema = graph.entry(document, target, Schema)
    return schema.placeholders


def _walk_calls(steps: list[Step]) -> Iterator[Call]:
    for step in steps:
        if isinstance(step, Call):
            yield step
        elif isinstance(step, If):
            yield from _walk_calls(step.then)
            if step.otherwise is not None:
                yield from _walk_calls(step.otherwise)
        elif isinstance(step, Foreach):
            yield from _walk_calls(step.steps)
        elif isinstance(step, Par):
            yield from _walk_calls(step.steps)


def _contract_error(source: str, target: str, error: PydanticCustomError) -> None:
    _raise(str(error.type), source, target, str(error))


def _validate_contracts(graph: ResolvedGraph) -> None:
    for document, node in graph.documents.items():
        for process in node.processes:
            try:
                validate_process_contract(
                    process,
                    _schema_names(graph, document, process.input),
                    _schema_names(graph, document, process.output),
                )
            except PydanticCustomError as error:
                _contract_error(document, f"process.{process.id}", error)
        for trigger in node.triggers:
            target_document, process = graph.entry(document, trigger.then, Process)
            if process.input is not None:
                _raise(
                    "trigger_process_input",
                    document,
                    trigger.then,
                    f"trigger {trigger.id} selects process {process.id} with an input schema",
                )
        for process in node.processes:
            for call in _walk_calls(process.steps):
                target_document, target = graph.entry(document, call.process, Process)
                try:
                    validate_call_contract(
                        call,
                        _schema_names(graph, target_document, target.input),
                        _schema_names(graph, target_document, target.output),
                    )
                except PydanticCustomError as error:
                    _contract_error(document, call.process, error)


def _call_edges(graph: ResolvedGraph) -> dict[tuple[str, str], list[tuple[str, str]]]:
    edges: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for document, node in graph.documents.items():
        for process in node.processes:
            source = (document, process.id)
            targets: list[tuple[str, str]] = []
            for target, expected in _steps_targets_in_process(process.steps):
                if expected is not Process:
                    continue
                target_document, target_process = graph.entry(document, target, Process)
                targets.append((target_document, target_process.id))
            edges[source] = targets
    return edges


def _validate_call_cycles(graph: ResolvedGraph) -> None:
    edges = _call_edges(graph)
    state: dict[tuple[str, str], int] = {}
    stack: list[tuple[str, str]] = []

    def visit(current: tuple[str, str]) -> None:
        state[current] = 1
        stack.append(current)
        for target in edges.get(current, []):
            target_state = state.get(target, 0)
            if target_state == 0:
                visit(target)
            elif target_state == 1:
                start = stack.index(target)
                cycle = stack[start:] + [target]
                text = " -> ".join(f"{document}#process.{identifier}" for document, identifier in cycle)
                _raise("cross_document_process_call_cycle", current[0], text, "resolved process calls form a cycle")
        stack.pop()
        state[current] = 2

    for process in edges:
        if state.get(process, 0) == 0:
            visit(process)


def resolve(
    node: Node,
    *,
    source: str | None = None,
    load: DocumentLoader | None = None,
    root: str | None = None,
) -> ResolvedGraph:
    """Resolve every reachable relative target through one explicit loader."""
    relative_exists = any(is_relative_target(target) for target, _expected in iter_targets(node))
    if source is None:
        if relative_exists:
            _raise("external_reference_without_source", None, "<relative>", "relative targets need a source document path")
        source = "document.oak.md"
    source = _normalize_source(source)
    documents: dict[str, Node] = {source: node}
    registries: dict[str, Mapping[str, Entry]] = {source: entry_registry(node)}
    pending = [source]
    while pending:
        current = pending.pop(0)
        current_node = documents[current]
        for target, _expected in iter_targets(current_node):
            relative, _part, _identifier = split_target(target)
            if relative is None:
                continue
            if load is None:
                _raise("external_document_missing", current, target, "relative target needs an explicit loader")
            document = _resolve_document(current, relative, root)
            if document in documents:
                continue
            loaded = _load_document(document, load, current)
            documents[document] = loaded
            registries[document] = entry_registry(loaded)
            pending.append(document)
    graph = ResolvedGraph(source, documents, registries)
    _validate_targets(graph)
    _validate_contracts(graph)
    _validate_call_cycles(graph)
    return graph
