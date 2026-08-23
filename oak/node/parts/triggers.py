"""The triggers part."""

from typing import Literal

from pydantic import ConfigDict, Field

from oak.base import Entry
from oak.vocabulary import IriId, NonBlankLine


class Trigger(Entry):
    """One arrival reason and the process it selects."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "triggers",
                    "id": "oak:trigger/write-oak",
                    "when": "The interpreter arrives to write OAK.",
                    "process": "oak:process/write-oak",
                }
            ]
        }
    )

    part: Literal["triggers"] = Field(
        default="triggers",
        description="The entry part discriminator.",
        examples=["triggers"],
    )
    when: NonBlankLine = Field(
        description="Why the interpreter enters the knowledge.",
        examples=["The interpreter arrives to write OAK."],
    )
    process: IriId = Field(
        description="The process entry selected by the trigger.",
        examples=["oak:process/write-oak"],
    )
