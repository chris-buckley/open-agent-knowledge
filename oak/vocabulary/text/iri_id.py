"""IriId: an ASCII scheme, a colon, and one or more non-whitespace characters."""

from typing import Annotated

from pydantic import StringConstraints

IRI_ID_PATTERN = r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$"

IriId = Annotated[str, StringConstraints(pattern=IRI_ID_PATTERN)]
