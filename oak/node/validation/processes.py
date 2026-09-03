"""Process contracts, step relationships, and local call-cycle validation."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from collections.abc import Set as AbstractSet

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
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.state import State
from oak.node.validation.conditions import condition_result, validate_condition
from oak.node.validation.contracts import find_cycle, inspect_emit_contract
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
from oak.rules.validation import rule_error
from oak.vocabulary.text.target_path import is_relative_target, target_id


def validate_process_contract(
    process: Process,
    inputs: AbstractSet[str],
    outputs: AbstractSet[str],
) -> None:
    """Validate one process against resolved input and output schemas."""
    visible = process_visible_bindings(process, inputs)
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
    inputs: AbstractSet[str] | None,
    outputs: AbstractSet[str] | None,
) -> None:
    """Validate one act against its resolved input and output schemas."""
    if inputs is not None:
        authored = [binding.placeholder for binding in act.inputs]

        if len(authored) != len(inputs) or set(authored) != inputs:
            raise rule_error(
                "act_schema_mismatch",
                (
                    "act input bindings differ from its input schema; "
                    "missing: {missing}; unused: {unused}"
                ),
                {
                    "missing": ", ".join(sorted(inputs - set(authored))) or "none",
                    "unused": ", ".join(sorted(set(authored) - inputs)) or "none",
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
                    "missing": ", ".join(sorted(outputs - declared)) or "none",
                    "unused": ", ".join(sorted(declared - outputs)) or "none",
                },
            )


def validate_call_contract(
    call: Call,
    inputs: AbstractSet[str],
    outputs: AbstractSet[str],
) -> None:
    """Validate one call against resolved process schemas."""
    authored_inputs = [binding.placeholder for binding in call.inputs]
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
            "input_missing": ", ".join(sorted(inputs - input_set)) or "none",
            "input_unused": ", ".join(sorted(input_set - inputs)) or "none",
            "output_missing": ", ".join(sorted(outputs - output_set)) or "none",
            "output_unused": ", ".join(sorted(output_set - outputs)) or "none",
        },
    )


def _static_emit_values(
    index: NodeIndex,
    process: Process,
    step: Emit,
) -> dict[str, object] | None:
    values: dict[str, object] = {}

    for binding in step.bindings:
        value = static_value(index, process, binding.value)

        if value is STATIC_MISSING:
            return None

        values[binding.placeholder] = value

    return values


def _validate_act_schema_contract(
    index: NodeIndex,
    process: Process,
    step: Act,
) -> None:
    input_schema = process_schema(index, process, step.input)
    output_schema = process_schema(index, process, step.output)
    input_known = step.input is None or input_schema is not None
    output_known = step.output is None or output_schema is not None

    if input_known and output_known:
        validate_act_contract(
            step,
            None if input_schema is None else input_schema.placeholders,
            None if output_schema is None else output_schema.placeholders,
        )


def _validate_call_schema_contract(
    index: NodeIndex,
    step: Call,
    target: Process,
) -> None:
    input_schema = process_schema(index, target, target.input)
    output_schema = process_schema(index, target, target.output)
    input_known = target.input is None or input_schema is not None
    output_known = target.output is None or output_schema is not None

    if input_known and output_known:
        validate_call_contract(
            step,
            set() if input_schema is None else input_schema.placeholders,
            set() if output_schema is None else output_schema.placeholders,
        )


def _validate_emit_step(index: NodeIndex, process: Process, step: Emit) -> None:
    interface = index.require(process, step.interface, Interface)

    if interface is None:
        return

    if interface.direction not in ("out", "inout"):
        direction_error(process, "emit", interface)

    schema = interface_schema(index, interface)

    if schema is None:
        return

    try:
        contract = inspect_emit_contract(
            schema,
            (binding.placeholder for binding in step.bindings),
            _static_emit_values(index, process, step),
        )

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

    if not contract.placeholders_match:
        raise PydanticCustomError(
            "emit_schema_binding_mismatch",
            (
                "process {process} emit bindings differ from interface "
                "{interface} schema; missing: {missing}; unused: {unused}"
            ),
            {
                "process": process.id,
                "interface": interface.id,
                "missing": ", ".join(contract.missing) or "none",
                "unused": ", ".join(contract.unused) or "none",
            },
        )


def _validate_if_step(index: NodeIndex, process: Process, step: If) -> None:
    validate_condition(index, process, step.condition)
    decision = condition_result(index, process, step.condition)

    if decision is False:
        raise PydanticCustomError(
            "dead_process_branch",
            "process {process} has an IF THEN branch that cannot run",
            {"process": process.id},
        )

    if decision is True and step.otherwise is not None:
        raise PydanticCustomError(
            "dead_process_branch",
            "process {process} has an ELSE branch that cannot run",
            {"process": process.id},
        )

    validate_process_steps(index, process, step.then)

    if step.otherwise is not None:
        validate_process_steps(index, process, step.otherwise)


def _validate_assert_step(index: NodeIndex, process: Process, step: Assert) -> None:
    validate_condition(index, process, step.condition)
    decision = condition_result(index, process, step.condition)

    if decision is False:
        raise PydanticCustomError(
            "assertion_always_fails",
            "process {process} has an assertion that is statically false",
            {"process": process.id},
        )

    if decision is True:
        raise PydanticCustomError(
            "redundant_assertion",
            "process {process} has an assertion that is statically true",
            {"process": process.id},
        )


def _validate_while_step(index: NodeIndex, process: Process, step: While) -> None:
    validate_condition(index, process, step.condition)

    if condition_result(index, process, step.condition) is False:
        raise PydanticCustomError(
            "dead_process_branch",
            "process {process} has a WHILE body that cannot run",
            {"process": process.id},
        )

    validate_process_steps(index, process, step.steps)


def _validate_par_step(index: NodeIndex, process: Process, step: Par) -> None:
    for child in step.steps:
        if isinstance(child, Act):
            for binding in child.inputs:
                validate_value(index, process, binding.value)

            _validate_act_schema_contract(index, process, child)


def _validate_call_step(index: NodeIndex, process: Process, step: Call) -> None:
    target = index.require(process, step.process, Process)

    if target is not None:
        _validate_call_schema_contract(index, step, target)


def validate_process_steps(
    index: NodeIndex,
    process: Process,
    steps: Sequence[Step],
) -> None:
    """Validate one process step sequence against local entries."""
    for step in steps:
        for value in step_values(step):
            validate_value(index, process, value)

        match step:
            case Set():
                index.require(process, step.state, State)

            case Emit():
                _validate_emit_step(index, process, step)

            case If():
                _validate_if_step(index, process, step)

            case Assert():
                _validate_assert_step(index, process, step)

            case While():
                _validate_while_step(index, process, step)

            case Foreach():
                validate_process_steps(index, process, step.steps)

            case Par():
                _validate_par_step(index, process, step)

            case Call():
                _validate_call_step(index, process, step)

            case Act():
                _validate_act_schema_contract(index, process, step)

            case Fail() | Join():
                pass

            case _:
                raise TypeError(f"unsupported process step {type(step).__name__}")


def validate_process_schema_contract(
    index: NodeIndex,
    process: Process,
) -> None:
    """Validate one process against its local input and output schemas."""
    input_schema = process_schema(index, process, process.input)
    output_schema = process_schema(index, process, process.output)
    input_known = process.input is None or input_schema is not None
    output_known = process.output is None or output_schema is not None

    if not input_known:
        return

    inputs = set() if input_schema is None else input_schema.placeholders

    if output_known:
        validate_process_contract(
            process,
            inputs,
            set() if output_schema is None else output_schema.placeholders,
        )

    else:
        process_visible_bindings(process, inputs)


def _local_calls(steps: Sequence[Step]) -> Iterator[str]:
    for step in steps:
        match step:
            case Call() if not is_relative_target(step.process):
                yield target_id(step.process)

            case If():
                yield from _local_calls(step.then)

                if step.otherwise is not None:
                    yield from _local_calls(step.otherwise)

            case Foreach() | While():
                yield from _local_calls(step.steps)


def validate_local_call_cycles(processes: Sequence[Process]) -> None:
    """Reject a cycle formed by local process calls."""
    graph = {process.id: list(_local_calls(process.steps)) for process in processes}
    cycle = find_cycle(graph)

    if cycle is None:
        return

    raise PydanticCustomError(
        "process_call_cycle",
        "process call cycle: {cycle}",
        {"cycle": " -> ".join(cycle)},
    )


__all__ = [
    "validate_act_contract",
    "validate_call_contract",
    "validate_local_call_cycles",
    "validate_process_contract",
    "validate_process_schema_contract",
    "validate_process_steps",
]
