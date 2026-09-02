"""Reusable repository paths, model fixtures, and comparison helpers."""

from __future__ import annotations

from pathlib import Path

from oak.base import OakModel
from oak.node.model import Node
from oak.node.parts.instructions import Instruction
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act
from oak.node.parts.processes.values import BindingValue, ValueBinding
from oak.node.parts.schemas.constraints import NonEmpty, Type
from oak.node.parts.schemas.model import Schema, where

ROOT = Path(__file__).resolve().parents[2]


def normalized(value: OakModel) -> object:
    """Return one model dump with generated instruction ids removed."""
    data = value.model_dump(
        mode="json",
        by_alias=True,
    )

    if isinstance(value, Instruction):
        data.pop("id", None)

    if isinstance(value, Node):
        for instruction in data.get("instructions", []):
            instruction.pop("id", None)

    return data


def contract_schemas() -> tuple[Schema, Schema]:
    """Return the shared raw-name and normal-name contract schemas."""
    return (
        Schema(
            id="raw-name",
            template="<RAW_NAME>",
            where=[
                where(
                    "RAW_NAME",
                    Type(of="string"),
                    NonEmpty(),
                )
            ],
        ),
        Schema(
            id="normal-name",
            template="<NORMAL_NAME>",
            where=[
                where(
                    "NORMAL_NAME",
                    Type(of="string"),
                    NonEmpty(),
                )
            ],
        ),
    )


def normalise_process() -> Process:
    """Return the shared typed name-normalisation process."""
    return Process(
        id="normalise",
        name="Normalise name",
        input="schema.raw-name",
        output="schema.normal-name",
        steps=[
            Act(
                instruction="Normalise <RAW_NAME> into <NORMAL_NAME>.",
                inputs=[
                    ValueBinding(
                        placeholder="RAW_NAME",
                        value=BindingValue(binding="RAW_NAME"),
                    )
                ],
                outputs=["NORMAL_NAME"],
            )
        ],
    )


__all__ = [
    "ROOT",
    "contract_schemas",
    "normalise_process",
    "normalized",
]
