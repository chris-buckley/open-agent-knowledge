"""The fixed OAK arrangement."""

from oak.node.parts.schemas import Schema
from oak.render.oak.syntax import WHERE_HEADING, where_line

PART_ORDER = (
    "instructions",
    "constants",
    "schemas",
    "state",
    "triggers",
    "processes",
    "interfaces",
)


def schema_text(schema: Schema) -> str:
    """Return one verbatim template and generated WHERE lines."""
    lines = [where_line(item) for item in schema.where]
    where_text = WHERE_HEADING + "\n" + "\n".join(lines)
    if lines:
        where_text += "\n"
    return schema.template + "\n\n" + where_text
