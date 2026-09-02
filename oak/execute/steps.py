"""Process invocation and ordered step execution."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from pydantic import JsonValue

from oak.execute.actions import invoke_action, run_parallel
from oak.execute.context import ExecutionContext, ProcessFrame
from oak.execute.models import ExecutionError, _JSON_ADAPTER
from oak.execute.values import (
    evaluate_condition,
    resolve_value,
    resolved_schema,
    validate_schema_values,
    validate_state_value,
)
from oak.node.parts import (
    Act,
    Assert,
    Call,
    Emit,
    Fail,
    Foreach,
    If,
    Interface,
    Join,
    Par,
    Process,
    Schema,
    SchemaBindingError,
    Set,
    State,
    Step,
    While,
)
from oak.vocabulary.text.target_path import target_id


def run_process(
    context: ExecutionContext,
    document: str,
    process: Process,
    inputs: Mapping[str, JsonValue],
) -> dict[str, JsonValue]:
    """Invoke one process with one fresh local binding scope."""
    input_schema = resolved_schema(
        context,
        document,
        process.input,
    )

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
        document,
        deepcopy(
            dict(inputs)
        ),
    )
    run_steps(
        context,
        frame,
        process.steps,
    )
    output_schema = resolved_schema(
        context,
        document,
        process.output,
    )

    if output_schema is None:
        return {}

    names = [
        item.placeholder
        for item in output_schema.where
    ]
    outputs = {
        name: deepcopy(
            frame.bindings[name]
        )
        for name in names
        if name in frame.bindings
    }

    try:
        output_schema.bind(outputs)

    except SchemaBindingError as error:
        raise ExecutionError(
            "invalid_process_output",
            f"process {process.id}: {error}",
        ) from None

    return outputs


def run_steps(
    context: ExecutionContext,
    frame: ProcessFrame,
    steps: list[Step],
) -> None:
    """Run one process step sequence in authored order."""
    pending: list[
        dict[str, JsonValue]
    ] | None = None

    for step in steps:
        if isinstance(step, Act):
            values = {
                binding.placeholder: resolve_value(
                    context,
                    frame,
                    binding.value,
                )
                for binding in step.inputs
            }
            validate_schema_values(
                context,
                frame.document,
                step.input,
                values,
                "invalid_act_input",
            )
            outputs = invoke_action(
                context,
                step,
                values,
            )
            validate_schema_values(
                context,
                frame.document,
                step.output,
                outputs,
                "invalid_act_output",
            )
            frame.bindings.update(outputs)

        elif isinstance(step, Set):
            identifier = target_id(step.state)
            state_document, entry = context.graph.entry(
                frame.document,
                step.state,
                State,
            )
            key = context.graph.display_target(
                frame.document,
                "state",
                identifier,
            )
            resolved = _JSON_ADAPTER.validate_python(
                resolve_value(
                    context,
                    frame,
                    step.value,
                )
            )
            validate_state_value(
                context,
                state_document,
                entry,
                resolved,
                key,
            )
            context.state[key] = resolved

        elif isinstance(step, Emit):
            identifier = target_id(step.interface)
            _interface_document, interface = context.graph.entry(
                frame.document,
                step.interface,
                Interface,
            )
            _schema_document, schema = context.graph.entry(
                frame.document,
                interface.schema_id,
                Schema,
            )
            values = {
                binding.placeholder: resolve_value(
                    context,
                    frame,
                    binding.value,
                )
                for binding in step.bindings
            }

            try:
                schema.bind(values)

            except SchemaBindingError as error:
                raise ExecutionError(
                    "invalid_emission",
                    f"interface {identifier}: {error}",
                ) from None

            context.emissions.append(
                context_emission(
                    context,
                    frame.document,
                    identifier,
                    values,
                )
            )

        elif isinstance(step, If):
            selected = (
                step.then
                if evaluate_condition(
                    context,
                    frame,
                    step.condition,
                )
                else step.otherwise
            )

            if selected is not None:
                run_steps(
                    context,
                    frame.child(),
                    selected,
                )

        elif isinstance(step, Call):
            values = {
                binding.placeholder: resolve_value(
                    context,
                    frame,
                    binding.value,
                )
                for binding in step.inputs
            }
            target_document, process = context.graph.entry(
                frame.document,
                step.process,
                Process,
            )
            outputs = run_process(
                context,
                target_document,
                process,
                values,
            )

            for name in step.outputs:
                frame.bindings[name] = deepcopy(
                    outputs[name]
                )

        elif isinstance(step, Fail):
            raise ExecutionError(
                "process_failed",
                step.message,
            )

        elif isinstance(step, Assert):
            if not evaluate_condition(
                context,
                frame,
                step.condition,
            ):
                raise ExecutionError(
                    "assertion_failed",
                    (
                        step.message
                        or "process assertion failed"
                    ),
                )

        elif isinstance(step, Foreach):
            items = resolve_value(
                context,
                frame,
                step.value,
            )

            if not isinstance(items, list):
                raise ExecutionError(
                    "foreach_source_not_list",
                    "FOREACH value is not a JSON list",
                )

            for item in items:
                child = frame.child()
                child.bindings[step.binding] = deepcopy(item)
                run_steps(
                    context,
                    child,
                    step.steps,
                )

        elif isinstance(step, While):
            for _iteration in range(step.limit):
                if not evaluate_condition(
                    context,
                    frame,
                    step.condition,
                ):
                    break

                run_steps(
                    context,
                    frame.child(),
                    step.steps,
                )

            else:
                if evaluate_condition(
                    context,
                    frame,
                    step.condition,
                ):
                    raise ExecutionError(
                        "while_limit_reached",
                        (
                            "WHILE condition remains true after "
                            f"{step.limit} iterations"
                        ),
                    )

        elif isinstance(step, Par):
            pending = run_parallel(
                context,
                frame,
                step,
            )

        elif isinstance(step, Join):
            if pending is None:
                raise ExecutionError(
                    "join_without_par",
                    "JOIN has no pending PAR",
                )

            for result in pending:
                frame.bindings.update(result)

            pending = None

        else:
            raise TypeError(
                type(step).__name__
            )

    if pending is not None:
        raise ExecutionError(
            "parallel_join_missing",
            "PAR has no JOIN",
        )


def context_emission(
    context: ExecutionContext,
    document: str,
    identifier: str,
    values: Mapping[str, JsonValue],
):
    """Build one emission at its root-relative interface target."""
    from oak.execute.models import Emission

    return Emission(
        interface=context.graph.display_target(
            document,
            "interface",
            identifier,
        ),
        values=deepcopy(
            dict(values)
        ),
    )


__all__ = [
    "run_process",
    "run_steps",
]
