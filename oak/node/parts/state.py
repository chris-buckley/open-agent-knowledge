"""The state part."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, JsonValue, model_validator

from oak.base import Entry
from oak.node.parts.interfaces import SchemaTarget
from oak.rules.validation import rule_error
from oak.vocabulary.text.placeholder import Placeholder


class State(Entry):
    """One JSON value that can change while the interpreter runs."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "state",
                    "id": "status",
                    "value": "ready",
                }
            ]
        }
    )

    part: Literal["state"] = Field(
        default="state",
        description="The entry part discriminator.",
        examples=["state"],
    )
    schema_id: SchemaTarget | None = Field(
        default=None,
        alias="schema",
        title="Schema",
        description="The optional local or relative schema target whose placeholder constrains every value.",
        examples=["schema.scaling"],
    )
    placeholder: Placeholder | None = Field(
        default=None,
        description="The schema placeholder every value must satisfy.",
        examples=["BALANCE"],
    )
    value: JsonValue = Field(
        description="The JSON value that can change.",
        examples=["ready", 0, {"complete": False}],
    )

    @model_validator(mode="after")
    def valid_binding(self) -> Self:
        if (self.schema_id is None) != (self.placeholder is None):
            raise rule_error(
                "incomplete_schema_binding",
                "a schema binding needs both a schema target and a placeholder",
            )
        return self
