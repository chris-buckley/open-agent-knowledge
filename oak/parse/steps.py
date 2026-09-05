"""Ordered process statements with delimiter continuation and indented suites."""

from __future__ import annotations

import json
import re
from collections.abc import Set as AbstractSet

from oak.node.parts.processes.steps import (
    Act, Assert, Call, Emit, Fail, Foreach, If, Join, Par, Set, Step, While,
)
from oak.parse.cursor import Cursor
from oak.parse.errors import ParseError
from oak.parse.expressions import ExpressionReader
from oak.parse.values import parse_act_attributes
from oak.surface.syntax import INDENT_WIDTH


def _act_step(
    cursor: Cursor,
    tool: str | None,
    act_input: str | None,
    act_output: str | None,
    body: str,
) -> Act:
    """Locate the typed suffix without interpreting punctuation in ACT prose."""
    position = len(body)
    errors: list[ParseError] = []
    while True:
        position = body.rfind(" (", 0, position)
        if position == -1:
            if errors:
                # Prefer the actual continued binding's error to an earlier prose candidate.
                raise max(errors, key=lambda error: error.failure.line or 0)
            cursor.fail("act_suffix", "ACT needs one (bindings) suffix")
        reader = ExpressionReader.at(cursor, body[position + 1 :])
        reader.path += ".inputs"
        try:
            bindings, outputs = reader.suffix()
            reader.finish(cursor)
        except ParseError as error:
            errors.append(error)
            continue
        return Act(
            tool=tool, input=act_input, output=act_output,
            instruction=body[:position], inputs=bindings, outputs=outputs,
        )


def _parse_act(cursor: Cursor, text: str) -> Act:
    tool = None
    if text.startswith("ACT TOOL "):
        rest = text[len("ACT TOOL ") :]
        try:
            tool, consumed = json.JSONDecoder().raw_decode(rest)
        except json.JSONDecodeError as error:
            cursor.fail("act_tool", str(error))
        if not isinstance(tool, str):
            cursor.fail("act_tool", "ACT TOOL needs one JSON string and colon")
        remainder = rest[consumed:]
        attributes = parse_act_attributes(remainder)
        if attributes is not None:
            act_input, act_output, body = attributes
        elif remainder.startswith(": "):
            act_input, act_output, body = None, None, remainder[2:]
        else:
            cursor.fail("act_tool", "ACT TOOL needs one JSON string and colon")
    else:
        attributes = parse_act_attributes(text[3:])
        act_input, act_output, body = (
            attributes if attributes is not None else (None, None, text[4:])
        )
    return _act_step(cursor, tool, act_input, act_output, body)


def _suite(cursor: Cursor, indent: int) -> list[Step]:
    steps = parse_steps(cursor, indent + INDENT_WIDTH)
    if not steps:
        cursor.fail("empty_suite", "an action suite needs at least one step")
    return steps


def _blank_lines(cursor: Cursor) -> None:
    while cursor.peek() == "":
        cursor.advance()


def _parse_if(cursor: Cursor, indent: int, text: str) -> If:
    reader = ExpressionReader.at(cursor, text[3:])
    condition = reader.condition()
    reader.expect(":")
    reader.finish(cursor)
    then = _suite(cursor, indent)
    otherwise = None
    if cursor.peek() == " " * indent + "ELSE:":
        cursor.advance()
        otherwise = _suite(cursor, indent)
    return If(condition=condition, then=then, otherwise=otherwise)


def _parse_while(cursor: Cursor, indent: int, text: str) -> While:
    reader = ExpressionReader.at(cursor, text[6:])
    condition = reader.condition()
    reader.space()
    reader.expect("LIMIT")
    reader.space()
    start = reader.position
    match = re.match(r"[0-9]+", reader.source[start:])
    if match is None or int(match.group()) < 1:
        reader.fail("while_limit", "WHILE LIMIT must be a positive decimal integer literal")
    limit = int(match.group())
    reader.position += len(match.group())
    reader.expect(":")
    reader.finish(cursor)
    return While(condition=condition, limit=limit, steps=_suite(cursor, indent))


def _parse_assert(cursor: Cursor, indent: int, text: str) -> Assert:
    reader = ExpressionReader.at(cursor, text[7:])
    condition = reader.condition()
    reader.finish(cursor)
    _blank_lines(cursor)
    message = None
    line = cursor.peek()
    prefix = " " * (indent + INDENT_WIDTH) + "MESSAGE "
    if line is not None and line.startswith(prefix):
        metadata = ExpressionReader.at(cursor, line[len(prefix) :])
        metadata.path += ".message"
        message = metadata.string()
        metadata.finish(cursor)
    return Assert(condition=condition, message=message)


def _parse_step(cursor: Cursor, indent: int, text: str) -> Step:
    if text.startswith("ACT "):
        return _parse_act(cursor, text)
    if text.startswith("IF "):
        return _parse_if(cursor, indent, text)
    if text.startswith("WHILE "):
        return _parse_while(cursor, indent, text)
    if text.startswith("ASSERT "):
        return _parse_assert(cursor, indent, text)
    if text.startswith("CALL "):
        reader = ExpressionReader.at(cursor, text[5:])
        process = reader.target("process")
        reader.space()
        inputs, outputs = reader.suffix()
        reader.finish(cursor)
        return Call(process=process, inputs=inputs, outputs=outputs)
    if text.startswith("SET "):
        reader = ExpressionReader.at(cursor, text[4:])
        state = reader.target("state")
        reader.expect("=")
        value = reader.value()
        reader.finish(cursor)
        return Set(state=state, value=value)
    if text.startswith("EMIT "):
        reader = ExpressionReader.at(cursor, text[5:])
        interface = reader.target("interface")
        reader.skip()
        bindings = []
        if reader.source.startswith("(", reader.position):
            bindings = reader.bindings()
            if not bindings:
                reader.fail("emit_empty_bindings", "EMIT () is invalid; omit the suffix")
        reader.finish(cursor)
        return Emit(interface=interface, bindings=bindings)
    if text.startswith("FAIL "):
        reader = ExpressionReader.at(cursor, text[5:])
        message = reader.string()
        reader.finish(cursor)
        return Fail(message=message)
    if text.startswith("FOREACH "):
        reader = ExpressionReader.at(cursor, text[8:])
        binding = reader.placeholder()
        reader.space()
        reader.expect("IN")
        reader.space()
        value = reader.value()
        reader.expect(":")
        reader.finish(cursor)
        return Foreach(binding=binding, value=value, steps=_suite(cursor, indent))
    if text == "PAR:":
        cursor.advance()
        return Par(steps=_suite(cursor, indent))
    if text == "JOIN":
        cursor.advance()
        return Join()
    cursor.fail("unknown_step", f"unknown process step {text}")


def parse_steps(
    cursor: Cursor, indent: int, stop: AbstractSet[str] | None = None,
) -> list[Step]:
    """Parse one ordered suite; a dedent belongs to its caller, including ELSE."""
    steps: list[Step] = []
    stop = stop or frozenset()
    while not cursor.at_end:
        _blank_lines(cursor)
        if cursor.at_end:
            break
        actual = cursor.indentation()
        if actual < indent:
            break
        if actual > indent:
            cursor.fail("step_indent", f"step needs {indent} spaces")
        text = cursor.peek()[indent:]
        if text in stop:
            break
        steps.append(_parse_step(cursor, indent, text))
    return steps


__all__ = ["parse_steps"]
