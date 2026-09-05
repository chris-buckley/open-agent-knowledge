"""Deterministic layout for OAK lists; JSON literals and prose remain atomic."""

from __future__ import annotations

from dataclasses import dataclass

from oak.surface.syntax import CANONICAL_WIDTH, INDENT_WIDTH


@dataclass(frozen=True, slots=True)
class ListText:
    """One named or anonymous parenthesised list, not an evaluated expression."""

    head: str
    items: tuple[str | ListText, ...]


def flat_text(expression: str | ListText) -> str:
    if isinstance(expression, str):
        return expression
    return expression.head + "(" + ", ".join(flat_text(item) for item in expression.items) + ")"


def prefixed(expression: str | ListText, prefix: str) -> str | ListText:
    """Label an expression without losing its available list breakpoints."""
    if isinstance(expression, str):
        return prefix + expression
    return ListText(prefix + expression.head, expression.items)


def expression_lines(
    expression: str | ListText, indent: int = 0, *, prefix: str = "", suffix: str = "",
) -> list[str]:
    """Fit the complete flat line, else expand its outer list and recurse."""
    padding = " " * indent
    flat = padding + prefix + flat_text(expression) + suffix
    if (
        len(flat) <= CANONICAL_WIDTH
        or isinstance(expression, str)
        or not expression.items
    ):
        return [flat]
    lines = [padding + prefix + expression.head + "("]
    for item in expression.items:
        lines.extend(expression_lines(item, indent + INDENT_WIDTH, suffix=","))
    lines.append(padding + ")" + suffix)
    return lines
