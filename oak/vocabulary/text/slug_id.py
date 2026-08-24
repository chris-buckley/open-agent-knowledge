"""SlugId: lower kebab case without a leading, trailing, or repeated hyphen."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import CharacterClass, LiteralText, Repeat, Rule, Sequence

SLUG_ID_SYNTAX = Rule(
    "slug_id",
    Sequence(
        (
            CharacterClass("a-z"),
            Repeat(CharacterClass("a-z0-9")),
            Repeat(
                Sequence(
                    (
                        LiteralText("-"),
                        Repeat(CharacterClass("a-z0-9"), minimum=1),
                    )
                )
            ),
        )
    ),
)

SlugId = Annotated[str, StringConstraints(pattern=SLUG_ID_SYNTAX.pattern)]
