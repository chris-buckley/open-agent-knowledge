"""Author the ported process execution table format as one OAK schema document."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Node, NonEmpty, OneOf, Schema, SchemaBindingError, Type, parse, render, resolve, where

PLACEHOLDER_PROCESS_ID = "PROCESS_ID"
PLACEHOLDER_PROCESS_NAME = "PROCESS_NAME"
PLACEHOLDER_STATUS = "STATUS"
PLACEHOLDER_STARTED_AT = "STARTED_AT"
PLACEHOLDER_ENDED_AT = "ENDED_AT"
PLACEHOLDER_DURATION_MS = "DURATION_MS"
PLACEHOLDER_OUTCOME = "OUTCOME"
PLACEHOLDER_ARTIFACTS = "ARTIFACTS"
PLACEHOLDER_ERRORS = "ERRORS"

STATUS_OK = "OK"

process_execution_table_schema = Schema(
    id="process-execution-table",
    name="Process Execution Table",
    purpose="Summarize process execution across processes in lexical order, one row per process.",
    template=(
        "| ProcessId | Name | Status | StartedAt | EndedAt | DurationMs | Outcome | Artifacts | Errors |\n"
        "| <PROCESS_ID> | <PROCESS_NAME> | <STATUS> | <STARTED_AT> | <ENDED_AT> | <DURATION_MS> | <OUTCOME> | <ARTIFACTS> | <ERRORS> |"
    ),
    where=[
        where(PLACEHOLDER_PROCESS_ID, Type(of="string"), NonEmpty(), description="the process identifier"),
        where(PLACEHOLDER_PROCESS_NAME, Type(of="string"), NonEmpty(), description="the process display name"),
        where(PLACEHOLDER_STATUS, Type(of="string"), OneOf(values=["PENDING", "RUNNING", STATUS_OK, "WARN", "ERROR"]), description="the execution status"),
        where(PLACEHOLDER_STARTED_AT, Type(of="datetime"), description="when the process started"),
        where(PLACEHOLDER_ENDED_AT, Type(of="datetime"), description="when the process ended"),
        where(PLACEHOLDER_DURATION_MS, Type(of="integer"), description="the run duration in milliseconds"),
        where(PLACEHOLDER_OUTCOME, Type(of="string"), NonEmpty(), description="the result in one clause"),
        where(PLACEHOLDER_ARTIFACTS, Type(of="string"), description="the produced artifacts, empty when none"),
        where(PLACEHOLDER_ERRORS, Type(of="string"), description="the errors, empty when none"),
    ],
)

process_execution_table_node = Node(schemas=[process_execution_table_schema])

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {
    PLACEHOLDER_PROCESS_ID: "sync-docs",
    PLACEHOLDER_PROCESS_NAME: "Sync docs",
    PLACEHOLDER_STATUS: STATUS_OK,
    PLACEHOLDER_STARTED_AT: "2026-08-31T09:00:00Z",
    PLACEHOLDER_ENDED_AT: "2026-08-31T09:01:00Z",
    PLACEHOLDER_DURATION_MS: 60000,
    PLACEHOLDER_OUTCOME: "synced",
    PLACEHOLDER_ARTIFACTS: "",
    PLACEHOLDER_ERRORS: "",
}
_REJECTED_BINDINGS = (
    (PLACEHOLDER_STATUS, "DONE"),
    (PLACEHOLDER_STARTED_AT, "2026-08-31"),
    (PLACEHOLDER_STARTED_AT, "1.5"),
    (PLACEHOLDER_ENDED_AT, datetime(2026, 8, 31, 9, 1, tzinfo=timezone.utc)),
)


def build() -> str:
    """Render, parse, resolve, round-trip, and bind the authored process execution table node."""
    rendered = render(process_execution_table_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("process execution table example changed during render and parse")
    schema = parsed.schemas[0]
    schema.bind(_ACCEPTED_BINDING)
    for placeholder, value in _REJECTED_BINDINGS:
        try:
            schema.bind({**_ACCEPTED_BINDING, placeholder: value})
        except SchemaBindingError:
            continue
        raise RuntimeError(f"process execution table accepted an invalid {placeholder}")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
