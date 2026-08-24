"""Display forms shared by every render."""

from oak.vocabulary.display.datetime import datetime_text
from oak.vocabulary.display.number import (
    DECIMAL_SEPARATOR,
    THIN_SPACE,
    number_text,
)
from oak.vocabulary.display.quantity import quantity_text

__all__ = [
    "DECIMAL_SEPARATOR",
    "THIN_SPACE",
    "datetime_text",
    "number_text",
    "quantity_text",
]
