"""The processes part: typed values, conditions, and ordered steps."""

from __future__ import annotations

from collections import Counter
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, JsonValue, model_validator
from pydantic_core import PydanticCustomError

from oak.base import DiscriminatedModel, Entry, OakModel
from oak.vocabulary import IriId, NonBlankLine, Placeholder
from oak.vocabulary.text.placeholder import placeholders_in


class ValueModel(DiscriminatedModel):
    """One tagged source for a process value."""

    discriminator_field = "source"


class LiteralValue(ValueModel):
    """One authored JSON value."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "literal",
                    "value": "critical",
                }
            ]
        }
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
    """One value read from a constant entry."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "constant",
                    "constant": "oak:constant/policy",
                }
            ]
        }
    )

    source: Literal["constant"] = Field(
        default="constant",
        description="The process value source discriminator.",
        examples=["constant"],
    )
    constant: IriId = Field(
        description="The constant entry to read.",
        examples=["oak:constant/policy"],
    )


class StateValue(ValueModel):
    """One value read from a state entry."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "state",
                    "state": "oak:state/status",
                }
            ]
        }
    )

    source: Literal["state"] = Field(
        default="state",
        description="The process value source discriminator.",
        examples=["state"],
    )
    state: IriId = Field(
        description="The state entry to read.",
        examples=["oak:state/status"],
    )


class InterfaceValue(ValueModel):
    """One placeholder value read from an active input interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "interface",
                    "interface": "oak:interface/request",
                    "placeholder": "REQUEST",
                }
            ]
        }
    )

    source: Literal["interface"] = Field(
        default="interface",
        description="The process value source discriminator.",
        examples=["interface"],
    )
    interface: IriId = Field(
        description="The active input interface to read.",
        examples=["oak:interface/request"],
    )
    placeholder: Placeholder = Field(
        description="The interface schema placeholder to read.",
        examples=["REQUEST"],
    )


class BindingValue(ValueModel):
    """One value read from a prior process-local binding."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "binding",
                    "binding": "RESULT",
                }
            ]
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
    LiteralValue | ConstantValue | StateValue | InterfaceValue | BindingValue,
    Field(discriminator="source"),
]


class ValueBinding(OakModel):
    """One placeholder bound to one process value."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "placeholder": "REQUEST",
                    "value": {
                        "source": "interface",
                        "interface": "oak:interface/request",
                        "placeholder": "REQUEST",
                    },
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
        examples=[
            {
                "source": "literal",
                "value": "ready",
            },
            {
                "source": "binding",
                "binding": "RESULT",
            },
        ],
    )


ConditionOperator = Literal["equals", "not_equals"]


class Condition(OakModel):
    """One comparison that selects an if branch."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "left": {
                        "source": "state",
                        "state": "oak:state/status",
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

    left: Value = Field(
        description="The value on the left of the comparison.",
        examples=[
            {
                "source": "state",
                "state": "oak:state/status",
            }
        ],
    )
    operator: ConditionOperator = Field(
        description="The structural JSON comparison operator.",
        examples=["equals", "not_equals"],
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


class StepModel(DiscriminatedModel):
    """One tagged process step."""

    discriminator_field = "kind"


class Act(StepModel):
    """One open-ended action with declared inputs and outputs."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "act",
                    "instruction": "Turn <REQUEST> into <RESULT>.",
                    "inputs": [
                        {
                            "placeholder": "REQUEST",
                            "value": {
                                "source": "interface",
                                "interface": "oak:interface/request",
                                "placeholder": "REQUEST",
                            },
                        }
                    ],
                    "outputs": ["RESULT"],
                }
            ]
        }
    )

    kind: Literal["act"] = Field(
        default="act",
        description="The process step discriminator.",
        examples=["act"],
    )
    instruction: NonBlankLine = Field(
        description="The action the interpreter performs.",
        examples=["Turn <REQUEST> into <RESULT>."],
    )
    inputs: list[ValueBinding] = Field(
        default_factory=list,
        description="The action input bindings in authored order.",
        examples=[
            [
                {
                    "placeholder": "REQUEST",
                    "value": {
                        "source": "interface",
                        "interface": "oak:interface/request",
                        "placeholder": "REQUEST",
                    },
                }
            ]
        ],
    )
    outputs: list[Placeholder] = Field(
        default_factory=list,
        description="The immutable local bindings the action must produce.",
        examples=[["RESULT"]],
    )

    @model_validator(mode="after")
    def placeholders(self) -> Self:
        input_names = [item.placeholder for item in self.inputs]
        output_names = list(self.outputs)
        duplicate_inputs = sorted(
            name for name, count in Counter(input_names).items() if count > 1
        )
        if duplicate_inputs:
            raise PydanticCustomError(
                "duplicate_act_input",
                "act repeats input placeholders: {placeholders}",
                {"placeholders": ", ".join(duplicate_inputs)},
            )
        duplicate_outputs = sorted(
            name for name, count in Counter(output_names).items() if count > 1
        )
        if duplicate_outputs:
            raise PydanticCustomError(
                "duplicate_act_output",
                "act repeats output placeholders: {placeholders}",
                {"placeholders": ", ".join(duplicate_outputs)},
            )
        overlap = sorted(set(input_names) & set(output_names))
        if overlap:
            raise PydanticCustomError(
                "act_binding_overlap",
                "act uses placeholders as both inputs and outputs: {placeholders}",
                {"placeholders": ", ".join(overlap)},
            )
        declared = set(input_names) | set(output_names)
        used = placeholders_in(self.instruction)
        missing = sorted(used - declared)
        unused = sorted(declared - used)
        if missing or unused:
            raise PydanticCustomError(
                "act_placeholder_mismatch",
                "act instruction and bindings differ; missing: {missing}; unused: {unused}",
                {
                    "missing": ", ".join(missing) or "none",
                    "unused": ", ".join(unused) or "none",
                },
            )
        return self


class Set(StepModel):
    """One state write."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "set",
                    "state": "oak:state/status",
                    "value": {
                        "source": "literal",
                        "value": "complete",
                    },
                }
            ]
        }
    )

    kind: Literal["set"] = Field(
        default="set",
        description="The process step discriminator.",
        examples=["set"],
    )
    state: IriId = Field(
        description="The state entry to write.",
        examples=["oak:state/status"],
    )
    value: Value = Field(
        description="The process value written to the state entry.",
        examples=[
            {
                "source": "literal",
                "value": "complete",
            }
        ],
    )


class Emit(StepModel):
    """One schema instance emitted through one output interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "emit",
                    "interface": "oak:interface/result",
                    "bindings": [
                        {
                            "placeholder": "RESULT",
                            "value": {
                                "source": "binding",
                                "binding": "RESULT",
                            },
                        }
                    ],
                }
            ]
        }
    )

    kind: Literal["emit"] = Field(
        default="emit",
        description="The process step discriminator.",
        examples=["emit"],
    )
    interface: IriId = Field(
        description="The output interface that carries the schema instance.",
        examples=["oak:interface/result"],
    )
    bindings: list[ValueBinding] = Field(
        min_length=1,
        description="One value binding for each interface schema placeholder.",
        examples=[
            [
                {
                    "placeholder": "RESULT",
                    "value": {
                        "source": "binding",
                        "binding": "RESULT",
                    },
                }
            ]
        ],
    )

    @model_validator(mode="after")
    def placeholders(self) -> Self:
        names = [item.placeholder for item in self.bindings]
        duplicates = sorted(
            name for name, count in Counter(names).items() if count > 1
        )
        if duplicates:
            raise PydanticCustomError(
                "duplicate_emit_placeholder",
                "emit repeats placeholders: {placeholders}",
                {"placeholders": ", ".join(duplicates)},
            )
        return self


class Call(StepModel):
    """One synchronous process invocation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "call",
                    "process": "oak:process/finalize",
                }
            ]
        }
    )

    kind: Literal["call"] = Field(
        default="call",
        description="The process step discriminator.",
        examples=["call"],
    )
    process: IriId = Field(
        description="The process entry to invoke synchronously.",
        examples=["oak:process/finalize"],
    )


class Fail(StepModel):
    """One explicit process failure."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "fail",
                    "message": "The result is empty.",
                }
            ]
        }
    )

    kind: Literal["fail"] = Field(
        default="fail",
        description="The process step discriminator.",
        examples=["fail"],
    )
    message: NonBlankLine = Field(
        description="The failure message.",
        examples=["The result is empty."],
    )


class If(StepModel):
    """One condition with a required then branch and an optional otherwise branch."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "if",
                    "condition": {
                        "left": {
                            "source": "state",
                            "state": "oak:state/status",
                        },
                        "operator": "equals",
                        "right": {
                            "source": "literal",
                            "value": "ready",
                        },
                    },
                    "then": [
                        {
                            "kind": "set",
                            "state": "oak:state/status",
                            "value": {
                                "source": "literal",
                                "value": "complete",
                            },
                        }
                    ],
                    "otherwise": [
                        {
                            "kind": "fail",
                            "message": "The state is not ready.",
                        }
                    ],
                }
            ]
        }
    )

    kind: Literal["if"] = Field(
        default="if",
        description="The process step discriminator.",
        examples=["if"],
    )
    condition: Condition = Field(
        description="The comparison that selects the branch.",
        examples=[
            {
                "left": {
                    "source": "state",
                    "state": "oak:state/status",
                },
                "operator": "equals",
                "right": {
                    "source": "literal",
                    "value": "ready",
                },
            }
        ],
    )
    then: list[Step] = Field(
        min_length=1,
        description="The steps run when the condition is true.",
        examples=[
            [
                {
                    "kind": "set",
                    "state": "oak:state/status",
                    "value": {
                        "source": "literal",
                        "value": "complete",
                    },
                }
            ]
        ],
    )
    otherwise: list[Step] | None = Field(
        default=None,
        min_length=1,
        description="The steps run when the condition is false.",
        examples=[
            [
                {
                    "kind": "fail",
                    "message": "The state is not ready.",
                }
            ]
        ],
    )


Step = Annotated[
    Act | Set | Emit | If | Call | Fail,
    Field(discriminator="kind"),
]

If.model_rebuild(_types_namespace={"Step": Step})


def _step_values(step: Step) -> list[Value]:
    if isinstance(step, Act):
        return [binding.value for binding in step.inputs]
    if isinstance(step, Set):
        return [step.value]
    if isinstance(step, Emit):
        return [binding.value for binding in step.bindings]
    if isinstance(step, If):
        return [step.condition.left, step.condition.right]
    return []


def _validate_bindings(steps: list[Step], visible: set[str]) -> None:
    for step in steps:
        for value in _step_values(step):
            if isinstance(value, BindingValue) and value.binding not in visible:
                raise PydanticCustomError(
                    "unbound_process_binding",
                    "process reads unbound local binding {binding}",
                    {"binding": value.binding},
                )
        if isinstance(step, Act):
            redefined = sorted(set(step.outputs) & visible)
            if redefined:
                raise PydanticCustomError(
                    "process_binding_redefined",
                    "process redefines visible local bindings: {bindings}",
                    {"bindings": ", ".join(redefined)},
                )
            visible.update(step.outputs)
        elif isinstance(step, If):
            _validate_bindings(step.then, set(visible))
            if step.otherwise is not None:
                _validate_bindings(step.otherwise, set(visible))


def _sequence_always_fails(steps: list[Step]) -> bool:
    for index, step in enumerate(steps):
        always_fails = isinstance(step, Fail)
        if isinstance(step, If):
            then_fails = _sequence_always_fails(step.then)
            otherwise_fails = (
                step.otherwise is not None
                and _sequence_always_fails(step.otherwise)
            )
            always_fails = then_fails and otherwise_fails
        if always_fails:
            if index + 1 < len(steps):
                raise PydanticCustomError(
                    "unreachable_process_step",
                    "a process step follows a path that always fails",
                )
            return True
    return False


class Process(Entry):
    """One named ordered way to do a task."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "processes",
                    "id": "oak:process/write-oak",
                    "name": "Write OAK",
                    "steps": [
                        {
                            "kind": "act",
                            "instruction": "Write the knowledge.",
                        }
                    ],
                }
            ]
        }
    )

    part: Literal["processes"] = Field(
        default="processes",
        description="The entry part discriminator.",
        examples=["processes"],
    )
    name: NonBlankLine = Field(
        description="The process display name.",
        examples=["Write OAK"],
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
        _validate_bindings(self.steps, set())
        _sequence_always_fails(self.steps)
        return self
