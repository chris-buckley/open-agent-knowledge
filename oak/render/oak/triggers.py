"""Trigger fact-group text rendering."""

from __future__ import annotations

from oak.node.parts.triggers import Trigger
from oak.render.oak.data import value_text
from oak.render.oak.processes import (
    condition_lines,
    process_value_text,
)
from oak.surface.registry import surface_for


def trigger_lines(
    trigger: object,
) -> list[str]:
    """Return one complete trigger fact group."""
    if not isinstance(
        trigger,
        Trigger,
    ):
        raise TypeError(
            "trigger_lines needs Trigger"
        )

    surface_for(trigger)
    prefix = (
        f"trigger.{trigger.id}."
    )
    lines = [
        (
            prefix
            + "event := "
            + value_text(
                trigger.event
            )
        )
    ]

    if trigger.source is not None:
        lines.append(
            prefix
            + "source := "
            + trigger.source
        )

    if trigger.guard is not True:
        condition = condition_lines(
            trigger.guard
        )

        if len(condition) == 1:
            lines.append(
                prefix
                + "guard := "
                + condition[0]
            )

        else:
            lines.append(
                prefix
                + "guard :="
            )
            lines.extend(
                "  " + line
                for line in condition
            )

    lines.append(
        prefix
        + "process := "
        + trigger.process
    )
    lines.extend(
        (
            prefix
            + "seed."
            + binding.placeholder
            + " := "
            + process_value_text(
                binding.value
            )
        )
        for binding in trigger.seed
    )
    return lines


def trigger_body(
    trigger: Trigger,
) -> str:
    """Return one trigger fact group as one text block."""
    return "\n".join(
        trigger_lines(trigger)
    )


__all__ = [
    "trigger_body",
    "trigger_lines",
]
