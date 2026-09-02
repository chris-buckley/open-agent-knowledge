"""Process contracts, step relationships, and local call-cycle validation."""

from __future__ import annotations

from collections.abc import Iterator

from pydantic_core import PydanticCustomError

from oak.node.index import NodeIndex
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Call,
    Emit,
    Fail,
    Foreach,
    If,
    Join,
    Par,
    Set,
    Step,
    While,
    step_values,
)
from oak.node.parts.schemas import SchemaBindingError
from oak.node.parts.state import State
from oak.node.validation.conditions import condition_result, validate_condition
from oak.node.validation.flow import (
    process_visible_bindings,
    sequence_always_fails,
)
from oak.node.validation.values import (
    STATIC_MISSING,
    direction_error,
    interface_schema,
    process_schema,
    static_value,
    validate_value,
)
from oak.rules import rule_error
from oak.vocabulary.text.target_path import is_relative_target, target_id


def validate_process_contract(
    process: Process,
    inputs: set[str],
    outputs: set[str],
) -> None:
    """Validate one process against resolved input and output schemas."""
    visible = process_visible_bindings(
        process,
        inputs,
    )
    missing = sorted(outputs - visible)

    if not missing or sequence_always_fails(process.steps):
        return

    raise rule_error(
        "process_output_binding_mismatch",
        "process {process} cannot supply output placeholders: {placeholders}",
        {
            "process": process.id,
            "placeholders": ", ".join(missing),
        },
    )


def validate_act_contract(
    act: Act,
    inputs: set[str] | None,
    outputs: set[str] | None,
) -> None:
    """Validate one act against its resolved input and output schemas."""
    if inputs is not None:
        authored = [
            binding.placeholder
            for binding in act.inputs
        ]

        if len(authored) != len(inputs) or set(authored) != inputs:
            raise rule_error(
                "act_schema_mismatch",
                (
                    "act input bindings differ from its input schema; "
                    "missing: {missing}; unused: {unused}"
                ),
                {
                    "missing": (
                        ", ".join(
                            sorted(inputs - set(authored))
                        )
                        or "none"
                    ),
                    "unused": (
                        ", ".join(
                            sorted(set(authored) - inputs)
                        )
                        or "none"
                    ),
                },
            )

    if outputs is not None:
        declared = set(act.outputs)

        if len(act.outputs) != len(outputs) or declared != outputs:
            raise rule_error(
                "act_schema_mismatch",
                (
                    "act outputs differ from its output schema; "
                    "missing: {missing}; unused: {unused}"
                ),
                {
                    "missing": (
                        ", ".join(
                            sorted(outputs - declared)
                        )
                        or "none"
                    ),
                    "unused": (
                        ", ".join(
                            sorted(declared - outputs)
                        )
                        or "none"
                    ),
                },
            )


def validate_call_contract(
    call: Call,
    inputs: set[str],
    outputs: set[str],
) -> None:
    """Validate one call against resolved process schemas."""
    authored_inputs = [
        binding.placeholder
        for binding in call.inputs
    ]
    authored_outputs = list(call.outputs)
    input_set = set(authored_inputs)
    output_set = set(authored_outputs)

    if (
        len(authored_inputs) == len(inputs)
        and input_set == inputs
        and len(authored_outputs) == len(outputs)
        and output_set == outputs
    ):
        return

    raise rule_error(
        "call_contract_mismatch",
        (
            "call contract differs; input missing: {input_missing}; "
            "input unused: {input_unused}; output missing: {output_missing}; "
            "output unused: {output_unused}"
        ),
        {
            "input_missing": (
                ", ".join(
                    sorted(inputs - input_set)
                )
                or "none"
            ),
            "input_unused": (
                ", ".join(
                    sorted(input_set - inputs)
                )
                or "none"
            ),
            "output_missing": (
                ", ".join(
                    sorted(outputs - output_set)
                )
                or "none"
            ),
            "output_unused": (
                ", ".join(
                    sorted(output_set - outputs)
                )
                or "none"
            ),
        },
    )


def _static_emit_values(
    index: NodeIndex,
    process: Process,
    step: Emit,
) -> dict[str, object] | None:
    values: dict[str, object] = {}

    for binding in step.bindings:
        value = static_value(
            index,
            process,
            binding.value,
        )

        if value is STATIC_MISSING:
            return None

        values[binding.placeholder] = value

    return values


def _validate_act_schema_contract(
    index: NodeIndex,
    process: Process,
    step: Act,
) -> None:
    input_schema = process_schema(
        index,
        process,
        step.input,
    )
    output_schema = process_schema(
        index,
        process,
        step.output,
    )
    input_known = (
        step.input is None
        or input_schema is not None
    )
    output_known = (
        step.output is None
        or output_schema is not None
    )

    if input_known and output_known:
        validate_act_contract(
            step,
            (
                None
                if input_schema is None
                else input_schema.placeholders
            ),
            (
                None
                if output_schema is None
                else output_schema.placeholders
            ),
        )


def _validate_call_schema_contract(
    index: NodeIndex,
    step: Call,
    target: Process,
) -> None:
    input_schema = process_schema(
        index,
        target,
        target.input,
    )
    output_schema = process_schema(
        index,
        target,
        target.output,
    )
    input_known = (
        target.input is None
        or input_schema is not None
    )
    output_known = (
        target.output is None
        or output_schema is not None
    )

    if input_known and output_known:
        validate_call_contract(
            step,
            (
                set()
                if input_schema is None
                else input_schema.placeholders
            ),
            (
                set()
                if output_schema is None
                else output_schema.placeholders
            ),
        )


def validate_process_steps(
    index: NodeIndex,
    process: Process,
    steps: list[Step],
) -> None:
    """Validate one process step sequence against local entries."""
    for step in steps:
        for value in step_values(step):
            validate_value(
                index,
                process,
                value,
            )

        if isinstance(step, Set):
            index.require(
                process,
                step.state,
                State,
            )
            continue

        if isinstance(step, Emit):
            interface = index.require(
                process,
                step.interface,
                Interface,
            )

            if interface is None:
                continue

            if interface.direction not in ("out", "inout"):
                direction_error(
                    process,
                    "emit",
                    interface,
                )

            schema = interface_schema(
                index,
                interface,
            )

            if schema is None:
                continue

            authored = {
                binding.placeholder
                for binding in step.bindings
            }
            expected = schema.placeholders

            if authored != expected:
                raise PydanticCustomError(
                    "emit_schema_binding_mismatch",
                    (
                        "process {process} emit bindings differ from interface "
                        "{interface} schema; missing: {missing}; unused: {unused}"
                    ),
                    {
                        "process": process.id,
                        "interface": interface.id,
                        "missing": (
                            ", ".join(
                                sorted(expected - authored)
                            )
                            or "none"
                        ),
                        "unused": (
                            ", ".join(
                                sorted(authored - expected)
                            )
                            or "none"
                        ),
                    },
                )

            static_values = _static_emit_values(
                index,
                process,
                step,
            )

            if static_values is not None:
                try:
                    schema.bind(static_values)

                except SchemaBindingError as error:
                    raise PydanticCustomError(
                        "invalid_static_schema_binding",
                        (
                            "process {process} emits an invalid static binding "
                            "through interface {interface}: {reason}"
                        ),
                        {
                            "process": process.id,
                            "interface": interface.id,
                            "reason": str(error),
                        },
                    ) from None

            continue

        if isinstance(step, If):
            validate_condition(
                index,
                process,
                step.condition,
            )
            result = condition_result(
                index,
                process,
                step.condition,
            )

            if result is False:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has an IF THEN branch that cannot run",
                    {"process": process.id},
                )

            if result is True and step.otherwise is not None:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has an ELSE branch that cannot run",
                    {"process": process.id},
                )

            validate_process_steps(
                index,
                process,
                step.then,
            )

            if step.otherwise is not None:
                validate_process_steps(
                    index,
                    process,
                    step.otherwise,
                )

            continue

        if isinstance(step, Assert):
            validate_condition(
                index,
                process,
                step.condition,
            )
            result = condition_result(
                index,
                process,
                step.condition,
            )

            if result is False:
                raise PydanticCustomError(
                    "assertion_always_fails",
                    "process {process} has an assertion that is statically false",
                    {"process": process.id},
                )

            if result is True:
                raise PydanticCustomError(
                    "redundant_assertion",
                    "process {process} has an assertion that is statically true",
                    {"process": process.id},
                )

            continue

        if isinstance(step, While):
            validate_condition(
                index,
                process,
                step.condition,
            )

            if condition_result(
                index,
                process,
                step.condition,
            ) is False:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has a WHILE body that cannot run",
                    {"process": process.id},
                )

            validate_process_steps(
                index,
                process,
                step.steps,
            )
            continue

        if isinstance(step, Foreach):
            validate_process_steps(
                index,
                process,
                step.steps,
            )
            continue

        if isinstance(step, Par):
            for child in step.steps:
                if isinstance(child, Act):
                    for binding in child.inputs:
                        validate_value(
                            index,
                            process,
                            binding.value,
                        )

                    _validate_act_schema_contract(
                        index,
                        process,
                        child,
                    )

            continue

        if isinstance(step, Call):
            target = index.require(
                process,
                step.process,
                Process,
            )

            if target is not None:
                _validate_call_schema_contract(
                    index,
                    step,
                    target,
                )

            continue

        if isinstance(step, Act):
            _validate_act_schema_contract(
                index,
                process,
                step,
            )
            continue

        if isinstance(step, (Fail, Join)):
            continue

        raise TypeError(
            f"unsupported process step {type(step).__name__}"
        )


def validate_process_schema_contract(
    index: NodeIndex,
    process: Process,
) -> None:
    """Validate one process against its local input and output schemas."""
    input_schema = process_schema(
        index,
        process,
        process.input,
    )
    output_schema = process_schema(
        index,
        process,
        process.output,
    )
    input_known = (
        process.input is None
        or input_schema is not None
    )
    output_known = (
        process.output is None
        or output_schema is not None
    )

    if not input_known:
        return

    inputs = (
        set()
        if input_schema is None
        else input_schema.placeholders
    )

    if output_known:
        validate_process_contract(
            process,
            inputs,
            (
                set()
                if output_schema is None
                else output_schema.placeholders
            ),
        )

    else:
        process_visible_bindings(
            process,
            inputs,
        )


def _calls(steps: list[Step]) -> Iterator[str]:
    for step in steps:
        if isinstance(step, Call) and not is_relative_target(step.process):
            yield target_id(step.process)
            continue

        if isinstance(step, If):
            yield from _calls(step.then)

            if step.otherwise is not None:
                yield from _calls(step.otherwise)

            continue

        if isinstance(step, Foreach):
            yield from _calls(step.steps)
            continue

        if isinstance(step, While):
            yield from _calls(step.steps)


def validate_local_call_cycles(processes: list[Process]) -> None:
    """Reject a cycle formed by local process calls."""
    graph = {
        process.id: list(_calls(process.steps))
        for process in processes
    }
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(process_id: str) -> None:
        state[process_id] = 1
        stack.append(process_id)

        for target in graph[process_id]:
            target_state = state.get(target, 0)

            if target_state == 0:
                visit(target)

            elif target_state == 1:
                start = stack.index(target)
                cycle = stack[start:] + [target]

                raise PydanticCustomError(
                    "process_call_cycle",
                    "process call cycle: {cycle}",
                    {"cycle": " -> ".join(cycle)},
                )

        stack.pop()
        state[process_id] = 2

    for process in processes:
        if state.get(process.id, 0) == 0:
            visit(process.id)


__all__ = [
    "validate_act_contract",
    "validate_call_contract",
    "validate_local_call_cycles",
    "validate_process_contract",
    "validate_process_schema_contract",
    "validate_process_steps",
]
