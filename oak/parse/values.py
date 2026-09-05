"""Process value and binding entry points, and ACT schema attributes."""

from __future__ import annotations

import re

from oak.node.parts.processes.values import Value, ValueBinding
from oak.parse.expressions import ExpressionReader

_ACT_INPUT_RE = re.compile(r'^ input="([^"]+)"')
_ACT_OUTPUT_RE = re.compile(r'^ output="([^"]+)"')


def parse_value(source: str, path: str, line: int) -> Value:
    """Parse one complete literal or typed value reference."""
    reader = ExpressionReader(source, path, line)
    value = reader.value()
    reader.finish()
    return value


def parse_binding(source: str, path: str, line: int) -> ValueBinding:
    """Parse one complete NAME=value binding."""
    reader = ExpressionReader(source, path, line)
    binding = reader.binding()
    reader.finish()
    return binding


def parse_act_attributes(
    source: str,
) -> tuple[
    str | None,
    str | None,
    str,
] | None:
    """Parse optional act input and output schema attributes."""
    input_target = None
    output_target = None
    rest = source

    match = _ACT_INPUT_RE.match(rest)
    if match:
        input_target = match.group(1)
        rest = rest[match.end() :]

    match = _ACT_OUTPUT_RE.match(rest)
    if match:
        output_target = match.group(1)
        rest = rest[match.end() :]

    if (
        input_target is None
        and output_target is None
    ):
        return None

    if not rest.startswith(": "):
        return None

    return (
        input_target,
        output_target,
        rest[2:],
    )


__all__ = ["parse_act_attributes", "parse_binding", "parse_value"]
