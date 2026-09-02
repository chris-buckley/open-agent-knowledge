"""The instructions part."""

from typing import Literal

from pydantic import ConfigDict, Field

from oak.base import Entry
from oak.vocabulary.text.non_blank_line import NonBlankLine


class Instruction(Entry):
    """One rule the interpreter must follow."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "instructions",
                    "id": "read-prd",
                    "body": "Read the product requirements before work.",
                }
            ]
        }
    )

    part: Literal["instructions"] = Field(
        default="instructions",
        description="The entry part discriminator.",
        examples=["instructions"],
    )
    body: NonBlankLine = Field(
        description="One directive or declarative rule.",
        examples=["Read the product requirements before work."],
    )
