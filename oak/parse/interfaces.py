"""Grouped interface entry parsing."""

from oak.node.parts.interfaces import Interface
from oak.parse.errors import fail
from oak.parse.grouping import GroupingName, parse_entries


def parse_interfaces(
    lines: list[str],
    start: int,
    grouping: GroupingName,
) -> list[Interface]:
    """Parse every grouped interface entry."""
    result = []

    for (
        attributes,
        body,
        number,
    ) in parse_entries(
        lines,
        start,
        "interface",
        grouping,
        "interfaces",
    ):
        for required in (
            "id",
            "direction",
            "schema",
        ):
            if required not in attributes:
                fail(
                    "interface_attribute",
                    "interfaces",
                    number,
                    f"interface needs {required}",
                )

        description = "\n".join(body) or None
        result.append(
            Interface(
                id=attributes["id"],
                direction=attributes["direction"],
                schema=attributes["schema"],
                description=description,
            )
        )

    return result


__all__ = [
    "parse_interfaces",
]
