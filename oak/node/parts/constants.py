"""The constants part."""

from typing import Literal

from pydantic import ConfigDict, Field, JsonValue

from oak.base import Entry
from oak.vocabulary import ConstantName


class Constant(Entry):
    """One named JSON value that stays the same during use."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "constants",
                    "id": "oak:constant/default-time-zone",
                    "name": "DEFAULT_TZ",
                    "value": "Z",
                }
            ]
        }
    )

    part: Literal["constants"] = Field(
        default="constants",
        description="The entry part discriminator.",
        examples=["constants"],
    )
    name: ConstantName = Field(
        description="The name used to refer to the constant.",
        examples=["DEFAULT_TZ"],
    )
    value: JsonValue = Field(
        description="The JSON value that stays the same.",
        examples=["Z", 3, {"enabled": True}],
    )
