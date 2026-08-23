"""Datatype: the closed catalog of datatype names a schema constraint may select, and the validator of each."""

from typing import Annotated, Literal

from pydantic import AnyUrl, AwareDatetime, ConfigDict, StringConstraints, TypeAdapter

Datatype = Literal["string", "integer", "number", "boolean", "datetime", "uri", "path"]

_STRICT = ConfigDict(strict=True, regex_engine="rust-regex")

DATATYPE_ADAPTERS: dict[str, TypeAdapter] = {
    "string": TypeAdapter(str, config=_STRICT),
    "integer": TypeAdapter(int, config=_STRICT),
    "number": TypeAdapter(int | float, config=_STRICT),
    "boolean": TypeAdapter(bool, config=_STRICT),
    "datetime": TypeAdapter(AwareDatetime, config=_STRICT),
    "uri": TypeAdapter(AnyUrl, config=_STRICT),
    "path": TypeAdapter(Annotated[str, StringConstraints(pattern=r"^[^\x00\r\n]+$")], config=_STRICT),
}
