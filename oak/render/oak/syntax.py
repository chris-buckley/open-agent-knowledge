"""The text syntax of OAK entry bodies."""

from __future__ import annotations

import csv
import io
import json

import yaml

from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes import (
    Act,
    All,
    Any,
    Assert,
    BindingValue,
    Call,
    Compare,
    Condition,
    ConstantValue,
    Emit,
    Fail,
    Foreach,
    If,
    InterfaceValue,
    Join,
    LiteralValue,
    Not,
    Par,
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
from oak.surface import surface_for
from oak.vocabulary.text.placeholder import token

WHERE_HEADING = "WHERE:"
WHERE_ENTRY_PREFIX = "- "
WHERE_DETAIL_SEPARATOR = "; "


def _scalar(value: str | int | float | bool) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


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
        return "has at most 1 line" if constraint.max == 1 else f"has at most {constraint.max} lines"
    return f"has at least {constraint.min} lines"


def constraint_text(constraint: Constraint) -> str:
    """Return the OAK text for one schema constraint."""
    surface_for(constraint)
    match constraint:
        case Type():
            return f"is {constraint.of}"
        case OneOf():
            return "is one of " + ", ".join(f"`{_scalar(value)}`" for value in constraint.values)
        case Regex():
            return f"matches `{constraint.pattern}`"
        case NonEmpty():
            return "is non-empty"
        case MaxChars():
            return f"is at most {constraint.n} characters"
        case Lines():
            return _lines(constraint)
        case ListOf():
            return f"is a list of {constraint.item} joined by `{constraint.separator}`"
        case AtLeast():
            return f"is at least {_bound(constraint.value)}"
        case AtMost():
            return f"is at most {_bound(constraint.value)}"
    raise TypeError(f"unsupported constraint {type(constraint).__name__}")


def where_line(where: Where) -> str:
    """Return one dense line for a schema placeholder."""
    surface_for(where)
    body = WHERE_DETAIL_SEPARATOR.join(constraint_text(item) for item in where.constraints)
    if where.examples:
        body += " (e.g. " + ", ".join(f"`{_scalar(example)}`" for example in where.examples) + ")"
    if where.description is not None:
        body += WHERE_DETAIL_SEPARATOR + where.description
    return WHERE_ENTRY_PREFIX + token(where.placeholder) + " " + body + "."


def value_text(value: object, *, indent: int | None = None) -> str:
    """Return canonical JSON text."""
    return json.dumps(value, ensure_ascii=False, indent=indent)


def _block(identifier: str, form: str, body: str) -> str:
    if any(line == ">>" for line in body.splitlines()):
        raise ValueError(f"constant {identifier} body contains the closing line >>")
    separator = "" if body.endswith("\n") else "\n"
    return f"{identifier}: {form}<<\n{body}{separator}>>"


def _csv_body(value: list[dict[str, object]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(value[0]), lineterminator="\n")
    writer.writeheader()
    for row in value:
        writer.writerow({key: json.dumps(cell, ensure_ascii=False) if not isinstance(cell, str) else cell for key, cell in row.items()})
    return stream.getvalue().rstrip("\n")


def constant_text(constant: Constant) -> str:
    """Return one inline or block constant entry."""
    surface_for(constant)
    if constant.form == "inline":
        return f"{constant.id}: {value_text(constant.value)}"
    if constant.form == "text":
        if not isinstance(constant.value, str):
            raise TypeError("a text constant must contain text")
        return _block(constant.id, "TEXT", constant.value)
    if constant.form == "json":
        return _block(constant.id, "JSON", value_text(constant.value, indent=2))
    if constant.form == "csv":
        if not isinstance(constant.value, list):
            raise TypeError("a CSV constant must contain rows")
        return _block(constant.id, "CSV", _csv_body(constant.value))
    if constant.form == "yaml":
        body = yaml.safe_dump(constant.value, allow_unicode=True, default_flow_style=False, sort_keys=False).rstrip("\n")
        return _block(constant.id, "YAML", body)
    raise TypeError(f"unsupported constant form {constant.form}")


def named_value_line(entry: State) -> str:
    """Return one state value line."""
    surface_for(entry)
    return f"{entry.id}: {value_text(entry.value)}"


def process_value_text(value: Value) -> str:
    """Return one JSON literal or process value reference."""
    surface_for(value)
    match value:
        case LiteralValue():
            return value_text(value.value)
        case ConstantValue():
            return "$" + value.constant
        case StateValue():
            return "$" + value.state
        case InterfaceValue():
            return "$" + value.interface + "." + value.placeholder
        case BindingValue():
            return "$" + value.binding
    raise TypeError(f"unsupported process value {type(value).__name__}")


_OPERATOR_TEXT = {
    "equals": "equals",
    "not_equals": "does not equal",
    "less_than": "is less than",
    "less_than_or_equal": "is at most",
    "greater_than": "is greater than",
    "greater_than_or_equal": "is at least",
}


def condition_lines(condition: Condition, indent: int = 0) -> list[str]:
    """Return one recursive condition in prefix form."""
    surface_for(condition)
    prefix = " " * indent
    if isinstance(condition, Compare):
        return [
            prefix
            + process_value_text(condition.left)
            + " "
            + _OPERATOR_TEXT[condition.operator]
            + " "
            + process_value_text(condition.right)
        ]
    if isinstance(condition, (All, Any)):
        lines = [prefix + ("ALL:" if isinstance(condition, All) else "ANY:")]
        for child in condition.conditions:
            lines.extend(condition_lines(child, indent + 2))
        return lines
    if isinstance(condition, Not):
        return [prefix + "NOT:", *condition_lines(condition.condition, indent + 2)]
    raise TypeError(f"unsupported condition {type(condition).__name__}")


def condition_text(condition: Condition) -> str:
    """Return one recursive condition."""
    return "\n".join(condition_lines(condition))


def _binding_line(binding: ValueBinding, indent: int) -> str:
    surface_for(binding)
    return " " * indent + f"{binding.placeholder} = " + process_value_text(binding.value)


def _act_lines(step: Act, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    surface_for(step)
    if step.tool is None:
        lines = [prefix + "ACT " + step.instruction]
    else:
        lines = [prefix + "ACT TOOL " + value_text(step.tool) + ": " + step.instruction]
    if step.inputs:
        lines.append(" " * inner + "INPUTS:")
        lines.extend(_binding_line(binding, inner + 2) for binding in step.inputs)
    if step.outputs:
        lines.append(" " * inner + "OUTPUTS: " + ", ".join(step.outputs))
    return lines


def _step_lines(step: Step, indent: int) -> list[str]:
    prefix = " " * indent
    inner = indent + 2
    surface_for(step)
    if isinstance(step, Act):
        return _act_lines(step, indent)
    if isinstance(step, Set):
        return [prefix + "SET " + step.state + " = " + process_value_text(step.value)]
    if isinstance(step, Emit):
        return [prefix + "EMIT " + step.interface + ":", *(_binding_line(binding, inner) for binding in step.bindings)]
    if isinstance(step, If):
        condition = condition_lines(step.condition)
        if len(condition) == 1:
            lines = [prefix + "IF " + condition[0] + ":"]
        else:
            lines = [prefix + "IF:", *(" " * inner + line for line in condition)]
        lines.append(" " * inner + "THEN:")
        for child in step.then:
            lines.extend(_step_lines(child, inner + 2))
        if step.otherwise is not None:
            lines.append(" " * inner + "ELSE:")
            for child in step.otherwise:
                lines.extend(_step_lines(child, inner + 2))
        return lines
    if isinstance(step, Call):
        return [prefix + "CALL " + step.process]
    if isinstance(step, Fail):
        return [prefix + "FAIL " + value_text(step.message)]
    if isinstance(step, Assert):
        condition = condition_lines(step.condition)
        if len(condition) == 1:
            lines = [prefix + "ASSERT " + condition[0]]
        else:
            lines = [prefix + "ASSERT:", *(" " * inner + line for line in condition)]
        if step.message is not None:
            lines.append(" " * inner + "MESSAGE " + value_text(step.message))
        return lines
    if isinstance(step, Foreach):
        lines = [prefix + f"FOREACH {step.binding} IN {process_value_text(step.value)}:"]
        for child in step.steps:
            lines.extend(_step_lines(child, inner))
        return lines
    if isinstance(step, Par):
        lines = [prefix + "PAR:"]
        for child in step.steps:
            lines.extend(_step_lines(child, inner))
        return lines
    if isinstance(step, Join):
        return [prefix + "JOIN"]
    raise TypeError(f"unsupported process step {type(step).__name__}")


def process_lines(process: Process) -> list[str]:
    """Return process steps in authored order."""
    surface_for(process)
    lines: list[str] = []
    for step in process.steps:
        lines.extend(_step_lines(step, 0))
    return lines


def trigger_lines(trigger: object) -> list[str]:
    """Return one complete trigger triple."""
    from oak.node.parts.triggers import Trigger

    if not isinstance(trigger, Trigger):
        raise TypeError("trigger_lines needs Trigger")
    surface_for(trigger)
    if trigger.given is True:
        lines = ["GIVEN: true"]
    else:
        condition = condition_lines(trigger.given)
        if len(condition) == 1:
            lines = ["GIVEN: " + condition[0]]
        else:
            lines = ["GIVEN:", *("  " + line for line in condition)]
    lines.extend(("WHEN: " + value_text(trigger.when), "THEN: " + trigger.then))
    return lines


def interface_body(interface: Interface) -> str:
    """Return the interface description or empty text."""
    surface_for(interface)
    return interface.description or ""


def binding_line(binding: ValueBinding, indent: int = 0) -> str:
    """Return one process binding line."""
    return _binding_line(binding, indent)


def step_lines(step: Step, indent: int = 0) -> list[str]:
    """Return one typed step in OAK syntax."""
    return _step_lines(step, indent)
