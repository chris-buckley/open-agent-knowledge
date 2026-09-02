"""The resolved representation of one reachable OAK document graph."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypeVar

from oak.base import Entry
from oak.node import Node
from oak.resolve.errors import raise_resolution
from oak.resolve.paths import (
    display_target,
    target_document,
)
from oak.vocabulary.text.target_path import split_target

TargetEntry = TypeVar(
    "TargetEntry",
    bound=Entry,
)


@dataclass(frozen=True, slots=True)
class ResolvedGraph:
    """One explicitly loaded and type-checked OAK document graph."""

    root: str
    documents: Mapping[str, Node]
    registries: Mapping[
        str,
        Mapping[str, Entry],
    ]

    def target_document(
        self,
        source: str,
        target: str,
    ) -> str:
        """Return the normalized document selected by one target."""
        return target_document(
            source,
            target,
        )

    def entry(
        self,
        source: str,
        target: str,
        expected: type[TargetEntry],
    ) -> tuple[str, TargetEntry]:
        """Return one resolved typed entry and its document."""
        document = self.target_document(
            source,
            target,
        )
        _relative, _part, identifier = split_target(target)
        entry = self.registries.get(
            document,
            {},
        ).get(identifier)

        if entry is None:
            raise_resolution(
                (
                    "external_entry_missing"
                    if document != source
                    else "missing_reference_target"
                ),
                source,
                target,
                "target entry does not exist",
            )

        if not isinstance(entry, expected):
            raise_resolution(
                "wrong_reference_target_type",
                source,
                target,
                f"target is not a {expected.__name__.lower()}",
            )

        return document, entry

    def display_target(
        self,
        document: str,
        part: str,
        identifier: str,
    ) -> str:
        """Return one root-relative public target."""
        return display_target(
            self.root,
            document,
            part,
            identifier,
        )


__all__ = [
    "ResolvedGraph",
]
