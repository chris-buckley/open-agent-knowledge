"""XML-tag and markdown-fence groupings for one OAK document."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Literal
from xml.sax.saxutils import quoteattr

from oak.node.model import Node
from oak.node.parts.processes.model import Process
from oak.node.parts.schemas.model import Schema
from oak.render.oak.arrangement import arrange_parts, schema_text
from oak.render.oak.interfaces import interface_text
from oak.render.oak.processes import process_lines
from oak.render.oak.styles import StyleName, styled_node
from oak.surface.registry import surface_for

GroupingName = Literal["xml", "markdown"]


def _xml_attributes(attributes: Mapping[str, str | None]) -> str:
    return "".join(
        f" {key}={quoteattr(value)}"
        for key, value in attributes.items()
        if value is not None
    )


def _xml_element(
    tag: str,
    attributes: Mapping[str, str | None],
    text: str,
) -> str:
    separator = "" if text.endswith("\n") else "\n"
    return (
        f"<{tag}{_xml_attributes(attributes)}>\n"
        f"{text}{separator}"
        f"</{tag}>"
    )


def schema_xml(schema: Schema) -> str:
    """Render one schema entry as an XML-like element."""
    descriptor = surface_for(schema)
    return _xml_element(
        descriptor.tag or "schema",
        {
            "id": schema.id,
            "name": schema.name,
            "purpose": schema.purpose,
        },
        schema_text(schema),
    )


def process_xml(process: Process) -> str:
    """Render one process entry as an XML-like element."""
    descriptor = surface_for(process)
    return _xml_element(
        descriptor.tag or "process",
        {
            "id": process.id,
            "name": process.name,
            "input": process.input,
            "output": process.output,
        },
        "\n".join(process_lines(process)),
    )


def _xml_part(
    tag: str,
    bodies: Sequence[str],
    separator: str = "\n",
) -> str:
    return _xml_element(tag, {}, separator.join(bodies))


def _node_xml(node: Node) -> str:
    return arrange_parts(
        node,
        schema_xml,
        process_xml,
        interface_text,
        _xml_part,
    )


def node_xml(
    node: Node,
    *,
    style: StyleName = "authored",
) -> str:
    """Render one OAK document with XML-like delimiters."""
    surface_for(node)
    return _node_xml(styled_node(node, style))


def _markdown_attributes(attributes: Mapping[str, str | None]) -> str:
    return "".join(
        f";{key}=" + json.dumps(value, ensure_ascii=False)
        for key, value in attributes.items()
        if value is not None
    )


def _markdown_entry(
    tag: str,
    attributes: Mapping[str, str | None],
    text: str,
) -> str:
    separator = "" if text.endswith("\n") else "\n"
    return (
        f"~~~{tag}{_markdown_attributes(attributes)}\n"
        f"{text}{separator}"
        "~~~"
    )


def schema_markdown(schema: Schema) -> str:
    """Render one schema entry as a markdown-fenced entry."""
    descriptor = surface_for(schema)
    return _markdown_entry(
        descriptor.tag or "schema",
        {
            "id": schema.id,
            "name": schema.name,
            "purpose": schema.purpose,
        },
        schema_text(schema),
    )


def process_markdown(process: Process) -> str:
    """Render one process entry as a markdown-fenced entry."""
    descriptor = surface_for(process)
    return _markdown_entry(
        descriptor.tag or "process",
        {
            "id": process.id,
            "name": process.name,
            "input": process.input,
            "output": process.output,
        },
        "\n".join(process_lines(process)),
    )


def _markdown_part(
    tag: str,
    bodies: Sequence[str],
    separator: str = "\n",
) -> str:
    text = separator.join(bodies)
    closing = "" if text.endswith("\n") else "\n"
    return f"~~~~{tag}\n{text}{closing}~~~~"


def _node_markdown(node: Node) -> str:
    return arrange_parts(
        node,
        schema_markdown,
        process_markdown,
        interface_text,
        _markdown_part,
    )


def node_markdown(
    node: Node,
    *,
    style: StyleName = "authored",
) -> str:
    """Render one OAK document with markdown fences."""
    surface_for(node)
    return _node_markdown(styled_node(node, style))


__all__ = [
    "GroupingName",
    "node_markdown",
    "node_xml",
    "process_markdown",
    "process_xml",
    "schema_markdown",
    "schema_xml",
]
