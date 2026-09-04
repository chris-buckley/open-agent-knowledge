"""Top-level transaction creation, trigger selection, and commit."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from pydantic import JsonValue, ValidationError
from pydantic_core import PydanticCustomError

from oak.execute.context import ExecutionContext, ProcessFrame
from oak.execute.models import (
    ActHandler,
    Arrival,
    ExecutionError,
    ExecutionResult,
    InterpreterHandler,
    ToolContract,
    _STATE_ADAPTER,
)
from oak.execute.steps import run_process
from oak.execute.values import evaluate_condition, resolve_value, validate_state_value
from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema
from oak.node.parts.triggers import Trigger
from oak.node.validation.tools import validate_tools
from oak.resolve.graph import ResolvedGraph
from oak.resolve.resolver import DocumentLoader, resolve


def receive_values(
    context: ExecutionContext,
    arrival: Arrival,
) -> dict[str, JsonValue]:
    """Validate and return one complete receive instance."""
    if arrival.interface is None:
        return {}

    interface_document, interface = context.graph.entry(
        context.graph.root,
        arrival.interface,
        Interface,
    )
    if interface.flow != "receives":
        raise ExecutionError(
            "invalid_arrival_interface",
            f"interface {arrival.interface} cannot receive input",
        )

    _schema_document, schema = context.graph.entry(
        interface_document,
        interface.schema_id,
        Schema,
    )
    try:
        schema.bind(arrival.values)
    except SchemaBindingError as error:
        raise ExecutionError(
            "invalid_interface_binding",
            f"interface {arrival.interface}: {error}",
        ) from None

    return deepcopy(arrival.values)


def authored_state(graph: ResolvedGraph) -> dict[str, JsonValue]:
    """Return every authored state value by root-relative target."""
    return {
        graph.display_target(document, "state", entry.id): deepcopy(entry.value)
        for document, node in graph.documents.items()
        for entry in node.state
    }


def execute(
    node: Node,
    arrival: Arrival,
    state: Mapping[str, JsonValue],
    *,
    act: ActHandler | None = None,
    interpreter: InterpreterHandler | None = None,
    tools: Mapping[str, ToolContract] | None = None,
    source: str | None = None,
    load: DocumentLoader | None = None,
    root: str | None = None,
) -> ExecutionResult:
    """Run one arrival cycle and commit state and emissions on success."""
    if act is not None and interpreter is not None:
        raise ExecutionError(
            "ambiguous_act_handler",
            "supply either act or interpreter, not both",
        )

    graph = resolve(node, source=source, load=load, root=root)
    tool_registry = tools or {}

    for document in graph.documents.values():
        try:
            validate_tools(document, tool_registry)
        except PydanticCustomError as error:
            raise ExecutionError(error.type, str(error)) from None

    try:
        working_state = _STATE_ADAPTER.validate_python(dict(state))
    except ValidationError as error:
        raise ExecutionError("invalid_execution_state", str(error)) from None

    expected_state = set(authored_state(graph))
    supplied_state = set(working_state)
    if supplied_state != expected_state:
        raise ExecutionError(
            "execution_state_mismatch",
            (
                "state differs; missing: "
                + (", ".join(sorted(expected_state - supplied_state)) or "none")
                + "; unknown: "
                + (", ".join(sorted(supplied_state - expected_state)) or "none")
            ),
        )

    context = ExecutionContext(
        graph=graph,
        state=working_state,
        emissions=[],
        act=act,
        tools=tool_registry,
        interpreter=interpreter,
    )

    for document, graph_node in graph.documents.items():
        for entry in graph_node.state:
            if entry.schema_id is None:
                continue

            key = graph.display_target(document, "state", entry.id)
            validate_state_value(
                context,
                document,
                entry,
                working_state[key],
                key,
            )

    received = receive_values(context, arrival)
    root_frame = ProcessFrame(graph.root, {})
    matches: list[Trigger] = []

    for trigger in node.triggers:
        if trigger.source is None:
            if arrival.event is None or trigger.event != arrival.event:
                continue
        elif arrival.interface is None or trigger.source != arrival.interface:
            continue

        if trigger.guard is True or evaluate_condition(
            context,
            root_frame,
            trigger.guard,
        ):
            matches.append(trigger)

    if len(matches) > 1:
        raise ExecutionError(
            "ambiguous_trigger_match",
            "arrival matches triggers " + ", ".join(item.id for item in matches),
        )

    if not matches:
        return ExecutionResult(state=working_state)

    trigger = matches[0]
    process_document, process = graph.entry(
        graph.root,
        trigger.process,
        Process,
    )
    seeded = (
        received
        if trigger.source is not None
        else {
            binding.placeholder: resolve_value(
                context,
                root_frame,
                binding.value,
            )
            for binding in trigger.seed
        }
    )

    run_process(context, process_document, process, seeded)

    return ExecutionResult(
        process=graph.display_target(process_document, "process", process.id),
        state=working_state,
        emissions=context.emissions,
    )


__all__ = ["execute"]
