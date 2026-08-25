"""XML-tag and markdown-fence groupings for one OAK document."""

from __future__ import annotations

import json
from typing import Literal
from xml.sax.saxutils import quoteattr

from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import Process
from oak.node.parts.schemas import Schema
from oak.node.parts.triggers import Trigger
from oak.render.oak.arrangement import PART_ORDER, schema_text
from oak.render.oak.instructions import instruction_lines
from oak.render.oak.styles import StyleName, styled_node
from oak.render.oak.syntax import constant_text, interface_body, named_value_line, process_lines, trigger_lines
from oak.surface import surface_for

GroupingName = Literal["xml", "markdown"]


def _xml_attributes(attributes: dict[str, str | None]) -> str:
    return "".join(f" {key}={quoteattr(value)}" for key, value in attributes.items() if value is not None)


def _xml_element(tag: str, attributes: dict[str, str | None], text: str) -> str:
    separator = "" if text.endswith("\n") else "\n"
    return f"<{tag}{_xml_attributes(attributes)}>\n{text}{separator}</{tag}>"


def schema_xml(schema: Schema) -> str:
    descriptor = surface_for(schema)
    return _xml_element(descriptor.tag or "schema", {"id": schema.id, "name": schema.name, "purpose": schema.purpose}, schema_text(schema))


def trigger_xml(trigger: Trigger) -> str:
    descriptor = surface_for(trigger)
    return _xml_element(descriptor.tag or "trigger", {"id": trigger.id}, "\n".join(trigger_lines(trigger)))


def process_xml(process: Process) -> str:
    descriptor = surface_for(process)
    return _xml_element(descriptor.tag or "process", {"id": process.id, "name": process.name}, "\n".join(process_lines(process)))


def interface_xml(interface: Interface) -> str:
    descriptor = surface_for(interface)
    return _xml_element(descriptor.tag or "interface", {"id": interface.id, "direction": interface.direction, "schema": interface.schema_id}, interface_body(interface))


def _xml_part(tag: str, bodies: list[str], separator: str = "\n") -> str:
    if not bodies:
        return f"<{tag}>\n</{tag}>"
    return _xml_element(tag, {}, separator.join(bodies))


def _node_xml(node: Node) -> str:
    parts = [
        _xml_part("instructions", instruction_lines(node)),
        _xml_part("constants", [constant_text(item) for item in node.constants], "\n\n"),
        _xml_part("schemas", [schema_xml(item) for item in node.schemas], "\n\n"),
        _xml_part("state", [named_value_line(item) for item in node.state]),
        _xml_part("triggers", [trigger_xml(item) for item in node.triggers], "\n\n"),
        _xml_part("processes", [process_xml(item) for item in node.processes], "\n\n"),
        _xml_part("interfaces", [interface_xml(item) for item in node.interfaces], "\n\n"),
    ]
    return "\n\n".join(parts)


def node_xml(node: Node, *, style: StyleName = "authored") -> str:
    """Render one OAK document with XML-like delimiters."""
    surface_for(node)
    return _node_xml(styled_node(node, style))


def _markdown_attributes(attributes: dict[str, str | None]) -> str:
    return "".join(f";{key}={json.dumps(value, ensure_ascii=False)}" for key, value in attributes.items() if value is not None)


def _markdown_entry(tag: str, attributes: dict[str, str | None], text: str) -> str:
    separator = "" if text.endswith("\n") else "\n"
    return f"~~~{tag}{_markdown_attributes(attributes)}\n{text}{separator}~~~"


def schema_markdown(schema: Schema) -> str:
    descriptor = surface_for(schema)
    return _markdown_entry(descriptor.tag or "schema", {"id": schema.id, "name": schema.name, "purpose": schema.purpose}, schema_text(schema))


def trigger_markdown(trigger: Trigger) -> str:
    descriptor = surface_for(trigger)
    return _markdown_entry(descriptor.tag or "trigger", {"id": trigger.id}, "\n".join(trigger_lines(trigger)))


def process_markdown(process: Process) -> str:
    descriptor = surface_for(process)
    return _markdown_entry(descriptor.tag or "process", {"id": process.id, "name": process.name}, "\n".join(process_lines(process)))


def interface_markdown(interface: Interface) -> str:
    descriptor = surface_for(interface)
    return _markdown_entry(descriptor.tag or "interface", {"id": interface.id, "direction": interface.direction, "schema": interface.schema_id}, interface_body(interface))


def _markdown_part(tag: str, bodies: list[str], separator: str = "\n") -> str:
    text = separator.join(bodies)
    closing = "" if not text or text.endswith("\n") else "\n"
    return f"~~~~{tag}\n{text}{closing}~~~~"


def _node_markdown(node: Node) -> str:
    parts = {
        "instructions": _markdown_part("instructions", instruction_lines(node)),
        "constants": _markdown_part("constants", [constant_text(item) for item in node.constants], "\n\n"),
        "schemas": _markdown_part("schemas", [schema_markdown(item) for item in node.schemas], "\n\n"),
        "state": _markdown_part("state", [named_value_line(item) for item in node.state]),
        "triggers": _markdown_part("triggers", [trigger_markdown(item) for item in node.triggers], "\n\n"),
        "processes": _markdown_part("processes", [process_markdown(item) for item in node.processes], "\n\n"),
        "interfaces": _markdown_part("interfaces", [interface_markdown(item) for item in node.interfaces], "\n\n"),
    }
    return "\n\n".join(parts[name] for name in PART_ORDER)


def node_markdown(node: Node, *, style: StyleName = "authored") -> str:
    """Render one OAK document with markdown fences."""
    surface_for(node)
    return _node_markdown(styled_node(node, style))
