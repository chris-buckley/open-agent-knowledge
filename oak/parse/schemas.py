"""Schema constraint, Where, and schema entry parsing."""

from __future__ import annotations

import json
import re

from oak.node.parts.schemas import (
    AtLeast,
    AtMost,
    Constraint,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Schema,
    Type,
    Where,
)
from oak.parse.data import parse_json_value
from oak.parse.errors import fail
from oak.parse.grouping import GroupingName, parse_entries


def parse_constraint(
    source: str,
    path: str,
    line: int,
) -> Constraint | None:
    """Parse one authored schema constraint phrase."""
    if source.startswith("is one of "):
        values = []

        for raw in re.findall(
            r"`([^`]*)`",
            source[len("is one of ") :],
        ):
            try:
                values.append(json.loads(raw))
            except json.JSONDecodeError:
                values.append(raw)

        return OneOf(values=values)

    if source.startswith("matches `") and source.endswith("`"):
        return Regex(pattern=source[9:-1])

    if source == "is non-empty":
        return NonEmpty()

    match = re.fullmatch(
        r"is at most ([0-9]+) characters",
        source,
    )
    if match:
        return MaxChars(
            n=int(match.group(1))
        )

    if source == "is one line":
        return Lines(
            min=1,
            max=1,
        )

    match = re.fullmatch(
        r"has ([0-9]+) lines",
        source,
    )
    if match:
        value = int(match.group(1))
        return Lines(
            min=value,
            max=value,
        )

    match = re.fullmatch(
        r"has ([0-9]+) to ([0-9]+) lines",
        source,
    )
    if match:
        return Lines(
            min=int(match.group(1)),
            max=int(match.group(2)),
        )

    match = re.fullmatch(
        r"has at most ([0-9]+) line(?:s)?",
        source,
    )
    if match:
        return Lines(
            max=int(match.group(1))
        )

    match = re.fullmatch(
        r"has at least ([0-9]+) line(?:s)?",
        source,
    )
    if match:
        return Lines(
            min=int(match.group(1))
        )

    match = re.fullmatch(
        r"is a list of ([a-z]+) joined by `([^`]*)`",
        source,
    )
    if match:
        return ListOf(
            item=match.group(1),
            separator=match.group(2),
        )

    if source.startswith("is at least "):
        raw = source[len("is at least ") :]
        value = (
            raw[1:-1]
            if raw.startswith("<")
            and raw.endswith(">")
            else parse_json_value(
                raw,
                path,
                line,
            )
        )
        return AtLeast(value=value)

    if source.startswith("is at most "):
        raw = source[len("is at most ") :]
        value = (
            raw[1:-1]
            if raw.startswith("<")
            and raw.endswith(">")
            else parse_json_value(
                raw,
                path,
                line,
            )
        )
        return AtMost(value=value)

    if source.startswith("is "):
        return Type(of=source[3:])

    return None


def parse_where(
    line_text: str,
    path: str,
    line: int,
) -> Where:
    """Parse one generated WHERE line."""
    match = re.fullmatch(
        r"- <([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)> (.*)\.",
        line_text,
    )

    if match is None:
        fail(
            "where_line",
            path,
            line,
            "invalid WHERE line",
        )

    placeholder, body = match.groups()
    example_match = re.search(
        r" \(e\.g\. (.*?)\)",
        body,
    )
    examples: list[object] = []

    if example_match:
        for raw in re.findall(
            r"`([^`]*)`",
            example_match.group(1),
        ):
            try:
                examples.append(json.loads(raw))
            except json.JSONDecodeError:
                examples.append(raw)

        body = (
            body[: example_match.start()]
            + body[example_match.end() :]
        )

    constraints = []
    description = None

    for segment in body.split("; "):
        item = parse_constraint(
            segment,
            path,
            line,
        )

        if item is None:
            if description is not None:
                fail(
                    "where_description",
                    path,
                    line,
                    "WHERE has more than one description segment",
                )

            description = segment

        else:
            constraints.append(item)

    if not constraints:
        fail(
            "where_constraint",
            path,
            line,
            "WHERE needs at least one constraint",
        )

    return Where(
        placeholder=placeholder,
        constraints=constraints,
        examples=examples,
        description=description,
    )


def parse_schemas(
    lines: list[str],
    start: int,
    grouping: GroupingName,
) -> list[Schema]:
    """Parse every grouped schema entry."""
    result = []

    for (
        attributes,
        body_lines,
        number,
    ) in parse_entries(
        lines,
        start,
        "schema",
        grouping,
        "schemas",
    ):
        if "id" not in attributes:
            fail(
                "schema_id",
                "schemas",
                number,
                "schema entry needs id",
            )

        body = "\n".join(body_lines)
        marker = "\n\nWHERE:"
        template, separator, where_text = body.rpartition(marker)

        if not separator:
            fail(
                "schema_where",
                f"schemas.{attributes['id']}",
                number,
                "schema body needs the generated WHERE separator",
            )

        result.append(
            Schema(
                id=attributes["id"],
                name=attributes.get("name"),
                purpose=attributes.get("purpose"),
                template=template,
                where=[
                    parse_where(
                        item,
                        f"schemas.{attributes['id']}.where",
                        (
                            number
                            + len(template.splitlines())
                            + 3
                            + index
                        ),
                    )
                    for index, item in enumerate(
                        where_text.splitlines()
                    )
                    if item
                ],
            )
        )

    return result


__all__ = [
    "parse_constraint",
    "parse_schemas",
    "parse_where",
]
