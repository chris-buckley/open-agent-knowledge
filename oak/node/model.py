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

_NODE_EXAMPLE = {
    "id": "example-node",
    "instructions": [
        {
            "part": "instructions",
            "id": "use-schema",
            "body": "Use the supplied schema.",
        }
    ],
}

_ROOT_EXAMPLE = {
    "id": "root",
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
                    "interface": "result-interface",
                    "bindings": [
                        {
                            "placeholder": "RESULT",
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
    "schemas": [
        {
            "part": "schemas",
            "id": "knowledge",
            "template": "<KNOWLEDGE>",
            "where": [
                {
                    "placeholder": "KNOWLEDGE",
                    "constraints": [{"kind": "type", "of": "string"}],
                }
            ],
        },
        {
            "part": "schemas",
            "id": "result",
            "template": "<RESULT>",
            "where": [
                {
                    "placeholder": "RESULT",
                    "constraints": [{"kind": "type", "of": "string"}],
                }
            ],
        },
    ],
    "interfaces": [
        {
            "part": "interfaces",
            "id": "knowledge-interface",
            "direction": "in",
            "schema": "knowledge",
        },
        {
            "part": "interfaces",
            "id": "result-interface",
            "direction": "out",
            "schema": "result",
        },
    ],
}


class Node(OakModel):
    """One complete set of the seven parts with nested child nodes."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [_NODE_EXAMPLE]}
    )

    id: SlugId = Field(
        description="The node id, unique across the tree.",
    )
    instructions: list[Instruction] = Field(
        default_factory=list,
        description="The node instructions in authored order.",
    )
    constants: list[Constant] = Field(
        default_factory=list,
        description="The node constants in authored order.",
    )
    schemas: list[Schema] = Field(
        default_factory=list,
        description="The node schemas in authored order.",
    )
    state: list[State] = Field(
        default_factory=list,
        description="The node state values in authored order.",
    )
    triggers: list[Trigger] = Field(
        default_factory=list,
        description="The node triggers in authored order.",
    )
    processes: list[Process] = Field(
        default_factory=list,
        description="The node processes in authored order.",
    )
    interfaces: list[Interface] = Field(
        default_factory=list,
        description="The node interfaces in authored order.",
    )
    children: list[Node] = Field(
        default_factory=list,
        description="The child nodes in authored order.",
    )


class Root(Node):
    """The one root node whose validator checks the complete tree graph."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [_ROOT_EXAMPLE]}
    )

    @model_validator(mode="after")
    def graph(self) -> Self:
        from oak.node.graph import validate_graph

        validate_graph(self)
        return self
