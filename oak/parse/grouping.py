"""Grouping inference, part splitting, and grouped entry extraction."""

from __future__ import annotations

import html
import json
import re
from typing import Literal

from oak.node.structure import PART_ORDER
from oak.parse.cursor import Cursor
from oak.parse.data import BLOCK_CONSTANT_OPEN
from oak.parse.errors import fail
from oak.surface.registry import entry_surface

GroupingName = Literal["xml", "markdown"]
ParsedEntry = tuple[dict[str, str], list[str], int]
MARKDOWN_FENCE = "~" * 4


def infer_grouping(text: str) -> GroupingName:
    """Infer one grouping from the first part delimiter."""
    first = text.partition("\n")[0]
    if first in {
        f"<{part}>"
        for part in PART_ORDER
    }:
        return "xml"
    if first in {
        f"{MARKDOWN_FENCE}{part}"
        for part in PART_ORDER
    }:
        return "markdown"
    fail(
        "unknown_grouping",
        "$",
        1,
        "document must start with one part delimiter",
    )


def split_parts(
    text: str,
    grouping: GroupingName,
) -> dict[str, tuple[list[str], int]]:
    """Split one document into present parts in canonical order."""
    cursor = Cursor(
        text.splitlines(),
        "$",
        1,
    )
    result: dict[
        str,
        tuple[list[str], int],
    ] = {}

    for part in PART_ORDER:
        opening = (
            f"<{part}>"
            if grouping == "xml"
            else f"{MARKDOWN_FENCE}{part}"
        )
        closing = (
            f"</{part}>"
            if grouping == "xml"
            else MARKDOWN_FENCE
        )
        position = cursor.index

        if result:
            if (
                position < len(cursor.lines)
                and cursor.lines[position] == opening
            ):
                fail(
                    "part_separator",
                    part,
                    position + 1,
                    "parts need one blank line between them",
                )

            if (
                position >= len(cursor.lines)
                or cursor.lines[position] != ""
            ):
                continue

            position += 1

        if (
            position >= len(cursor.lines)
            or cursor.lines[position] != opening
        ):
            continue

        cursor.index = position
        start = cursor.index + 2
        cursor.advance()
        body: list[str] = []
        block: tuple[str, int] | None = None
        depth = 1

        while not cursor.at_end:
            line = cursor.peek()
            if line is None:
                break

            if block is None:
                if grouping == "xml":
                    if line == opening:
                        depth += 1
                    elif line == closing:
                        depth -= 1
                        if depth == 0:
                            break
                elif line == closing:
                    break

            body.append(line)

            if part == "constants":
                match = BLOCK_CONSTANT_OPEN.fullmatch(line)
                if block is None and match is not None:
                    block = (
                        match.group(1),
                        cursor.line_number,
                    )
                elif block is not None and line == ">>":
                    block = None

            cursor.advance()

        if block is not None:
            fail(
                "block_constant_unterminated",
                f"constants.{block[0]}",
                block[1],
                "missing >>",
            )

        if cursor.at_end:
            fail(
                "part_unterminated",
                part,
                start,
                f"missing {closing}",
            )

        result[part] = (
            body,
            start,
        )
        cursor.advance()

    if not cursor.at_end:
        fail(
            "part_order",
            "$",
            cursor.line_number,
            "parts appear once in OAK order",
        )

    return result


def _xml_attributes(
    line: str,
    tag: str,
    path: str,
    number: int,
) -> dict[str, str]:
    if (
        not line.startswith(f"<{tag}")
        or not line.endswith(">")
    ):
        fail(
            "entry_open",
            path,
            number,
            f"expected <{tag}> entry",
        )

    source = line[
        len(tag) + 1 : -1
    ].strip()
    attributes: dict[str, str] = {}
    pattern = re.compile(
        r'([A-Za-z_][A-Za-z0-9_-]*)='
        r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
    )
    position = 0

    for match in pattern.finditer(source):
        if source[
            position : match.start()
        ].strip():
            fail(
                "entry_attribute",
                path,
                number,
                "invalid XML-like attribute syntax",
            )

        key = match.group(1)
        raw = match.group(2)
        attributes[key] = html.unescape(
            raw[1:-1]
        )
        position = match.end()

    if source[position:].strip():
        fail(
            "entry_attribute",
            path,
            number,
            "invalid XML-like attribute syntax",
        )

    return attributes


def _markdown_attributes(
    line: str,
    tag: str,
    path: str,
    number: int,
) -> dict[str, str]:
    prefix = f"~~~{tag}"

    if not line.startswith(prefix):
        fail(
            "entry_open",
            path,
            number,
            f"expected {prefix}",
        )

    tail = line[len(prefix) :]
    attributes: dict[str, str] = {}

    if not tail:
        return attributes

    if not tail.startswith(";"):
        fail(
            "entry_attribute",
            path,
            number,
            "markdown attributes must start with ;",
        )

    for item in tail[1:].split(";"):
        if "=" not in item:
            fail(
                "entry_attribute",
                path,
                number,
                "markdown attribute needs =",
            )

        key, raw = item.split(
            "=",
            1,
        )

        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            fail(
                "entry_attribute",
                path,
                number,
                str(error),
            )

        if not isinstance(value, str):
            fail(
                "entry_attribute",
                path,
                number,
                "markdown attribute must be a JSON string",
            )

        attributes[key] = value

    return attributes


def parse_entries(
    lines: list[str],
    start: int,
    tag: str,
    grouping: GroupingName,
    path: str,
) -> list[ParsedEntry]:
    """Parse every grouped body entry of one kind."""
    entry_surface(tag)
    cursor = Cursor(
        lines,
        path,
        start,
    )
    result: list[ParsedEntry] = []

    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue

        number = cursor.line_number
        line = cursor.peek()
        if line is None:
            break

        attributes = (
            _xml_attributes(
                line,
                tag,
                path,
                number,
            )
            if grouping == "xml"
            else _markdown_attributes(
                line,
                tag,
                path,
                number,
            )
        )
        closing = (
            f"</{tag}>"
            if grouping == "xml"
            else "~~~"
        )
        cursor.advance()
        body: list[str] = []
        depth = 1

        while not cursor.at_end:
            line = cursor.peek()
            if line is None:
                break

            if grouping == "xml":
                if (
                    line == f"<{tag}>"
                    or line.startswith(
                        f"<{tag} "
                    )
                ):
                    depth += 1
                elif line == closing:
                    depth -= 1
                    if depth == 0:
                        break
            elif line == closing:
                break

            body.append(line)
            cursor.advance()

        if cursor.at_end:
            fail(
                "entry_unterminated",
                path,
                number,
                f"missing {closing}",
            )

        result.append(
            (
                attributes,
                body,
                number,
            )
        )
        cursor.advance()

    return result


__all__ = [
    "GroupingName",
    "parse_entries",
    "infer_grouping",
    "split_parts",
]
