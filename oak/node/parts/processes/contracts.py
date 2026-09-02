"""Resolved schema contracts for process entries and steps."""

from __future__ import annotations

from oak.node.parts.processes.model import (
    Process,
    process_visible_bindings,
)
from oak.node.parts.processes.steps import (
    Act,
    Call,
    sequence_always_fails,
)
from oak.rules import rule_error


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
    if (
        not missing
        or sequence_always_fails(process.steps)
    ):
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
        if (
            len(authored) != len(inputs)
            or set(authored) != inputs
        ):
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
        if (
            len(act.outputs) != len(outputs)
            or declared != outputs
        ):
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


__all__ = [
    "validate_act_contract",
    "validate_call_contract",
    "validate_process_contract",
]
