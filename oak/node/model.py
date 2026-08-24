"""The node and root models."""

from __future__ import annotations

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
from oak.vocabulary import SlugId


class Node(OakModel):
    """One complete set of the seven parts with nested child nodes."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "example-node",
                    "instructions": [
                        {
                            "part": "instructions",
                            "id": "use-schema",
                            "body": "Use the supplied schema.",
                        }
                    ],
                }
            ]
        }
    )

    id: SlugId = Field(
        description="The node id, unique across the tree.",
        examples=["example-node"],
    )
    instructions: list[Instruction] = Field(
        default_factory=list,
        description="The node instructions in authored order.",
        examples=[
            [
                {
                    "part": "instructions",
                    "id": "use-schema",
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
                    "id": "default-time-zone",
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
                    "id": "title",
                    "template": "<TITLE>",
                    "where": [
                        {
                            "placeholder": "TITLE",
                            "constraints": [
                                {
                                    "kind": "type",
                                    "of": "string",
                                }
                            ],
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
                    "id": "status",
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
                    "id": "write-trigger",
                    "when": "The interpreter arrives to write OAK.",
                    "process": "write-oak",
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
                    "id": "write-oak",
                    "name": "Write OAK",
                    "steps": [
                        {
                            "kind": "act",
                            "instruction": "Write the knowledge.",
                        }
                    ],
                }
            ]
        ],
    )
    interfaces: list[Interface] = Field(
        default_factory=list,
        description="The node interfaces in authored order.",
        examples=[
            [
                {
                    "part": "interfaces",
                    "id": "request",
                    "direction": "in",
                    "schema": "request-shape",
                    "description": "The request supplied to the tree.",
                }
            ]
        ],
    )
    children: list[Node] = Field(
        default_factory=list,
        description="The child nodes in authored order.",
        examples=[[{"id": "child"}]],
    )


class Root(Node):
    """The one root node whose validator checks the complete tree graph."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "root",
                    "schemas": [
                        {
                            "part": "schemas",
                            "id": "knowledge",
                            "template": "<KNOWLEDGE>",
                            "where": [
                                {
                                    "placeholder": "KNOWLEDGE",
                                    "constraints": [
                                        {
                                            "kind": "type",
                                            "of": "string",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                    "triggers": [
                        {
                            "part": "triggers",
                            "id": "run-trigger",
                            "when": "The interpreter arrives to transform knowledge.",
                            "process": "run",
                        }
                    ],
                    "processes": [
                        {
                            "part": "processes",
                            "id": "run",
                            "name": "Transform knowledge",
                            "steps": [
                                {
                                    "kind": "act",
                                    "instruction": "Transform <KNOWLEDGE> into <RESULT>.",
                                    "inputs": [
                                        {
                                            "placeholder": "KNOWLEDGE",
                                            "value": {
                                                "source": "interface",
                                                "interface": "knowledge-interface",
                                                "placeholder": "KNOWLEDGE",
                                            },
                                        }
                                    ],
                                    "outputs": ["RESULT"],
                                },
                                {
                                    "kind": "emit",
                                    "interface": "knowledge-interface",
                                    "bindings": [
                                        {
                                            "placeholder": "KNOWLEDGE",
                                            "value": {
                                                "source": "binding",
                                                "binding": "RESULT",
                                            },
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                    "interfaces": [
                        {
                            "part": "interfaces",
                            "id": "knowledge-interface",
                            "direction": "inout",
                            "schema": "knowledge",
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
