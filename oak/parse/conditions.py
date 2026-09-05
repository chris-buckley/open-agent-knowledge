"""Shared condition-expression entry points."""

from oak.node.parts.processes.conditions import Compare, Condition
from oak.parse.cursor import Cursor
from oak.parse.expressions import ExpressionReader


def parse_compare(source: str, path: str, line: int) -> Compare:
    """Parse exactly one comparison without looking inside quoted operands."""
    reader = ExpressionReader(source, path, line)
    condition = reader.condition()
    reader.finish()
    if not isinstance(condition, Compare):
        reader.fail("condition_compare", "expected one comparison", 0)
    return condition


def parse_condition(cursor: Cursor, indent: int) -> Condition:
    """Parse one flat or delimiter-continued condition, preserving physical lines."""
    if cursor.at_end:
        cursor.fail("condition_missing", "condition is missing")
    if cursor.indentation() != indent:
        cursor.fail("condition_indent", f"condition needs {indent} spaces")
    reader = ExpressionReader.at(cursor, cursor.peek()[indent:])
    condition = reader.condition()
    reader.finish(cursor)
    return condition


__all__ = ["parse_compare", "parse_condition"]
