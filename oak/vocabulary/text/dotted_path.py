"""DottedPath: one local part-qualified target."""

from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX

DOTTED_PATH_PATTERN = (
    r"^(?:constant|schema|state|process|interface)\."
    + SLUG_ID_SYNTAX.body
    + r"$"
)
DOTTED_PATH_EBNF = (
    "dotted_path = "
    "( \"constant\" | \"schema\" | \"state\" | "
    "\"process\" | \"interface\" ), "
    "\".\", slug_id ;"
)

DottedPath = Annotated[
    str,
    StringConstraints(pattern=DOTTED_PATH_PATTERN),
]
