"""Typed target traversal across one OAK document."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence

from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.entry import Entry
from oak.node.parts.processes.conditions import condition_values
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Call,
    Emit,
    Foreach,
    If,
    Par,
    Set,
    Step,
    While,
    iter_steps,
)
from oak.node.parts.processes.values import ConstantValue, Value
from oak.node.parts.schemas.model import Schema

TypedTarget = tuple[str, type[Entry]]


def value_targets(values: Iterable[Value]) -> Iterator[TypedTarget]:
    """Yield each externally resolvable target read by process values."""
    for value in values:
        if isinstance(value, ConstantValue):
            yield value.constant, Constant


def step_references(step: Step) -> Iterator[TypedTarget]:
    """Yield every typed target used by one step and its children."""
    match step:
        case Act():
            if step.input is not None:
                yield step.input, Schema

            if step.output is not None:
                yield step.output, Schema

            yield from value_targets(binding.value for binding in step.inputs)

        case Set() | Foreach():
            yield from value_targets((step.value,))

        case Emit():
            yield from value_targets(binding.value for binding in step.bindings)

        case If() | Assert() | While():
            yield from value_targets(condition_values(step.condition))

        case Call():
            yield from value_targets(binding.value for binding in step.inputs)
            yield step.process, Process

    match step:
        case If():
            yield from steps_targets_in_process(step.then)

            if step.otherwise is not None:
                yield from steps_targets_in_process(step.otherwise)

        case Foreach() | While() | Par():
            yield from steps_targets_in_process(step.steps)


def iter_targets(node: Node) -> Iterator[TypedTarget]:
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
        yield from value_targets(binding.value for binding in trigger.seed)

        if trigger.guard is not True:
            yield from value_targets(condition_values(trigger.guard))

    for process in node.processes:
        yield from steps_targets_in_process(process.steps)


def steps_targets_in_process(steps: Sequence[Step]) -> Iterator[TypedTarget]:
    """Yield each typed target used by one process step sequence."""
    for step in steps:
        yield from step_references(step)


def walk_calls(steps: Sequence[Step]) -> Iterator[Call]:
    """Yield each process call recursively in authored order."""
    return (step for step in iter_steps(steps) if isinstance(step, Call))


__all__ = [
    "iter_targets",
    "step_references",
    "steps_targets_in_process",
    "value_targets",
    "walk_calls",
]
