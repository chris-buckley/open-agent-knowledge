"""Process step models and direct value traversal."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, PositiveInt, model_validator
from pydantic_core import PydanticCustomError

from oak.base import DiscriminatedModel
from oak.node.parts.interfaces import SchemaTarget
from oak.node.parts.processes.conditions import Condition, condition_values
from oak.node.parts.processes.targets import (
    InterfaceTarget,
    ProcessTarget,
    StateTarget,
)
from oak.node.parts.processes.values import Value, ValueBinding
from oak.vocabulary import NonBlankLine, Placeholder
from oak.vocabulary.text.placeholder import placeholders_in


class StepModel(DiscriminatedModel):
    """One tagged process step."""

    discriminator_field = "kind"


class Act(StepModel):
    """One interpreter-native or exact named-tool action."""

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
                                "interface": "interface.request",
                                "placeholder": "REQUEST",
                            },
                        }
                    ],
                    "outputs": ["RESULT"],
                },
                {
                    "kind": "act",
                    "tool": "mcp__docs__search",
                    "input": "schema.query",
                    "output": "schema.result",
                    "instruction": "Find <QUERY> and return <RESULT>.",
                    "inputs": [
                        {
                            "placeholder": "QUERY",
                            "value": {
                                "source": "literal",
                                "value": "OAK",
                            },
                        }
                    ],
                    "outputs": ["RESULT"],
                },
            ]
        }
    )
    kind: Literal["act"] = Field(
        default="act",
        description="The process step discriminator.",
        examples=["act"],
    )
    tool: NonBlankLine | None = Field(
        default=None,
        description="The exact host tool name, or null for interpreter-native work.",
        examples=["mcp__docs__search"],
    )
    input: SchemaTarget | None = Field(
        default=None,
        description="The optional schema that validates the resolved input values before invocation.",
        examples=["schema.query"],
    )
    output: SchemaTarget | None = Field(
        default=None,
        description="The optional schema that validates the produced outputs before promotion.",
        examples=["schema.result"],
    )
    instruction: NonBlankLine = Field(
        description="The action the interpreter or exact tool performs.",
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
                        "interface": "interface.request",
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
    def reserved_prefix(self) -> Self:
        if self.instruction.startswith(('input="', 'output="')):
            raise PydanticCustomError(
                "invalid_act_instruction",
                "an act instruction cannot start with an act schema attribute",
            )
        return self

    @model_validator(mode="after")
    def placeholders(self) -> Self:
        input_names = [
            item.placeholder
            for item in self.inputs
        ]
        output_names = list(self.outputs)
        duplicate_inputs = sorted(
            name
            for name, count in Counter(input_names).items()
            if count > 1
        )
        duplicate_outputs = sorted(
            name
            for name, count in Counter(output_names).items()
            if count > 1
        )

        if duplicate_inputs:
            raise PydanticCustomError(
                "duplicate_act_input",
                "act repeats input placeholders: {placeholders}",
                {
                    "placeholders": ", ".join(
                        duplicate_inputs
                    )
                },
            )

        if duplicate_outputs:
            raise PydanticCustomError(
                "duplicate_act_output",
                "act repeats output placeholders: {placeholders}",
                {
                    "placeholders": ", ".join(
                        duplicate_outputs
                    )
                },
            )

        overlap = sorted(
            set(input_names)
            & set(output_names)
        )

        if overlap:
            raise PydanticCustomError(
                "act_binding_overlap",
                "act uses placeholders as both inputs and outputs: {placeholders}",
                {
                    "placeholders": ", ".join(
                        overlap
                    )
                },
            )

        declared = (
            set(input_names)
            | set(output_names)
        )
        used = placeholders_in(
            self.instruction
        )
        missing = sorted(
            used - declared
        )
        unused = sorted(
            declared - used
        )

        if missing or unused:
            raise PydanticCustomError(
                "act_placeholder_mismatch",
                (
                    "act instruction and bindings differ; "
                    "missing: {missing}; unused: {unused}"
                ),
                {
                    "missing": (
                        ", ".join(missing)
                        or "none"
                    ),
                    "unused": (
                        ", ".join(unused)
                        or "none"
                    ),
                },
            )

        return self


class Set(StepModel):
    """One local state write."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "set",
                    "state": "state.status",
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
    state: StateTarget = Field(
        description="The local state target to write.",
        examples=["state.status"],
    )
    value: Value = Field(
        description="The process value written to state.",
        examples=[
            {
                "source": "literal",
                "value": "complete",
            }
        ],
    )


class Emit(StepModel):
    """One schema instance emitted through one local output interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "emit",
                    "interface": "interface.result",
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
    interface: InterfaceTarget = Field(
        description="The local output interface target.",
        examples=["interface.result"],
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
        names = [
            item.placeholder
            for item in self.bindings
        ]
        duplicates = sorted(
            name
            for name, count in Counter(names).items()
            if count > 1
        )

        if duplicates:
            raise PydanticCustomError(
                "duplicate_emit_placeholder",
                "emit repeats placeholders: {placeholders}",
                {
                    "placeholders": ", ".join(
                        duplicates
                    )
                },
            )

        return self


class If(StepModel):
    """One recursive condition with a then branch and optional else branch."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "if",
                    "condition": {
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
                    "then": [
                        {
                            "kind": "set",
                            "state": "state.status",
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
        description="The recursive condition that selects the branch.",
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
                    "kind": "fail",
                    "message": "Example failure.",
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
                    "message": "Example failure.",
                }
            ]
        ],
    )


class Call(StepModel):
    """One synchronous process invocation with schema-bound inputs and outputs."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "call",
                    "process": "process.normalise",
                    "inputs": [
                        {
                            "placeholder": "RAW_NAME",
                            "value": {
                                "source": "literal",
                                "value": " ada ",
                            },
                        }
                    ],
                    "outputs": ["NORMAL_NAME"],
                },
                {
                    "kind": "call",
                    "process": "../shared/processes.oak.md#process.finalize",
                },
            ]
        }
    )
    kind: Literal["call"] = Field(
        default="call",
        description="The process step discriminator.",
        examples=["call"],
    )
    process: ProcessTarget = Field(
        description="The local or relative process target to invoke.",
        examples=["process.normalise"],
    )
    inputs: list[ValueBinding] = Field(
        default_factory=list,
        description="The called process input bindings in authored order.",
        examples=[
            [
                {
                    "placeholder": "RAW_NAME",
                    "value": {
                        "source": "literal",
                        "value": " ada ",
                    },
                }
            ]
        ],
    )
    outputs: list[Placeholder] = Field(
        default_factory=list,
        description="The called process outputs promoted to this process.",
        examples=[["NORMAL_NAME"]],
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


class Assert(StepModel):
    """One required condition that aborts the transaction when false."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "assert",
                    "condition": {
                        "kind": "compare",
                        "left": {
                            "source": "binding",
                            "binding": "RESULT",
                        },
                        "operator": "not_equals",
                        "right": {
                            "source": "literal",
                            "value": "",
                        },
                    },
                    "message": "The result must not be empty.",
                }
            ]
        }
    )
    kind: Literal["assert"] = Field(
        default="assert",
        description="The process step discriminator.",
        examples=["assert"],
    )
    condition: Condition = Field(
        description="The required recursive condition.",
        examples=[
            {
                "kind": "compare",
                "left": {
                    "source": "binding",
                    "binding": "RESULT",
                },
                "operator": "not_equals",
                "right": {
                    "source": "literal",
                    "value": "",
                },
            }
        ],
    )
    message: NonBlankLine | None = Field(
        default=None,
        description="The optional assertion failure message.",
        examples=["The result must not be empty."],
    )


class Foreach(StepModel):
    """One deterministic sequential iteration over a JSON list."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "foreach",
                    "binding": "ITEM",
                    "value": {
                        "source": "literal",
                        "value": ["a", "b"],
                    },
                    "steps": [
                        {
                            "kind": "act",
                            "instruction": "Transform <ITEM> into <RESULT>.",
                            "inputs": [
                                {
                                    "placeholder": "ITEM",
                                    "value": {
                                        "source": "binding",
                                        "binding": "ITEM",
                                    },
                                }
                            ],
                            "outputs": ["RESULT"],
                        }
                    ],
                }
            ]
        }
    )
    kind: Literal["foreach"] = Field(
        default="foreach",
        description="The process step discriminator.",
        examples=["foreach"],
    )
    binding: Placeholder = Field(
        description="The immutable loop binding.",
        examples=["ITEM"],
    )
    value: Value = Field(
        description="The process value that must resolve to a JSON list.",
        examples=[
            {
                "source": "literal",
                "value": ["a", "b"],
            }
        ],
    )
    steps: list[Step] = Field(
        min_length=1,
        description="The sequential iteration steps.",
        examples=[
            [
                {
                    "kind": "fail",
                    "message": "Example failure.",
                }
            ]
        ],
    )


class While(StepModel):
    """One bounded pre-test loop over a recursive condition."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "while",
                    "condition": {
                        "kind": "compare",
                        "left": {
                            "source": "state",
                            "state": "state.status",
                        },
                        "operator": "not_equals",
                        "right": {
                            "source": "literal",
                            "value": "complete",
                        },
                    },
                    "limit": 10,
                    "steps": [
                        {
                            "kind": "set",
                            "state": "state.status",
                            "value": {
                                "source": "literal",
                                "value": "complete",
                            },
                        }
                    ],
                }
            ]
        }
    )
    kind: Literal["while"] = Field(
        default="while",
        description="The process step discriminator.",
        examples=["while"],
    )
    condition: Condition = Field(
        description="The recursive condition tested before every iteration.",
        examples=[
            {
                "kind": "compare",
                "left": {
                    "source": "state",
                    "state": "state.status",
                },
                "operator": "not_equals",
                "right": {
                    "source": "literal",
                    "value": "complete",
                },
            }
        ],
    )
    limit: PositiveInt = Field(
        description="The hard maximum number of iterations.",
        examples=[10],
    )
    steps: list[Step] = Field(
        min_length=1,
        description="The steps run in one fresh child binding scope per iteration.",
        examples=[
            [
                {
                    "kind": "set",
                    "state": "state.status",
                    "value": {
                        "source": "literal",
                        "value": "complete",
                    },
                }
            ]
        ],
    )


class Par(StepModel):
    """One deterministic group of exact named-tool acts."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
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
                }
            ]
        }
    )
    kind: Literal["par"] = Field(
        default="par",
        description="The process step discriminator.",
        examples=["par"],
    )
    steps: list[Step] = Field(
        min_length=1,
        description="The exact named-tool acts launched in authored order.",
        examples=[
            [
                {
                    "kind": "act",
                    "tool": "tool-a",
                    "instruction": "Produce <A>.",
                    "outputs": ["A"],
                }
            ]
        ],
    )

    @model_validator(mode="after")
    def parallel_steps(self) -> Self:
        acts: list[Act] = []

        for step in self.steps:
            if not isinstance(step, Act) or step.tool is None:
                raise PydanticCustomError(
                    "parallel_step_not_tool_act",
                    "PAR contains a step that is not an exact named-tool act",
                )

            acts.append(step)

        outputs = [
            output
            for act in acts
            for output in act.outputs
        ]
        duplicates = sorted(
            name
            for name, count in Counter(outputs).items()
            if count > 1
        )

        if duplicates:
            raise PydanticCustomError(
                "parallel_output_collision",
                "PAR repeats outputs: {outputs}",
                {
                    "outputs": ", ".join(
                        duplicates
                    )
                },
            )

        return self


class Join(StepModel):
    """The barrier immediately after one parallel group."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "join",
                }
            ]
        }
    )
    kind: Literal["join"] = Field(
        default="join",
        description="The process step discriminator.",
        examples=["join"],
    )


Step = Annotated[
    Act
    | Set
    | Emit
    | If
    | Call
    | Fail
    | Assert
    | Foreach
    | While
    | Par
    | Join,
    Field(discriminator="kind"),
]

If.model_rebuild(
    _types_namespace={
        "Step": Step,
        "Condition": Condition,
    }
)
Foreach.model_rebuild(
    _types_namespace={
        "Step": Step,
    }
)
While.model_rebuild(
    _types_namespace={
        "Step": Step,
        "Condition": Condition,
    }
)
Par.model_rebuild(
    _types_namespace={
        "Step": Step,
    }
)


def step_values(step: Step) -> list[Value]:
    """Return every value read directly by one step."""
    if isinstance(step, Act):
        return [
            binding.value
            for binding in step.inputs
        ]

    if isinstance(step, Set):
        return [step.value]

    if isinstance(step, Emit):
        return [
            binding.value
            for binding in step.bindings
        ]

    if isinstance(step, (If, Assert, While)):
        return condition_values(step.condition)

    if isinstance(step, Call):
        return [
            binding.value
            for binding in step.inputs
        ]

    if isinstance(step, Foreach):
        return [step.value]

    if isinstance(step, Par):
        return [
            binding.value
            for child in step.steps
            if isinstance(child, Act)
            for binding in child.inputs
        ]

    return []


def iter_steps(steps: list[Step]) -> Iterator[Step]:
    """Yield each step and its nested steps recursively in authored order."""
    for step in steps:
        yield step

        if isinstance(step, If):
            yield from iter_steps(step.then)

            if step.otherwise is not None:
                yield from iter_steps(step.otherwise)

        elif isinstance(step, (Foreach, While, Par)):
            yield from iter_steps(step.steps)


__all__ = [
    "Act",
    "Assert",
    "Call",
    "Emit",
    "Fail",
    "Foreach",
    "If",
    "Join",
    "Par",
    "Set",
    "Step",
    "StepModel",
    "While",
    "iter_steps",
    "step_values",
]
