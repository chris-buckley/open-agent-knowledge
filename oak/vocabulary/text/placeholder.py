"""Placeholder: an upper-snake name; `<NAME>` is its template text syntax."""

import re
from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import CharacterClass, LiteralText, Repeat, Rule, Sequence

PLACEHOLDER_SYNTAX = Rule(
    "placeholder",
    Sequence(
        (
            CharacterClass("A-Z"),
            Repeat(CharacterClass("A-Z0-9")),
            Repeat(
                Sequence(
                    (
                        LiteralText("_"),
                        Repeat(CharacterClass("A-Z0-9"), minimum=1),
                    )
                )
            ),
        )
    ),
)

Placeholder = Annotated[str, StringConstraints(pattern=PLACEHOLDER_SYNTAX.pattern)]

_TOKEN = re.compile(f"<({PLACEHOLDER_SYNTAX.body})>")


def placeholders_in(template: str) -> set[str]:
    """Return every distinct placeholder delimited in template text."""
    return {match.group(1) for match in _TOKEN.finditer(template)}


def token(placeholder: str) -> str:
    """Return the template text syntax of one placeholder."""
    return f"<{placeholder}>"
