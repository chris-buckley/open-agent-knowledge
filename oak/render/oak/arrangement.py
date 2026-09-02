"""The fixed OAK arrangement: part order, part bodies, and separators shared by every grouping."""

from collections.abc import Callable

from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.schemas.model import Schema
from oak.node.structure import PART_ORDER
from oak.render.oak.data import WHERE_HEADING, constant_text, named_value_line, where_line
from oak.render.oak.instructions import instruction_lines
from oak.render.oak.triggers import trigger_body

PART_SEPARATORS = {
    "instructions": "\n",
    "constants": "\n\n",
    "schemas": "\n\n",
    "state": "\n",
    "triggers": "\n\n",
    "processes": "\n\n",
    "interfaces": "\n\n",
}


def schema_text(
    schema: Schema,
) -> str:
    """Return one verbatim template and generated WHERE lines."""
    lines = [
        where_line(item)
        for item in schema.where
    ]
    where_text = (
        WHERE_HEADING
        + "\n"
        + "\n".join(lines)
    )

    if lines:
        where_text += "\n"

    return (
        schema.template
        + "\n\n"
        + where_text
    )


def part_bodies(
    node: Node,
    schema: Callable[[Schema], str],
    process: Callable[[Process], str],
    interface: Callable[[Interface], str],
) -> dict[str, list[str]]:
    """Return the rendered entry bodies of every part, keyed by part name."""
    return {
        "instructions": instruction_lines(node),
        "constants": [constant_text(item) for item in node.constants],
        "schemas": [schema(item) for item in node.schemas],
        "state": [named_value_line(item) for item in node.state],
        "triggers": [trigger_body(item) for item in node.triggers],
        "processes": [process(item) for item in node.processes],
        "interfaces": [interface(item) for item in node.interfaces],
    }


def arrange_parts(
    node: Node,
    schema: Callable[[Schema], str],
    process: Callable[[Process], str],
    interface: Callable[[Interface], str],
    part: Callable[[str, list[str], str], str],
) -> str:
    """Assemble the non-empty parts in OAK order, one blank line apart, through one grouping's part delimiter."""
    bodies = part_bodies(node, schema, process, interface)
    return "\n\n".join(
        part(tag, bodies[tag], PART_SEPARATORS[tag])
        for tag in PART_ORDER
        if bodies[tag]
    )


__all__ = [
    "PART_SEPARATORS",
    "arrange_parts",
    "part_bodies",
    "schema_text",
]
