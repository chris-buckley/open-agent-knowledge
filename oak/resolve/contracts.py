"""Cross-document schemas, process contracts, and call-cycle checks."""

from __future__ import annotations

from collections.abc import Set as AbstractSet

from pydantic_core import PydanticCustomError

from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, Emit, Step, iter_steps
from oak.node.parts.processes.values import ConstantValue, LiteralValue
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema
from oak.node.validation.contracts import find_cycle, inspect_emit_contract
from oak.node.validation.processes import (
    validate_act_contract,
    validate_call_contract,
    validate_inferred_emit,
    validate_process_contract,
)
from oak.node.validation.triggers import validate_trigger_contract
from oak.node.validation.values import validate_typed_value
from oak.resolve.errors import raise_resolution
from oak.resolve.graph import ResolvedGraph
from oak.resolve.references import steps_targets_in_process, walk_calls
from oak.vocabulary.text.target_path import is_relative_target


def schema_names(
    graph: ResolvedGraph,
    document: str,
    target: str | None,
) -> set[str]:
    """Return the placeholders of one resolved optional schema."""
    if target is None:
        return set()

    _schema_document, schema = graph.entry(document, target, Schema)
    return schema.placeholders


def contract_error(
    source: str,
    target: str,
    error: PydanticCustomError,
) -> None:
    """Translate one contract failure into a resolution failure."""
    raise_resolution(str(error.type), source, target, str(error))


def static_emit_values(
    graph: ResolvedGraph,
    document: str,
    step: Emit,
) -> dict[str, object] | None:
    """Return one fully static explicit emission when available."""
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


def _validate_resolved_emit(
    graph: ResolvedGraph,
    document: str,
    process: Process,
    step: Emit,
    visible: AbstractSet[str],
) -> None:
    interface_document, interface = graph.entry(
        document,
        step.interface,
        Interface,
    )
    if interface.flow != "emits":
        raise PydanticCustomError(
            "emit_target_not_emit",
            "process {process} emits through non-EMITS interface {interface}",
            {
                "process": process.id,
                "interface": interface.id,
            },
        )

    _schema_document, schema = graph.entry(
        interface_document,
        interface.schema_id,
        Schema,
    )

    if not step.bindings:
        validate_inferred_emit(process, step, schema, visible)
        return

    try:
        contract = inspect_emit_contract(
            schema,
            (binding.placeholder for binding in step.bindings),
            static_emit_values(graph, document, step),
        )
    except SchemaBindingError as error:
        raise PydanticCustomError(
            "invalid_static_schema_binding",
            "process {process} emits an invalid static binding: {reason}",
            {
                "process": process.id,
                "reason": str(error),
            },
        ) from None

    if not contract.placeholders_match:
        raise PydanticCustomError(
            "emit_schema_binding_mismatch",
            (
                "process {process} emit bindings differ from interface schema; "
                "missing: {missing}; unused: {unused}"
            ),
            {
                "process": process.id,
                "missing": ", ".join(contract.missing) or "none",
                "unused": ", ".join(contract.unused) or "none",
            },
        )


def _validate_process(
    graph: ResolvedGraph,
    document: str,
    process: Process,
) -> None:
    def visit(step: Step, visible: AbstractSet[str]) -> None:
        if isinstance(step, Emit):
            _validate_resolved_emit(
                graph,
                document,
                process,
                step,
                visible,
            )

    validate_process_contract(
        process,
        schema_names(graph, document, process.input),
        schema_names(graph, document, process.output),
        visit=visit,
    )


def _validate_trigger(
    graph: ResolvedGraph,
    document: str,
    trigger: object,
) -> None:
    target_document, process = graph.entry(
        document,
        trigger.process,
        Process,
    )

    if trigger.source is None:
        validate_trigger_contract(
            trigger,
            (
                None
                if process.input is None
                else schema_names(graph, target_document, process.input)
            ),
        )
        return

    _interface_document, interface = graph.entry(
        document,
        trigger.source,
        Interface,
    )
    if interface.flow != "receives":
        raise PydanticCustomError(
            "trigger_source_not_receive",
            "trigger {trigger} source is not a RECEIVES interface",
            {"trigger": trigger.id},
        )
    if process.input is None:
        raise PydanticCustomError(
            "source_trigger_process_input",
            "source-backed trigger {trigger} selects a process without input",
            {"trigger": trigger.id},
        )

    receive_schema = graph.entry(document, interface.schema_id, Schema)[:2]
    process_schema = graph.entry(target_document, process.input, Schema)[:2]
    receive_identity = (receive_schema[0], receive_schema[1].id)
    process_identity = (process_schema[0], process_schema[1].id)

    if receive_identity != process_identity:
        raise PydanticCustomError(
            "source_trigger_schema_mismatch",
            (
                "trigger {trigger} receive schema differs from the selected "
                "process input schema"
            ),
            {"trigger": trigger.id},
        )


def validate_contracts(graph: ResolvedGraph) -> None:
    """Validate every relationship that depends on resolved documents."""
    for document, node in graph.documents.items():
        for process in node.processes:
            try:
                _validate_process(graph, document, process)
            except PydanticCustomError as error:
                contract_error(document, f"process.{process.id}", error)

        for entry in (*node.constants, *node.state):
            if entry.schema_id is None or not is_relative_target(entry.schema_id):
                continue

            _schema_document, schema = graph.entry(
                document,
                entry.schema_id,
                Schema,
            )
            try:
                validate_typed_value(entry, schema)
            except PydanticCustomError as error:
                contract_error(document, entry.schema_id, error)

        for trigger in node.triggers:
            try:
                _validate_trigger(graph, document, trigger)
            except PydanticCustomError as error:
                contract_error(document, trigger.process, error)

        for process in node.processes:
            for step in iter_steps(process.steps):
                if not isinstance(step, Act) or (
                    step.input is None and step.output is None
                ):
                    continue

                try:
                    validate_act_contract(
                        step,
                        (
                            None
                            if step.input is None
                            else schema_names(graph, document, step.input)
                        ),
                        (
                            None
                            if step.output is None
                            else schema_names(graph, document, step.output)
                        ),
                    )
                except PydanticCustomError as error:
                    contract_error(
                        document,
                        step.input or step.output or "",
                        error,
                    )

        for process in node.processes:
            for call in walk_calls(process.steps):
                target_document, target = graph.entry(
                    document,
                    call.process,
                    Process,
                )
                try:
                    validate_call_contract(
                        call,
                        schema_names(graph, target_document, target.input),
                        schema_names(graph, target_document, target.output),
                    )
                except PydanticCustomError as error:
                    contract_error(document, call.process, error)


def call_edges(
    graph: ResolvedGraph,
) -> dict[tuple[str, str], list[tuple[str, str]]]:
    """Return each resolved process and its called processes."""
    edges: dict[tuple[str, str], list[tuple[str, str]]] = {}

    for document, node in graph.documents.items():
        for process in node.processes:
            source = (document, process.id)
            targets: list[tuple[str, str]] = []

            for target, expected in steps_targets_in_process(process.steps):
                if expected is not Process:
                    continue

                target_document, target_process = graph.entry(
                    document,
                    target,
                    Process,
                )
                targets.append((target_document, target_process.id))

            edges[source] = targets

    return edges


def validate_call_cycles(graph: ResolvedGraph) -> None:
    """Reject a cycle formed by resolved process calls."""
    cycle = find_cycle(call_edges(graph))

    if cycle is None:
        return

    text = " -> ".join(
        f"{document}#process.{identifier}"
        for document, identifier in cycle
    )
    raise_resolution(
        "cross_document_process_call_cycle",
        cycle[-2][0],
        text,
        "resolved process calls form a cycle",
    )


__all__ = ["validate_call_cycles", "validate_contracts"]
