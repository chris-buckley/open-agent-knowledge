"""ConstantName: ASCII upper snake case without a leading, trailing, or repeated underscore."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import CharacterClass, LiteralText, Repeat, Rule, Sequence

CONSTANT_NAME_SYNTAX = Rule(
    "constant_name",
    Sequence(
        (
            CharacterClass("A-Z"),
            Repeat(CharacterClass("A-Z0-9")),
            Repeat(Sequence((LiteralText("_"), Repeat(CharacterClass("A-Z0-9"), minimum=1)))),
        )
    ),
)

ConstantName = Annotated[str, StringConstraints(pattern=CONSTANT_NAME_SYNTAX.pattern)]
