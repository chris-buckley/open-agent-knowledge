"""The process entry model and its local flow validation."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from oak.base import Entry
from oak.node.parts.interfaces import SchemaTarget
from oak.node.parts.processes.steps import (
    Step,
    sequence_always_fails,
    visible_bindings,
)
from oak.vocabulary import ProcessName


class Process(Entry):
    """One named ordered way to do a task."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "processes",
                    "id": "normalise",
                    "name": "Normalise name",
                    "input": "schema.raw-name",
                    "output": "schema.normal-name",
                    "steps": [
                        {
                            "kind": "act",
                            "instruction": "Normalise <RAW_NAME> into <NORMAL_NAME>.",
                            "inputs": [
                                {
                                    "placeholder": "RAW_NAME",
                                    "value": {
                                        "source": "binding",
                                        "binding": "RAW_NAME",
                                    },
                                }
                            ],
                            "outputs": ["NORMAL_NAME"],
                        }
                    ],
                },
                {
                    "part": "processes",
                    "id": "parallel-search",
                    "name": "Search sources",
                    "steps": [
                        {
                            "kind": "par",
                            "steps": [
                                {
                                    "kind": "act",
                                    "tool": "tool-a",
                                    "instruction": "Produce <A>.",
                                    "outputs": ["A"],
                                },
                                {
                                    "kind": "act",
                                    "tool": "tool-b",
                                    "instruction": "Produce <B>.",
                                    "outputs": ["B"],
                                },
                            ],
                        },
                        {
                            "kind": "join",
                        },
                    ],
                },
            ]
        }
    )
    part: Literal["processes"] = Field(
        default="processes",
        description="The entry part discriminator.",
        examples=["processes"],
    )
    name: ProcessName = Field(
        description="The two-word process display name.",
        examples=["Write OAK", "Route command"],
    )
    input: SchemaTarget | None = Field(
        default=None,
        description="The optional schema that defines initial local bindings.",
        examples=["schema.raw-name"],
    )
    output: SchemaTarget | None = Field(
        default=None,
        description="The optional schema that defines successful local outputs.",
        examples=["schema.normal-name"],
    )
    steps: list[Step] = Field(
        min_length=1,
        description="The typed process steps in authored order.",
        examples=[
            [
                {
                    "kind": "act",
                    "instruction": "Write the knowledge.",
                }
            ]
        ],
    )

    @model_validator(mode="after")
    def control_flow(self) -> Self:
        if self.input is None:
            visible_bindings(
                self.steps,
                set(),
            )
        sequence_always_fails(
            self.steps
        )
        return self


def process_visible_bindings(
    process: Process,
    inputs: set[str],
) -> set[str]:
    """Return every binding visible after successful process completion."""
    return visible_bindings(
        process.steps,
        inputs,
    )


__all__ = [
    "Process",
    "process_visible_bindings",
]
