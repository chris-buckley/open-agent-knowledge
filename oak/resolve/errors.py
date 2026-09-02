"""Stable diagnostics for resolving one OAK document graph."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn


@dataclass(frozen=True, slots=True)
class ResolutionFailure:
    """One stable document-graph resolution failure."""

    code: str
    source: str | None
    target: str
    message: str

    def __str__(self) -> str:
        location = self.source or "<unknown>"
        return f"[{self.code}] {location} -> {self.target}: {self.message}"


class ResolutionError(ValueError):
    """One explicit document-graph resolution failure."""

    def __init__(self, failure: ResolutionFailure) -> None:
        self.failure = failure
        self.code = failure.code
        super().__init__(str(failure))


def raise_resolution(
    code: str,
    source: str | None,
    target: str,
    message: str,
) -> NoReturn:
    """Raise one stable resolution failure."""
    raise ResolutionError(
        ResolutionFailure(
            code,
            source,
            target,
            message,
        )
    )


__all__ = [
    "ResolutionError",
    "ResolutionFailure",
]
