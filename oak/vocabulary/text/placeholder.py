"""Placeholder: the bare name of a variable part of a template; `<NAME>` is its template text syntax."""

import re

from oak.vocabulary.text.constant_name import CONSTANT_NAME_BODY, ConstantName

Placeholder = ConstantName

PLACEHOLDER_TOKEN_PATTERN = rf"^<{CONSTANT_NAME_BODY}>$"

_TOKEN = re.compile(rf"<({CONSTANT_NAME_BODY})>")


def placeholders_in(template: str) -> set[str]:
    """Every distinct placeholder a template delimits with `<` and `>`; other `<` is literal."""
    return {match.group(1) for match in _TOKEN.finditer(template)}


def token(placeholder: str) -> str:
    """The template text syntax of one placeholder."""
    return f"<{placeholder}>"
