"""The interfaces part."""

from typing import Literal

from pydantic import ConfigDict, Field

from oak.base import Entry
from oak.vocabulary import IriId, NonBlankLine

Direction = Literal["in", "out", "inout"]


class Interface(Entry):
    """One named crossing of information at the tree boundary."""

    model_config = ConfigDict(
        serialize_by_alias=True,
        json_schema_extra={
            "examples": [
                {
                    "part": "interfaces",
                    "id": "oak:interface/request",
                    "direction": "in",
                    "schema": "oak:schema/request",
                    "description": "The request supplied to the tree.",
                }
            ]
        },
    )

    part: Literal["interfaces"] = Field(
        default="interfaces",
        description="The entry part discriminator.",
        examples=["interfaces"],
    )
    direction: Direction = Field(
        description="The direction across the tree boundary.",
        examples=["in", "out", "inout"],
    )
    schema_id: IriId = Field(
        alias="schema",
        title="Schema",
        description="The schema entry that defines the information shape.",
        examples=["oak:schema/request"],
    )
    description: NonBlankLine | None = Field(
        default=None,
        description="What the tree boundary crossing means.",
        examples=["The request supplied to the tree."],
    )
