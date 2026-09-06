"""Typed target traversal across one OAK document."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence

from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.entry import Entry
from oak.node.parts.processes.conditions import condition_values
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.statements import (
    Act,
    Assert,
    Call,
    Emit,
    Foreach,
    If,
    Par,
    Set,
    Statement,
    While,
    iter_statements,
)
from oak.node.parts.processes.values import ConstantValue, Value
from oak.node.parts.schemas.model import Schema

TypedTarget = tuple[str, type[Entry]]


def value_targets(values: Iterable[Value]) -> Iterator[TypedTarget]:
    """Yield each externally resolvable target read by process values."""
    for value in values:
        if isinstance(value, ConstantValue):
            yield value.constant, Constant


def statement_references(step: Statement) -> Iterator[TypedTarget]:
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
            yield from statements_targets_in_process(step.then)

            if step.otherwise is not None:
                yield from statements_targets_in_process(step.otherwise)

        case Foreach() | While() | Par():
            yield from statements_targets_in_process(step.body)


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
        yield from statements_targets_in_process(process.body)


def statements_targets_in_process(body: Sequence[Statement]) -> Iterator[TypedTarget]:
    """Yield each typed target used by one process step sequence."""
    for step in body:
        yield from statement_references(step)


def walk_calls(body: Sequence[Statement]) -> Iterator[Call]:
    """Yield each process call recursively in authored order."""
    return (step for step in iter_statements(body) if isinstance(step, Call))


__all__ = [
    "iter_targets",
    "statement_references",
    "statements_targets_in_process",
    "value_targets",
    "walk_calls",
]
