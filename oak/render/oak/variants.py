"""Layer 4, the xml variant: tags delimit parts and character data stays verbatim."""

from xml.sax.saxutils import escape, quoteattr

from oak.node.parts.schemas import Schema
from oak.render.oak.arrangement import schema_text


def character_data(text: str) -> str:
    """Well-formed XML character data that preserves carriage returns after parsing."""
    return escape(text).replace("\r", "&#13;")


def element(tag: str, attributes: dict[str, str | None], text: str) -> str:
    """One well-formed element; an attribute whose value is None is omitted."""
    attrs = "".join(f" {key}={quoteattr(value)}" for key, value in attributes.items() if value is not None)
    return f"<{tag}{attrs}>{character_data(text)}</{tag}>"


def schema_xml(schema: Schema) -> str:
    """One schema in the xml variant."""
    return element("schema", {"id": schema.id, "name": schema.name, "purpose": schema.purpose}, schema_text(schema))
