"""Canonical one-line interface rendering."""

import json

from oak.node.parts.interfaces import INTERFACE_FLOW_BY_NAME, Interface
from oak.surface.registry import surface_for


def interface_text(interface: Interface) -> str:
    """Render one one-way boundary contract."""
    surface_for(interface)
    definition = INTERFACE_FLOW_BY_NAME[interface.flow]
    text = f"{interface.id} {definition.keyword} {interface.schema_id}"

    if interface.description is not None:
        text += ": " + json.dumps(
            interface.description,
            ensure_ascii=False,
        )

    return text


__all__ = ["interface_text"]
