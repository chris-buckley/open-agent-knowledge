"""The text syntax of OAK entry bodies."""

import csv
import io
import json

import yaml
from pydantic import ConfigDict, TypeAdapter

from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import (
    Act,
    BindingValue,
    Call,
    Condition,
    ConstantValue,
    Emit,
    Fail,
    If,
    InterfaceValue,
    LiteralValue,
    Process,
    Set,
    StateValue,
    Step,
    Value,
    ValueBinding,
)
from oak.node.parts.schemas import (
    AtLeast,
    AtMost,
    Constraint,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Type,
    Where,
)
from oak.node.parts.state import State
from oak.vocabulary import DottedPath, ValueReference
from oak.vocabulary.text.placeholder import token

WHERE_HEADING = "WHERE:"
WHERE_ENTRY_PREFIX = "- "
WHERE_DETAIL_SEPARATOR = "; "

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)
_DOTTED_PATH_ADAPTER = TypeAdapter(
    DottedPath,
    config=_STRICT,
)
_VALUE_REFERENCE_ADAPTER = TypeAdapter(
    ValueReference,
    config=_STRICT,
)


def _scalar(value: str | int | float | bool) -> str:
    return (
        value
        if isinstance(value, str)
        else json.dumps(value, ensure_ascii=False)
    )


def _bound(value: int | float | str) -> str:
    return token(value) if isinstance(value, str) else _scalar(value)


def _lines(constraint: Lines) -> str:
    if constraint.min is not None and constraint.max is not None:
        if constraint.min == constraint.max == 1:
            return "is one line"
        if constraint.min == constraint.max:
            return f"has {constraint.min} lines"
        return f"has {constraint.min} to {constraint.max} lines"

    if constraint.max is not None:
        return (
            "is one line"
            if constraint.max == 1
            else f"has at most {constraint.max} lines"
        )

    return f"has at least {constraint.min} lines"


def constraint_text(constraint: Constraint) -> str:
    """Return the OAK text for one schema constraint."""
    match constraint:
        case Type():
            return f"is {constraint.of}"
        case OneOf():
            return "is one of " + ", ".join(
                f"`{_scalar(value)}`"
                for value in constraint.values
            )
        case Regex():
            return f"matches `{constraint.pattern}`"
        case NonEmpty():
            return "is non-empty"
        case MaxChars():
            return f"is at most {constraint.n} characters"
        case Lines():
            return _lines(constraint)
        case ListOf():
            return (
                f"is a list of {constraint.item} joined by "
                f"`{constraint.separator}`"
            )
        case AtLeast():
            return f"is at least {_bound(constraint.value)}"
        case AtMost():
            return f"is at most {_bound(constraint.value)}"

    raise TypeError(
        f"unsupported constraint {type(constraint).__name__}"
    )


def where_line(where: Where) -> str:
    """Return one dense line for a schema placeholder."""
    body = WHERE_DETAIL_SEPARATOR.join(
        constraint_text(constraint)
        for constraint in where.constraints
    )

    if where.examples:
        body += " (e.g. " + ", ".join(
            f"`{_scalar(example)}`"
            for example in where.examples
        ) + ")"

    if where.description is not None:
        body += WHERE_DETAIL_SEPARATOR + where.description

    return (
        WHERE_ENTRY_PREFIX
        + token(where.placeholder)
        + " "
        + body
        + "."
    )


def value_text(
    value: object,
    *,
    indent: int | None = None,
) -> str:
    """Return canonical JSON text."""
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
    )


def _block(
    identifier: str,
    form: str,
    body: str,
) -> str:
    if any(line == ">>" for line in body.splitlines()):
        raise ValueError(
            f"constant {identifier} body contains the closing line >>"
        )

    separator = "" if body.endswith("\n") else "\n"
    return (
        f"{identifier}: {form}<<\n"
        f"{body}"
        f"{separator}"
        ">>"
    )


def _csv_body(value: list[dict[str, object]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=list(value[0]),
        lineterminator="\n",
    )
    writer.writeheader()

    for row in value:
        writer.writerow(
            {
                key: (
                    json.dumps(cell, ensure_ascii=False)
                    if not isinstance(cell, str)
                    else cell
                )
                for key, cell in row.items()
            }
        )

    return stream.getvalue().rstrip("\n")


def constant_text(constant: Constant) -> str:
    """Return one inline or block constant entry."""
    if constant.form == "inline":
        return f"{constant.id}: {value_text(constant.value)}"

    if constant.form == "text":
        if not isinstance(constant.value, str):
            raise TypeError("a text constant must contain text")
        return _block(
            constant.id,
            "TEXT",
            constant.value,
        )

    if constant.form == "json":
        return _block(
            constant.id,
            "JSON",
            value_text(constant.value, indent=2),
        )

    if constant.form == "csv":
        if not isinstance(constant.value, list):
            raise TypeError("a CSV constant must contain rows")
        return _block(
            constant.id,
            "CSV",
            _csv_body(constant.value),
        )

    if constant.form == "yaml":
        body = yaml.safe_dump(
            constant.value,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        ).rstrip("\n")
        return _block(
            constant.id,
            "YAML",
            body,
        )

    raise TypeError(
        f"unsupported constant form {constant.form}"
    )


def named_value_line(entry: State) -> str:
    """Return one state value line."""
    return f"{entry.id}: {value_text(entry.value)}"


def _path(
    part: str,
    identifier: str,
    placeholder: str | None = None,
) -> str:
    text = f"{part}.{identifier}"
    if placeholder is not None:
        text += f".{placeholder}"
    return _DOTTED_PATH_ADAPTER.validate_python(text)


def _reference(path: str) -> str:
    return _VALUE_REFERENCE_ADAPTER.validate_python(
        f"${path}"
    )


def process_value_text(value: Value) -> str:
    """Return one JSON literal or process value reference."""
    match value:
        case LiteralValue():
            return value_text(value.value)
        case ConstantValue():
            return _reference(
                _path("constant", value.constant)
            )
        case StateValue():
            return _reference(
                _path("state", value.state)
            )
        case InterfaceValue():
            return _reference(
                _path(
                    "interface",
                    value.interface,
                    value.placeholder,
                )
            )
        case BindingValue():
            return _reference(value.binding)

    raise TypeError(
        f"unsupported process value {type(value).__name__}"
    )


def condition_text(condition: Condition) -> str:
    """Return one process or trigger condition."""
    operator = (
        "equals"
        if condition.operator == "equals"
        else "does not equal"
    )
    return (
        f"{process_value_text(condition.left)} "
        f"{operator} "
        f"{process_value_text(condition.right)}"
    )


def _binding_line(
    binding: ValueBinding,
    indent: int,
) -> str:
    return (
        " " * indent
        + f"{binding.placeholder} = "
        + process_value_text(binding.value)
    )


def _step_lines(
    step: Step,
    indent: int,
) -> list[str]:
    prefix = " " * indent
    inner = indent + 2

    if isinstance(step, Act):
        lines = [
            prefix + f"ACT {step.instruction}"
        ]

        if step.inputs:
            lines.append(
                " " * inner + "INPUTS:"
            )
            lines.extend(
                _binding_line(binding, inner + 2)
                for binding in step.inputs
            )

        if step.outputs:
            lines.append(
                " " * inner
                + "OUTPUTS: "
                + ", ".join(step.outputs)
            )

        return lines

    if isinstance(step, Set):
        return [
            prefix
            + "SET "
            + _path("state", step.state)
            + " = "
            + process_value_text(step.value)
        ]

    if isinstance(step, Emit):
        lines = [
            prefix
            + "EMIT "
            + _path("interface", step.interface)
            + ":"
        ]
        lines.extend(
            _binding_line(binding, inner)
            for binding in step.bindings
        )
        return lines

    if isinstance(step, If):
        lines = [
            prefix
            + f"IF {condition_text(step.condition)}:"
        ]

        for child in step.then:
            lines.extend(
                _step_lines(child, inner)
            )

        if step.otherwise is not None:
            lines.append(
                prefix + "ELSE:"
            )
            for child in step.otherwise:
                lines.extend(
                    _step_lines(child, inner)
                )

        return lines

    if isinstance(step, Call):
        return [
            prefix
            + "CALL "
            + _path("process", step.process)
        ]

    if isinstance(step, Fail):
        return [
            prefix
            + f"FAIL {value_text(step.message)}"
        ]

    raise TypeError(
        f"unsupported process step {type(step).__name__}"
    )


def process_lines(process: Process) -> list[str]:
    """Return the process steps in authored order."""
    lines: list[str] = []

    for step in process.steps:
        lines.extend(
            _step_lines(step, 0)
        )

    return lines


def interface_body(interface: Interface) -> str:
    """Return the interface description or empty text."""
    return interface.description or ""
