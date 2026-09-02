"""Process value, condition, step, and process text rendering."""

from __future__ import annotations

from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Condition,
    Not,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.operators import OPERATOR_TEXT
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
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    InterfaceValue,
    LiteralValue,
    StateValue,
    Value,
    ValueBinding,
)
from oak.render.oak.data import value_text
from oak.surface.registry import surface_for


def process_value_text(
    value: Value,
) -> str:
    """Return one JSON literal or process value reference."""
    surface_for(value)

    match value:
        case LiteralValue():
            return value_text(
                value.value
            )

        case ConstantValue():
            return (
                "$"
                + value.constant
            )

        case StateValue():
            return (
                "$"
                + value.state
            )

        case InterfaceValue():
            return (
                "$"
                + value.interface
                + "."
                + value.placeholder
            )

        case BindingValue():
            return (
                "$"
                + value.binding
            )

    raise TypeError(
        "unsupported process value "
        f"{type(value).__name__}"
    )


def condition_lines(
    condition: Condition,
    indent: int = 0,
) -> list[str]:
    """Return one recursive condition in prefix form."""
    surface_for(condition)
    prefix = " " * indent

    if isinstance(
        condition,
        Compare,
    ):
        return [
            (
                prefix
                + process_value_text(
                    condition.left
                )
                + " "
                + OPERATOR_TEXT[
                    condition.operator
                ]
                + " "
                + process_value_text(
                    condition.right
                )
            )
        ]

    if isinstance(
        condition,
        (
            All,
            Any,
        ),
    ):
        lines = [
            prefix
            + (
                "ALL:"
                if isinstance(
                    condition,
                    All,
                )
                else "ANY:"
            )
        ]

        for child in condition.conditions:
            lines.extend(
                condition_lines(
                    child,
                    indent + 2,
                )
            )

        return lines

    if isinstance(
        condition,
        Not,
    ):
        return [
            prefix + "NOT:",
            *condition_lines(
                condition.condition,
                indent + 2,
            ),
        ]

    raise TypeError(
        "unsupported condition "
        f"{type(condition).__name__}"
    )


def condition_text(
    condition: Condition,
) -> str:
    """Return one recursive condition."""
    return "\n".join(
        condition_lines(condition)
    )


def _binding_line(
    binding: ValueBinding,
    indent: int,
) -> str:
    surface_for(binding)
    return (
        " " * indent
        + f"{binding.placeholder}="
        + process_value_text(
            binding.value
        )
    )


def _suffix_text(
    bindings: list[ValueBinding],
    outputs: list[str],
) -> str:
    body = (
        "("
        + ", ".join(
            _binding_line(
                binding,
                0,
            )
            for binding in bindings
        )
        + ")"
    )

    if outputs:
        body += (
            " -> "
            + ", ".join(outputs)
        )

    return body


def _act_attributes(
    step: Act,
) -> str:
    attributes = ""

    if step.input is not None:
        attributes += (
            f' input="{step.input}"'
        )

    if step.output is not None:
        attributes += (
            f' output="{step.output}"'
        )

    return attributes


def _act_lines(
    step: Act,
    indent: int,
) -> list[str]:
    prefix = " " * indent
    surface_for(step)
    attributes = _act_attributes(
        step
    )

    if step.tool is None:
        head = (
            "ACT"
            + attributes
            + (
                ": "
                if attributes
                else " "
            )
            + step.instruction
        )

    else:
        head = (
            "ACT TOOL "
            + value_text(step.tool)
            + attributes
            + ": "
            + step.instruction
        )

    return [
        (
            prefix
            + head
            + " "
            + _suffix_text(
                step.inputs,
                step.outputs,
            )
        )
    ]


def _call_lines(
    step: Call,
    indent: int,
) -> list[str]:
    prefix = " " * indent
    return [
        (
            prefix
            + "CALL "
            + step.process
            + " "
            + _suffix_text(
                step.inputs,
                step.outputs,
            )
        )
    ]


def _step_lines(
    step: Step,
    indent: int,
) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    surface_for(step)

    if isinstance(
        step,
        Act,
    ):
        return _act_lines(
            step,
            indent,
        )

    if isinstance(
        step,
        Set,
    ):
        return [
            (
                prefix
                + "SET "
                + step.state
                + " = "
                + process_value_text(
                    step.value
                )
            )
        ]

    if isinstance(
        step,
        Emit,
    ):
        return [
            (
                prefix
                + "EMIT "
                + step.interface
                + " "
                + _suffix_text(
                    step.bindings,
                    [],
                )
            )
        ]

    if isinstance(
        step,
        If,
    ):
        condition = condition_lines(
            step.condition
        )

        if len(condition) == 1:
            lines = [
                (
                    prefix
                    + "IF "
                    + condition[0]
                    + ":"
                )
            ]

        else:
            lines = [
                prefix + "IF:",
                *(
                    " " * inner
                    + line
                    for line in condition
                ),
            ]

        lines.append(
            " " * inner
            + "THEN:"
        )

        for child in step.then:
            lines.extend(
                _step_lines(
                    child,
                    inner + 2,
                )
            )

        if step.otherwise is not None:
            lines.append(
                " " * inner
                + "ELSE:"
            )

            for child in step.otherwise:
                lines.extend(
                    _step_lines(
                        child,
                        inner + 2,
                    )
                )

        return lines

    if isinstance(
        step,
        Call,
    ):
        return _call_lines(
            step,
            indent,
        )

    if isinstance(
        step,
        Fail,
    ):
        return [
            (
                prefix
                + "FAIL "
                + value_text(
                    step.message
                )
            )
        ]

    if isinstance(
        step,
        Assert,
    ):
        condition = condition_lines(
            step.condition
        )

        if len(condition) == 1:
            lines = [
                (
                    prefix
                    + "ASSERT "
                    + condition[0]
                )
            ]

        else:
            lines = [
                prefix + "ASSERT:",
                *(
                    " " * inner
                    + line
                    for line in condition
                ),
            ]

        if step.message is not None:
            lines.append(
                (
                    " " * inner
                    + "MESSAGE "
                    + value_text(
                        step.message
                    )
                )
            )

        return lines

    if isinstance(
        step,
        Foreach,
    ):
        lines = [
            (
                prefix
                + f"FOREACH {step.binding} IN "
                + process_value_text(
                    step.value
                )
                + ":"
            )
        ]

        for child in step.steps:
            lines.extend(
                _step_lines(
                    child,
                    inner,
                )
            )

        return lines

    if isinstance(
        step,
        While,
    ):
        condition = condition_lines(
            step.condition
        )

        if len(condition) == 1:
            lines = [
                (
                    prefix
                    + "WHILE "
                    + condition[0]
                    + f" LIMIT {step.limit}:"
                )
            ]
            child_indent = inner

        else:
            lines = [
                (
                    prefix
                    + f"WHILE LIMIT {step.limit}:"
                ),
                *(
                    " " * inner
                    + line
                    for line in condition
                ),
                (
                    " " * inner
                    + "THEN:"
                ),
            ]
            child_indent = (
                inner + 2
            )

        for child in step.steps:
            lines.extend(
                _step_lines(
                    child,
                    child_indent,
                )
            )

        return lines

    if isinstance(
        step,
        Par,
    ):
        lines = [
            prefix + "PAR:"
        ]

        for child in step.steps:
            lines.extend(
                _step_lines(
                    child,
                    inner,
                )
            )

        return lines

    if isinstance(
        step,
        Join,
    ):
        return [
            prefix + "JOIN"
        ]

    raise TypeError(
        "unsupported process step "
        f"{type(step).__name__}"
    )


def process_lines(
    process: Process,
) -> list[str]:
    """Return process steps in authored order."""
    surface_for(process)
    lines: list[str] = []

    for step in process.steps:
        lines.extend(
            _step_lines(
                step,
                0,
            )
        )

    return lines


def binding_line(
    binding: ValueBinding,
    indent: int = 0,
) -> str:
    """Return one process binding line."""
    return _binding_line(
        binding,
        indent,
    )


def step_lines(
    step: Step,
    indent: int = 0,
) -> list[str]:
    """Return one typed step in OAK syntax."""
    return _step_lines(
        step,
        indent,
    )


__all__ = [
    "binding_line",
    "condition_lines",
    "condition_text",
    "process_lines",
    "process_value_text",
    "step_lines",
]
