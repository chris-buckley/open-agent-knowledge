"""Built-in interpretation instructions for the OAK render."""

from oak.node.interpretation import (
    ACT_SCHEMA_INSTRUCTION,
    CONTRACT_INSTRUCTION,
    CONTROL_INSTRUCTION,
    PART_INSTRUCTIONS,
    REFERENCE_INSTRUCTION,
    TRIGGER_SEED_INSTRUCTION,
    TRIGGER_SOURCE_INSTRUCTION,
    TYPED_ENTRY_INSTRUCTION,
)
from oak.node.model import Node
from oak.node.parts.processes.steps import Act, Assert, Call, Foreach, Join, Par, While, iter_steps


def instruction_lines(node: Node) -> list[str]:
    """Return the interpretation preamble, one blank separator, then authored instructions."""
    lines: list[str] = []
    steps = tuple(
        step
        for process in node.processes
        for step in iter_steps(process.steps)
    )
    if node.processes or node.triggers:
        lines.append(REFERENCE_INSTRUCTION)
    if any(isinstance(step, (Assert, Foreach, While, Par, Join)) for step in steps):
        lines.append(CONTROL_INSTRUCTION)
    if (
        any(process.input is not None or process.output is not None for process in node.processes)
        or any(isinstance(step, Call) and (step.inputs or step.outputs) for step in steps)
    ):
        lines.append(CONTRACT_INSTRUCTION)
    if any(
        isinstance(step, Act) and (step.input is not None or step.output is not None)
        for step in steps
    ):
        lines.append(ACT_SCHEMA_INSTRUCTION)
    if any(trigger.seed for trigger in node.triggers):
        lines.append(TRIGGER_SEED_INSTRUCTION)
    if any(trigger.source is not None for trigger in node.triggers):
        lines.append(TRIGGER_SOURCE_INSTRUCTION)
    if any(entry.schema_id is not None for entry in (*node.constants, *node.state)):
        lines.append(TYPED_ENTRY_INSTRUCTION)
    for field, instruction in PART_INSTRUCTIONS:
        if getattr(node, field):
            lines.append(instruction)
    if lines and node.instructions:
        lines.append("")
    lines.extend(instruction.body for instruction in node.instructions)
    return lines
