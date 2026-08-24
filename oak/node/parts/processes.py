"""The processes part."""

from typing import Literal

from pydantic import ConfigDict, Field

from oak.base import Entry
from oak.vocabulary import IriId, NonBlankLine


class Process(Entry):
    """One named ordered way to do a task."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "processes",
                    "id": "oak:process/write-oak",
                    "name": "Write OAK",
                    "consumes": ["oak:interface/request"],
                    "emits": ["oak:interface/result"],
                    "steps": ["Read the requirements.", "Write the knowledge."],
                }
            ]
        },
    )

    part: Literal["processes"] = Field(
        default="processes",
        description="The entry part discriminator.",
        examples=["processes"],
    )
    name: NonBlankLine = Field(
        description="The process display name.",
        examples=["Write OAK"],
    )
    consumes: list[IriId] = Field(
        default_factory=list,
        description="The input interfaces the process consumes.",
        examples=[["oak:interface/request"]],
    )
    emits: list[IriId] = Field(
        default_factory=list,
        description="The output interfaces the process emits.",
        examples=[["oak:interface/result"]],
    )
    steps: list[NonBlankLine] = Field(
        min_length=1,
        description="The ordered process steps.",
        examples=[["Read the requirements.", "Write the knowledge."]],
    )
