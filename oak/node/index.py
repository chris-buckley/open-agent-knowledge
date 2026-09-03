"""The typed local entry index for one OAK node."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from pydantic_core import PydanticCustomError

from oak.node.parts.entry import Entry
from oak.node.structure import PART_ORDER
from oak.vocabulary.text.target_path import is_relative_target, target_id

if TYPE_CHECKING:
    from oak.node.model import Node

TargetEntry = TypeVar("TargetEntry", bound=Entry)


def iter_entries(node: Node) -> Iterator[Entry]:
    """Yield one node's entries in OAK part order."""
    for part in PART_ORDER:
        yield from getattr(node, part)


@dataclass(frozen=True, slots=True, eq=False)
class NodeIndex(Mapping[str, Entry]):
    """One node's unique local entries indexed by id."""

    entries: Mapping[str, Entry]

    @classmethod
    def build(cls, node: Node) -> NodeIndex:
        """Build one index and reject duplicate ids."""
        entries: dict[str, Entry] = {}
        duplicates: set[str] = set()

        for entry in iter_entries(node):
            if entry.id in entries:
                duplicates.add(entry.id)
            else:
                entries[entry.id] = entry

        if duplicates:
            raise PydanticCustomError(
                "duplicate_id",
                "document repeats ids: {ids}",
                {"ids": ", ".join(sorted(duplicates))},
            )

        return cls(entries)

    def __getitem__(self, identifier: str) -> Entry:
        return self.entries[identifier]

    def __iter__(self) -> Iterator[str]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def require(
        self,
        source: Entry,
        path: str,
        expected: type[TargetEntry],
    ) -> TargetEntry | None:
        """Return one typed local target, or null for a relative target."""
        if is_relative_target(path):
            return None

        identifier = target_id(path)
        target = self.entries.get(identifier)
        source_type = type(source).__name__.lower()
        target_type = expected.__name__.lower()

        if target is None:
            raise PydanticCustomError(
                "missing_reference_target",
                "{source_type} {source} targets missing {target_type} {target}",
                {
                    "source_type": source_type,
                    "source": source.id,
                    "target_type": target_type,
                    "target": path,
                },
            )

        if not isinstance(target, expected):
            raise PydanticCustomError(
                "wrong_reference_target_type",
                "{source_type} {source} targets {target}, which is not a {target_type}",
                {
                    "source_type": source_type,
                    "source": source.id,
                    "target": path,
                    "target_type": target_type,
                },
            )

        return target


__all__ = [
    "NodeIndex",
    "iter_entries",
]
