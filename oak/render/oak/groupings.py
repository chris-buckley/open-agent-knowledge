"""XML-tag and markdown-fence groupings for one OAK body."""

from __future__ import annotations

import json
from typing import Literal
from xml.sax.saxutils import quoteattr

from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import Process
from oak.node.parts.schemas import Schema
from oak.node.parts.triggers import Trigger
from oak.render.oak.arrangement import (
    PART_ORDER,
    schema_text,
)
from oak.render.oak.instructions import instruction_lines
from oak.render.oak.styles import (
    StyleName,
    styled_node,
)
from oak.render.oak.syntax import (
    condition_text,
    constant_text,
    interface_body,
    named_value_line,
    process_lines,
)

GroupingName = Literal["xml", "markdown"]


def _xml_attributes(
    attributes: dict[str, str | None],
) -> str:
    return "".join(
        f" {key}={quoteattr(value)}"
        for key, value in attributes.items()
        if value is not None
    )


def _xml_element(
    tag: str,
    attributes: dict[str, str | None],
    text: str,
) -> str:
    closing_separator = (
        ""
        if text.endswith("\n")
        else "\n"
    )

    return (
        f"<{tag}{_xml_attributes(attributes)}>\n"
        f"{text}"
        f"{closing_separator}"
        f"</{tag}>"
    )


def schema_xml(schema: Schema) -> str:
    """Render one schema with XML-like delimiters."""
    return _xml_element(
        "schema",
        {
            "id": schema.id,
            "name": schema.name,
            "purpose": schema.purpose,
        },
        schema_text(schema),
    )


def trigger_xml(trigger: Trigger) -> str:
    """Render one trigger as one self-closing tag."""
    given = (
        condition_text(trigger.given)
        if trigger.given is not None
        else None
    )

    return (
        "<trigger"
        + _xml_attributes(
            {
                "id": trigger.id,
                "given": given,
                "when": trigger.when,
                "process": trigger.process,
            }
        )
        + " />"
    )


def process_xml(process: Process) -> str:
    """Render one process with XML-like delimiters."""
    return _xml_element(
        "process",
        {
            "id": process.id,
            "name": process.name,
        },
        "\n".join(
            process_lines(process)
        ),
    )


def interface_xml(interface: Interface) -> str:
    """Render one interface with XML-like delimiters."""
    return _xml_element(
        "interface",
        {
            "id": interface.id,
            "direction": interface.direction,
            "schema": interface.schema_id,
        },
        interface_body(interface),
    )


def _xml_part(
    tag: str,
    bodies: list[str],
    separator: str = "\n",
) -> str:
    if not bodies:
        return f"<{tag}>\n</{tag}>"

    return _xml_element(
        tag,
        {},
        separator.join(bodies),
    )


def _node_xml(node: Node) -> str:
    parts = [
        _xml_part(
            "instructions",
            instruction_lines(node),
        ),
        _xml_part(
            "constants",
            [
                constant_text(constant)
                for constant in node.constants
            ],
            "\n\n",
        ),
        _xml_part(
            "schemas",
            [
                schema_xml(schema)
                for schema in node.schemas
            ],
            "\n\n",
        ),
        _xml_part(
            "state",
            [
                named_value_line(value)
                for value in node.state
            ],
        ),
        _xml_part(
            "triggers",
            [
                trigger_xml(trigger)
                for trigger in node.triggers
            ],
        ),
        _xml_part(
            "processes",
            [
                process_xml(process)
                for process in node.processes
            ],
            "\n\n",
        ),
        _xml_part(
            "interfaces",
            [
                interface_xml(interface)
                for interface in node.interfaces
            ],
            "\n\n",
        ),
    ]

    parts.extend(
        _xml_element(
            "node",
            {},
            _node_xml(child),
        )
        for child in node.children
    )

    return "\n\n".join(parts)


def node_xml(
    node: Node,
    *,
    style: StyleName = "authored",
) -> str:
    """Render one tree with XML-like delimiters."""
    return _node_xml(
        styled_node(node, style)
    )


def _markdown_attributes(
    attributes: dict[str, str | None],
) -> str:
    return "".join(
        (
            f";{key}="
            f"{json.dumps(value, ensure_ascii=False)}"
        )
        for key, value in attributes.items()
        if value is not None
    )


def _markdown_entry(
    tag: str,
    attributes: dict[str, str | None],
    text: str,
) -> str:
    closing_separator = (
        ""
        if text.endswith("\n")
        else "\n"
    )

    return (
        f"~~~{tag}"
        f"{_markdown_attributes(attributes)}\n"
        f"{text}"
        f"{closing_separator}"
        "~~~"
    )


def schema_markdown(schema: Schema) -> str:
    """Render one schema with markdown fences."""
    return _markdown_entry(
        "schema",
        {
            "id": schema.id,
            "name": schema.name,
            "purpose": schema.purpose,
        },
        schema_text(schema),
    )


def trigger_markdown(trigger: Trigger) -> str:
    """Render one trigger as one bodiless entry line."""
    given = (
        condition_text(trigger.given)
        if trigger.given is not None
        else None
    )

    return (
        "~~~trigger"
        + _markdown_attributes(
            {
                "id": trigger.id,
                "given": given,
                "when": trigger.when,
                "process": trigger.process,
            }
        )
    )


def process_markdown(process: Process) -> str:
    """Render one process with markdown fences."""
    return _markdown_entry(
        "process",
        {
            "id": process.id,
            "name": process.name,
        },
        "\n".join(
            process_lines(process)
        ),
    )


def interface_markdown(
    interface: Interface,
) -> str:
    """Render one interface with markdown fences."""
    return _markdown_entry(
        "interface",
        {
            "id": interface.id,
            "direction": interface.direction,
            "schema": interface.schema_id,
        },
        interface_body(interface),
    )


def _markdown_part(
    tag: str,
    bodies: list[str],
    separator: str = "\n",
) -> str:
    if not bodies:
        return f"~~~~{tag}\n~~~~"

    text = separator.join(bodies)
    closing_separator = (
        ""
        if text.endswith("\n")
        else "\n"
    )

    return (
        f"~~~~{tag}\n"
        f"{text}"
        f"{closing_separator}"
        "~~~~"
    )


def _node_fence_length(node: Node) -> int:
    if not node.children:
        return 5

    return 1 + max(
        _node_fence_length(child)
        for child in node.children
    )


def _child_markdown(node: Node) -> str:
    fence = "~" * _node_fence_length(node)
    body = _node_markdown(node)

    return (
        f"{fence}node\n"
        f"{body}\n"
        f"{fence}"
    )


def _node_markdown(node: Node) -> str:
    parts = {
        "instructions": _markdown_part(
            "instructions",
            instruction_lines(node),
        ),
        "constants": _markdown_part(
            "constants",
            [
                constant_text(constant)
                for constant in node.constants
            ],
            "\n\n",
        ),
        "schemas": _markdown_part(
            "schemas",
            [
                schema_markdown(schema)
                for schema in node.schemas
            ],
            "\n\n",
        ),
        "state": _markdown_part(
            "state",
            [
                named_value_line(value)
                for value in node.state
            ],
        ),
        "triggers": _markdown_part(
            "triggers",
            [
                trigger_markdown(trigger)
                for trigger in node.triggers
            ],
        ),
        "processes": _markdown_part(
            "processes",
            [
                process_markdown(process)
                for process in node.processes
            ],
            "\n\n",
        ),
        "interfaces": _markdown_part(
            "interfaces",
            [
                interface_markdown(interface)
                for interface in node.interfaces
            ],
            "\n\n",
        ),
    }

    sections = [
        parts[name]
        for name in PART_ORDER
    ]

    sections.extend(
        _child_markdown(child)
        for child in node.children
    )

    return "\n\n".join(sections)


def node_markdown(
    node: Node,
    *,
    style: StyleName = "authored",
) -> str:
    """Render one tree with markdown fences."""
    return _node_markdown(
        styled_node(node, style)
    )
