"""How information is conveyed without ambiguity inside every render."""

from oak.vocabulary.text import (
    DottedPath,
    NonBlankLine,
    Placeholder,
    ProcessName,
    RegexPattern,
    SlugId,
    TargetPath,
    ValueReference,
)
from oak.vocabulary.units import Unit

__all__ = [
    "DATATYPE_ADAPTERS",
    "DECIMAL_SEPARATOR",
    "Datatype",
    "DateTime",
    "DottedPath",
    "NonBlankLine",
    "Placeholder",
    "ProcessName",
    "Quantity",
    "RegexPattern",
    "SlugId",
    "THIN_SPACE",
    "TargetPath",
    "Unit",
    "ValueReference",
    "datetime_text",
    "number_text",
    "quantity_text",
]


def __getattr__(name: str) -> object:
    if name in {
        "DATATYPE_ADAPTERS",
        "Datatype",
        "DateTime",
        "Quantity",
    }:
        from oak.vocabulary import datatypes

        return getattr(
            datatypes,
            name,
        )

    if name in {
        "DECIMAL_SEPARATOR",
        "THIN_SPACE",
        "datetime_text",
        "number_text",
        "quantity_text",
    }:
        from oak.vocabulary import display

        return getattr(
            display,
            name,
        )

    raise AttributeError(name)
