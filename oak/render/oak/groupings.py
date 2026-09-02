"""XML-tag and markdown-fence groupings for one OAK document."""

from __future__ import annotations

import json
from typing import Literal
from xml.sax.saxutils import quoteattr

from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.schemas.model import Schema
from oak.render.oak.arrangement import arrange_parts, schema_text
from oak.render.oak.processes import process_lines
from oak.render.oak.styles import StyleName, styled_node
from oak.surface.registry import surface_for

GroupingName = Literal[
    "xml",
    "markdown",
]


def _interface_body(
    interface: Interface,
) -> str:
    surface_for(interface)
    return (
        interface.description
        or ""
    )


def _xml_attributes(
    attributes: dict[
        str,
        str | None,
    ],
) -> str:
    return "".join(
        (
            f" {key}="
            f"{quoteattr(value)}"
        )
        for key, value in attributes.items()
        if value is not None
    )


def _xml_element(
    tag: str,
    attributes: dict[
        str,
        str | None,
    ],
    text: str,
) -> str:
    separator = (
        ""
        if text.endswith("\n")
        else "\n"
    )
    return (
        f"<{tag}"
        f"{_xml_attributes(attributes)}>\n"
        f"{text}{separator}"
        f"</{tag}>"
    )


def schema_xml(
    schema: Schema,
) -> str:
    """Render one schema entry as an XML-like element."""
    descriptor = surface_for(schema)
    return _xml_element(
        descriptor.tag
        or "schema",
        {
            "id": schema.id,
            "name": schema.name,
            "purpose": schema.purpose,
        },
        schema_text(schema),
    )


def process_xml(
    process: Process,
) -> str:
    """Render one process entry as an XML-like element."""
    descriptor = surface_for(process)
    return _xml_element(
        descriptor.tag
        or "process",
        {
            "id": process.id,
            "name": process.name,
            "input": process.input,
            "output": process.output,
        },
        "\n".join(
            process_lines(process)
        ),
    )


def interface_xml(
    interface: Interface,
) -> str:
    """Render one interface entry as an XML-like element."""
    descriptor = surface_for(
        interface
    )
    return _xml_element(
        descriptor.tag
        or "interface",
        {
            "id": interface.id,
            "direction": (
                interface.direction
            ),
            "schema": (
                interface.schema_id
            ),
        },
        _interface_body(interface),
    )


def _xml_part(
    tag: str,
    bodies: list[str],
    separator: str = "\n",
) -> str:
    return _xml_element(
        tag,
        {},
        separator.join(bodies),
    )


def _node_xml(
    node: Node,
) -> str:
    return arrange_parts(
        node,
        schema_xml,
        process_xml,
        interface_xml,
        _xml_part,
    )


def node_xml(
    node: Node,
    *,
    style: StyleName = "authored",
) -> str:
    """Render one OAK document with XML-like delimiters."""
    surface_for(node)
    return _node_xml(
        styled_node(
            node,
            style,
        )
    )


def _markdown_attributes(
    attributes: dict[
        str,
        str | None,
    ],
) -> str:
    return "".join(
        (
            f";{key}="
            + json.dumps(
                value,
                ensure_ascii=False,
            )
        )
        for key, value in attributes.items()
        if value is not None
    )


def _markdown_entry(
    tag: str,
    attributes: dict[
        str,
        str | None,
    ],
    text: str,
) -> str:
    separator = (
        ""
        if text.endswith("\n")
        else "\n"
    )
    return (
        f"~~~{tag}"
        f"{_markdown_attributes(attributes)}\n"
        f"{text}{separator}"
        "~~~"
    )


def schema_markdown(
    schema: Schema,
) -> str:
    """Render one schema entry as a markdown-fenced entry."""
    descriptor = surface_for(schema)
    return _markdown_entry(
        descriptor.tag
        or "schema",
        {
            "id": schema.id,
            "name": schema.name,
            "purpose": schema.purpose,
        },
        schema_text(schema),
    )


def process_markdown(
    process: Process,
) -> str:
    """Render one process entry as a markdown-fenced entry."""
    descriptor = surface_for(process)
    return _markdown_entry(
        descriptor.tag
        or "process",
        {
            "id": process.id,
            "name": process.name,
            "input": process.input,
            "output": process.output,
        },
        "\n".join(
            process_lines(process)
        ),
    )


def interface_markdown(
    interface: Interface,
) -> str:
    """Render one interface entry as a markdown-fenced entry."""
    descriptor = surface_for(
        interface
    )
    return _markdown_entry(
        descriptor.tag
        or "interface",
        {
            "id": interface.id,
            "direction": (
                interface.direction
            ),
            "schema": (
                interface.schema_id
            ),
        },
        _interface_body(interface),
    )


def _markdown_part(
    tag: str,
    bodies: list[str],
    separator: str = "\n",
) -> str:
    text = separator.join(bodies)
    closing = (
        ""
        if text.endswith("\n")
        else "\n"
    )
    return (
        f"~~~~{tag}\n"
        f"{text}{closing}"
        "~~~~"
    )


def _node_markdown(
    node: Node,
) -> str:
    return arrange_parts(
        node,
        schema_markdown,
        process_markdown,
        interface_markdown,
        _markdown_part,
    )


def node_markdown(
    node: Node,
    *,
    style: StyleName = "authored",
) -> str:
    """Render one OAK document with markdown fences."""
    surface_for(node)
    return _node_markdown(
        styled_node(
            node,
            style,
        )
    )
