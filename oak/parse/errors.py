"""Stable diagnostics for parsing one OAK document."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, NoReturn


@dataclass(frozen=True, slots=True)
class ParseFailure:
    """One stable OAK parse failure."""

    code: str
    path: str
    line: int | None
    message: str

    def __str__(self) -> str:
        location = self.path
        if self.line is not None:
            location += f":{self.line}"
        return f"[{self.code}] {location}: {self.message}"


class OakParseError(ValueError):
    """Every failure collected while parsing one OAK document."""

    code = "oak_parse_invalid"

    def __init__(self, failures: Iterable[ParseFailure]) -> None:
        self.failures = tuple(failures)
        super().__init__(
            "\n".join(
                str(failure)
                for failure in self.failures
            )
        )


class ParseError(ValueError):
    """One internal parse failure before public collection."""

    def __init__(
        self,
        code: str,
        path: str,
        line: int | None,
        message: str,
    ) -> None:
        self.failure = ParseFailure(
            code,
            path,
            line,
            message,
        )
        super().__init__(str(self.failure))


def fail(
    code: str,
    path: str,
    line: int | None,
    message: str,
) -> NoReturn:
    """Raise one internal parse failure."""
    raise ParseError(
        code,
        path,
        line,
        message,
    )


__all__ = [
    "OakParseError",
    "ParseFailure",
]
