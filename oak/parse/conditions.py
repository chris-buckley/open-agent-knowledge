"""Inline and recursive process condition parsing."""

from __future__ import annotations

from oak.node.parts.processes import (
    All,
    Any,
    Compare,
    Condition,
    Not,
)
from oak.node.parts.processes.operators import OPERATOR_PHRASES
from oak.parse.cursor import Cursor
from oak.parse.errors import fail
from oak.parse.values import parse_value


def parse_compare(
    source: str,
    path: str,
    line: int,
) -> Compare:
    """Parse one inline comparison."""
    for phrase, operator in OPERATOR_PHRASES:
        if phrase in source:
            left, right = source.split(
                phrase,
                1,
            )
            return Compare(
                left=parse_value(
                    left,
                    path,
                    line,
                ),
                operator=operator,
                right=parse_value(
                    right,
                    path,
                    line,
                ),
            )

    fail(
        "condition_compare",
        path,
        line,
        "condition needs one comparison operator",
    )


def parse_condition(
    cursor: Cursor,
    indent: int,
) -> Condition:
    """Parse one inline or recursive condition at the cursor."""
    if cursor.at_end:
        cursor.fail(
            "condition_missing",
            "condition is missing",
        )

    number = cursor.line_number
    actual = cursor.indentation()

    if actual != indent:
        cursor.fail(
            "condition_indent",
            f"condition needs {indent} spaces",
        )

    line = cursor.peek()
    if line is None:
        cursor.fail(
            "condition_missing",
            "condition is missing",
        )

    text = line[indent:]

    if text in ("ALL:", "ANY:"):
        kind = text[:-1]
        cursor.advance()
        children = []

        while (
            not cursor.at_end
            and cursor.indentation() >= indent + 2
        ):
            children.append(
                parse_condition(
                    cursor,
                    indent + 2,
                )
            )

        return (
            All(conditions=children)
            if kind == "ALL"
            else Any(conditions=children)
        )

    if text == "NOT:":
        cursor.advance()
        return Not(
            condition=parse_condition(
                cursor,
                indent + 2,
            )
        )

    cursor.advance()
    return parse_compare(
        text,
        cursor.path,
        number,
    )


__all__ = [
    "parse_compare",
    "parse_condition",
]
