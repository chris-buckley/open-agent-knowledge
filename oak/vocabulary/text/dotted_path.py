"""DottedPath: one part-qualified entity or interface value path."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import Choice, LiteralText, Rule, Sequence
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX

DOTTED_PATH_SYNTAX = Rule(
    "dotted_path",
    Choice(
        (
            Sequence((LiteralText("constant."), SLUG_ID_SYNTAX.reference())),
            Sequence((LiteralText("state."), SLUG_ID_SYNTAX.reference())),
            Sequence((LiteralText("process."), SLUG_ID_SYNTAX.reference())),
            Sequence((LiteralText("interface."), SLUG_ID_SYNTAX.reference())),
            Sequence(
                (
                    LiteralText("interface."),
                    SLUG_ID_SYNTAX.reference(),
                    LiteralText("."),
                    PLACEHOLDER_SYNTAX.reference(),
                )
            ),
        )
    ),
)

DottedPath = Annotated[str, StringConstraints(pattern=DOTTED_PATH_SYNTAX.pattern)]
