"""Process binding visibility and local control-flow validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_core import PydanticCustomError

from oak.node.parts.processes.steps import (
    Act,
    Call,
    Fail,
    Foreach,
    If,
    Join,
    Par,
    Step,
    While,
    step_values,
)
from oak.node.parts.processes.values import BindingValue, LiteralValue, Value

if TYPE_CHECKING:
    from oak.node.parts.processes.model import Process


def _check_value(
    value: Value,
    visible: set[str],
) -> None:
    if isinstance(value, BindingValue) and value.binding not in visible:
        raise PydanticCustomError(
            "unbound_process_binding",
            "process reads unbound local binding {binding}",
            {"binding": value.binding},
        )


def _promote(
    outputs: set[str],
    visible: set[str],
    label: str = "process",
) -> None:
    redefined = sorted(outputs & visible)

    if redefined:
        raise PydanticCustomError(
            "process_binding_redefined",
            f"{label} redefines visible local bindings: {{bindings}}",
            {"bindings": ", ".join(redefined)},
        )

    visible.update(outputs)


def visible_bindings(
    steps: list[Step],
    initial: set[str],
) -> set[str]:
    """Return the bindings visible after one successful step sequence."""
    visible = set(initial)
    pending: set[str] | None = None

    for step in steps:
        if pending is not None and not isinstance(step, Join):
            raise PydanticCustomError(
                "parallel_join_not_adjacent",
                "a step occurs between PAR and JOIN",
            )

        for value in step_values(step):
            _check_value(value, visible)

        if isinstance(step, Act):
            _promote(set(step.outputs), visible)

        elif isinstance(step, If):
            visible_bindings(step.then, visible)

            if step.otherwise is not None:
                visible_bindings(step.otherwise, visible)

        elif isinstance(step, Call):
            _promote(set(step.outputs), visible)

        elif isinstance(step, Foreach):
            if step.binding in visible:
                raise PydanticCustomError(
                    "foreach_binding_redefined",
                    "FOREACH redefines visible binding {binding}",
                    {"binding": step.binding},
                )

            if isinstance(step.value, LiteralValue) and not isinstance(
                step.value.value,
                list,
            ):
                raise PydanticCustomError(
                    "foreach_source_not_list",
                    "FOREACH literal source is not a list",
                )

            visible_bindings(
                step.steps,
                visible | {step.binding},
            )

        elif isinstance(step, While):
            visible_bindings(step.steps, visible)

        elif isinstance(step, Par):
            outputs = {
                output
                for child in step.steps
                if isinstance(child, Act)
                for output in child.outputs
            }
            redefined = sorted(outputs & visible)

            if redefined:
                raise PydanticCustomError(
                    "process_binding_redefined",
                    "PAR redefines visible local bindings: {bindings}",
                    {"bindings": ", ".join(redefined)},
                )

            pending = outputs

        elif isinstance(step, Join):
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


def sequence_always_fails(steps: list[Step]) -> bool:
    """Return whether one step sequence always ends in explicit failure."""
    for index, step in enumerate(steps):
        always_fails = isinstance(step, Fail)

        if isinstance(step, If):
            always_fails = (
                sequence_always_fails(step.then)
                and step.otherwise is not None
                and sequence_always_fails(step.otherwise)
            )

        elif isinstance(step, While):
            sequence_always_fails(step.steps)

        if always_fails:
            if index + 1 < len(steps):
                raise PydanticCustomError(
                    "unreachable_process_step",
                    "a process step follows a path that always fails",
                )

            return True

    return False


def validate_process_flow(process: Process) -> None:
    """Validate one process's local binding and failure flow."""
    if process.input is None:
        visible_bindings(process.steps, set())

    sequence_always_fails(process.steps)


def process_visible_bindings(
    process: Process,
    inputs: set[str],
) -> set[str]:
    """Return every binding visible after successful process completion."""
    return visible_bindings(process.steps, inputs)


__all__ = [
    "process_visible_bindings",
    "sequence_always_fails",
    "validate_process_flow",
    "visible_bindings",
]
