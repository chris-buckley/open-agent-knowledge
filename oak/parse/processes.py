"""Grouped process entry parsing."""

from oak.node.parts.processes import Process
from oak.parse.cursor import Cursor
from oak.parse.errors import fail
from oak.parse.grouping import GroupingName, parse_entries
from oak.parse.steps import parse_steps


def parse_processes(
    lines: list[str],
    start: int,
    grouping: GroupingName,
) -> list[Process]:
    """Parse every grouped process entry."""
    result = []

    for (
        attributes,
        body,
        number,
    ) in parse_entries(
        lines,
        start,
        "process",
        grouping,
        "processes",
    ):
        if (
            "id" not in attributes
            or "name" not in attributes
        ):
            fail(
                "process_attributes",
                "processes",
                number,
                "process needs id and name",
            )

        path = f"processes.{attributes['id']}"
        cursor = Cursor(
            body,
            path,
            number + 1,
        )
        steps = parse_steps(
            cursor,
            0,
        )

        if not cursor.at_end:
            fail(
                "process_trailing",
                path,
                cursor.line_number,
                "unparsed process text",
            )

        result.append(
            Process(
                id=attributes["id"],
                name=attributes["name"],
                input=attributes.get("input"),
                output=attributes.get("output"),
                steps=steps,
            )
        )

    return result


__all__ = [
    "parse_processes",
]
