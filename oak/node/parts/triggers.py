"""The triggers part."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.parts.processes import (
    BindingValue,
    Condition,
    InterfaceValue,
    ProcessTarget,
    StateValue,
    ValueBinding,
    condition_values,
)
from oak.rules import rule_error
from oak.vocabulary import NonBlankLine


def validate_trigger_contract(
    trigger: "Trigger",
    inputs: set[str] | None,
) -> None:
    """Validate one trigger against the selected process input schema."""
    authored = [binding.placeholder for binding in trigger.inputs]
    if inputs is None:
        if authored:
            raise rule_error(
                "trigger_contract_mismatch",
                "trigger {trigger} binds inputs but its process has no input schema",
                {"trigger": trigger.id},
            )
        return
    if len(authored) == len(inputs) and set(authored) == inputs:
        return
    raise rule_error(
        "trigger_contract_mismatch",
        (
            "trigger {trigger} inputs differ from the process input schema; "
            "missing: {missing}; unused: {unused}"
        ),
        {
            "trigger": trigger.id,
            "missing": ", ".join(sorted(inputs - set(authored))) or "none",
            "unused": ", ".join(sorted(set(authored) - inputs)) or "none",
        },
    )


class Trigger(Entry):
    """One GIVEN, WHEN, and THEN signpost to a process."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "triggers",
                    "id": "write-oak-trigger",
                    "given": True,
                    "when": "Source material arrives to write OAK.",
                    "then": "process.write-oak",
                },
                {
                    "part": "triggers",
                    "id": "ready-trigger",
                    "given": {
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
                    "when": "A request arrives.",
                    "then": "process.run",
                },
            ]
        }
    )

    part: Literal["triggers"] = Field(
        default="triggers",
        description="The entry part discriminator.",
        examples=["triggers"],
    )
    given: Literal[True] | Condition = Field(
        default=True,
        description="True or the recursive state guard checked after WHEN.",
        examples=[
            True,
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
        ],
    )
    when: NonBlankLine = Field(
        description="Why the interpreter enters the knowledge.",
        examples=["Source material arrives to write OAK."],
    )
    then: ProcessTarget = Field(
        description="The local or relative process target selected by the trigger.",
        examples=[
            "process.write-oak",
            "../shared/processes.oak.md#process.write-oak",
        ],
    )
    inputs: list[ValueBinding] = Field(
        default_factory=list,
        description="The input bindings that seed the selected process input schema.",
        examples=[
            [
                {
                    "placeholder": "REQUEST",
                    "value": {
                        "source": "interface",
                        "interface": "interface.request",
                        "placeholder": "REQUEST",
                    },
                }
            ]
        ],
    )

    @model_validator(mode="after")
    def valid_inputs(self) -> Self:
        if any(
            isinstance(binding.value, BindingValue)
            for binding in self.inputs
        ):
            raise PydanticCustomError(
                "invalid_trigger_input_value",
                "trigger input cannot read a local binding",
            )
        return self

    @model_validator(mode="after")
    def guard(self) -> Self:
        if self.given is True:
            return self

        values = condition_values(self.given)

        if any(
            isinstance(value, (InterfaceValue, BindingValue))
            for value in values
        ):
            raise PydanticCustomError(
                "invalid_trigger_guard_value",
                "trigger guard cannot read an interface or local binding",
            )

        if not any(
            isinstance(value, StateValue)
            for value in values
        ):
            raise PydanticCustomError(
                "trigger_guard_missing_state",
                "trigger guard must read at least one state value",
            )

        return self
