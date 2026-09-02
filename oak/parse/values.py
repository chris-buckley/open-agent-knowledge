"""Process values, bindings, and binding-suffix parsing."""

from __future__ import annotations

import json
import re

from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    InterfaceValue,
    LiteralValue,
    StateValue,
    Value,
    ValueBinding,
)
from oak.parse.data import parse_json_value
from oak.parse.errors import fail
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX

_SUFFIX_PLACEHOLDER_RE = re.compile(
    PLACEHOLDER_SYNTAX.body
)
_ACT_INPUT_RE = re.compile(
    r'^ input="([^"]+)"'
)
_ACT_OUTPUT_RE = re.compile(
    r'^ output="([^"]+)"'
)


def parse_value(
    source: str,
    path: str,
    line: int,
) -> Value:
    """Parse one literal or referenced process value."""
    if not source.startswith("$"):
        return LiteralValue(
            value=parse_json_value(
                source,
                path,
                line,
            )
        )

    target = source[1:]

    if target.startswith("state."):
        return StateValue(
            state=target
        )

    if target.startswith("interface."):
        parts = target.split(".")

        if len(parts) != 3:
            fail(
                "interface_value",
                path,
                line,
                "interface value needs one placeholder",
            )

        return InterfaceValue(
            interface=".".join(
                parts[:2]
            ),
            placeholder=parts[2],
        )

    if (
        target.startswith("constant.")
        or "#constant." in target
    ):
        return ConstantValue(
            constant=target
        )

    return BindingValue(
        binding=target
    )


def parse_binding(
    source: str,
    path: str,
    line: int,
) -> ValueBinding:
    """Parse one PLACEHOLDER=value binding."""
    placeholder, separator, value = source.partition("=")

    if not separator:
        fail(
            "binding",
            path,
            line,
            "binding needs NAME=value",
        )

    return ValueBinding(
        placeholder=placeholder,
        value=parse_value(
            value,
            path,
            line,
        ),
    )


def _suffix_value(
    source: str,
    position: int,
) -> int | None:
    if source.startswith(
        "$",
        position,
    ):
        end = position + 1

        while (
            end < len(source)
            and source[end] not in ",)"
        ):
            end += 1

        return end

    try:
        _, end = json.JSONDecoder().raw_decode(
            source,
            position,
        )
    except json.JSONDecodeError:
        return None

    return end


def parse_suffix(
    source: str,
) -> tuple[
    list[tuple[str, str]],
    list[str],
] | None:
    """Return bindings and outputs from one exact binding suffix."""
    if not source.startswith("("):
        return None

    bindings: list[
        tuple[str, str]
    ] = []
    position = 1

    if source.startswith(
        ")",
        position,
    ):
        position += 1

    else:
        while True:
            end = source.find(
                "=",
                position,
            )

            if (
                end == -1
                or _SUFFIX_PLACEHOLDER_RE.fullmatch(
                    source,
                    position,
                    end,
                )
                is None
            ):
                return None

            value_start = end + 1
            value_end = _suffix_value(
                source,
                value_start,
            )

            if value_end is None:
                return None

            bindings.append(
                (
                    source[position:end],
                    source[value_start:value_end],
                )
            )
            position = value_end

            if source.startswith(
                ", ",
                position,
            ):
                position += 2
                continue

            if source.startswith(
                ")",
                position,
            ):
                position += 1
                break

            return None

    if position == len(source):
        return bindings, []

    if not source.startswith(
        " -> ",
        position,
    ):
        return None

    outputs = source[
        position + 4 :
    ].split(", ")

    if any(
        _SUFFIX_PLACEHOLDER_RE.fullmatch(item)
        is None
        for item in outputs
    ):
        return None

    return bindings, outputs


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


def parse_suffix_bindings(
    bindings: list[tuple[str, str]],
    path: str,
    line: int,
) -> list[ValueBinding]:
    """Parse every value in one binding suffix."""
    return [
        ValueBinding(
            placeholder=placeholder,
            value=parse_value(
                value,
                path,
                line,
            ),
        )
        for placeholder, value in bindings
    ]


__all__ = [
    "parse_act_attributes",
    "parse_binding",
    "parse_suffix",
    "parse_suffix_bindings",
    "parse_value",
]
