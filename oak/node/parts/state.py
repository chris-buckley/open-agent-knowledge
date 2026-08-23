"""The state part."""

from typing import Literal

from pydantic import ConfigDict, Field, JsonValue

from oak.base import Entry
from oak.vocabulary import ConstantName


class State(Entry):
    """One named JSON value that can change while the interpreter runs."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "state",
                    "id": "oak:state/status",
                    "name": "STATUS",
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
    name: ConstantName = Field(
        description="The name used to refer to the state value.",
        examples=["STATUS"],
    )
    value: JsonValue = Field(
        description="The JSON value that can change.",
        examples=["ready", 0, {"complete": False}],
    )
