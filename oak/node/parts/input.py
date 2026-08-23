"""The input part."""

from typing import Literal

from pydantic import ConfigDict, Field

from oak.base import Entry
from oak.vocabulary import NonBlankLine


class Input(Entry):
    """The text contract for what the knowledge expects to receive."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "input",
                    "id": "oak:input/request",
                    "body": "A request to write one OAK tree.",
                }
            ]
        }
    )

    part: Literal["input"] = Field(
        default="input",
        description="The entry part discriminator.",
        examples=["input"],
    )
    body: NonBlankLine = Field(
        description="What the knowledge expects to receive.",
        examples=["A request to write one OAK tree."],
    )
