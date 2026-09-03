"""RegexPattern: an anchored portable subset compiled by rust-regex."""

from functools import lru_cache
from typing import Annotated

from pydantic import AfterValidator, ConfigDict, StringConstraints, TypeAdapter
from pydantic_core import PydanticCustomError, SchemaError

from oak.vocabulary.syntax import CharacterClass, Choice, LiteralText, Optional, Repeat, Rule, Sequence

_DIGIT = CharacterClass("0-9")
_PLAIN_ATOM = CharacterClass(r"^\r\n\\.^$*+?{}\[\]()|")
_ESCAPED_PUNCTUATION = Sequence(
    (
        LiteralText("\\"),
        CharacterClass(r"\\.^$|?*+(){}\[\]/-"),
    )
)
_ESCAPED_CONTROL = Sequence((LiteralText("\\"), CharacterClass("nrt")))

_CLASS_CHAR = CharacterClass(r"^\r\n\\\[\]\-&~")
_CLASS_ESCAPE = Choice((_ESCAPED_PUNCTUATION, _ESCAPED_CONTROL))
_CLASS_RANGE = Sequence((_CLASS_CHAR, LiteralText("-"), _CLASS_CHAR))
_CLASS_ITEM = Choice((_CLASS_RANGE, _CLASS_ESCAPE, _CLASS_CHAR))
_CHARACTER_CLASS = Sequence(
    (
        LiteralText("["),
        Optional(LiteralText("^")),
        Repeat(_CLASS_ITEM, minimum=1),
        LiteralText("]"),
    )
)

_ATOM = Choice((LiteralText("."), _CHARACTER_CLASS, _ESCAPED_PUNCTUATION, _ESCAPED_CONTROL, _PLAIN_ATOM))
_COUNT = Repeat(_DIGIT, minimum=1)
_QUANTIFIER = Choice(
    (
        LiteralText("*"),
        LiteralText("+"),
        LiteralText("?"),
        Sequence((LiteralText("{"), _COUNT, LiteralText("}"))),
        Sequence((LiteralText("{"), _COUNT, LiteralText(",}"))),
        Sequence((LiteralText("{"), _COUNT, LiteralText(","), _COUNT, LiteralText("}"))),
    )
)
_PIECE = Sequence((_ATOM, Optional(_QUANTIFIER)))

REGEX_PATTERN_SYNTAX = Rule(
    "regex_pattern",
    Sequence((LiteralText("^"), Repeat(_PIECE), LiteralText("$"))),
)
REGEX_SOURCE_PATTERN = REGEX_PATTERN_SYNTAX.pattern


@lru_cache(maxsize=512)
def rust_regex_adapter(pattern: str) -> TypeAdapter[str]:
    """Return one cached strict rust-regex adapter for an authored pattern."""
    return TypeAdapter(
        Annotated[str, StringConstraints(pattern=pattern)],
        config=ConfigDict(strict=True, regex_engine="rust-regex"),
    )


def _validated_pattern(pattern: str) -> str:
    try:
        rust_regex_adapter(pattern)
    except SchemaError as error:
        raise PydanticCustomError(
            "invalid_rust_regex",
            "rust-regex cannot compile the pattern: {reason}",
            {"reason": str(error)},
        ) from None
    return pattern


RegexPattern = Annotated[
    str,
    StringConstraints(pattern=REGEX_SOURCE_PATTERN),
    AfterValidator(_validated_pattern),
]
