"""The closed datatype catalog and one validator for each datatype."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AnyUrl,
    AwareDatetime,
    ConfigDict,
    StringConstraints,
    TypeAdapter,
)

from oak.vocabulary.datatypes.quantity import Quantity

Datatype = Literal[
    "string",
    "integer",
    "number",
    "boolean",
    "quantity",
    "datetime",
    "uri",
    "path",
]

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)

DATATYPE_ADAPTERS: dict[str, TypeAdapter] = {
    "string": TypeAdapter(str, config=_STRICT),
    "integer": TypeAdapter(int, config=_STRICT),
    "number": TypeAdapter(int | float | Decimal, config=_STRICT),
    "boolean": TypeAdapter(bool, config=_STRICT),
    "quantity": TypeAdapter(Quantity),
    "datetime": TypeAdapter(AwareDatetime, config=_STRICT),
    "uri": TypeAdapter(AnyUrl, config=_STRICT),
    "path": TypeAdapter(
        Annotated[
            str,
            StringConstraints(pattern=r"^[^\x00\r\n]+$"),
        ],
        config=_STRICT,
    ),
}
