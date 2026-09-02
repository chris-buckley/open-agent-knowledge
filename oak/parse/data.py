"""Instruction, constant, state, JSON, CSV, and YAML parsing."""

from __future__ import annotations

import csv
import io
import json
import re

import yaml

from oak.node.interpretation import BUILT_IN_INSTRUCTIONS
from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.state import State
from oak.parse.cursor import Cursor
from oak.parse.errors import fail
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX

AS_CLAUSE = (
    r"(?: AS ([^ :]+?)\.("
    + PLACEHOLDER_SYNTAX.body
    + r"))?"
)
BLOCK_CONSTANT_OPEN = re.compile(
    r"^([a-z][a-z0-9]*(?:-[a-z0-9]+)*)"
    + AS_CLAUSE
    + r": (TEXT|JSON|CSV|YAML)<<$"
)
_INLINE_NAMED_VALUE = re.compile(
    r"^([a-z][a-z0-9]*(?:-[a-z0-9]+)*)"
    + AS_CLAUSE
    + r": (.+)$"
)


def parse_instructions(
    lines: list[str],
    start: int,
) -> list[Instruction]:
    """Parse authored instructions after stripping the exact preamble."""
    authored = [
        line
        for line in lines
        if line
        and line not in BUILT_IN_INSTRUCTIONS
    ]
    return [
        Instruction(
            id=f"instruction-{index}",
            body=line,
        )
        for index, line in enumerate(
            authored,
            1,
        )
    ]


def parse_json_value(
    source: str,
    path: str,
    line: int,
) -> object:
    """Parse one JSON value with one stable failure."""
    try:
        return json.loads(source)
    except json.JSONDecodeError as error:
        fail(
            "invalid_json",
            path,
            line,
            str(error),
        )


def parse_csv_value(
    body: str,
    path: str,
    line: int,
) -> list[dict[str, object]]:
    """Parse one CSV block into JSON-scalar rows."""
    try:
        rows = list(
            csv.DictReader(
                io.StringIO(body)
            )
        )
    except csv.Error as error:
        fail(
            "invalid_csv",
            path,
            line,
            str(error),
        )

    result: list[dict[str, object]] = []

    for row in rows:
        converted: dict[str, object] = {}

        for key, value in row.items():
            if key is None or value is None:
                fail(
                    "invalid_csv",
                    path,
                    line,
                    "CSV row has an absent key or value",
                )

            try:
                converted[key] = json.loads(value)
            except json.JSONDecodeError:
                converted[key] = value

        result.append(converted)

    return result


def _block_body(
    cursor: Cursor,
    identifier: str,
    number: int,
) -> str:
    cursor.advance()
    body_lines: list[str] = []

    while (
        not cursor.at_end
        and cursor.peek() != ">>"
    ):
        line = cursor.peek()
        if line is None:
            break
        body_lines.append(line)
        cursor.advance()

    if cursor.at_end:
        fail(
            "block_constant_unterminated",
            f"constants.{identifier}",
            number,
            "missing >>",
        )

    body = "\n".join(body_lines)
    cursor.advance()
    return body


def parse_constants(
    lines: list[str],
    start: int,
) -> list[Constant]:
    """Parse inline and block constants."""
    cursor = Cursor(
        lines,
        "constants",
        start,
    )
    result: list[Constant] = []

    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue

        number = cursor.line_number
        line = cursor.peek()
        if line is None:
            break

        block_match = BLOCK_CONSTANT_OPEN.fullmatch(line)

        if block_match is not None:
            (
                identifier,
                schema_target,
                placeholder,
                form,
            ) = block_match.groups()
            body = _block_body(
                cursor,
                identifier,
                number,
            )

            if form == "TEXT":
                value: object = body
                constant_form = "text"
            elif form == "JSON":
                value = parse_json_value(
                    body,
                    f"constants.{identifier}",
                    number,
                )
                constant_form = "json"
            elif form == "CSV":
                value = parse_csv_value(
                    body,
                    f"constants.{identifier}",
                    number,
                )
                constant_form = "csv"
            else:
                try:
                    value = yaml.safe_load(body)
                except yaml.YAMLError as error:
                    fail(
                        "invalid_yaml",
                        f"constants.{identifier}",
                        number,
                        str(error),
                    )
                constant_form = "yaml"

            result.append(
                Constant(
                    id=identifier,
                    form=constant_form,
                    schema=schema_target,
                    placeholder=placeholder,
                    value=value,
                )
            )
            continue

        inline_match = _INLINE_NAMED_VALUE.fullmatch(line)

        if inline_match is None:
            fail(
                "named_value",
                "constants",
                number,
                "expected id: JSON",
            )

        (
            identifier,
            schema_target,
            placeholder,
            source,
        ) = inline_match.groups()
        value = parse_json_value(
            source,
            f"constants.{identifier}",
            number,
        )
        result.append(
            Constant(
                id=identifier,
                schema=schema_target,
                placeholder=placeholder,
                value=value,
            )
        )
        cursor.advance()

    return result


def parse_state(
    lines: list[str],
    start: int,
) -> list[State]:
    """Parse inline state entries."""
    cursor = Cursor(
        lines,
        "state",
        start,
    )
    result: list[State] = []

    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue

        number = cursor.line_number
        line = cursor.peek()
        if line is None:
            break

        block_match = BLOCK_CONSTANT_OPEN.fullmatch(line)

        if block_match is not None:
            identifier = block_match.group(1)
            _block_body(
                cursor,
                identifier,
                number,
            )
            fail(
                "invalid_state",
                "state",
                number,
                "state does not accept block values",
            )

        inline_match = _INLINE_NAMED_VALUE.fullmatch(line)

        if inline_match is None:
            fail(
                "named_value",
                "state",
                number,
                "expected id: JSON",
            )

        (
            identifier,
            schema_target,
            placeholder,
            source,
        ) = inline_match.groups()
        value = parse_json_value(
            source,
            f"state.{identifier}",
            number,
        )
        result.append(
            State(
                id=identifier,
                schema=schema_target,
                placeholder=placeholder,
                value=value,
            )
        )
        cursor.advance()

    return result


__all__ = [
    "BLOCK_CONSTANT_OPEN",
    "parse_constants",
    "parse_instructions",
    "parse_json_value",
    "parse_state",
]
