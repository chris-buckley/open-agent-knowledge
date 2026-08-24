"""ProcessName: exactly two ASCII words in action object form."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import CharacterClass, LiteralText, Repeat, Rule, Sequence

_ACTION_SEGMENT = Sequence(
    (
        CharacterClass("A-Z"),
        Repeat(CharacterClass("A-Za-z0-9")),
    )
)
_ACTION_WORD = Sequence(
    (
        _ACTION_SEGMENT,
        Repeat(
            Sequence(
                (
                    LiteralText("-"),
                    Repeat(CharacterClass("A-Za-z0-9"), minimum=1),
                )
            )
        ),
    )
)
_OBJECT_SEGMENT = Sequence(
    (
        CharacterClass("A-Za-z0-9"),
        Repeat(CharacterClass("A-Za-z0-9")),
    )
)
_OBJECT_WORD = Sequence(
    (
        _OBJECT_SEGMENT,
        Repeat(
            Sequence(
                (
                    LiteralText("-"),
                    Repeat(CharacterClass("A-Za-z0-9"), minimum=1),
                )
            )
        ),
    )
)

PROCESS_NAME_SYNTAX = Rule(
    "process_name",
    Sequence((_ACTION_WORD, LiteralText(" "), _OBJECT_WORD)),
)

ProcessName = Annotated[
    str,
    StringConstraints(pattern=PROCESS_NAME_SYNTAX.pattern),
]
