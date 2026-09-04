"""The interfaces part and its closed one-way flow registry."""

from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import AfterValidator, ConfigDict, Field

from oak.node.parts.entry import Entry
from oak.vocabulary.text.non_blank_line import NonBlankLine
from oak.vocabulary.text.target_path import TargetPath, typed_target

InterfaceFlow = Literal["receives", "emits"]
SchemaTarget = Annotated[
    TargetPath,
    AfterValidator(lambda value: typed_target(value, "schema")),
]


@dataclass(frozen=True, slots=True)
class InterfaceFlowDefinition:
    """One interface flow, canonical keyword, and interpretation instruction."""

    flow: InterfaceFlow
    keyword: str
    instruction: str


INTERFACE_FLOWS = (
    InterfaceFlowDefinition(
        "receives",
        "RECEIVES",
        "RECEIVES accepts one complete instance of its schema.",
    ),
    InterfaceFlowDefinition(
        "emits",
        "EMITS",
        "EMITS publishes one complete instance of its schema.",
    ),
)
INTERFACE_FLOW_BY_NAME = {
    definition.flow: definition
    for definition in INTERFACE_FLOWS
}
INTERFACE_FLOW_BY_KEYWORD = {
    definition.keyword: definition
    for definition in INTERFACE_FLOWS
}


class Interface(Entry):
    """One identified one-way crossing at the active document boundary."""

    model_config = ConfigDict(
        serialize_by_alias=True,
        json_schema_extra={
            "examples": [
                {
                    "part": "interfaces",
                    "id": "request",
                    "flow": "receives",
                    "schema": "schema.request-shape",
                },
                {
                    "part": "interfaces",
                    "id": "result",
                    "flow": "emits",
                    "schema": "../shared/contracts.oak.md#schema.result-shape",
                    "description": "Returned only to the coordinator.",
                },
            ]
        },
    )

    part: Literal["interfaces"] = Field(
        default="interfaces",
        description="The entry part discriminator.",
        examples=["interfaces"],
    )
    flow: InterfaceFlow = Field(
        description="The one-way flow across the document boundary.",
        examples=["receives", "emits"],
    )
    schema_id: SchemaTarget = Field(
        alias="schema",
        title="Schema",
        description="The local or relative schema target that defines the instance.",
        examples=["schema.request-shape"],
    )
    description: NonBlankLine | None = Field(
        default=None,
        description="Boundary meaning absent from the interface id and schema.",
        examples=["Returned only to the coordinator."],
    )


__all__ = [
    "INTERFACE_FLOWS",
    "INTERFACE_FLOW_BY_KEYWORD",
    "INTERFACE_FLOW_BY_NAME",
    "Interface",
    "InterfaceFlow",
    "InterfaceFlowDefinition",
    "SchemaTarget",
]
