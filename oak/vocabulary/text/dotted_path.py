"""DottedPath: one local target or one local interface placeholder path."""

import re
from typing import Annotated

from pydantic import AfterValidator, StringConstraints
from pydantic_core import PydanticCustomError

from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX

DOTTED_PATH_PATTERN = (
    r"^(?:constant|schema|state|process|interface)\."
    + SLUG_ID_SYNTAX.body
    + r"(?:\."
    + PLACEHOLDER_SYNTAX.body
    + r")?$"
)
DOTTED_PATH_EBNF = (
    "dotted_path = "
    "( \"constant\" | \"schema\" | \"state\" | "
    "\"process\" | \"interface\" ), "
    "\".\", slug_id, [ \".\", placeholder ] ;"
)

_PATH_RE = re.compile(DOTTED_PATH_PATTERN)


def _dotted_path(value: str) -> str:
    if _PATH_RE.fullmatch(value) is None:
        raise PydanticCustomError(
            "invalid_document_path",
            "dotted path is invalid",
        )

    segments = value.split(".")
    if (
        len(segments) == 3
        and segments[0] != "interface"
    ):
        raise PydanticCustomError(
            "invalid_document_path",
            "only an interface path can end in a placeholder",
        )

    return value


DottedPath = Annotated[
    str,
    StringConstraints(
        pattern=DOTTED_PATH_PATTERN,
    ),
    AfterValidator(_dotted_path),
]
