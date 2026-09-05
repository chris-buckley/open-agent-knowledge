"""Canonical named trigger declaration rendering."""

from oak.node.parts.triggers import Trigger
from oak.render.oak.data import value_text
from oak.render.oak.expressions import ListText, expression_lines, prefixed
from oak.render.oak.processes import binding_expression, condition_expression
from oak.surface.registry import surface_for
from oak.surface.syntax import TRIGGER_FIELDS


def trigger_lines(trigger: object) -> list[str]:
    """Render one logical declaration in fixed field order, omitting defaults."""
    if not isinstance(trigger, Trigger):
        raise TypeError("trigger_lines needs Trigger")
    surface_for(trigger)
    fields: dict[str, str | ListText] = {"event": value_text(trigger.event)}
    if trigger.source is not None:
        fields["source"] = trigger.source
    if trigger.guard is not True:
        fields["guard"] = condition_expression(trigger.guard)
    fields["process"] = trigger.process
    if trigger.seed:
        fields["seed"] = binding_expression(trigger.seed)
    declaration = ListText(
        trigger.id,
        tuple(prefixed(fields[name], name + "=") for name in TRIGGER_FIELDS if name in fields),
    )
    return expression_lines(declaration)


def trigger_body(trigger: Trigger) -> str:
    """Return one flat or wrapped trigger declaration."""
    return "\n".join(trigger_lines(trigger))


__all__ = ["trigger_body", "trigger_lines"]
