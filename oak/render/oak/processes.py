"""Process value, condition, step, and process text rendering."""

from __future__ import annotations

from collections.abc import Sequence

from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Condition,
    Not,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.operators import OPERATOR_TEXT
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
    Step,
    While,
)
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    LiteralValue,
    StateValue,
    Value,
    ValueBinding,
)
from oak.render.oak.data import value_text
from oak.surface.registry import surface_for


def process_value_text(value: Value) -> str:
    """Return one JSON literal or process value reference."""
    surface_for(value)

    match value:
        case LiteralValue():
            return value_text(value.value)

        case ConstantValue():
            return "$" + value.constant

        case StateValue():
            return "$" + value.state

        case BindingValue():
            return "$" + value.binding

    raise TypeError(f"unsupported process value {type(value).__name__}")


def condition_lines(condition: Condition, indent: int = 0) -> list[str]:
    """Return one recursive condition in prefix form."""
    surface_for(condition)
    prefix = " " * indent

    match condition:
        case Compare():
            return [
                prefix
                + process_value_text(condition.left)
                + " "
                + OPERATOR_TEXT[condition.operator]
                + " "
                + process_value_text(condition.right)
            ]

        case All() | Any():
            lines = [prefix + ("ALL:" if isinstance(condition, All) else "ANY:")]

            for child in condition.conditions:
                lines.extend(condition_lines(child, indent + 2))

            return lines

        case Not():
            return [prefix + "NOT:", *condition_lines(condition.condition, indent + 2)]

    raise TypeError(f"unsupported condition {type(condition).__name__}")


def condition_text(condition: Condition) -> str:
    """Return one recursive condition."""
    return "\n".join(condition_lines(condition))


def _binding_line(binding: ValueBinding, indent: int) -> str:
    surface_for(binding)
    return " " * indent + f"{binding.placeholder}=" + process_value_text(binding.value)


def _suffix_text(bindings: Sequence[ValueBinding], outputs: Sequence[str]) -> str:
    body = "(" + ", ".join(_binding_line(binding, 0) for binding in bindings) + ")"

    if outputs:
        body += " -> " + ", ".join(outputs)

    return body


def _act_attributes(step: Act) -> str:
    attributes = ""

    if step.input is not None:
        attributes += f' input="{step.input}"'

    if step.output is not None:
        attributes += f' output="{step.output}"'

    return attributes


def _act_lines(step: Act, indent: int) -> list[str]:
    prefix = " " * indent
    surface_for(step)
    attributes = _act_attributes(step)

    if step.tool is None:
        head = "ACT" + attributes + (": " if attributes else " ") + step.instruction

    else:
        head = "ACT TOOL " + value_text(step.tool) + attributes + ": " + step.instruction

    return [prefix + head + " " + _suffix_text(step.inputs, step.outputs)]


def _call_lines(step: Call, indent: int) -> list[str]:
    prefix = " " * indent
    return [prefix + "CALL " + step.process + " " + _suffix_text(step.inputs, step.outputs)]


def _set_lines(step: Set, indent: int) -> list[str]:
    prefix = " " * indent
    return [prefix + "SET " + step.state + " = " + process_value_text(step.value)]


def _emit_lines(step: Emit, indent: int) -> list[str]:
    prefix = " " * indent
    suffix = (
        ""
        if not step.bindings
        else " " + _suffix_text(step.bindings, [])
    )
    return [prefix + "EMIT " + step.interface + suffix]


def _child_lines(steps: Sequence[Step], indent: int) -> list[str]:
    lines: list[str] = []

    for child in steps:
        lines.extend(_step_lines(child, indent))

    return lines


def _if_lines(step: If, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    condition = condition_lines(step.condition)

    if len(condition) == 1:
        lines = [prefix + "IF " + condition[0] + ":"]

    else:
        lines = [prefix + "IF:", *(" " * inner + line for line in condition)]

    lines.append(" " * inner + "THEN:")
    lines.extend(_child_lines(step.then, inner + 2))

    if step.otherwise is not None:
        lines.append(" " * inner + "ELSE:")
        lines.extend(_child_lines(step.otherwise, inner + 2))

    return lines


def _fail_lines(step: Fail, indent: int) -> list[str]:
    prefix = " " * indent
    return [prefix + "FAIL " + value_text(step.message)]


def _assert_lines(step: Assert, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    condition = condition_lines(step.condition)

    if len(condition) == 1:
        lines = [prefix + "ASSERT " + condition[0]]

    else:
        lines = [prefix + "ASSERT:", *(" " * inner + line for line in condition)]

    if step.message is not None:
        lines.append(" " * inner + "MESSAGE " + value_text(step.message))

    return lines


def _foreach_lines(step: Foreach, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    head = prefix + f"FOREACH {step.binding} IN " + process_value_text(step.value) + ":"
    return [head, *_child_lines(step.steps, inner)]


def _while_lines(step: While, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    condition = condition_lines(step.condition)

    if len(condition) == 1:
        lines = [prefix + "WHILE " + condition[0] + f" LIMIT {step.limit}:"]
        child_indent = inner

    else:
        lines = [
            prefix + f"WHILE LIMIT {step.limit}:",
            *(" " * inner + line for line in condition),
            " " * inner + "THEN:",
        ]
        child_indent = inner + 2

    lines.extend(_child_lines(step.steps, child_indent))
    return lines


def _par_lines(step: Par, indent: int) -> list[str]:
    prefix = " " * indent
    return [prefix + "PAR:", *_child_lines(step.steps, indent + 2)]


def _step_lines(step: Step, indent: int) -> list[str]:
    surface_for(step)

    match step:
        case Act():
            return _act_lines(step, indent)

        case Set():
            return _set_lines(step, indent)

        case Emit():
            return _emit_lines(step, indent)

        case If():
            return _if_lines(step, indent)

        case Call():
            return _call_lines(step, indent)

        case Fail():
            return _fail_lines(step, indent)

        case Assert():
            return _assert_lines(step, indent)

        case Foreach():
            return _foreach_lines(step, indent)

        case While():
            return _while_lines(step, indent)

        case Par():
            return _par_lines(step, indent)

        case Join():
            return [" " * indent + "JOIN"]

    raise TypeError(f"unsupported process step {type(step).__name__}")


def process_lines(process: Process) -> list[str]:
    """Return process steps in authored order."""
    surface_for(process)
    return _child_lines(process.steps, 0)


def binding_line(binding: ValueBinding, indent: int = 0) -> str:
    """Return one process binding line."""
    return _binding_line(binding, indent)


def step_lines(step: Step, indent: int = 0) -> list[str]:
    """Return one typed step in OAK syntax."""
    return _step_lines(step, indent)


__all__ = [
    "binding_line",
    "condition_lines",
    "condition_text",
    "process_lines",
    "process_value_text",
    "step_lines",
]
