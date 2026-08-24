"""Root graph checks for ids and typed references."""

from collections.abc import Iterator
from typing import TypeVar

from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.model import Node
from oak.node.parts import Interface, Process, Schema

TargetEntry = TypeVar("TargetEntry", bound=Entry)


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
    yield from node.interfaces


def _target(
    registry: dict[str, Node | Entry],
    source: Entry,
    target_id: str,
    expected: type[TargetEntry],
) -> TargetEntry:
    source_type = type(source).__name__.lower()
    target_type = expected.__name__.lower()
    target = registry.get(target_id)
    if target is None:
        raise PydanticCustomError(
            "missing_reference_target",
            "{source_type} {source} targets missing {target_type} {target}",
            {
                "source_type": source_type,
                "source": source.id,
                "target_type": target_type,
                "target": target_id,
            },
        )
    if not isinstance(target, expected):
        raise PydanticCustomError(
            "wrong_reference_target_type",
            "{source_type} {source} targets {target}, which is not a {target_type}",
            {
                "source_type": source_type,
                "source": source.id,
                "target": target_id,
                "target_type": target_type,
            },
        )
    return target


def validate_graph(root: Node) -> None:
    """Reject duplicate ids and invalid typed references."""
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
            _target(registry, trigger, trigger.process, Process)

        for interface in node.interfaces:
            _target(registry, interface, interface.schema_id, Schema)

        for process in node.processes:
            for action, references, allowed in (
                ("consume", process.consumes, ("in", "inout")),
                ("emit", process.emits, ("out", "inout")),
            ):
                for reference in references:
                    interface = _target(registry, process, reference, Interface)
                    if interface.direction not in allowed:
                        raise PydanticCustomError(
                            "interface_direction_mismatch",
                            "process {process} cannot {action} interface {interface} with direction {direction}",
                            {
                                "process": process.id,
                                "action": action,
                                "interface": interface.id,
                                "direction": interface.direction,
                            },
                        )
