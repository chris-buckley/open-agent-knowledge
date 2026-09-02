"""Top-level transaction creation, trigger selection, and commit."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from pydantic import JsonValue, ValidationError

from oak.execute.context import ExecutionContext, ProcessFrame
from oak.execute.models import (
    ActHandler,
    Arrival,
    Emission,
    ExecutionError,
    ExecutionResult,
    ToolContract,
    _STATE_ADAPTER,
)
from oak.execute.steps import run_process
from oak.execute.values import (
    evaluate_condition,
    resolve_value,
    validate_state_value,
)
from oak.node import Node
from oak.node.parts import (
    Interface,
    Process,
    Schema,
    SchemaBindingError,
    Trigger,
)
from oak.node.validation.tools import validate_tools
from oak.resolve import DocumentLoader, ResolvedGraph, resolve
from oak.vocabulary.text.target_path import target_id


def active_interfaces(
    context: ExecutionContext,
    arrival: Arrival,
) -> dict[
    tuple[str, str],
    dict[str, JsonValue],
]:
    """Validate and activate every interface payload on one arrival."""
    active: dict[
        tuple[str, str],
        dict[str, JsonValue],
    ] = {}

    for target, values in arrival.interfaces.items():
        document, interface = context.graph.entry(
            context.graph.root,
            target,
            Interface,
        )

        if interface.direction not in ("in", "inout"):
            raise ExecutionError(
                "interface_direction_mismatch",
                f"interface {target} cannot receive input",
            )

        _schema_document, schema = context.graph.entry(
            document,
            interface.schema_id,
            Schema,
        )

        try:
            schema.bind(values)

        except SchemaBindingError as error:
            raise ExecutionError(
                "invalid_interface_binding",
                f"interface {target}: {error}",
            ) from None

        active[
            (
                document,
                interface.id,
            )
        ] = deepcopy(values)

    return active


def authored_state(
    graph: ResolvedGraph,
) -> dict[str, JsonValue]:
    """Return every authored state value by root-relative target."""
    return {
        graph.display_target(
            document,
            "state",
            entry.id,
        ): deepcopy(entry.value)
        for document, node in graph.documents.items()
        for entry in node.state
    }


def execute(
    node: Node,
    arrival: Arrival,
    state: Mapping[str, JsonValue],
    *,
    act: ActHandler | None = None,
    tools: Mapping[str, ToolContract] | None = None,
    source: str | None = None,
    load: DocumentLoader | None = None,
    root: str | None = None,
) -> ExecutionResult:
    """Run one arrival cycle and commit state and emissions on success."""
    graph = resolve(
        node,
        source=source,
        load=load,
        root=root,
    )
    tool_registry = tools or {}

    for document in graph.documents.values():
        try:
            validate_tools(
                document,
                tool_registry,
            )

        except Exception as error:
            code = (
                getattr(
                    error,
                    "type",
                    None,
                )
                or getattr(
                    error,
                    "code",
                    None,
                )
                or "tool_validation_failed"
            )
            raise ExecutionError(
                str(code),
                str(error),
            ) from None

    try:
        working_state = _STATE_ADAPTER.validate_python(
            dict(state)
        )

    except ValidationError as error:
        raise ExecutionError(
            "invalid_execution_state",
            str(error),
        ) from None

    expected_state = set(
        authored_state(graph)
    )
    supplied_state = set(working_state)

    if supplied_state != expected_state:
        raise ExecutionError(
            "execution_state_mismatch",
            (
                "state differs; missing: "
                + (
                    ", ".join(
                        sorted(
                            expected_state
                            - supplied_state
                        )
                    )
                    or "none"
                )
                + "; unknown: "
                + (
                    ", ".join(
                        sorted(
                            supplied_state
                            - expected_state
                        )
                    )
                    or "none"
                )
            ),
        )

    context = ExecutionContext(
        graph=graph,
        state=working_state,
        interfaces={},
        emissions=[],
        act=act,
        tools=tool_registry,
    )

    for document, graph_node in graph.documents.items():
        for entry in graph_node.state:
            if entry.schema_id is None:
                continue

            key = graph.display_target(
                document,
                "state",
                entry.id,
            )
            validate_state_value(
                context,
                document,
                entry,
                working_state[key],
                key,
            )

    context.interfaces = active_interfaces(
        context,
        arrival,
    )

    if (
        arrival.source is not None
        and arrival.source not in arrival.interfaces
    ):
        raise ExecutionError(
            "invalid_arrival_source",
            (
                f"arrival source {arrival.source} "
                "carries no payload"
            ),
        )

    root_frame = ProcessFrame(
        graph.root,
        {},
    )
    matches: list[Trigger] = []

    for trigger in node.triggers:
        if trigger.source is None:
            if trigger.event != arrival.event:
                continue

        elif trigger.source != arrival.source:
            continue

        if (
            trigger.guard is True
            or evaluate_condition(
                context,
                root_frame,
                trigger.guard,
            )
        ):
            matches.append(trigger)

    if len(matches) > 1:
        raise ExecutionError(
            "ambiguous_trigger_match",
            (
                "arrival matches triggers "
                + ", ".join(
                    item.id
                    for item in matches
                )
            ),
        )

    if not matches:
        return ExecutionResult(
            state=working_state
        )

    process_document, process = graph.entry(
        graph.root,
        matches[0].process,
        Process,
    )
    seeded = {
        binding.placeholder: resolve_value(
            context,
            root_frame,
            binding.value,
        )
        for binding in matches[0].seed
    }

    run_process(
        context,
        process_document,
        process,
        seeded,
    )

    return ExecutionResult(
        process=graph.display_target(
            process_document,
            "process",
            process.id,
        ),
        state=working_state,
        emissions=context.emissions,
    )


__all__ = [
    "execute",
]
