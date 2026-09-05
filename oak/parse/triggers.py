"""Named trigger declarations, sharing process conditions and input bindings."""

from __future__ import annotations

from collections.abc import Sequence

from oak.node.parts.triggers import Trigger
from oak.parse.cursor import Cursor
from oak.parse.expressions import ExpressionReader
from oak.surface.syntax import REQUIRED_TRIGGER_FIELDS, TRIGGER_FIELDS


def parse_triggers(lines: Sequence[str], start: int) -> list[Trigger]:
    """Parse each logical declaration; field order is authored, not positional."""
    cursor = Cursor(lines, "triggers", start)
    triggers: list[Trigger] = []
    seen: set[str] = set()
    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue
        if cursor.indentation() != 0:
            cursor.fail("trigger_indent", "a trigger declaration starts at column one")
        reader = ExpressionReader.at(cursor, cursor.peek())
        identifier = reader.slug()
        reader.path += "." + identifier
        if identifier in seen:
            reader.fail("duplicate_id", f"duplicate trigger {identifier}", 0)
        seen.add(identifier)
        fields: dict[str, object] = {}
        positions: dict[str, int] = {}

        def field() -> None:
            reader.skip()
            position = reader.position
            name = reader.name()
            if name not in TRIGGER_FIELDS:
                reader.fail("trigger_field", f"unknown trigger field {name}", position)
            if name in fields:
                reader.fail("trigger_field", f"duplicate trigger field {name}", position)
            reader.expect("=")
            previous = reader.path
            reader.path += "." + name
            try:
                if name == "event":
                    value = reader.string()
                    if not value.strip() or "\n" in value or "\r" in value:
                        reader.fail("trigger_event", "event must be one non-blank line", position)
                elif name in ("source", "process"):
                    value = reader.target("interface" if name == "source" else "process")
                elif name == "guard":
                    value = reader.condition()
                else:
                    value = reader.bindings()
                    if not value:
                        reader.fail("trigger_seed", "omit an empty seed field", position)
                fields[name] = value
                positions[name] = position
            finally:
                reader.path = previous

        reader.enclosed(field)
        missing = REQUIRED_TRIGGER_FIELDS - fields.keys()
        if missing:
            reader.fail("trigger_fields", "missing trigger fields: " + ", ".join(sorted(missing)), 0)
        if "source" in fields and "seed" in fields:
            reader.fail("source_trigger_seed", "a source-backed trigger cannot declare seeds", positions["seed"])
        trigger = reader.checked(lambda: Trigger(id=identifier, **fields), positions.get("guard", 0))
        reader.finish(cursor)
        triggers.append(trigger)
    return triggers


__all__ = ["parse_triggers"]
