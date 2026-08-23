"""Layer 4, the xml variant: tags delimit the parts, attributes carry the fields, character data stays verbatim in CDATA."""

from xml.sax.saxutils import quoteattr

from oak.node.parts.schemas import Schema
from oak.render.oak.arrangement import schema_text


def cdata(text: str) -> str:
    """Well-formed CDATA for any text; a literal `]]>` is split across two sections."""
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def element(tag: str, attributes: dict[str, str | None], text: str) -> str:
    """One well-formed element; an attribute whose value is None is omitted."""
    attrs = "".join(f" {k}={quoteattr(v)}" for k, v in attributes.items() if v is not None)
    return f"<{tag}{attrs}>{cdata(text)}</{tag}>"


def schema_xml(schema: Schema) -> str:
    """One schema in the xml variant."""
    return element("schema", {"id": schema.id, "name": schema.name, "purpose": schema.purpose}, "\n" + schema_text(schema))
