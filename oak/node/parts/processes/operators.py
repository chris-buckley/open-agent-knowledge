"""Condition operator names, authored text, and strict comparison semantics."""

from __future__ import annotations

from typing import Literal

ConditionOperator = Literal[
    "equals",
    "not_equals",
    "less_than",
    "less_than_or_equal",
    "greater_than",
    "greater_than_or_equal",
]

OPERATOR_TEXT: dict[ConditionOperator, str] = {
    "equals": "equals",
    "not_equals": "does not equal",
    "less_than": "is less than",
    "less_than_or_equal": "is at most",
    "greater_than": "is greater than",
    "greater_than_or_equal": "is at least",
}

OPERATOR_PHRASES: tuple[tuple[str, ConditionOperator], ...] = (
    (" does not equal ", "not_equals"),
    (" is less than ", "less_than"),
    (" is at most ", "less_than_or_equal"),
    (" is greater than ", "greater_than"),
    (" is at least ", "greater_than_or_equal"),
    (" equals ", "equals"),
)

_INVERSE_OPERATOR: dict[ConditionOperator, ConditionOperator] = {
    "equals": "not_equals",
    "not_equals": "equals",
    "less_than": "greater_than_or_equal",
    "less_than_or_equal": "greater_than",
    "greater_than": "less_than_or_equal",
    "greater_than_or_equal": "less_than",
}

_REVERSE_OPERATOR: dict[ConditionOperator, ConditionOperator] = {
    "equals": "equals",
    "not_equals": "not_equals",
    "less_than": "greater_than",
    "less_than_or_equal": "greater_than_or_equal",
    "greater_than": "less_than",
    "greater_than_or_equal": "less_than_or_equal",
}


class OrderedComparisonTypeError(ValueError):
    """Two values cannot participate in one ordered comparison."""


def json_equal(left: object, right: object) -> bool:
    """Return strict JSON equality without treating booleans as numbers."""
    if isinstance(left, bool) or isinstance(right, bool):
        return (
            isinstance(left, bool)
            and isinstance(right, bool)
            and left == right
        )
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            json_equal(a, b)
            for a, b in zip(left, right, strict=True)
        )
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            json_equal(left[key], right[key])
            for key in left
        )
    return type(left) is type(right) and left == right


def ordered_pair(
    left: object,
    right: object,
) -> tuple[int | float | str, int | float | str] | None:
    """Return comparable ordered operands, or null when their types differ."""
    if isinstance(left, bool) or isinstance(right, bool):
        return None
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left, right
    if isinstance(left, str) and isinstance(right, str):
        return left, right
    return None


def compare_values(
    operator: ConditionOperator,
    left: object,
    right: object,
) -> bool:
    """Evaluate one strict equality or ordered comparison."""
    if operator == "equals":
        return json_equal(left, right)
    if operator == "not_equals":
        return not json_equal(left, right)

    pair = ordered_pair(left, right)
    if pair is None:
        raise OrderedComparisonTypeError(
            "ordered comparison needs two numbers or two strings"
        )

    a, b = pair
    if operator == "less_than":
        return a < b
    if operator == "less_than_or_equal":
        return a <= b
    if operator == "greater_than":
        return a > b
    return a >= b


def invert_operator(operator: ConditionOperator) -> ConditionOperator:
    """Return the logical inverse of one comparison operator."""
    return _INVERSE_OPERATOR[operator]


def reverse_operator(operator: ConditionOperator) -> ConditionOperator:
    """Return the equivalent operator after swapping its operands."""
    return _REVERSE_OPERATOR[operator]


__all__ = [
    "ConditionOperator",
    "OPERATOR_PHRASES",
    "OPERATOR_TEXT",
    "OrderedComparisonTypeError",
    "compare_values",
    "invert_operator",
    "json_equal",
    "ordered_pair",
    "reverse_operator",
]
