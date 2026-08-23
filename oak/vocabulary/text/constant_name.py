"""ConstantName: ASCII upper snake case without a leading, trailing, or repeated underscore."""

from typing import Annotated

from pydantic import StringConstraints

CONSTANT_NAME_BODY = r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*"
CONSTANT_NAME_PATTERN = rf"^{CONSTANT_NAME_BODY}$"

ConstantName = Annotated[str, StringConstraints(pattern=CONSTANT_NAME_PATTERN)]
