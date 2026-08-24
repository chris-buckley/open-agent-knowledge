"""The state part."""

from typing import Literal

from pydantic import ConfigDict, Field, JsonValue

from oak.base import Entry


class State(Entry):
    """One JSON value that can change while the interpreter runs."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "state",
                    "id": "status",
                    "value": "ready",
                }
            ]
        }
    )

    part: Literal["state"] = Field(
        default="state",
        description="The entry part discriminator.",
        examples=["state"],
    )
    value: JsonValue = Field(
        description="The JSON value that can change.",
        examples=["ready", 0, {"complete": False}],
    )
