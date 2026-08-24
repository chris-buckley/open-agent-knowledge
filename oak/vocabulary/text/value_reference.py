"""ValueReference: `$` followed by a readable dotted path or local placeholder."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import Choice, LiteralText, Rule, Sequence
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX

VALUE_REFERENCE_SYNTAX = Rule(
    "value_reference",
    Sequence(
        (
            LiteralText("$"),
            Choice(
                (
                    Sequence(
                        (LiteralText("constant."), SLUG_ID_SYNTAX.reference())
                    ),
                    Sequence((LiteralText("state."), SLUG_ID_SYNTAX.reference())),
                    Sequence(
                        (
                            LiteralText("interface."),
                            SLUG_ID_SYNTAX.reference(),
                            LiteralText("."),
                            PLACEHOLDER_SYNTAX.reference(),
                        )
                    ),
                    PLACEHOLDER_SYNTAX.reference(),
                )
            ),
        )
    ),
)

ValueReference = Annotated[
    str,
    StringConstraints(pattern=VALUE_REFERENCE_SYNTAX.pattern),
]
