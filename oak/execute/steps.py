"""Process invocation and ordered step execution."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy

from pydantic import JsonValue

from oak.execute.actions import invoke_action, run_parallel
from oak.execute.context import ExecutionContext, ProcessFrame
from oak.execute.models import JSON_ADAPTER, Emission, ExecutionError
from oak.execute.values import (
    evaluate_condition,
    resolve_value,
    resolved_schema,
    validate_schema_values,
    validate_state_value,
)
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
)
from oak.node.parts.processes.values import ValueBinding
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema
from oak.node.parts.state import State
from oak.vocabulary.text.target_path import target_id


def run_process(
    context: ExecutionContext,
    document: str,
    process: Process,
    inputs: Mapping[str, JsonValue],
) -> dict[str, JsonValue]:
    """Invoke one process with one fresh local binding scope."""
    input_schema = resolved_schema(context, document, process.input)

    if input_schema is None:
        if inputs:
            raise ExecutionError(
                "invalid_process_input",
                f"process {process.id} has no input schema",
            )

    else:
        try:
            input_schema.bind(inputs)

        except SchemaBindingError as error:
            raise ExecutionError(
                "invalid_process_input",
                f"process {process.id}: {error}",
            ) from None

    frame = ProcessFrame(
        document, deepcopy(dict(inputs)),
        context.graph.display_target(document, "process", process.id),
    )
    run_steps(context, frame, process.steps)
    output_schema = resolved_schema(context, document, process.output)

    if output_schema is None:
        return {}

    placeholders = [clause.placeholder for clause in output_schema.where]
    outputs = {
        placeholder: deepcopy(frame.bindings[placeholder])
        for placeholder in placeholders
        if placeholder in frame.bindings
    }

    try:
        output_schema.bind(outputs)

    except SchemaBindingError as error:
        raise ExecutionError(
            "invalid_process_output",
            f"process {process.id}: {error}",
        ) from None

    return outputs


def _bound_values(
    context: ExecutionContext,
    frame: ProcessFrame,
    bindings: Sequence[ValueBinding],
) -> dict[str, JsonValue]:
    return {
        binding.placeholder: resolve_value(context, frame, binding.value)
        for binding in bindings
    }


def _run_act(context: ExecutionContext, frame: ProcessFrame, step: Act) -> None:
    values = _bound_values(context, frame, step.inputs)
    validate_schema_values(
        context,
        frame.document,
        step.input,
        values,
        "invalid_act_input",
    )
    outputs = invoke_action(context, frame, step, values)
    validate_schema_values(
        context,
        frame.document,
        step.output,
        outputs,
        "invalid_act_output",
    )
    frame.bindings.update(outputs)


def _run_set(context: ExecutionContext, frame: ProcessFrame, step: Set) -> None:
    identifier = target_id(step.state)
    state_document, entry = context.graph.entry(frame.document, step.state, State)
    key = context.graph.display_target(frame.document, "state", identifier)
    resolved = JSON_ADAPTER.validate_python(resolve_value(context, frame, step.value))
    validate_state_value(context, state_document, entry, resolved, key)
    context.state[key] = resolved


def _run_emit(context: ExecutionContext, frame: ProcessFrame, step: Emit) -> None:
    identifier = target_id(step.interface)
    interface_document, interface = context.graph.entry(
        frame.document,
        step.interface,
        Interface,
    )
    if interface.flow != "emits":
        raise ExecutionError(
            "emit_target_not_emit",
            f"interface {identifier} cannot emit output",
        )

    _schema_document, schema = context.graph.entry(
        interface_document,
        interface.schema_id,
        Schema,
    )
    if step.bindings:
        values = _bound_values(context, frame, step.bindings)
    else:
        placeholders = [item.placeholder for item in schema.where]
        missing = [name for name in placeholders if name not in frame.bindings]
        if missing:
            raise ExecutionError(
                "inferred_emit_binding_mismatch",
                "missing visible bindings: " + ", ".join(missing),
            )
        values = {
            name: deepcopy(frame.bindings[name])
            for name in placeholders
        }

    try:
        schema.bind(values)
    except SchemaBindingError as error:
        raise ExecutionError(
            "invalid_emission",
            f"interface {identifier}: {error}",
        ) from None

    context.emissions.append(
        context_emission(context, frame.document, identifier, values)
    )


def _run_if(context: ExecutionContext, frame: ProcessFrame, step: If) -> None:
    selected = (
        step.then
        if evaluate_condition(context, frame, step.condition)
        else step.otherwise
    )

    if selected is not None:
        run_steps(context, frame.child(), selected)


def _run_call(context: ExecutionContext, frame: ProcessFrame, step: Call) -> None:
    values = _bound_values(context, frame, step.inputs)
    target_document, process = context.graph.entry(
        frame.document,
        step.process,
        Process,
    )
    outputs = run_process(context, target_document, process, values)

    for name in step.outputs:
        frame.bindings[name] = deepcopy(outputs[name])


def _run_assert(context: ExecutionContext, frame: ProcessFrame, step: Assert) -> None:
    if not evaluate_condition(context, frame, step.condition):
        raise ExecutionError(
            "assertion_failed",
            step.message or "process assertion failed",
        )


def _run_foreach(context: ExecutionContext, frame: ProcessFrame, step: Foreach) -> None:
    elements = resolve_value(context, frame, step.value)

    if not isinstance(elements, list):
        raise ExecutionError(
            "foreach_source_not_list",
            "FOREACH value is not a JSON list",
        )

    for element in elements:
        child = frame.child()
        child.bindings[step.binding] = deepcopy(element)
        run_steps(context, child, step.steps)


def _run_while(context: ExecutionContext, frame: ProcessFrame, step: While) -> None:
    for _iteration in range(step.limit):
        if not evaluate_condition(context, frame, step.condition):
            return

        run_steps(context, frame.child(), step.steps)

    if evaluate_condition(context, frame, step.condition):
        raise ExecutionError(
            "while_limit_reached",
            f"WHILE condition remains true after {step.limit} iterations",
        )


def _join(frame: ProcessFrame, pending: Sequence[Mapping[str, JsonValue]] | None) -> None:
    if pending is None:
        raise ExecutionError("join_without_par", "JOIN has no pending PAR")

    for outputs in pending:
        frame.bindings.update(outputs)


def run_steps(
    context: ExecutionContext,
    frame: ProcessFrame,
    steps: Sequence[Step],
) -> None:
    """Run one process step sequence in authored order."""
    pending: list[dict[str, JsonValue]] | None = None

    for step in steps:
        match step:
            case Act():
                _run_act(context, frame, step)

            case Set():
                _run_set(context, frame, step)

            case Emit():
                _run_emit(context, frame, step)

            case If():
                _run_if(context, frame, step)

            case Call():
                _run_call(context, frame, step)

            case Fail():
                raise ExecutionError("process_failed", step.message)

            case Assert():
                _run_assert(context, frame, step)

            case Foreach():
                _run_foreach(context, frame, step)

            case While():
                _run_while(context, frame, step)

            case Par():
                pending = run_parallel(context, frame, step)

            case Join():
                _join(frame, pending)
                pending = None

            case _:
                raise TypeError(type(step).__name__)

    if pending is not None:
        raise ExecutionError("parallel_join_missing", "PAR has no JOIN")


def context_emission(
    context: ExecutionContext,
    document: str,
    identifier: str,
    values: Mapping[str, JsonValue],
) -> Emission:
    """Build one emission at its root-relative interface target."""
    return Emission(
        interface=context.graph.display_target(document, "interface", identifier),
        values=deepcopy(dict(values)),
    )


__all__ = [
    "run_process",
    "run_steps",
]
