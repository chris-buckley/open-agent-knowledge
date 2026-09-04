"""Interpreter-native and exact named-tool action execution."""

from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import Future, ThreadPoolExecutor
from copy import deepcopy

from pydantic import JsonValue

from oak.context import build_interpreter_context
from oak.execute.context import ExecutionContext, ProcessFrame
from oak.execute.models import (
    ActHandler,
    ExecutionError,
    ToolHandler,
    _BINDING_ADAPTER,
)
from oak.execute.values import (
    resolve_value,
    validate_schema_values,
)
from oak.node.parts.processes.steps import Act, Par


def invoke_action(
    context: ExecutionContext,
    frame: ProcessFrame,
    step: Act,
    values: Mapping[str, JsonValue],
) -> dict[str, JsonValue]:
    """Invoke one interpreter-native or exact named-tool action."""
    handler: ActHandler | ToolHandler | None

    if step.tool is None:
        handler = context.act

        if handler is None and context.interpreter is None:
            raise ExecutionError(
                "act_handler_missing",
                "an interpreter-native act needs an act or interpreter handler",
            )

    else:
        contract = context.tools.get(step.tool)

        if contract is None:
            raise ExecutionError(
                "unknown_tool",
                f"tool {step.tool} is absent",
            )

        handler = contract.handler

    try:
        if step.tool is None and context.interpreter is not None:
            if frame.process is None:
                raise ExecutionError("missing_process_context", "native action has no process")
            request = build_interpreter_context(
                context.graph, frame.process, step, values, state=context.state,
            )
            authored = context.interpreter(request)
        else:
            if handler is None:
                raise ExecutionError("act_handler_missing", "native action has no handler")
            authored = handler(step, values)
        outputs = _BINDING_ADAPTER.validate_python(
            dict(authored)
        )

    except ExecutionError:
        raise

    except Exception as error:
        raise ExecutionError(
            (
                "act_failed"
                if step.tool is None
                else "tool_failed"
            ),
            str(error),
        ) from None

    expected = set(step.outputs)
    supplied = set(outputs)

    if supplied != expected:
        raise ExecutionError(
            "act_output_mismatch",
            (
                "act outputs differ; missing: "
                + (
                    ", ".join(
                        sorted(expected - supplied)
                    )
                    or "none"
                )
                + "; unused: "
                + (
                    ", ".join(
                        sorted(supplied - expected)
                    )
                    or "none"
                )
            ),
        )

    return deepcopy(outputs)


def run_parallel(
    context: ExecutionContext,
    frame: ProcessFrame,
    step: Par,
) -> list[dict[str, JsonValue]]:
    """Run one parallel group and return outputs in authored order."""
    acts = [
        child
        for child in step.steps
        if isinstance(child, Act)
    ]
    prepared = [
        {
            binding.placeholder: resolve_value(
                context,
                frame,
                binding.value,
            )
            for binding in child.inputs
        }
        for child in acts
    ]

    for child, values in zip(
        acts,
        prepared,
        strict=True,
    ):
        validate_schema_values(
            context,
            frame.document,
            child.input,
            values,
            "invalid_act_input",
        )

    futures: list[
        Future[dict[str, JsonValue]]
    ] = []

    with ThreadPoolExecutor(
        max_workers=len(acts)
    ) as executor:
        for child, values in zip(
            acts,
            prepared,
            strict=True,
        ):
            futures.append(
                executor.submit(
                    invoke_action,
                    context,
                    frame,
                    child,
                    values,
                )
            )

        results: list[
            dict[str, JsonValue] | None
        ] = []
        failures: list[str] = []

        for child, future in zip(
            acts,
            futures,
            strict=True,
        ):
            try:
                outputs = future.result()
                validate_schema_values(
                    context,
                    frame.document,
                    child.output,
                    outputs,
                    "invalid_act_output",
                )
                results.append(outputs)

            except Exception as error:
                results.append(None)
                failures.append(str(error))

    if failures:
        raise ExecutionError(
            "parallel_failed",
            failures[0],
            suppressed=tuple(failures[1:]),
        )

    return [
        result
        for result in results
        if result is not None
    ]


__all__ = [
    "invoke_action",
    "run_parallel",
]
