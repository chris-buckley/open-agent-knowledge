"""Process value models and placeholder bindings."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import ConfigDict, Field, JsonValue

from oak.base import DiscriminatedModel, OakModel
from oak.node.parts.processes.targets import ConstantTarget, StateTarget
from oak.vocabulary.text.placeholder import Placeholder


class ValueModel(DiscriminatedModel):
    """One tagged source for a process value."""

    discriminator_field = "source"


class LiteralValue(ValueModel):
    """One authored JSON value."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"source": "literal", "value": "critical"}]}
    )
    source: Literal["literal"] = Field(
        default="literal",
        description="The process value source discriminator.",
        examples=["literal"],
    )
    value: JsonValue = Field(
        description="The authored JSON value.",
        examples=["critical", 3, {"ready": True}],
    )


class ConstantValue(ValueModel):
    """One value read from a local or relative constant entry."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"source": "constant", "constant": "constant.policy"}]
        }
    )
    source: Literal["constant"] = Field(
        default="constant",
        description="The process value source discriminator.",
        examples=["constant"],
    )
    constant: ConstantTarget = Field(
        description="The local or relative constant target to read.",
        examples=["constant.policy"],
    )


class StateValue(ValueModel):
    """One value read from local state."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"source": "state", "state": "state.status"}]
        }
    )
    source: Literal["state"] = Field(
        default="state",
        description="The process value source discriminator.",
        examples=["state"],
    )
    state: StateTarget = Field(
        description="The local state target to read.",
        examples=["state.status"],
    )


class BindingValue(ValueModel):
    """One value read from a visible process-local binding."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"source": "binding", "binding": "RESULT"}]
        }
    )
    source: Literal["binding"] = Field(
        default="binding",
        description="The process value source discriminator.",
        examples=["binding"],
    )
    binding: Placeholder = Field(
        description="The visible process-local binding to read.",
        examples=["RESULT"],
    )


Value = Annotated[
    LiteralValue | ConstantValue | StateValue | BindingValue,
    Field(discriminator="source"),
]


class ValueBinding(OakModel):
    """One placeholder bound to one process value."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "placeholder": "REQUEST",
                    "value": {"source": "binding", "binding": "REQUEST"},
                }
            ]
        }
    )
    placeholder: Placeholder = Field(
        description="The placeholder receiving the process value.",
        examples=["REQUEST"],
    )
    value: Value = Field(
        description="The process value bound to the placeholder.",
        examples=[{"source": "literal", "value": "ready"}],
    )


__all__ = [
    "BindingValue",
    "ConstantValue",
    "LiteralValue",
    "StateValue",
    "Value",
    "ValueBinding",
    "ValueModel",
]
