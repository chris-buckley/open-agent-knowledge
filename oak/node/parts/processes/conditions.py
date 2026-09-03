"""Recursive process condition models and value traversal."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from oak.base import DiscriminatedModel
from oak.node.parts.processes.operators import ConditionOperator
from oak.node.parts.processes.values import Value


class ConditionModel(DiscriminatedModel):
    """One tagged recursive condition."""

    discriminator_field = "kind"


class Compare(ConditionModel):
    """One strict structural or ordered comparison."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "compare",
                    "left": {
                        "source": "state",
                        "state": "state.status",
                    },
                    "operator": "equals",
                    "right": {
                        "source": "literal",
                        "value": "ready",
                    },
                }
            ]
        }
    )
    kind: Literal["compare"] = Field(
        default="compare",
        description="The condition discriminator.",
        examples=["compare"],
    )
    left: Value = Field(
        description="The value on the left of the comparison.",
        examples=[
            {
                "source": "state",
                "state": "state.status",
            }
        ],
    )
    operator: ConditionOperator = Field(
        description="The strict comparison operator.",
        examples=["equals", "greater_than"],
    )
    right: Value = Field(
        description="The value on the right of the comparison.",
        examples=[
            {
                "source": "literal",
                "value": "ready",
            }
        ],
    )


class All(ConditionModel):
    """Every child condition must be true in authored order."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "all",
                    "conditions": [
                        {
                            "kind": "compare",
                            "left": {
                                "source": "state",
                                "state": "state.status",
                            },
                            "operator": "equals",
                            "right": {
                                "source": "literal",
                                "value": "ready",
                            },
                        },
                        {
                            "kind": "compare",
                            "left": {
                                "source": "state",
                                "state": "state.count",
                            },
                            "operator": "greater_than",
                            "right": {
                                "source": "literal",
                                "value": 0,
                            },
                        },
                    ],
                }
            ]
        }
    )
    kind: Literal["all"] = Field(
        default="all",
        description="The condition discriminator.",
        examples=["all"],
    )
    conditions: list[Condition] = Field(
        description="The child conditions in authored order.",
        examples=[[]],
    )

    @model_validator(mode="after")
    def length(self) -> Self:
        if len(self.conditions) < 2:
            raise PydanticCustomError(
                "condition_group_too_short",
                "ALL needs at least two conditions",
            )
        return self


class Any(ConditionModel):
    """At least one child condition must be true in authored order."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "any",
                    "conditions": [
                        {
                            "kind": "compare",
                            "left": {
                                "source": "state",
                                "state": "state.status",
                            },
                            "operator": "equals",
                            "right": {
                                "source": "literal",
                                "value": "ready",
                            },
                        },
                        {
                            "kind": "compare",
                            "left": {
                                "source": "state",
                                "state": "state.override",
                            },
                            "operator": "equals",
                            "right": {
                                "source": "literal",
                                "value": True,
                            },
                        },
                    ],
                }
            ]
        }
    )
    kind: Literal["any"] = Field(
        default="any",
        description="The condition discriminator.",
        examples=["any"],
    )
    conditions: list[Condition] = Field(
        description="The child conditions in authored order.",
        examples=[[]],
    )

    @model_validator(mode="after")
    def length(self) -> Self:
        if len(self.conditions) < 2:
            raise PydanticCustomError(
                "condition_group_too_short",
                "ANY needs at least two conditions",
            )
        return self


class Not(ConditionModel):
    """One child condition whose result is inverted."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "not",
                    "condition": {
                        "kind": "compare",
                        "left": {
                            "source": "state",
                            "state": "state.status",
                        },
                        "operator": "equals",
                        "right": {
                            "source": "literal",
                            "value": "closed",
                        },
                    },
                }
            ]
        }
    )
    kind: Literal["not"] = Field(
        default="not",
        description="The condition discriminator.",
        examples=["not"],
    )
    condition: Condition = Field(
        description="The child condition to invert.",
        examples=[
            {
                "kind": "compare",
                "left": {
                    "source": "state",
                    "state": "state.status",
                },
                "operator": "equals",
                "right": {
                    "source": "literal",
                    "value": "closed",
                },
            }
        ],
    )


Condition = Annotated[
    Compare | All | Any | Not,
    Field(discriminator="kind"),
]

All.model_rebuild(_types_namespace={"Condition": Condition})
Any.model_rebuild(_types_namespace={"Condition": Condition})
Not.model_rebuild(_types_namespace={"Condition": Condition})


def condition_values(condition: Condition) -> list[Value]:
    """Return every process value read by one recursive condition."""
    if isinstance(condition, Compare):
        return [condition.left, condition.right]
    if isinstance(condition, (All, Any)):
        return [
            value
            for child in condition.conditions
            for value in condition_values(child)
        ]
    if isinstance(condition, Not):
        return condition_values(condition.condition)
    raise TypeError(f"unsupported condition {type(condition).__name__}")


__all__ = [
    "All",
    "Any",
    "Compare",
    "Condition",
    "ConditionModel",
    "Not",
    "condition_values",
]
