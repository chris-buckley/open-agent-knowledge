"""The xml variant: XML-like tags delimit verbatim text."""

from xml.sax.saxutils import quoteattr

from oak.node.parts.schemas import Schema
from oak.render.oak.arrangement import schema_text


def element(tag: str, attributes: dict[str, str | None], text: str) -> str:
    """Return one XML-like delimiter pair with verbatim inner text."""
    attrs = "".join(f" {key}={quoteattr(value)}" for key, value in attributes.items() if value is not None)
    closing_separator = "" if text.endswith("\n") else "\n"
    return f"<{tag}{attrs}>\n{text}{closing_separator}</{tag}>"


def schema_xml(schema: Schema) -> str:
    """Render one schema with xml delimiters and authored text."""
    return element(
        "schema",
        {"id": schema.id, "name": schema.name, "purpose": schema.purpose},
        schema_text(schema),
    )
