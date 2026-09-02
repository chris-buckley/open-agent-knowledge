"""The triggers part."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.parts.processes import (
    BindingValue,
    Condition,
    InterfaceTarget,
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
    """Validate one trigger seed against the selected process input schema."""
    authored = [binding.placeholder for binding in trigger.seed]
    if inputs is None:
        if authored:
            raise rule_error(
                "trigger_contract_mismatch",
                "trigger {trigger} seeds a process that has no input schema",
                {"trigger": trigger.id},
            )
        return
    if len(authored) == len(inputs) and set(authored) == inputs:
        return
    raise rule_error(
        "trigger_contract_mismatch",
        (
            "trigger {trigger} seeds differ from the process input schema; "
            "missing: {missing}; unused: {unused}"
        ),
        {
            "trigger": trigger.id,
            "missing": ", ".join(sorted(inputs - set(authored))) or "none",
            "unused": ", ".join(sorted(set(authored) - inputs)) or "none",
        },
    )


class Trigger(Entry):
    """One outside event routed to one process."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "triggers",
                    "id": "write-oak-trigger",
                    "event": "Source material arrives to write OAK.",
                    "process": "process.write-oak",
                },
                {
                    "part": "triggers",
                    "id": "ready-trigger",
                    "event": "A request arrives.",
                    "source": "interface.request",
                    "guard": {
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
                    "process": "process.run",
                    "seed": [
                        {
                            "placeholder": "REQUEST",
                            "value": {
                                "source": "interface",
                                "interface": "interface.request",
                                "placeholder": "REQUEST",
                            },
                        }
                    ],
                },
            ]
        }
    )

    part: Literal["triggers"] = Field(
        default="triggers",
        description="The entry part discriminator.",
        examples=["triggers"],
    )
    event: NonBlankLine = Field(
        description=(
            "The semantic signpost matched exactly "
            "when the trigger has no source."
        ),
        examples=["Source material arrives to write OAK."],
    )
    source: InterfaceTarget | None = Field(
        default=None,
        description=(
            "The optional local in or inout interface whose arrival "
            "fires the trigger."
        ),
        examples=["interface.request"],
    )
    guard: Literal[True] | Condition = Field(
        default=True,
        description="True or the recursive state guard checked after the match.",
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
    process: ProcessTarget = Field(
        description="The local or relative process target selected by the trigger.",
        examples=[
            "process.write-oak",
            "../shared/processes.oak.md#process.write-oak",
        ],
    )
    seed: list[ValueBinding] = Field(
        default_factory=list,
        description="The seed bindings that fill the selected process input schema.",
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
    def valid_seed(self) -> Self:
        if any(
            isinstance(binding.value, BindingValue)
            for binding in self.seed
        ):
            raise PydanticCustomError(
                "invalid_trigger_seed_value",
                "trigger seed cannot read a local binding",
            )
        return self

    @model_validator(mode="after")
    def valid_guard(self) -> Self:
        if self.guard is True:
            return self

        values = condition_values(self.guard)

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
