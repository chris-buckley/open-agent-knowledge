"""The OAK display form for numbers."""

from decimal import Decimal

THIN_SPACE = "\u2009"
DECIMAL_SEPARATOR = "."


def number_text(value: Decimal | int | float) -> str:
    """Render one number with OAK separators."""
    if isinstance(value, bool):
        raise TypeError("a boolean is not an OAK number")

    decimal = value if isinstance(value, Decimal) else Decimal(str(value))
    source = format(decimal, "f")
    sign = ""

    if source.startswith("-"):
        sign = "-"
        source = source[1:]

    integer, separator, fraction = source.partition(".")
    groups: list[str] = []

    while integer:
        groups.append(integer[-3:])
        integer = integer[:-3]

    text = sign + THIN_SPACE.join(reversed(groups or ["0"]))
    if separator:
        text += DECIMAL_SEPARATOR + fraction
    return text
