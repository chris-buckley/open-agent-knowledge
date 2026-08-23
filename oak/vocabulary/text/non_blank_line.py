"""NonBlankLine: one line containing at least one non-whitespace character."""

from typing import Annotated

from pydantic import StringConstraints

NON_BLANK_LINE_PATTERN = r"^[^\r\n]*[^\s][^\r\n]*$"

NonBlankLine = Annotated[str, StringConstraints(pattern=NON_BLANK_LINE_PATTERN)]
