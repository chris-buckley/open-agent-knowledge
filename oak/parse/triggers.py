"""Trigger fact-group parsing."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

from oak.node.parts.processes.conditions import Condition
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

_OPENED = 0
_AFTER_EVENT = 1
_AFTER_SOURCE = 2
_AFTER_GUARD = 3
_AFTER_PROCESS = 4


def _trigger_chunks(
    lines: Sequence[str],
    start: int,
) -> list[tuple[int, list[str]]]:
    chunks: list[tuple[int, list[str]]] = []
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

            chunks.append((current_start, current))
            current = []
            continue

        if not current:
            current_start = offset

        current.append(line)

    if current:
        chunks.append((current_start, current))

    elif chunks:
        fail(
            "trigger_separator",
            "triggers",
            start + len(lines) - 1,
            "one blank line separates triggers",
        )

    return chunks


@dataclass(slots=True)
class _TriggerDraft:
    """One trigger's facts collected in authored order."""

    identifier: str
    path: str
    event: str | None = None
    source: str | None = None
    guard: Condition | Literal[True] = True
    process: str | None = None
    seed: list[ValueBinding] = field(default_factory=list)
    stage: int = _OPENED

    def take_event(self, value: str, line_number: int) -> None:
        if self.stage != _OPENED:
            fail("trigger_order", self.path, line_number, "event opens one trigger")

        parsed = parse_json_value(value, self.path + ".event", line_number)

        if not isinstance(parsed, str):
            fail("trigger_event", self.path, line_number, "event must be a JSON string")

        self.event = parsed
        self.stage = _AFTER_EVENT

    def take_source(self, value: str, line_number: int) -> None:
        if self.stage != _AFTER_EVENT:
            fail("trigger_order", self.path, line_number, "source follows event")

        self.source = value
        self.stage = _AFTER_SOURCE

    def take_guard(self, cursor: Cursor, value: str, line_number: int) -> None:
        if self.stage not in (_AFTER_EVENT, _AFTER_SOURCE):
            fail("trigger_order", self.path, line_number, "guard follows event and source")

        if value:
            self.guard = parse_compare(value, self.path + ".guard", line_number)
            cursor.advance()

        else:
            cursor.advance()
            previous_path = cursor.path
            cursor.path = self.path + ".guard"

            try:
                self.guard = parse_condition(cursor, 2)
            finally:
                cursor.path = previous_path

        self.stage = _AFTER_GUARD

    def take_process(self, value: str, line_number: int) -> None:
        if self.stage not in (_AFTER_EVENT, _AFTER_SOURCE, _AFTER_GUARD):
            fail(
                "trigger_order",
                self.path,
                line_number,
                "process follows event, source, and guard",
            )

        self.process = value
        self.stage = _AFTER_PROCESS

    def take_seed(self, placeholder: str, value: str, line_number: int) -> None:
        if self.stage != _AFTER_PROCESS:
            fail("trigger_order", self.path, line_number, "seeds follow process")

        if any(binding.placeholder == placeholder for binding in self.seed):
            fail("trigger_seed", self.path, line_number, "seed placeholders are unique")

        self.seed.append(
            ValueBinding(
                placeholder=placeholder,
                value=parse_value(value, self.path + ".seed." + placeholder, line_number),
            )
        )


def _fact_value(rest: str, path: str, line_number: int) -> str:
    if rest and (not rest.startswith(" ") or rest == " " or rest.startswith("  ")):
        fail("trigger_fact", path, line_number, "one space follows :=")

    return rest[1:]


def _parse_trigger(chunk: list[str], number: int, seen: set[str]) -> Trigger:
    cursor = Cursor(chunk, "triggers", number)
    draft: _TriggerDraft | None = None

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

        entry_id, fact, placeholder, rest = match.groups()

        if draft is None:
            if entry_id in seen:
                fail(
                    "trigger_fact",
                    f"triggers.{entry_id}",
                    line_number,
                    "one trigger's facts stay contiguous",
                )

            draft = _TriggerDraft(entry_id, f"triggers.{entry_id}")
            seen.add(entry_id)

        elif entry_id != draft.identifier:
            fail(
                "trigger_fact",
                draft.path,
                line_number,
                "one trigger's facts stay contiguous",
            )

        value = _fact_value(rest, draft.path, line_number)

        if fact == "guard":
            draft.take_guard(cursor, value, line_number)
            continue

        if not value:
            fail("trigger_fact", draft.path, line_number, "trigger fact needs one value")

        if fact == "event":
            draft.take_event(value, line_number)
        elif fact == "source":
            draft.take_source(value, line_number)
        elif fact == "process":
            draft.take_process(value, line_number)
        else:
            draft.take_seed(placeholder, value, line_number)

        cursor.advance()

    if draft is None or draft.process is None:
        fail(
            "trigger_process",
            f"triggers.{None if draft is None else draft.identifier}",
            number + len(chunk),
            "trigger needs process",
        )

    return Trigger(
        id=draft.identifier,
        event=draft.event,
        source=draft.source,
        guard=draft.guard,
        process=draft.process,
        seed=draft.seed,
    )


def parse_triggers(lines: Sequence[str], start: int) -> list[Trigger]:
    """Parse every canonical trigger fact group."""
    seen: set[str] = set()
    return [
        _parse_trigger(chunk, start + chunk_start, seen)
        for chunk_start, chunk in _trigger_chunks(lines, start)
    ]


__all__ = [
    "parse_triggers",
]
