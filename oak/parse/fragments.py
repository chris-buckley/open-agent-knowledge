"""Intentional parsing of one rendered authoring-surface fragment."""

from __future__ import annotations

from oak.base import OakModel
from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Not,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Call,
    Emit,
    Fail,
    Foreach,
    If,
    Join,
    Par,
    Set,
    While,
)
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    LiteralValue,
    StateValue,
    ValueBinding,
)
from oak.node.parts.schemas.constraints import (
    AtLeast,
    AtMost,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Type,
)
from oak.node.parts.schemas.model import Schema, Where
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.parse.conditions import parse_condition
from oak.parse.cursor import Cursor
from oak.parse.data import parse_constants, parse_state
from oak.parse.document import parse
from oak.parse.grouping import GroupingName
from oak.parse.interfaces import parse_interfaces
from oak.parse.processes import parse_processes
from oak.parse.schemas import (
    parse_constraint,
    parse_schemas,
    parse_where,
)
from oak.parse.steps import parse_steps
from oak.parse.triggers import parse_triggers
from oak.parse.values import parse_binding, parse_value

_CONSTRAINT_MODELS = (
    Type,
    OneOf,
    Regex,
    NonEmpty,
    MaxChars,
    Lines,
    ListOf,
    AtLeast,
    AtMost,
)
_VALUE_MODELS = (
    LiteralValue,
    ConstantValue,
    StateValue,
    BindingValue,
)
_CONDITION_MODELS = (
    Compare,
    All,
    Any,
    Not,
)
_STEP_MODELS = (
    Act,
    Set,
    Emit,
    If,
    Call,
    Fail,
    Assert,
    Foreach,
    While,
    Par,
    Join,
)


def parse_fragment(
    model: type[OakModel],
    text: str,
    *,
    grouping: GroupingName = "xml",
    path: str | None = None,
    line: int = 1,
) -> OakModel:
    """Parse one canonical fragment through the document parser components."""
    path = path or model.__name__.lower()
    lines = text.splitlines()

    if model is Node:
        return parse(
            text,
            grouping=grouping,
        )

    if model is Instruction:
        return Instruction(
            id="generated",
            body=text,
        )

    if model is Constant:
        return parse_constants(
            lines,
            line,
        )[0]

    if model is Schema:
        return parse_schemas(
            lines,
            line,
            grouping,
        )[0]

    if model is State:
        return parse_state(
            lines,
            line,
        )[0]

    if model is Trigger:
        return parse_triggers(
            lines,
            line,
        )[0]

    if model is Process:
        return parse_processes(
            lines,
            line,
            grouping,
        )[0]

    if model is Interface:
        return parse_interfaces(
            lines,
            line,
            grouping,
        )[0]

    if model in _CONSTRAINT_MODELS:
        constraint = parse_constraint(
            text,
            path,
            line,
        )
        if constraint is None:
            raise TypeError(
                f"unsupported constraint fragment {text}"
            )
        return constraint

    if model is Where:
        return parse_where(
            text,
            path,
            line,
        )

    if model in _VALUE_MODELS:
        return parse_value(
            text,
            path,
            line,
        )

    if model is ValueBinding:
        return parse_binding(
            text,
            path,
            line,
        )

    if model in _CONDITION_MODELS:
        return parse_condition(
            Cursor(
                lines,
                path,
                line,
            ),
            0,
        )

    if model in _STEP_MODELS:
        return parse_steps(
            Cursor(
                lines,
                path,
                line,
            ),
            0,
        )[0]

    raise TypeError(model.__name__)


__all__ = [
    "parse_fragment",
]
