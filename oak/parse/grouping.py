"""Grouping inference, part splitting, and grouped entry extraction."""

from __future__ import annotations

import html
import json
import re
from collections.abc import Sequence
from typing import Literal

from oak.node.structure import PART_ORDER
from oak.parse.cursor import Cursor
from oak.parse.data import BLOCK_CONSTANT_OPEN
from oak.parse.errors import fail
from oak.surface.registry import entry_surface

GroupingName = Literal["xml", "markdown"]
ParsedEntry = tuple[dict[str, str], list[str], int]
MARKDOWN_FENCE = "~" * 4

_ATTRIBUTE = re.compile(
    r'([A-Za-z_][A-Za-z0-9_-]*)='
    r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
)


def infer_grouping(text: str) -> GroupingName:
    """Infer one grouping from the first part delimiter."""
    first = text.partition("\n")[0]

    if first in {f"<{part}>" for part in PART_ORDER}:
        return "xml"

    if first in {f"{MARKDOWN_FENCE}{part}" for part in PART_ORDER}:
        return "markdown"

    fail("unknown_grouping", "$", 1, "document must start with one part delimiter")


def _next_depth(opens: bool, closes: bool, grouping: GroupingName, depth: int) -> int | None:
    """Return the nesting depth after one line, or None when the line closes the group."""
    if grouping == "xml":
        if opens:
            return depth + 1

        if closes:
            return None if depth == 1 else depth - 1

        return depth

    return None if closes else depth


def _block_state(block: tuple[str, int] | None, line: str, number: int) -> tuple[str, int] | None:
    """Return the open block constant after one line: its id and opening line."""
    if block is None:
        match = BLOCK_CONSTANT_OPEN.fullmatch(line)
        return None if match is None else (match.group(1), number)

    return None if line == ">>" else block


def _part_body(cursor: Cursor, part: str, opening: str, closing: str, grouping: GroupingName) -> list[str]:
    """Collect one part body up to its closing delimiter, honouring block constants."""
    body: list[str] = []
    block: tuple[str, int] | None = None
    depth = 1

    while not cursor.at_end:
        line = cursor.peek()
        if line is None:
            break

        if block is None:
            next_depth = _next_depth(line == opening, line == closing, grouping, depth)

            if next_depth is None:
                break

            depth = next_depth

        body.append(line)

        if part == "constants":
            block = _block_state(block, line, cursor.line_number)

        cursor.advance()

    if block is not None:
        fail("block_constant_unterminated", f"constants.{block[0]}", block[1], "missing >>")

    return body


def split_parts(text: str, grouping: GroupingName) -> dict[str, tuple[list[str], int]]:
    """Split one document into present parts in canonical order."""
    cursor = Cursor(text.splitlines(), "$", 1)
    parts: dict[str, tuple[list[str], int]] = {}

    for part in PART_ORDER:
        opening = f"<{part}>" if grouping == "xml" else f"{MARKDOWN_FENCE}{part}"
        closing = f"</{part}>" if grouping == "xml" else MARKDOWN_FENCE
        position = cursor.index

        if parts:
            if position < len(cursor.lines) and cursor.lines[position] == opening:
                fail("part_separator", part, position + 1, "parts need one blank line between them")

            if position >= len(cursor.lines) or cursor.lines[position] != "":
                continue

            position += 1

        if position >= len(cursor.lines) or cursor.lines[position] != opening:
            continue

        cursor.index = position
        start = cursor.index + 2
        cursor.advance()
        body = _part_body(cursor, part, opening, closing, grouping)

        if cursor.at_end:
            fail("part_unterminated", part, start, f"missing {closing}")

        parts[part] = (body, start)
        cursor.advance()

    if not cursor.at_end:
        fail("part_order", "$", cursor.line_number, "parts appear once in OAK order")

    return parts


def _xml_attributes(line: str, tag: str, path: str, number: int) -> dict[str, str]:
    if not line.startswith(f"<{tag}") or not line.endswith(">"):
        fail("entry_open", path, number, f"expected <{tag}> entry")

    source = line[len(tag) + 1 : -1].strip()
    attributes: dict[str, str] = {}
    position = 0

    for match in _ATTRIBUTE.finditer(source):
        if source[position : match.start()].strip():
            fail("entry_attribute", path, number, "invalid XML-like attribute syntax")

        attributes[match.group(1)] = html.unescape(match.group(2)[1:-1])
        position = match.end()

    if source[position:].strip():
        fail("entry_attribute", path, number, "invalid XML-like attribute syntax")

    return attributes


def _markdown_attributes(line: str, tag: str, path: str, number: int) -> dict[str, str]:
    prefix = f"~~~{tag}"

    if not line.startswith(prefix):
        fail("entry_open", path, number, f"expected {prefix}")

    tail = line[len(prefix) :]
    attributes: dict[str, str] = {}

    if not tail:
        return attributes

    if not tail.startswith(";"):
        fail("entry_attribute", path, number, "markdown attributes must start with ;")

    for attribute in tail[1:].split(";"):
        if "=" not in attribute:
            fail("entry_attribute", path, number, "markdown attribute needs =")

        key, raw = attribute.split("=", 1)

        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            fail("entry_attribute", path, number, str(error))

        if not isinstance(value, str):
            fail("entry_attribute", path, number, "markdown attribute must be a JSON string")

        attributes[key] = value

    return attributes


def _entry_body(cursor: Cursor, tag: str, closing: str, grouping: GroupingName) -> list[str]:
    """Collect one entry body up to its closing delimiter."""
    body: list[str] = []
    depth = 1

    while not cursor.at_end:
        line = cursor.peek()
        if line is None:
            break

        opens = line == f"<{tag}>" or line.startswith(f"<{tag} ")
        next_depth = _next_depth(opens, line == closing, grouping, depth)

        if next_depth is None:
            break

        depth = next_depth
        body.append(line)
        cursor.advance()

    return body


def parse_entries(
    lines: Sequence[str],
    start: int,
    tag: str,
    grouping: GroupingName,
    path: str,
) -> list[ParsedEntry]:
    """Parse every grouped body entry of one kind."""
    entry_surface(tag)
    cursor = Cursor(lines, path, start)
    entries: list[ParsedEntry] = []
    closing = f"</{tag}>" if grouping == "xml" else "~~~"

    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue

        number = cursor.line_number
        line = cursor.peek()
        if line is None:
            break

        attributes = (
            _xml_attributes(line, tag, path, number)
            if grouping == "xml"
            else _markdown_attributes(line, tag, path, number)
        )
        cursor.advance()
        body = _entry_body(cursor, tag, closing, grouping)

        if cursor.at_end:
            fail("entry_unterminated", path, number, f"missing {closing}")

        entries.append((attributes, body, number))
        cursor.advance()

    return entries


__all__ = [
    "GroupingName",
    "parse_entries",
    "infer_grouping",
    "split_parts",
]
