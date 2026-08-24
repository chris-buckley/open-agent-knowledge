"""A decimal quantity with one catalog unit."""

from decimal import Decimal

from pydantic import ConfigDict, Field

from oak.base import OakModel
from oak.vocabulary.units import Unit


class Quantity(OakModel):
    """One decimal value and one unit."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "value": Decimal("10"),
                    "unit": Unit.KILOGRAM,
                }
            ]
        }
    )

    value: Decimal = Field(
        description="The decimal quantity value.",
        examples=[Decimal("10"), Decimal("12.5")],
    )
    unit: Unit = Field(
        description="The unit selected from the shared catalog.",
        examples=[Unit.KILOGRAM, Unit.PERCENT],
    )
