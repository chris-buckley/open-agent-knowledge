"""The closed unit catalog."""

from enum import StrEnum


class Unit(StrEnum):
    """One unit selected from the shared OAK catalog."""

    PERCENT = "%"
    KILOGRAM = "kg"
    CELSIUS = "°C"
    NEWTON = "kg·m/s²"
