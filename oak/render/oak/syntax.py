"""The text syntax of schema and process content in the OAK render."""

import json

from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import (
    Act,
    BindingValue,
    Call,
    Condition,
    ConstantValue,
    Emit,
    Fail,
    If,
    InterfaceValue,
    LiteralValue,
    Process,
    Set,
    StateValue,
    Step,
    Value,
    ValueBinding,
)
from oak.node.parts.schemas import (
    AtLeast,
    AtMost,
    Constraint,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Type,
    Where,
)
from oak.node.parts.state import State
from oak.vocabulary.text.placeholder import token

WHERE_HEADING = "WHERE:"
WHERE_ENTRY_PREFIX = "- "
WHERE_DETAIL_SEPARATOR = "; "


def _scalar(value: str | int | float | bool) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _bound(value: int | float | str) -> str:
    return token(value) if isinstance(value, str) else _scalar(value)


def _lines(constraint: Lines) -> str:
    if constraint.min is not None and constraint.max is not None:
        if constraint.min == constraint.max == 1:
            return "is one line"
        if constraint.min == constraint.max:
            return f"has {constraint.min} lines"
        return f"has {constraint.min} to {constraint.max} lines"
    if constraint.max is not None:
        return "is one line" if constraint.max == 1 else f"has at most {constraint.max} lines"
    return f"has at least {constraint.min} lines"


def constraint_text(constraint: Constraint) -> str:
    """Return the OAK text for one schema constraint."""
    match constraint:
        case Type():
            return f"is {constraint.of}"
        case OneOf():
            return "is one of " + ", ".join(
                f"`{_scalar(value)}`" for value in constraint.values
            )
        case Regex():
            return f"matches `{constraint.pattern}`"
        case NonEmpty():
            return "is non-empty"
        case MaxChars():
            return f"is at most {constraint.n} characters"
        case Lines():
            return _lines(constraint)
        case ListOf():
            return f"is a list of {constraint.item} joined by `{constraint.separator}`"
        case AtLeast():
            return f"is at least {_bound(constraint.value)}"
        case AtMost():
            return f"is at most {_bound(constraint.value)}"
    raise TypeError(f"unsupported constraint {type(constraint).__name__}")


def where_line(where: Where) -> str:
    """Return one dense line: the delimited placeholder, then its details."""
    body = WHERE_DETAIL_SEPARATOR.join(
        constraint_text(constraint) for constraint in where.constraints
    )
    if where.examples:
        body += " (e.g. " + ", ".join(
            f"`{_scalar(example)}`" for example in where.examples
        ) + ")"
    if where.description is not None:
        body += WHERE_DETAIL_SEPARATOR + where.description
    return WHERE_ENTRY_PREFIX + token(where.placeholder) + " " + body + "."


def value_text(value: object) -> str:
    """Return one JSON value on one line."""
    return json.dumps(value, ensure_ascii=False)


def named_value_line(entry: Constant | State) -> str:
    """Return one `NAME: value` line for a constant or a state value."""
    return f"{entry.name}: {value_text(entry.value)}"


def process_value_text(value: Value) -> str:
    """Return one dense process value reference."""
    match value:
        case LiteralValue():
            return value_text(value.value)
        case ConstantValue():
            return f"constant {value.constant}"
        case StateValue():
            return f"state {value.state}"
        case InterfaceValue():
            return f"interface {value.interface} {token(value.placeholder)}"
        case BindingValue():
            return f"binding {token(value.binding)}"
    raise TypeError(f"unsupported process value {type(value).__name__}")


def condition_text(condition: Condition) -> str:
    """Return one process condition."""
    operator = "equals" if condition.operator == "equals" else "does not equal"
    return (
        f"{process_value_text(condition.left)} {operator} "
        f"{process_value_text(condition.right)}"
    )


def _binding_line(binding: ValueBinding, indent: int) -> str:
    return " " * indent + f"{token(binding.placeholder)} = {process_value_text(binding.value)}"


def _step_lines(step: Step, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2

    if isinstance(step, Act):
        lines = [prefix + f"ACT {step.instruction}"]
        if step.inputs:
            lines.append(" " * inner + "INPUTS:")
            lines.extend(_binding_line(binding, inner + 2) for binding in step.inputs)
        if step.outputs:
            outputs = ", ".join(token(output) for output in step.outputs)
            lines.append(" " * inner + f"OUTPUTS: {outputs}")
        return lines
    if isinstance(step, Set):
        return [prefix + f"SET state {step.state} = {process_value_text(step.value)}"]
    if isinstance(step, Emit):
        lines = [prefix + f"EMIT interface {step.interface}:"]
        lines.extend(_binding_line(binding, inner) for binding in step.bindings)
        return lines
    if isinstance(step, If):
        lines = [prefix + f"IF {condition_text(step.condition)}:"]
        for child in step.then:
            lines.extend(_step_lines(child, inner))
        if step.otherwise is not None:
            lines.append(prefix + "ELSE:")
            for child in step.otherwise:
                lines.extend(_step_lines(child, inner))
        return lines
    if isinstance(step, Call):
        return [prefix + f"CALL process {step.process}"]
    if isinstance(step, Fail):
        return [prefix + f"FAIL {value_text(step.message)}"]
    raise TypeError(f"unsupported process step {type(step).__name__}")


def process_lines(process: Process) -> list[str]:
    """Return the process inner lines: its steps in order, grouped by indentation."""
    lines: list[str] = []
    for step in process.steps:
        lines.extend(_step_lines(step, 0))
    return lines


def interface_body(interface: Interface) -> str:
    """Return the interface inner text: its description, or nothing."""
    return interface.description or ""
