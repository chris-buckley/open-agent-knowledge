"""NonBlankLine: one line containing at least one non-whitespace character."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import CharacterClass, Repeat, Rule, Sequence

NON_BLANK_LINE_SYNTAX = Rule(
    "non_blank_line",
    Sequence(
        (
            Repeat(CharacterClass(r"^\r\n")),
            CharacterClass(r"^\s"),
            Repeat(CharacterClass(r"^\r\n")),
        )
    ),
)

NonBlankLine = Annotated[str, StringConstraints(pattern=NON_BLANK_LINE_SYNTAX.pattern)]
