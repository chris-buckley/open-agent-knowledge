"""Root graph checks for ids and typed references."""

from collections.abc import Iterator

from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.model import Node
from oak.node.parts import Process, Trigger


def iter_nodes(root: Node) -> Iterator[Node]:
    """Yield the root and every child node in authored order."""
    yield root
    for child in root.children:
        yield from iter_nodes(child)


def iter_entries(node: Node) -> Iterator[Entry]:
    """Yield one node's entries in OAK part order."""
    yield from node.instructions
    yield from node.constants
    yield from node.schemas
    yield from node.state
    yield from node.triggers
    yield from node.processes
    if node.input is not None:
        yield node.input


def validate_graph(root: Node) -> None:
    """Reject duplicate ids and invalid trigger process targets."""
    registry: dict[str, Node | Entry] = {}
    duplicates: set[str] = set()

    for node in iter_nodes(root):
        for item in (node, *iter_entries(node)):
            if item.id in registry:
                duplicates.add(item.id)
            else:
                registry[item.id] = item

    if duplicates:
        raise PydanticCustomError(
            "duplicate_id",
            "tree repeats ids: {ids}",
            {"ids": ", ".join(sorted(duplicates))},
        )

    for node in iter_nodes(root):
        for trigger in node.triggers:
            target = registry.get(trigger.process)
            if target is None:
                raise PydanticCustomError(
                    "missing_reference_target",
                    "trigger {trigger} targets missing process {process}",
                    {"trigger": trigger.id, "process": trigger.process},
                )
            if not isinstance(target, Process):
                raise PydanticCustomError(
                    "wrong_reference_target_type",
                    "trigger {trigger} targets {process}, which is not a process",
                    {"trigger": trigger.id, "process": trigger.process},
                )
