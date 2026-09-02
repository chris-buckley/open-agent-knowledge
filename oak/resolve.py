"""Explicit offline resolution for one reachable OAK document graph."""

from __future__ import annotations

import posixpath
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import TypeVar

from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node import Node
from oak.node.index import NodeIndex
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
    InterfaceValue,
    LiteralValue,
    Not,
    Par,
    Process,
    Schema,
    SchemaBindingError,
    Set,
    Step,
    Trigger,
    Value,
    While,
    step_values,
)
from oak.node.validation.flow import process_visible_bindings
from oak.node.validation.processes import (
    validate_act_contract,
    validate_call_contract,
    validate_process_contract,
)
from oak.node.validation.triggers import validate_trigger_contract
from oak.node.validation.values import validate_typed_value
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


def _raise(
    code: str,
    source: str | None,
    target: str,
    message: str,
) -> None:
    raise ResolutionError(
        ResolutionFailure(
            code,
            source,
            target,
            message,
        )
    )


def _normalize_source(source: str) -> str:
    if (
        "\\" in source
        or "\x00" in source
        or "?" in source
        or "#" in source
    ):
        _raise(
            "invalid_document_path",
            source,
            source,
            "source path must be a clean POSIX path",
        )

    normalized = posixpath.normpath(source)

    if (
        normalized in ("", ".", "..")
        or source.endswith("/")
    ):
        _raise(
            "invalid_document_path",
            source,
            source,
            "source path must identify one .oak.md document",
        )

    if not normalized.endswith(".oak.md"):
        _raise(
            "invalid_document_path",
            source,
            source,
            "source path must end in .oak.md",
        )

    return normalized


def _resolve_document(
    source: str,
    relative: str,
    root: str | None,
) -> str:
    target = posixpath.normpath(
        posixpath.join(
            posixpath.dirname(source),
            relative,
        )
    )

    if root is not None:
        root_path = posixpath.normpath(root)

        try:
            common = posixpath.commonpath(
                (
                    root_path,
                    target,
                )
            )

        except ValueError:
            common = ""

        if common != root_path:
            _raise(
                "invalid_document_path",
                source,
                relative,
                "relative target escapes the allowed root",
            )

    return target


def _condition_values(
    condition: Condition,
) -> Iterator[Value]:
    if isinstance(condition, Compare):
        yield condition.left
        yield condition.right

    elif isinstance(condition, (All, Any)):
        for child in condition.conditions:
            yield from _condition_values(child)

    elif isinstance(condition, Not):
        yield from _condition_values(condition.condition)


def _value_targets(
    values: Iterable[Value],
) -> Iterator[tuple[str, type[Entry]]]:
    for value in values:
        if isinstance(value, ConstantValue):
            yield value.constant, Constant


def _step_references(
    step: Step,
) -> Iterator[tuple[str, type[Entry]]]:
    if isinstance(step, Act):
        if step.input is not None:
            yield step.input, Schema

        if step.output is not None:
            yield step.output, Schema

        yield from _value_targets(
            binding.value
            for binding in step.inputs
        )

    elif isinstance(step, Set):
        yield from _value_targets((step.value,))

    elif isinstance(step, Emit):
        yield from _value_targets(
            binding.value
            for binding in step.bindings
        )

    elif isinstance(step, If):
        yield from _value_targets(
            _condition_values(step.condition)
        )

        for child in step.then:
            yield from _step_references(child)

        if step.otherwise is not None:
            for child in step.otherwise:
                yield from _step_references(child)

    elif isinstance(step, Assert):
        yield from _value_targets(
            _condition_values(step.condition)
        )

    elif isinstance(step, Foreach):
        yield from _value_targets((step.value,))

        for child in step.steps:
            yield from _step_references(child)

    elif isinstance(step, While):
        yield from _value_targets(
            _condition_values(step.condition)
        )

        for child in step.steps:
            yield from _step_references(child)

    elif isinstance(step, Par):
        for child in step.steps:
            yield from _step_references(child)

    elif isinstance(step, Call):
        yield from _value_targets(
            binding.value
            for binding in step.inputs
        )
        yield step.process, Process


def iter_targets(
    node: Node,
) -> Iterator[tuple[str, type[Entry]]]:
    """Yield every resolvable typed target in one document."""
    for entry in (*node.constants, *node.state):
        if entry.schema_id is not None:
            yield entry.schema_id, Schema

    for interface in node.interfaces:
        yield interface.schema_id, Schema

    for process in node.processes:
        if process.input is not None:
            yield process.input, Schema

        if process.output is not None:
            yield process.output, Schema

    for trigger in node.triggers:
        yield trigger.process, Process
        yield from _value_targets(
            binding.value
            for binding in trigger.seed
        )

        if trigger.guard is not True:
            yield from _value_targets(
                _condition_values(trigger.guard)
            )

    for process in node.processes:
        for step in process.steps:
            yield from _step_references(step)


def _steps_targets_in_process(
    steps: list[Step],
) -> Iterator[tuple[str, type[Entry]]]:
    for step in steps:
        yield from _step_references(step)


@dataclass(frozen=True, slots=True)
class ResolvedGraph:
    """One explicitly loaded and type-checked OAK document graph."""

    root: str
    documents: Mapping[str, Node]
    registries: Mapping[str, Mapping[str, Entry]]

    def target_document(
        self,
        source: str,
        target: str,
    ) -> str:
        """Return the normalized document selected by one target."""
        relative, _part, _identifier = split_target(target)

        return (
            source
            if relative is None
            else posixpath.normpath(
                posixpath.join(
                    posixpath.dirname(source),
                    relative,
                )
            )
        )

    def entry(
        self,
        source: str,
        target: str,
        expected: type[TargetEntry],
    ) -> tuple[str, TargetEntry]:
        """Return one resolved typed entry and its document."""
        document = self.target_document(
            source,
            target,
        )
        _relative, _part, identifier = split_target(target)
        entry = self.registries.get(
            document,
            {},
        ).get(identifier)

        if entry is None:
            _raise(
                (
                    "external_entry_missing"
                    if document != source
                    else "missing_reference_target"
                ),
                source,
                target,
                "target entry does not exist",
            )

        if not isinstance(entry, expected):
            _raise(
                "wrong_reference_target_type",
                source,
                target,
                f"target is not a {expected.__name__.lower()}",
            )

        return document, entry

    def display_target(
        self,
        document: str,
        part: str,
        identifier: str,
    ) -> str:
        """Return one root-relative public target."""
        if document == self.root:
            return f"{part}.{identifier}"

        relative = posixpath.relpath(
            document,
            posixpath.dirname(self.root),
        )
        return f"{relative}#{part}.{identifier}"


def _load_document(
    path: str,
    loader: DocumentLoader,
    source: str,
) -> Node:
    loaded = loader(path)

    if loaded is None:
        _raise(
            "external_document_missing",
            source,
            path,
            "explicit loader returned no document",
        )

    if isinstance(loaded, Node):
        return loaded

    try:
        return parse(loaded)

    except OakParseError as error:
        _raise(
            "external_document_invalid",
            source,
            path,
            str(error),
        )


def _validate_targets(graph: ResolvedGraph) -> None:
    for source, node in graph.documents.items():
        for target, expected in iter_targets(node):
            graph.entry(
                source,
                target,
                expected,
            )


def _schema_names(
    graph: ResolvedGraph,
    document: str,
    target: str | None,
) -> set[str]:
    if target is None:
        return set()

    _schema_document, schema = graph.entry(
        document,
        target,
        Schema,
    )
    return schema.placeholders


def _walk_calls(
    steps: list[Step],
) -> Iterator[Call]:
    for step in steps:
        if isinstance(step, Call):
            yield step

        elif isinstance(step, If):
            yield from _walk_calls(step.then)

            if step.otherwise is not None:
                yield from _walk_calls(step.otherwise)

        elif isinstance(step, Foreach):
            yield from _walk_calls(step.steps)

        elif isinstance(step, While):
            yield from _walk_calls(step.steps)

        elif isinstance(step, Par):
            yield from _walk_calls(step.steps)


def _contract_error(
    source: str,
    target: str,
    error: PydanticCustomError,
) -> None:
    _raise(
        str(error.type),
        source,
        target,
        str(error),
    )


def _iter_steps(
    steps: list[Step],
) -> Iterator[Step]:
    for step in steps:
        yield step

        if isinstance(step, If):
            yield from _iter_steps(step.then)

            if step.otherwise is not None:
                yield from _iter_steps(step.otherwise)

        elif isinstance(step, (Foreach, While, Par)):
            yield from _iter_steps(step.steps)


def _static_emit_values(
    graph: ResolvedGraph,
    document: str,
    step: Emit,
) -> dict[str, object] | None:
    values: dict[str, object] = {}

    for binding in step.bindings:
        value = binding.value

        if isinstance(value, LiteralValue):
            values[binding.placeholder] = value.value

        elif isinstance(value, ConstantValue):
            _constant_document, constant = graph.entry(
                document,
                value.constant,
                Constant,
            )
            values[binding.placeholder] = constant.value

        else:
            return None

    return values


def _validate_relative_interfaces(
    graph: ResolvedGraph,
    document: str,
    node: Node,
) -> None:
    schemas = {
        f"interface.{interface.id}": graph.entry(
            document,
            interface.schema_id,
            Schema,
        )[1]
        for interface in node.interfaces
        if is_relative_target(interface.schema_id)
    }

    if not schemas:
        return

    for trigger in node.triggers:
        for binding in trigger.seed:
            value = binding.value

            if (
                isinstance(value, InterfaceValue)
                and value.interface in schemas
                and value.placeholder
                not in schemas[value.interface].placeholders
            ):
                _raise(
                    "unknown_interface_placeholder",
                    document,
                    value.interface,
                    (
                        f"trigger {trigger.id} reads placeholder "
                        f"{value.placeholder} absent from the resolved "
                        "interface schema"
                    ),
                )

    for process in node.processes:
        for step in _iter_steps(process.steps):
            if isinstance(step, Emit) and step.interface in schemas:
                schema = schemas[step.interface]
                bound = {
                    binding.placeholder
                    for binding in step.bindings
                }

                if bound != schema.placeholders:
                    _raise(
                        "emit_schema_binding_mismatch",
                        document,
                        step.interface,
                        (
                            f"process {process.id} emit bindings differ from "
                            "the resolved interface schema placeholders"
                        ),
                    )

                static_values = _static_emit_values(
                    graph,
                    document,
                    step,
                )

                if static_values is not None:
                    try:
                        schema.bind(static_values)

                    except SchemaBindingError as error:
                        _raise(
                            "invalid_static_schema_binding",
                            document,
                            step.interface,
                            (
                                f"process {process.id} emits an invalid "
                                f"static binding: {error}"
                            ),
                        )

            for value in step_values(step):
                if (
                    isinstance(value, InterfaceValue)
                    and value.interface in schemas
                    and value.placeholder
                    not in schemas[value.interface].placeholders
                ):
                    _raise(
                        "unknown_interface_placeholder",
                        document,
                        value.interface,
                        (
                            f"process {process.id} reads placeholder "
                            f"{value.placeholder} absent from the resolved "
                            "interface schema"
                        ),
                    )


def _validate_contracts(graph: ResolvedGraph) -> None:
    for document, node in graph.documents.items():
        _validate_relative_interfaces(
            graph,
            document,
            node,
        )

        for process in node.processes:
            try:
                validate_process_contract(
                    process,
                    _schema_names(
                        graph,
                        document,
                        process.input,
                    ),
                    _schema_names(
                        graph,
                        document,
                        process.output,
                    ),
                )

            except PydanticCustomError as error:
                _contract_error(
                    document,
                    f"process.{process.id}",
                    error,
                )

        for entry in (*node.constants, *node.state):
            if (
                entry.schema_id is None
                or not is_relative_target(entry.schema_id)
            ):
                continue

            _schema_document, schema = graph.entry(
                document,
                entry.schema_id,
                Schema,
            )

            try:
                validate_typed_value(
                    entry,
                    schema,
                )

            except PydanticCustomError as error:
                _contract_error(
                    document,
                    entry.schema_id,
                    error,
                )

        for trigger in node.triggers:
            target_document, process = graph.entry(
                document,
                trigger.process,
                Process,
            )

            try:
                validate_trigger_contract(
                    trigger,
                    (
                        None
                        if process.input is None
                        else _schema_names(
                            graph,
                            target_document,
                            process.input,
                        )
                    ),
                )

            except PydanticCustomError as error:
                _contract_error(
                    document,
                    trigger.process,
                    error,
                )

        for process in node.processes:
            for step in _iter_steps(process.steps):
                if (
                    not isinstance(step, Act)
                    or (
                        step.input is None
                        and step.output is None
                    )
                ):
                    continue

                try:
                    validate_act_contract(
                        step,
                        (
                            None
                            if step.input is None
                            else _schema_names(
                                graph,
                                document,
                                step.input,
                            )
                        ),
                        (
                            None
                            if step.output is None
                            else _schema_names(
                                graph,
                                document,
                                step.output,
                            )
                        ),
                    )

                except PydanticCustomError as error:
                    _contract_error(
                        document,
                        step.input or step.output or "",
                        error,
                    )

        for process in node.processes:
            for call in _walk_calls(process.steps):
                target_document, target = graph.entry(
                    document,
                    call.process,
                    Process,
                )

                try:
                    validate_call_contract(
                        call,
                        _schema_names(
                            graph,
                            target_document,
                            target.input,
                        ),
                        _schema_names(
                            graph,
                            target_document,
                            target.output,
                        ),
                    )

                except PydanticCustomError as error:
                    _contract_error(
                        document,
                        call.process,
                        error,
                    )


def _call_edges(
    graph: ResolvedGraph,
) -> dict[
    tuple[str, str],
    list[tuple[str, str]],
]:
    edges: dict[
        tuple[str, str],
        list[tuple[str, str]],
    ] = {}

    for document, node in graph.documents.items():
        for process in node.processes:
            source = (
                document,
                process.id,
            )
            targets: list[tuple[str, str]] = []

            for target, expected in _steps_targets_in_process(
                process.steps
            ):
                if expected is not Process:
                    continue

                target_document, target_process = graph.entry(
                    document,
                    target,
                    Process,
                )
                targets.append(
                    (
                        target_document,
                        target_process.id,
                    )
                )

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
            target_state = state.get(
                target,
                0,
            )

            if target_state == 0:
                visit(target)

            elif target_state == 1:
                start = stack.index(target)
                cycle = stack[start:] + [target]
                text = " -> ".join(
                    f"{document}#process.{identifier}"
                    for document, identifier in cycle
                )
                _raise(
                    "cross_document_process_call_cycle",
                    current[0],
                    text,
                    "resolved process calls form a cycle",
                )

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
    relative_exists = any(
        is_relative_target(target)
        for target, _expected in iter_targets(node)
    )

    if source is None:
        if relative_exists:
            _raise(
                "external_reference_without_source",
                None,
                "<relative>",
                "relative targets need a source document path",
            )

        source = "document.oak.md"

    source = _normalize_source(source)
    documents: dict[str, Node] = {
        source: node,
    }
    registries: dict[str, Mapping[str, Entry]] = {
        source: NodeIndex.build(node),
    }
    pending = [source]

    while pending:
        current = pending.pop(0)
        current_node = documents[current]

        for target, _expected in iter_targets(current_node):
            relative, _part, _identifier = split_target(target)

            if relative is None:
                continue

            if load is None:
                _raise(
                    "external_document_missing",
                    current,
                    target,
                    "relative target needs an explicit loader",
                )

            document = _resolve_document(
                current,
                relative,
                root,
            )

            if document in documents:
                continue

            loaded = _load_document(
                document,
                load,
                current,
            )
            documents[document] = loaded
            registries[document] = NodeIndex.build(loaded)
            pending.append(document)

    graph = ResolvedGraph(
        source,
        documents,
        registries,
    )
    _validate_targets(graph)
    _validate_contracts(graph)
    _validate_call_cycles(graph)
    return graph
