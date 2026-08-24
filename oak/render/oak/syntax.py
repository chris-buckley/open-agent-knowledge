"""The text syntax of schema content in the OAK render."""

import json

from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import Process
from oak.node.parts.schemas import AtLeast, AtMost, Constraint, Lines, ListOf, MaxChars, NonEmpty, OneOf, Regex, Type, Where
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
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
            return "is one of " + ", ".join(f"`{_scalar(value)}`" for value in constraint.values)
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
    """Return one dense line: the delimited placeholder, then its details joined by `; `."""
    body = WHERE_DETAIL_SEPARATOR.join(constraint_text(constraint) for constraint in where.constraints)
    if where.examples:
        body += " (e.g. " + ", ".join(f"`{_scalar(example)}`" for example in where.examples) + ")"
    if where.description is not None:
        body += WHERE_DETAIL_SEPARATOR + where.description
    return WHERE_ENTRY_PREFIX + token(where.placeholder) + " " + body + "."


def value_text(value: object) -> str:
    """Return one JSON value on one line."""
    return json.dumps(value, ensure_ascii=False)


def named_value_line(entry: Constant | State) -> str:
    """Return one `NAME: value` line for a constant or a state value."""
    return f"{entry.name}: {value_text(entry.value)}"


def trigger_line(trigger: Trigger) -> str:
    """Return one trigger line: its text, then an arrow to its process id."""
    return f"- {trigger.when} -> {trigger.process}"


def process_lines(process: Process) -> list[str]:
    """Return the process inner lines: references, then numbered steps."""
    lines = []
    if process.consumes:
        lines.append("consumes: " + ", ".join(process.consumes))
    if process.emits:
        lines.append("emits: " + ", ".join(process.emits))
    lines.extend(f"{number}. {step}" for number, step in enumerate(process.steps, start=1))
    return lines


def interface_body(interface: Interface) -> str:
    """Return the interface inner text: its description, or nothing."""
    return interface.description or ""
