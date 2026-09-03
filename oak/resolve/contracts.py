"""Cross-document schemas, process contracts, and call-cycle checks."""

from __future__ import annotations

from pydantic_core import PydanticCustomError

from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, Emit, iter_steps, step_values
from oak.node.parts.processes.values import (
    ConstantValue,
    InterfaceValue,
    LiteralValue,
)
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema
from oak.node.validation.contracts import find_cycle, inspect_emit_contract
from oak.node.validation.processes import (
    validate_act_contract,
    validate_call_contract,
    validate_process_contract,
)
from oak.node.validation.triggers import validate_trigger_contract
from oak.node.validation.values import validate_typed_value
from oak.resolve.errors import raise_resolution
from oak.resolve.graph import ResolvedGraph
from oak.resolve.references import (
    steps_targets_in_process,
    walk_calls,
)
from oak.vocabulary.text.target_path import is_relative_target


def schema_names(
    graph: ResolvedGraph,
    document: str,
    target: str | None,
) -> set[str]:
    """Return the placeholders of one resolved optional schema."""
    if target is None:
        return set()

    _schema_document, schema = graph.entry(
        document,
        target,
        Schema,
    )
    return schema.placeholders


def contract_error(
    source: str,
    target: str,
    error: PydanticCustomError,
) -> None:
    """Translate one local contract failure into a resolution failure."""
    raise_resolution(
        str(error.type),
        source,
        target,
        str(error),
    )


def static_emit_values(
    graph: ResolvedGraph,
    document: str,
    step: Emit,
) -> dict[str, object] | None:
    """Return one fully static emission binding when available."""
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


def validate_relative_interfaces(
    graph: ResolvedGraph,
    document: str,
    node: Node,
) -> None:
    """Validate interfaces whose schemas resolve in another document."""
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
                raise_resolution(
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
        for step in iter_steps(process.steps):
            if isinstance(step, Emit) and step.interface in schemas:
                schema = schemas[step.interface]

                try:
                    contract = inspect_emit_contract(
                        schema,
                        (
                            binding.placeholder
                            for binding in step.bindings
                        ),
                        static_emit_values(
                            graph,
                            document,
                            step,
                        ),
                    )

                except SchemaBindingError as error:
                    raise_resolution(
                        "invalid_static_schema_binding",
                        document,
                        step.interface,
                        (
                            f"process {process.id} emits an invalid "
                            f"static binding: {error}"
                        ),
                    )

                if not contract.placeholders_match:
                    raise_resolution(
                        "emit_schema_binding_mismatch",
                        document,
                        step.interface,
                        (
                            f"process {process.id} emit bindings differ from "
                            "the resolved interface schema placeholders"
                        ),
                    )

            for value in step_values(step):
                if (
                    isinstance(value, InterfaceValue)
                    and value.interface in schemas
                    and value.placeholder
                    not in schemas[value.interface].placeholders
                ):
                    raise_resolution(
                        "unknown_interface_placeholder",
                        document,
                        value.interface,
                        (
                            f"process {process.id} reads placeholder "
                            f"{value.placeholder} absent from the resolved "
                            "interface schema"
                        ),
                    )


def validate_contracts(graph: ResolvedGraph) -> None:
    """Validate every relationship that depends on resolved documents."""
    for document, node in graph.documents.items():
        validate_relative_interfaces(
            graph,
            document,
            node,
        )

        for process in node.processes:
            try:
                validate_process_contract(
                    process,
                    schema_names(
                        graph,
                        document,
                        process.input,
                    ),
                    schema_names(
                        graph,
                        document,
                        process.output,
                    ),
                )

            except PydanticCustomError as error:
                contract_error(
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
                contract_error(
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
                        else schema_names(
                            graph,
                            target_document,
                            process.input,
                        )
                    ),
                )

            except PydanticCustomError as error:
                contract_error(
                    document,
                    trigger.process,
                    error,
                )

        for process in node.processes:
            for step in iter_steps(process.steps):
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
                            else schema_names(
                                graph,
                                document,
                                step.input,
                            )
                        ),
                        (
                            None
                            if step.output is None
                            else schema_names(
                                graph,
                                document,
                                step.output,
                            )
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
                        schema_names(
                            graph,
                            target_document,
                            target.input,
                        ),
                        schema_names(
                            graph,
                            target_document,
                            target.output,
                        ),
                    )

                except PydanticCustomError as error:
                    contract_error(
                        document,
                        call.process,
                        error,
                    )


def call_edges(
    graph: ResolvedGraph,
) -> dict[
    tuple[str, str],
    list[tuple[str, str]],
]:
    """Return each resolved process and its called processes."""
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

            for target, expected in steps_targets_in_process(
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


def validate_call_cycles(graph: ResolvedGraph) -> None:
    """Reject a cycle formed by resolved process calls."""
    cycle = find_cycle(
        call_edges(graph)
    )

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


__all__ = [
    "validate_call_cycles",
    "validate_contracts",
]
