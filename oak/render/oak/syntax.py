"""The text syntax of schema content in the OAK render."""

import json

from oak.node.parts.schemas import AtLeast, AtMost, Constraint, Lines, ListOf, MaxChars, NonEmpty, OneOf, Regex, Type, Where
from oak.vocabulary.text.placeholder import token

WHERE_HEADING = "WHERE:"
WHERE_ENTRY_PREFIX = "- "
WHERE_DETAIL_PREFIX = "  - "


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


def where_lines(where: Where) -> list[str]:
    """Return one placeholder line and its authored detail lines."""
    details = [constraint_text(constraint) for constraint in where.constraints]
    details.extend(f"example: `{_scalar(example)}`" for example in where.examples)
    if where.description is not None:
        details.append(where.description)
    return [
        WHERE_ENTRY_PREFIX + token(where.placeholder),
        *(WHERE_DETAIL_PREFIX + detail for detail in details),
    ]
