"""Ordered validation of relationships inside one OAK node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oak.node.index import NodeIndex
from oak.node.validation.processes import (
    validate_local_call_cycles,
    validate_process_schema_contract,
    validate_process_steps,
)
from oak.node.validation.triggers import validate_triggers
from oak.node.validation.values import (
    interface_schema,
    validate_typed_entries,
)

if TYPE_CHECKING:
    from oak.node.model import Node


def validate_node(node: Node) -> None:
    """Reject invalid ids, local references, guards, and process flow."""
    index = NodeIndex.build(node)

    for interface in node.interfaces:
        interface_schema(
            index,
            interface,
        )

    validate_typed_entries(
        index,
        node,
    )

    for process in node.processes:
        validate_process_schema_contract(
            index,
            process,
        )

    validate_triggers(
        index,
        node.triggers,
    )

    for process in node.processes:
        validate_process_steps(
            index,
            process,
            process.steps,
        )

    validate_local_call_cycles(node.processes)


__all__ = [
    "validate_node",
]
