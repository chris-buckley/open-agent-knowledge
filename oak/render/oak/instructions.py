"""Built-in interpretation instructions for the OAK render."""

from oak.node.model import Node

REFERENCE_INSTRUCTION = (
    "$ reads a value; a dotted path starts with its part; a bare $NAME is local "
    "to the running process; SET, CALL, and EMIT omit $."
)

_PART_INSTRUCTIONS = (
    (
        "constants",
        "Constants hold values that do not change while the knowledge runs.",
    ),
    (
        "schemas",
        "Each schema is one information shape: a template with <PLACEHOLDER> "
        "slots, and WHERE lines that constrain each slot.",
    ),
    (
        "state",
        "State holds values that persist and can change while processes run.",
    ),
    (
        "triggers",
        "Each trigger names one arrival reason, an optional state guard, and the "
        "process that runs when both match.",
    ),
    (
        "processes",
        "Each process is the exact way to do one task; follow its steps in "
        "order, top to bottom.",
    ),
    (
        "interfaces",
        "Each interface is one information crossing: in arrives, out is "
        "emitted, and inout does both.",
    ),
)


def instruction_lines(node: Node) -> list[str]:
    """Return built-in lines followed by authored instructions."""
    lines: list[str] = []

    guarded_trigger = any(
        trigger.given is not None
        for trigger in node.triggers
    )
    if node.processes or guarded_trigger:
        lines.append(REFERENCE_INSTRUCTION)

    for field, instruction in _PART_INSTRUCTIONS:
        if getattr(node, field):
            lines.append(instruction)

    lines.extend(instruction.body for instruction in node.instructions)
    return lines
