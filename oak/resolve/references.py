"""Typed target traversal across one OAK document."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from oak.base import Entry
from oak.node import Node
from oak.node.parts import (
    Act,
    Assert,
    Call,
    Constant,
    ConstantValue,
    Emit,
    Foreach,
    If,
    Par,
    Process,
    Schema,
    Set,
    Step,
    While,
)
from oak.node.parts.processes.conditions import condition_values
from oak.node.parts.processes.values import Value


def value_targets(
    values: Iterable[Value],
) -> Iterator[tuple[str, type[Entry]]]:
    """Yield each externally resolvable target read by process values."""
    for value in values:
        if isinstance(value, ConstantValue):
            yield value.constant, Constant


def step_references(
    step: Step,
) -> Iterator[tuple[str, type[Entry]]]:
    """Yield every typed target used by one step and its children."""
    if isinstance(step, Act):
        if step.input is not None:
            yield step.input, Schema

        if step.output is not None:
            yield step.output, Schema

        yield from value_targets(
            binding.value
            for binding in step.inputs
        )

    elif isinstance(step, Set):
        yield from value_targets(
            (step.value,)
        )

    elif isinstance(step, Emit):
        yield from value_targets(
            binding.value
            for binding in step.bindings
        )

    elif isinstance(step, If):
        yield from value_targets(
            condition_values(step.condition)
        )

        for child in step.then:
            yield from step_references(child)

        if step.otherwise is not None:
            for child in step.otherwise:
                yield from step_references(child)

    elif isinstance(step, Assert):
        yield from value_targets(
            condition_values(step.condition)
        )

    elif isinstance(step, Foreach):
        yield from value_targets(
            (step.value,)
        )

        for child in step.steps:
            yield from step_references(child)

    elif isinstance(step, While):
        yield from value_targets(
            condition_values(step.condition)
        )

        for child in step.steps:
            yield from step_references(child)

    elif isinstance(step, Par):
        for child in step.steps:
            yield from step_references(child)

    elif isinstance(step, Call):
        yield from value_targets(
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
        yield from value_targets(
            binding.value
            for binding in trigger.seed
        )

        if trigger.guard is not True:
            yield from value_targets(
                condition_values(trigger.guard)
            )

    for process in node.processes:
        for step in process.steps:
            yield from step_references(step)


def steps_targets_in_process(
    steps: list[Step],
) -> Iterator[tuple[str, type[Entry]]]:
    """Yield each typed target used by one process step sequence."""
    for step in steps:
        yield from step_references(step)


def iter_steps(
    steps: list[Step],
) -> Iterator[Step]:
    """Yield each step recursively in authored order."""
    for step in steps:
        yield step

        if isinstance(step, If):
            yield from iter_steps(step.then)

            if step.otherwise is not None:
                yield from iter_steps(step.otherwise)

        elif isinstance(step, (Foreach, While, Par)):
            yield from iter_steps(step.steps)


def walk_calls(
    steps: list[Step],
) -> Iterator[Call]:
    """Yield each process call recursively in authored order."""
    for step in steps:
        if isinstance(step, Call):
            yield step

        elif isinstance(step, If):
            yield from walk_calls(step.then)

            if step.otherwise is not None:
                yield from walk_calls(step.otherwise)

        elif isinstance(step, Foreach):
            yield from walk_calls(step.steps)

        elif isinstance(step, While):
            yield from walk_calls(step.steps)

        elif isinstance(step, Par):
            yield from walk_calls(step.steps)


__all__ = [
    "iter_steps",
    "iter_targets",
    "step_references",
    "steps_targets_in_process",
    "value_targets",
    "walk_calls",
]
