"""The node and root models."""

from __future__ import annotations

from typing import Self

from pydantic import ConfigDict, Field, model_validator

from oak.base import OakModel
from oak.node.parts import Constant, Input, Instruction, Process, Schema, State, Trigger
from oak.vocabulary import IriId


class Node(OakModel):
    """One complete set of the seven parts with nested child nodes."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "oak:node/example",
                    "instructions": [
                        {
                            "part": "instructions",
                            "id": "oak:instruction/example",
                            "body": "Use the supplied schema.",
                        }
                    ],
                }
            ]
        }
    )

    id: IriId = Field(
        description="The node id, unique across the tree.",
        examples=["oak:node/example"],
    )
    instructions: list[Instruction] = Field(
        default_factory=list,
        description="The node instructions in authored order.",
        examples=[
            [
                {
                    "part": "instructions",
                    "id": "oak:instruction/example",
                    "body": "Use the supplied schema.",
                }
            ]
        ],
    )
    constants: list[Constant] = Field(
        default_factory=list,
        description="The node constants in authored order.",
        examples=[
            [
                {
                    "part": "constants",
                    "id": "oak:constant/default-time-zone",
                    "name": "DEFAULT_TZ",
                    "value": "Z",
                }
            ]
        ],
    )
    schemas: list[Schema] = Field(
        default_factory=list,
        description="The node schemas in authored order.",
        examples=[
            [
                {
                    "part": "schemas",
                    "id": "oak:schema/title",
                    "template": "<TITLE>",
                    "where": [
                        {
                            "placeholder": "TITLE",
                            "constraints": [{"kind": "type", "of": "string"}],
                        }
                    ],
                }
            ]
        ],
    )
    state: list[State] = Field(
        default_factory=list,
        description="The node state values in authored order.",
        examples=[
            [
                {
                    "part": "state",
                    "id": "oak:state/status",
                    "name": "STATUS",
                    "value": "ready",
                }
            ]
        ],
    )
    triggers: list[Trigger] = Field(
        default_factory=list,
        description="The node triggers in authored order.",
        examples=[
            [
                {
                    "part": "triggers",
                    "id": "oak:trigger/write",
                    "when": "The interpreter arrives to write OAK.",
                    "process": "oak:process/write",
                }
            ]
        ],
    )
    processes: list[Process] = Field(
        default_factory=list,
        description="The node processes in authored order.",
        examples=[
            [
                {
                    "part": "processes",
                    "id": "oak:process/write",
                    "name": "Write OAK",
                    "steps": ["Write the knowledge."],
                }
            ]
        ],
    )
    input: Input | None = Field(
        default=None,
        description="The node input contract.",
        examples=[
            {
                "part": "input",
                "id": "oak:input/request",
                "body": "A request to write OAK.",
            }
        ],
    )
    children: list[Node] = Field(
        default_factory=list,
        description="The child nodes in authored order.",
        examples=[[{"id": "oak:node/child"}]],
    )


class Root(Node):
    """The one root node whose validator checks the complete tree graph."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "oak:root",
                    "triggers": [
                        {
                            "part": "triggers",
                            "id": "oak:trigger/write",
                            "when": "The interpreter arrives to write OAK.",
                            "process": "oak:process/write",
                        }
                    ],
                    "processes": [
                        {
                            "part": "processes",
                            "id": "oak:process/write",
                            "name": "Write OAK",
                            "steps": ["Write the knowledge."],
                        }
                    ],
                }
            ]
        }
    )

    @model_validator(mode="after")
    def graph(self) -> Self:
        from oak.node.graph import validate_graph

        validate_graph(self)
        return self
