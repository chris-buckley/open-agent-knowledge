"""The closed datatype catalog and one validator for each datatype."""

from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AnyUrl,
    AwareDatetime,
    BeforeValidator,
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
    allow_inf_nan=False,
)

_ISO_DATETIME = (
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)
_AWARE = TypeAdapter(AwareDatetime)
_QUANTITY = TypeAdapter(Quantity)


def _aware_text(value: str) -> str:
    _AWARE.validate_python(value)
    return value


def _quantity_object(value: dict) -> dict:
    _QUANTITY.validate_python(value, strict=False)
    return value


def _json_number(value: object) -> object:
    if not isinstance(value, (int, float)):
        raise ValueError(
            f"{value!r} is not one JSON number"
        )
    return value


DATATYPE_ADAPTERS: dict[str, TypeAdapter] = {
    "string": TypeAdapter(str, config=_STRICT),
    "integer": TypeAdapter(int, config=_STRICT),
    "number": TypeAdapter(
        Annotated[
            int | float,
            BeforeValidator(_json_number),
        ],
        config=_STRICT,
    ),
    "boolean": TypeAdapter(bool, config=_STRICT),
    "quantity": TypeAdapter(
        Annotated[
            dict,
            AfterValidator(_quantity_object),
        ],
        config=_STRICT,
    ),
    "datetime": TypeAdapter(
        Annotated[
            str,
            StringConstraints(pattern=_ISO_DATETIME),
            AfterValidator(_aware_text),
        ],
        config=_STRICT,
    ),
    "uri": TypeAdapter(AnyUrl, config=_STRICT),
    "path": TypeAdapter(
        Annotated[
            str,
            StringConstraints(pattern=r"^[^\x00\r\n]+$"),
        ],
        config=_STRICT,
    ),
}
