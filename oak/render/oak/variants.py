"""The xml variant: XML-like tags delimit verbatim text."""

from xml.sax.saxutils import quoteattr

from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import Process
from oak.node.parts.schemas import Schema
from oak.node.parts.triggers import Trigger
from oak.render.oak.arrangement import schema_text
from oak.render.oak.syntax import interface_body, named_value_line, process_lines


def _attributes(attributes: dict[str, str | None]) -> str:
    return "".join(f" {key}={quoteattr(value)}" for key, value in attributes.items() if value is not None)


def element(tag: str, attributes: dict[str, str | None], text: str) -> str:
    """Return one XML-like delimiter pair with verbatim inner text."""
    closing_separator = "" if text.endswith("\n") else "\n"
    return f"<{tag}{_attributes(attributes)}>\n{text}{closing_separator}</{tag}>"


def schema_xml(schema: Schema) -> str:
    """Render one schema with xml delimiters and authored text."""
    return element(
        "schema",
        {"id": schema.id, "name": schema.name, "purpose": schema.purpose},
        schema_text(schema),
    )


def _entries(tag: str, bodies: list[str], separator: str = "\n") -> str:
    """Return one part tag pair holding its entry bodies, empty when there are none."""
    return element(tag, {}, separator.join(bodies)) if bodies else f"<{tag}>\n</{tag}>"


def trigger_xml(trigger: Trigger) -> str:
    """Render one trigger as one self-closing tag."""
    return f"<trigger{_attributes({'id': trigger.id, 'when': trigger.when, 'process': trigger.process})} />"


def process_xml(process: Process) -> str:
    """Render one process with xml delimiters."""
    return element("process", {"id": process.id, "name": process.name}, "\n".join(process_lines(process)))


def interface_xml(interface: Interface) -> str:
    """Render one interface with xml delimiters."""
    return element(
        "interface",
        {"id": interface.id, "direction": interface.direction, "schema": interface.schema_id},
        interface_body(interface),
    )


def node_xml(node: Node) -> str:
    """Render one node: the seven parts in order, then one nested `<node>` block per child."""
    parts = [
        _entries("instructions", [instruction.body for instruction in node.instructions]),
        _entries("constants", [named_value_line(constant) for constant in node.constants]),
        _entries("schemas", [schema_xml(schema) for schema in node.schemas], "\n\n"),
        _entries("state", [named_value_line(value) for value in node.state]),
        _entries("triggers", [trigger_xml(trigger) for trigger in node.triggers]),
        _entries("processes", [process_xml(process) for process in node.processes], "\n\n"),
        _entries("interfaces", [interface_xml(interface) for interface in node.interfaces], "\n\n"),
    ]
    parts.extend(element("node", {}, node_xml(child)) for child in node.children)
    return "\n\n".join(parts)
