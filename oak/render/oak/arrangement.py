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


def _template_separator(template: str) -> str:
    if template.endswith(("\n\n", "\r\n\r\n", "\r\r")):
        return ""
    if template.endswith(("\n", "\r")):
        return "\n"
    return "\n\n"


def schema_text(schema: Schema) -> str:
    """Return one template and its generated WHERE lines."""
    lines = [where_line(item) for item in schema.where]
    where_text = WHERE_HEADING + "\n" + "\n".join(lines)
    if lines:
        where_text += "\n"
    return schema.template + _template_separator(schema.template) + where_text
