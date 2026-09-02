"""Trigger fact-group parsing."""

from __future__ import annotations

import re

from oak.node.parts.processes.values import ValueBinding
from oak.node.parts.triggers import Trigger
from oak.parse.conditions import parse_compare, parse_condition
from oak.parse.cursor import Cursor
from oak.parse.data import parse_json_value
from oak.parse.errors import fail
from oak.parse.values import parse_value
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX

_TRIGGER_FACT = re.compile(
    r"^trigger\.([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\."
    r"(event|source|guard|process|seed\.("
    + PLACEHOLDER_SYNTAX.body
    + r")) :=(.*)$"
)


def _trigger_chunks(
    lines: list[str],
    start: int,
) -> list[tuple[int, list[str]]]:
    chunks: list[
        tuple[int, list[str]]
    ] = []
    current: list[str] = []
    current_start = 0

    for offset, line in enumerate(lines):
        if line == "":
            if not current:
                fail(
                    "trigger_separator",
                    "triggers",
                    start + offset,
                    "one blank line separates triggers",
                )

            chunks.append(
                (
                    current_start,
                    current,
                )
            )
            current = []
            continue

        if not current:
            current_start = offset

        current.append(line)

    if current:
        chunks.append(
            (
                current_start,
                current,
            )
        )

    elif chunks:
        fail(
            "trigger_separator",
            "triggers",
            start + len(lines) - 1,
            "one blank line separates triggers",
        )

    return chunks


def parse_triggers(
    lines: list[str],
    start: int,
) -> list[Trigger]:
    """Parse every canonical trigger fact group."""
    result: list[Trigger] = []
    seen: set[str] = set()

    for chunk_start, chunk in _trigger_chunks(
        lines,
        start,
    ):
        number = start + chunk_start
        cursor = Cursor(
            chunk,
            "triggers",
            number,
        )
        identifier: str | None = None
        event: str | None = None
        source: str | None = None
        guard: object = True
        process: str | None = None
        seed: list[ValueBinding] = []
        stage = 0

        while not cursor.at_end:
            line_number = cursor.line_number
            line = cursor.peek()
            if line is None:
                break

            match = _TRIGGER_FACT.fullmatch(line)

            if match is None:
                fail(
                    "trigger_fact",
                    "triggers",
                    line_number,
                    "trigger fact must be trigger.<id>.<fact> := <value>",
                )

            (
                entry_id,
                field,
                placeholder,
                rest,
            ) = (
                match.group(1),
                match.group(2),
                match.group(3),
                match.group(4),
            )

            if identifier is None:
                if entry_id in seen:
                    fail(
                        "trigger_fact",
                        f"triggers.{entry_id}",
                        line_number,
                        "one trigger's facts stay contiguous",
                    )

                identifier = entry_id
                seen.add(entry_id)

            elif entry_id != identifier:
                fail(
                    "trigger_fact",
                    f"triggers.{identifier}",
                    line_number,
                    "one trigger's facts stay contiguous",
                )

            path = f"triggers.{identifier}"

            if (
                rest
                and (
                    not rest.startswith(" ")
                    or rest == " "
                    or rest.startswith("  ")
                )
            ):
                fail(
                    "trigger_fact",
                    path,
                    line_number,
                    "one space follows :=",
                )

            value = rest[1:]

            if field == "guard":
                if stage not in (1, 2):
                    fail(
                        "trigger_order",
                        path,
                        line_number,
                        "guard follows event and source",
                    )

                if value:
                    guard = parse_compare(
                        value,
                        path + ".guard",
                        line_number,
                    )
                    cursor.advance()

                else:
                    cursor.advance()
                    previous_path = cursor.path
                    cursor.path = path + ".guard"

                    try:
                        guard = parse_condition(
                            cursor,
                            2,
                        )
                    finally:
                        cursor.path = previous_path

                stage = 3
                continue

            if not value:
                fail(
                    "trigger_fact",
                    path,
                    line_number,
                    "trigger fact needs one value",
                )

            if field == "event":
                if stage != 0:
                    fail(
                        "trigger_order",
                        path,
                        line_number,
                        "event opens one trigger",
                    )

                parsed = parse_json_value(
                    value,
                    path + ".event",
                    line_number,
                )

                if not isinstance(parsed, str):
                    fail(
                        "trigger_event",
                        path,
                        line_number,
                        "event must be a JSON string",
                    )

                event = parsed
                stage = 1

            elif field == "source":
                if stage != 1:
                    fail(
                        "trigger_order",
                        path,
                        line_number,
                        "source follows event",
                    )

                source = value
                stage = 2

            elif field == "process":
                if stage not in (1, 2, 3):
                    fail(
                        "trigger_order",
                        path,
                        line_number,
                        "process follows event, source, and guard",
                    )

                process = value
                stage = 4

            else:
                if stage != 4:
                    fail(
                        "trigger_order",
                        path,
                        line_number,
                        "seeds follow process",
                    )

                if any(
                    binding.placeholder == placeholder
                    for binding in seed
                ):
                    fail(
                        "trigger_seed",
                        path,
                        line_number,
                        "seed placeholders are unique",
                    )

                seed.append(
                    ValueBinding(
                        placeholder=placeholder,
                        value=parse_value(
                            value,
                            path + ".seed." + placeholder,
                            line_number,
                        ),
                    )
                )

            cursor.advance()

        if process is None:
            fail(
                "trigger_process",
                f"triggers.{identifier}",
                number + len(chunk),
                "trigger needs process",
            )

        result.append(
            Trigger(
                id=identifier,
                event=event,
                source=source,
                guard=guard,
                process=process,
                seed=seed,
            )
        )

    return result


__all__ = [
    "parse_triggers",
]
