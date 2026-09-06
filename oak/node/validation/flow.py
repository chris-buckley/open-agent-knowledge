"""Process binding visibility and local control-flow validation."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from collections.abc import Set as AbstractSet
from typing import TYPE_CHECKING

from pydantic_core import PydanticCustomError

from oak.node.parts.processes.statements import (
    Act,
    Call,
    Fail,
    Foreach,
    If,
    Join,
    Par,
    Statement,
    While,
    statement_values,
)
from oak.node.parts.processes.values import BindingValue, LiteralValue, Value

if TYPE_CHECKING:
    from oak.node.parts.processes.model import Process

StatementVisitor = Callable[[Statement, AbstractSet[str]], None]


def _check_binding_visible(value: Value, visible: AbstractSet[str]) -> None:
    if isinstance(value, BindingValue) and value.binding not in visible:
        raise PydanticCustomError(
            "unbound_process_binding",
            "process reads unbound local binding {binding}",
            {"binding": value.binding},
        )


def _check_redefined(
    outputs: AbstractSet[str],
    visible: AbstractSet[str],
    label: str,
) -> None:
    redefined = sorted(outputs & visible)

    if redefined:
        raise PydanticCustomError(
            "process_binding_redefined",
            f"{label} redefines visible local bindings: {{bindings}}",
            {"bindings": ", ".join(redefined)},
        )


def _promote_outputs(outputs: AbstractSet[str], visible: set[str]) -> None:
    _check_redefined(outputs, visible, "process")
    visible.update(outputs)


def _check_foreach(step: Foreach, visible: AbstractSet[str]) -> None:
    if step.binding in visible:
        raise PydanticCustomError(
            "foreach_binding_redefined",
            "FOREACH redefines visible binding {binding}",
            {"binding": step.binding},
        )

    if isinstance(step.value, LiteralValue) and not isinstance(step.value.value, list):
        raise PydanticCustomError(
            "foreach_source_not_list",
            "FOREACH literal source is not a list",
        )


def _parallel_outputs(step: Par, visible: AbstractSet[str]) -> set[str]:
    outputs = {
        output
        for child in step.body
        if isinstance(child, Act)
        for output in child.outputs
    }
    _check_redefined(outputs, visible, "PAR")
    return outputs


def visible_bindings(
    body: Sequence[Statement],
    initial: AbstractSet[str],
    *,
    visit: StatementVisitor | None = None,
) -> set[str]:
    """Return bindings visible after one successful step sequence."""
    visible = set(initial)
    pending: set[str] | None = None

    for step in body:
        if pending is not None and not isinstance(step, Join):
            raise PydanticCustomError(
                "parallel_join_not_adjacent",
                "a step occurs between PAR and JOIN",
            )

        for value in statement_values(step):
            _check_binding_visible(value, visible)

        if visit is not None:
            visit(step, frozenset(visible))

        match step:
            case Act() | Call():
                _promote_outputs(set(step.outputs), visible)

            case If():
                visible_bindings(step.then, visible, visit=visit)

                if step.otherwise is not None:
                    visible_bindings(step.otherwise, visible, visit=visit)

            case Foreach():
                _check_foreach(step, visible)
                visible_bindings(
                    step.body,
                    visible | {step.binding},
                    visit=visit,
                )

            case While():
                visible_bindings(step.body, visible, visit=visit)

            case Par():
                pending = _parallel_outputs(step, visible)

            case Join():
                if pending is None:
                    raise PydanticCustomError(
                        "join_without_par",
                        "JOIN has no immediately preceding PAR",
                    )

                visible.update(pending)
                pending = None

    if pending is not None:
        raise PydanticCustomError(
            "parallel_join_missing",
            "PAR has no following JOIN",
        )

    return visible


def sequence_always_fails(body: Sequence[Statement]) -> bool:
    """Return whether one step sequence always ends in explicit failure."""
    for index, step in enumerate(body):
        always_fails = isinstance(step, Fail)

        if isinstance(step, If):
            always_fails = (
                sequence_always_fails(step.then)
                and step.otherwise is not None
                and sequence_always_fails(step.otherwise)
            )

        elif isinstance(step, While):
            sequence_always_fails(step.body)

        if always_fails:
            if index + 1 < len(body):
                raise PydanticCustomError(
                    "unreachable_process_step",
                    "a process step follows a path that always fails",
                )

            return True

    return False


def validate_process_flow(process: Process) -> None:
    """Validate one process's local binding and failure flow."""
    if process.input is None:
        visible_bindings(process.body, set())

    sequence_always_fails(process.body)


def process_visible_bindings(
    process: Process,
    inputs: AbstractSet[str],
    *,
    visit: StatementVisitor | None = None,
) -> set[str]:
    """Return bindings visible after successful process completion."""
    return visible_bindings(process.body, inputs, visit=visit)


__all__ = [
    "StatementVisitor",
    "process_visible_bindings",
    "sequence_always_fails",
    "validate_process_flow",
    "visible_bindings",
]
