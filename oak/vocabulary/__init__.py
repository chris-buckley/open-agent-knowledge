"""How information is conveyed without ambiguity inside every render."""

from oak.vocabulary.datatypes.datetime import DateTime
from oak.vocabulary.datatypes.names import DATATYPE_ADAPTERS, Datatype
from oak.vocabulary.datatypes.quantity import Quantity
from oak.vocabulary.display.datetime import datetime_text
from oak.vocabulary.display.number import (
    DECIMAL_SEPARATOR,
    THIN_SPACE,
    number_text,
)
from oak.vocabulary.display.quantity import quantity_text
from oak.vocabulary.text.dotted_path import DottedPath
from oak.vocabulary.text.non_blank_line import NonBlankLine
from oak.vocabulary.text.placeholder import Placeholder
from oak.vocabulary.text.process_name import ProcessName
from oak.vocabulary.text.regex_pattern import RegexPattern
from oak.vocabulary.text.slug_id import SlugId
from oak.vocabulary.text.target_path import TargetPath
from oak.vocabulary.text.value_reference import ValueReference
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
