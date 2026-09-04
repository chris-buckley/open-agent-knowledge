"""Vocabulary text aliases and display-form verification."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, TypeAdapter

from oak.vocabulary.datatypes.datetime import DateTime
from oak.vocabulary.datatypes.quantity import Quantity
from oak.vocabulary.display.datetime import datetime_text
from oak.vocabulary.display.number import number_text
from oak.vocabulary.display.quantity import quantity_text
from oak.vocabulary.text.dotted_path import DottedPath
from oak.vocabulary.text.non_blank_line import NonBlankLine
from oak.vocabulary.text.placeholder import Placeholder
from oak.vocabulary.text.process_name import ProcessName
from oak.vocabulary.text.regex_pattern import RegexPattern
from oak.vocabulary.text.slug_id import SlugId
from oak.vocabulary.text.target_path import TargetPath
from oak.vocabulary.text.value_reference import ValueReference
from oak.vocabulary.units import Unit

TEXT_EXAMPLES = (
    (SlugId, ("triage-decision", "stdin", "mode")),
    (Placeholder, ("COMMAND", "NEXT_ACTION")),
    (
        TargetPath,
        (
            "process.route",
            "../shared/processes.oak.md#process.route",
        ),
    ),
    (
        DottedPath,
        (
            "constant.policy",
            "state.mode",
            "interface.stdin",
        ),
    ),
    (
        ValueReference,
        (
            "$constant.policy",
            "$state.mode",
            "$RESULT",
        ),
    ),
    (ProcessName, ("Route command", "Write OAK")),
    (NonBlankLine, ("Use the supplied schema.",)),
    (RegexPattern, ("^[0-9]+$",)),
)

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)


def validate_text_examples() -> None:
    """Validate every representative vocabulary text value."""
    for annotation, examples in TEXT_EXAMPLES:
        adapter = TypeAdapter(
            annotation,
            config=_STRICT,
        )

        for example in examples:
            adapter.validate_python(example)


def validate_display_values() -> None:
    """Verify number, quantity, and datetime display forms."""
    if number_text(12345.5) != "12\u2009345.5":
        raise RuntimeError("number display failed")

    if quantity_text(
        Quantity(
            value=Decimal("10"),
            unit=Unit.KILOGRAM,
        )
    ) != "10 kg":
        raise RuntimeError("quantity display failed")

    value = DateTime(
        value=datetime.fromisoformat(
            "2026-08-24T17:35:38+10:00"
        ),
        zone="Australia/Brisbane",
    )
    if datetime_text(value) != (
        "2026-08-24T17:35:38+10:00 "
        "[Australia/Brisbane]"
    ):
        raise RuntimeError("datetime display failed")


__all__ = [
    "validate_display_values",
    "validate_text_examples",
]
