"""The OAK display form for quantities."""

from oak.vocabulary.datatypes.quantity import Quantity
from oak.vocabulary.display.number import number_text


def quantity_text(quantity: Quantity) -> str:
    """Render one number, one space, and one unit."""
    return f"{number_text(quantity.value)} {quantity.unit.value}"
