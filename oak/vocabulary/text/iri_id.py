"""IriId: an ASCII scheme, a colon, and one or more non-whitespace characters."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import CharacterClass, LiteralText, Repeat, Rule, Sequence

IRI_ID_SYNTAX = Rule(
    "iri_id",
    Sequence(
        (
            CharacterClass("A-Za-z"),
            Repeat(CharacterClass(r"A-Za-z0-9+.\-")),
            LiteralText(":"),
            Repeat(CharacterClass(r"^\s"), minimum=1),
        )
    ),
)

IriId = Annotated[str, StringConstraints(pattern=IRI_ID_SYNTAX.pattern)]
