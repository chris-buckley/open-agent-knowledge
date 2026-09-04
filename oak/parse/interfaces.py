"""Canonical one-line interface parsing."""

from __future__ import annotations

import json
from collections.abc import Sequence

from oak.node.parts.interfaces import INTERFACE_FLOW_BY_KEYWORD, Interface
from oak.parse.errors import fail
from oak.parse.grouping import GroupingName


def parse_interfaces(
    lines: Sequence[str],
    start: int,
    _grouping: GroupingName,
) -> list[Interface]:
    """Parse one interface entry per non-blank line."""
    interfaces: list[Interface] = []

    for offset, line in enumerate(lines):
        number = start + offset

        if not line:
            fail(
                "interface_separator",
                "interfaces",
                number,
                "interface entries use one LF without blank separators",
            )

        identifier, first, rest = line.partition(" ")
        keyword, second, body = rest.partition(" ")

        if not first or not second or not identifier or not keyword or not body:
            fail(
                "interface_entry",
                "interfaces",
                number,
                "interface needs ID RECEIVES|EMITS SCHEMA",
            )

        definition = INTERFACE_FLOW_BY_KEYWORD.get(keyword)
        if definition is None:
            fail(
                "interface_flow",
                f"interfaces.{identifier}",
                number,
                "interface flow must be RECEIVES or EMITS",
            )

        schema, separator, raw_description = body.partition(": ")
        if not schema or " " in schema:
            fail(
                "interface_schema",
                f"interfaces.{identifier}",
                number,
                "interface schema must be one target path",
            )

        description = None
        if separator:
            try:
                description = json.loads(raw_description)
            except json.JSONDecodeError as error:
                fail(
                    "interface_description",
                    f"interfaces.{identifier}",
                    number,
                    str(error),
                )

            if not isinstance(description, str):
                fail(
                    "interface_description",
                    f"interfaces.{identifier}",
                    number,
                    "interface description must be one JSON string",
                )

        interfaces.append(
            Interface(
                id=identifier,
                flow=definition.flow,
                schema=schema,
                description=description,
            )
        )

    return interfaces


__all__ = ["parse_interfaces"]
