"""The interfaces part."""

from typing import Annotated, Literal

from pydantic import AfterValidator, ConfigDict, Field

from oak.base import Entry
from oak.vocabulary.text.non_blank_line import NonBlankLine
from oak.vocabulary.text.target_path import TargetPath, typed_target

Direction = Literal["in", "out", "inout"]
SchemaTarget = Annotated[
    TargetPath,
    AfterValidator(lambda value: typed_target(value, "schema")),
]


class Interface(Entry):
    """One crossing of information at the active document boundary."""

    model_config = ConfigDict(
        serialize_by_alias=True,
        json_schema_extra={
            "examples": [
                {
                    "part": "interfaces",
                    "id": "request",
                    "direction": "in",
                    "schema": "schema.request-shape",
                    "description": "The request supplied to the document.",
                },
                {
                    "part": "interfaces",
                    "id": "shared-request",
                    "direction": "in",
                    "schema": "../shared/contracts.oak.md#schema.request-shape",
                },
            ]
        },
    )

    part: Literal["interfaces"] = Field(
        default="interfaces",
        description="The entry part discriminator.",
        examples=["interfaces"],
    )
    direction: Direction = Field(
        description="The direction across the document boundary.",
        examples=["in", "out", "inout"],
    )
    schema_id: SchemaTarget = Field(
        alias="schema",
        title="Schema",
        description="The local or relative schema target that defines the shape.",
        examples=["schema.request-shape"],
    )
    description: NonBlankLine | None = Field(
        default=None,
        description="What the document boundary crossing means.",
        examples=["The request supplied to the document."],
    )
