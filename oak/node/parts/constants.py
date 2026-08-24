"""The constants part."""

from typing import Literal

from pydantic import ConfigDict, Field, JsonValue

from oak.base import Entry


class Constant(Entry):
    """One JSON value that stays the same during use."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "constants",
                    "id": "default-time-zone",
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
    value: JsonValue = Field(
        description="The JSON value that stays the same.",
        examples=["Z", 3, {"enabled": True}],
    )
