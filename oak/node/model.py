"""The single OAK node model."""

from typing import Self

from pydantic import ConfigDict, Field, model_validator

from oak.base import OakModel
from oak.node.parts import (
    Constant,
    Instruction,
    Interface,
    Process,
    Schema,
    State,
    Trigger,
)

_NODE_EXAMPLE = {
    "instructions": [
        {
            "part": "instructions",
            "id": "use-schema",
            "body": "Use the supplied schema.",
        }
    ],
}


class Node(OakModel):
    """One complete idless set of the seven OAK parts."""

    model_config = ConfigDict(json_schema_extra={"examples": [_NODE_EXAMPLE]})

    instructions: list[Instruction] = Field(
        default_factory=list,
        description="The node instructions in authored order.",
        examples=[_NODE_EXAMPLE["instructions"]],
    )
    constants: list[Constant] = Field(
        default_factory=list,
        description="The node constants in authored order.",
        examples=[[]],
    )
    schemas: list[Schema] = Field(
        default_factory=list,
        description="The node schemas in authored order.",
        examples=[[]],
    )
    state: list[State] = Field(
        default_factory=list,
        description="The node state values in authored order.",
        examples=[[]],
    )
    triggers: list[Trigger] = Field(
        default_factory=list,
        description="The node triggers in authored order.",
        examples=[[]],
    )
    processes: list[Process] = Field(
        default_factory=list,
        description="The node processes in authored order.",
        examples=[[]],
    )
    interfaces: list[Interface] = Field(
        default_factory=list,
        description="The node interfaces in authored order.",
        examples=[[]],
    )

    @model_validator(mode="after")
    def graph(self) -> Self:
        from oak.node.graph import validate_graph

        validate_graph(self)
        return self
