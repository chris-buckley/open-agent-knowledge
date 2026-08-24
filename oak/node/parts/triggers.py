"""The triggers part."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.parts.processes import (
    BindingValue,
    Condition,
    InterfaceValue,
    StateValue,
)
from oak.vocabulary import NonBlankLine, SlugId


class Trigger(Entry):
    """One arrival reason, optional state guard, and selected process."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "triggers",
                    "id": "write-oak-trigger",
                    "given": {
                        "left": {
                            "source": "state",
                            "state": "status",
                        },
                        "operator": "equals",
                        "right": {
                            "source": "literal",
                            "value": "ready",
                        },
                    },
                    "when": "The interpreter arrives to write OAK.",
                    "process": "write-oak",
                }
            ]
        }
    )

    part: Literal["triggers"] = Field(
        default="triggers",
        description="The entry part discriminator.",
        examples=["triggers"],
    )
    given: Condition | None = Field(
        default=None,
        description="The optional state condition checked after when matches.",
        examples=[
            {
                "left": {
                    "source": "state",
                    "state": "status",
                },
                "operator": "equals",
                "right": {
                    "source": "literal",
                    "value": "ready",
                },
            }
        ],
    )
    when: NonBlankLine = Field(
        description="Why the interpreter enters the knowledge.",
        examples=["The interpreter arrives to write OAK."],
    )
    process: SlugId = Field(
        description="The process entry selected by the trigger.",
        examples=["write-oak"],
    )

    @model_validator(mode="after")
    def guard(self) -> Self:
        if self.given is None:
            return self
        values = (self.given.left, self.given.right)
        if any(isinstance(value, (InterfaceValue, BindingValue)) for value in values):
            raise PydanticCustomError(
                "invalid_trigger_guard_value",
                "trigger guard cannot read an interface or local binding",
            )
        if not any(isinstance(value, StateValue) for value in values):
            raise PydanticCustomError(
                "trigger_guard_missing_state",
                "trigger guard must read at least one state value",
            )
        return self
