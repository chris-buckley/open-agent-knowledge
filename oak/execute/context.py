"""The shared transaction context and local process frame."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import JsonValue

from oak.execute.models import ActHandler, Emission, ToolContract
from oak.resolve.graph import ResolvedGraph


@dataclass(slots=True)
class ExecutionContext:
    """The shared mutable state of one top-level execution transaction."""

    graph: ResolvedGraph
    state: dict[str, JsonValue]
    emissions: list[Emission]
    act: ActHandler | None
    tools: Mapping[str, ToolContract]


@dataclass(slots=True)
class ProcessFrame:
    """One process-local binding scope in one document."""

    document: str
    bindings: dict[str, JsonValue]

    def child(self) -> ProcessFrame:
        """Return one fresh child scope with the current bindings."""
        return ProcessFrame(self.document, dict(self.bindings))


__all__ = ["ExecutionContext", "ProcessFrame"]
