"""Built-in interpretation instructions for the OAK render."""

from oak.node.model import Node

REFERENCE_INSTRUCTION = (
    "$ reads a value; local targets start with their part; relative targets "
    "start with a document path; a bare $NAME is local to the running process; "
    "SET, CALL, EMIT, and THEN omit $."
)

_PART_INSTRUCTIONS = (
    ("constants", "Constants hold values that do not change while the knowledge runs."),
    ("schemas", "Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot."),
    ("state", "State holds values that persist and can change while processes run."),
    ("triggers", "Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process."),
    ("processes", "Each process is the exact ordered way to do one task; follow its typed steps from top to bottom."),
    ("interfaces", "Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both."),
)

CONTROL_INSTRUCTION = (
    "Conditions are typed trees; ALL, ANY, and NOT compose comparisons; "
    "ASSERT fails a false condition; FOREACH is sequential; PAR outputs become visible only at JOIN."
)

BUILT_IN_INSTRUCTIONS = frozenset(
    (
        REFERENCE_INSTRUCTION,
        CONTROL_INSTRUCTION,
        *(text for _field, text in _PART_INSTRUCTIONS),
    )
)


def instruction_lines(node: Node) -> list[str]:
    """Return built-in lines followed by authored instructions."""
    lines: list[str] = []
    if node.processes or node.triggers:
        lines.append(REFERENCE_INSTRUCTION)
    if any(
        step.kind in {"assert", "foreach", "par", "join"}
        for process in node.processes
        for step in process.steps
    ):
        lines.append(CONTROL_INSTRUCTION)
    for field, instruction in _PART_INSTRUCTIONS:
        if getattr(node, field):
            lines.append(instruction)
    lines.extend(instruction.body for instruction in node.instructions)
    return lines
