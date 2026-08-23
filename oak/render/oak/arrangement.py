"""The OAK arrangement of a schema: its template, WHERE:, then one line per Where."""

import json

from oak.node.parts.schemas import AtLeast, AtMost, Lines, ListOf, MaxChars, NonEmpty, OneOf, Regex, Schema, Type, Where
from oak.vocabulary.text.placeholder import token


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


def sentence(constraint: Type | OneOf | Regex | NonEmpty | MaxChars | Lines | ListOf | AtLeast | AtMost) -> str:
    """The text the renderer writes for one constraint."""
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


def where_line(where: Where) -> str:
    """One WHERE line in authored order."""
    parts = [sentence(constraint) for constraint in where.constraints]
    parts += [f"example: `{_scalar(example)}`" for example in where.examples]
    if where.description is not None:
        parts.append(where.description)
    return f"- {token(where.placeholder)} " + "; ".join(parts) + "."


def schema_text(schema: Schema) -> str:
    """The exact template, one separator line feed when needed, then generated WHERE text."""
    separator = "" if schema.template.endswith(("\n", "\r")) else "\n"
    return schema.template + separator + "WHERE:\n" + "".join(where_line(where) + "\n" for where in schema.where)
