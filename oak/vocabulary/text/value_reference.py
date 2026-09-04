"""ValueReference: one readable value prefixed by $."""

import re
from typing import Annotated

from pydantic import AfterValidator, StringConstraints
from pydantic_core import PydanticCustomError

from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX
from oak.vocabulary.text.target_path import (
    DOCUMENT_PATH_BODY,
    is_relative_target,
    split_target,
    validate_target_path,
)

VALUE_REFERENCE_PATTERN = (
    r"^\$(?:"
    + PLACEHOLDER_SYNTAX.body
    + rf"|(?:{DOCUMENT_PATH_BODY}#)?constant\."
    + SLUG_ID_SYNTAX.body
    + r"|state\."
    + SLUG_ID_SYNTAX.body
    + r")$"
)
VALUE_REFERENCE_EBNF = (
    'value_reference = "$", '
    "( placeholder | constant_target | state_target ) ;\n"
    'constant_target = [ relative_document_path, "#" ], "constant", ".", slug_id ;\n'
    'state_target = "state", ".", slug_id ;'
)

_BARE_RE = re.compile(rf"^\${PLACEHOLDER_SYNTAX.body}$")
_STATE_RE = re.compile(rf"^\$state\.{SLUG_ID_SYNTAX.body}$")


def _value_reference(value: str) -> str:
    if _BARE_RE.fullmatch(value) or _STATE_RE.fullmatch(value):
        return value

    source = value[1:]

    try:
        validate_target_path(source)
    except PydanticCustomError:
        raise PydanticCustomError(
            "invalid_document_path",
            "value reference is invalid",
        ) from None

    _, part, _ = split_target(source)
    if part != "constant":
        raise PydanticCustomError(
            "wrong_reference_target_type",
            "relative value reference must target a constant",
        )

    if is_relative_target(source) or source.startswith("constant."):
        return value

    raise PydanticCustomError(
        "invalid_document_path",
        "value reference is invalid",
    )


ValueReference = Annotated[
    str,
    StringConstraints(pattern=VALUE_REFERENCE_PATTERN),
    AfterValidator(_value_reference),
]
