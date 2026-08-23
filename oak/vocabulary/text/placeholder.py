"""Placeholder: the bare name of a variable part; `<NAME>` is its template text syntax."""

import re
from typing import Annotated

from pydantic import StringConstraints

from oak.vocabulary.syntax import Rule
from oak.vocabulary.text.constant_name import CONSTANT_NAME_SYNTAX

PLACEHOLDER_SYNTAX = Rule("placeholder", CONSTANT_NAME_SYNTAX.reference())

Placeholder = Annotated[str, StringConstraints(pattern=PLACEHOLDER_SYNTAX.pattern)]

_TOKEN = re.compile(f"<({PLACEHOLDER_SYNTAX.body})>")


def placeholders_in(template: str) -> set[str]:
    """Every distinct placeholder a template delimits with `<` and `>`; other `<` is literal."""
    return {match.group(1) for match in _TOKEN.finditer(template)}


def token(placeholder: str) -> str:
    """The template text syntax of one placeholder."""
    return f"<{placeholder}>"
