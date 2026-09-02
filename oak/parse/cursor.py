"""The mutable position for parsing one line sequence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn

from oak.parse.errors import fail


@dataclass(slots=True)
class Cursor:
    """One current position in one source line sequence."""

    lines: list[str]
    path: str
    first_line: int
    index: int = 0

    @property
    def line_number(self) -> int:
        """Return the current one-based source line."""
        return self.first_line + self.index

    @property
    def at_end(self) -> bool:
        """Return whether the cursor has consumed every line."""
        return self.index >= len(self.lines)

    def peek(self) -> str | None:
        """Return the current line without consuming it."""
        if self.at_end:
            return None
        return self.lines[self.index]

    def take(self) -> str:
        """Return and consume the current line."""
        line = self.peek()
        if line is None:
            self.fail(
                "unexpected_end",
                "unexpected end of input",
            )
        self.index += 1
        return line

    def advance(self, count: int = 1) -> None:
        """Consume the named number of lines."""
        self.index += count

    def indentation(self) -> int:
        """Return current space indentation and reject tabs."""
        line = self.peek()
        if line is None:
            return 0
        if "\t" in line:
            self.fail(
                "tab",
                "tabs are not allowed",
            )
        return len(line) - len(line.lstrip(" "))

    def fail(
        self,
        code: str,
        message: str,
        *,
        path: str | None = None,
        line: int | None = None,
    ) -> NoReturn:
        """Raise one failure at this cursor position."""
        fail(
            code,
            self.path if path is None else path,
            self.line_number if line is None else line,
            message,
        )


__all__ = [
    "Cursor",
]
