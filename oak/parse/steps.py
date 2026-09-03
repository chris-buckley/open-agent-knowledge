"""Process step parsing with one shared source cursor."""

from __future__ import annotations

import json
from collections.abc import Set as AbstractSet

from oak.node.parts.processes.conditions import Condition
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
from oak.parse.conditions import parse_compare, parse_condition
from oak.parse.cursor import Cursor
from oak.parse.data import parse_json_value
from oak.parse.values import (
    parse_act_attributes,
    parse_suffix,
    parse_suffix_bindings,
    parse_value,
)


def _act_step(
    cursor: Cursor,
    number: int,
    tool: str | None,
    act_input: str | None,
    act_output: str | None,
    body: str,
) -> Act:
    position = len(body)
    parsed = None

    while parsed is None:
        position = body.rfind(" (", 0, position)

        if position == -1:
            cursor.fail("act_suffix", "ACT needs one (bindings) suffix")

        parsed = parse_suffix(body[position + 1 :])

    bindings, outputs = parsed
    cursor.advance()
    return Act(
        tool=tool,
        input=act_input,
        output=act_output,
        instruction=body[:position],
        inputs=parse_suffix_bindings(bindings, cursor.path, number),
        outputs=outputs,
    )


def _parse_tool_act(cursor: Cursor, text: str, number: int) -> Act:
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

    return _act_step(cursor, number, tool, act_input, act_output, body)


def _parse_act(cursor: Cursor, text: str, number: int) -> Act:
    attributes = parse_act_attributes(text[3:])

    if attributes is not None:
        act_input, act_output, body = attributes
    else:
        act_input, act_output, body = None, None, text[4:]

    return _act_step(cursor, number, None, act_input, act_output, body)


def _parse_set(cursor: Cursor, text: str, number: int) -> Set:
    body = text[4:]

    if " = " not in body:
        cursor.fail("set", "SET needs target = value")

    target, value = body.split(" = ", 1)
    cursor.advance()
    return Set(state=target, value=parse_value(value, cursor.path, number))


def _parse_emit(cursor: Cursor, text: str, number: int) -> Emit:
    target, _, remainder = text[5:].partition(" ")
    parsed = parse_suffix(remainder)

    if parsed is None:
        cursor.fail("emit_suffix", "EMIT needs target (bindings)")

    bindings, outputs = parsed

    if outputs:
        cursor.fail("emit_suffix", "EMIT takes no outputs")

    cursor.advance()
    return Emit(
        interface=target,
        bindings=parse_suffix_bindings(bindings, cursor.path, number),
    )


def _parse_call(cursor: Cursor, text: str, number: int) -> Call:
    target, _, remainder = text[5:].partition(" ")
    parsed = parse_suffix(remainder)

    if parsed is None:
        cursor.fail("call_suffix", "CALL needs target (bindings)")

    bindings, outputs = parsed
    cursor.advance()
    return Call(
        process=target,
        inputs=parse_suffix_bindings(bindings, cursor.path, number),
        outputs=outputs,
    )


def _parse_fail(cursor: Cursor, text: str, number: int) -> Fail:
    message = parse_json_value(text[5:], cursor.path, number)

    if not isinstance(message, str):
        cursor.fail("fail_message", "FAIL message must be a JSON string")

    cursor.advance()
    return Fail(message=message)


def _keyword_condition(
    cursor: Cursor,
    indent: int,
    inline: str | None,
    number: int,
) -> Condition:
    """Parse one inline comparison or, when inline is None, one block condition."""
    if inline is not None:
        condition = parse_compare(inline, cursor.path, number)
        cursor.advance()
        return condition

    cursor.advance()
    return parse_condition(cursor, indent + 2)


def _at_keyword(cursor: Cursor, indent: int, keyword: str) -> bool:
    line = cursor.peek()
    return (
        line is not None
        and cursor.indentation() == indent + 2
        and line[indent + 2 :] == keyword
    )


def _parse_if(cursor: Cursor, indent: int, text: str, number: int) -> If:
    condition = _keyword_condition(
        cursor,
        indent,
        text[3:-1] if text != "IF:" else None,
        number,
    )

    if not _at_keyword(cursor, indent, "THEN:"):
        cursor.fail("if_then", "IF needs THEN")

    cursor.advance()
    then = parse_steps(cursor, indent + 4, {"ELSE:"})
    otherwise = None

    if _at_keyword(cursor, indent, "ELSE:"):
        cursor.advance()
        otherwise = parse_steps(cursor, indent + 4)

    return If(condition=condition, then=then, otherwise=otherwise)


def _parse_assert(cursor: Cursor, indent: int, text: str, number: int) -> Assert:
    condition = _keyword_condition(
        cursor,
        indent,
        text[7:] if text != "ASSERT:" else None,
        number,
    )
    message = None
    line = cursor.peek()

    if (
        line is not None
        and cursor.indentation() == indent + 2
        and line[indent + 2 :].startswith("MESSAGE ")
    ):
        raw = parse_json_value(line[indent + 10 :], cursor.path, cursor.line_number)

        if not isinstance(raw, str):
            cursor.fail("assert_message", "MESSAGE must be a JSON string")

        message = raw
        cursor.advance()

    return Assert(condition=condition, message=message)


def _parse_foreach(cursor: Cursor, indent: int, text: str, number: int) -> Foreach:
    body = text[8:-1]

    if " IN " not in body:
        cursor.fail("foreach", "FOREACH needs binding IN value")

    binding, value = body.split(" IN ", 1)
    cursor.advance()
    children = parse_steps(cursor, indent + 2)
    return Foreach(
        binding=binding,
        value=parse_value(value, cursor.path, number),
        steps=children,
    )


def _while_limit(cursor: Cursor, limit_text: str) -> int:
    if not limit_text.isdigit() or int(limit_text) < 1:
        cursor.fail("while_limit", "WHILE LIMIT must be a positive integer")

    return int(limit_text)


def _parse_while(cursor: Cursor, indent: int, text: str, number: int) -> While:
    body = text[6:-1]

    if body.startswith("LIMIT "):
        limit = _while_limit(cursor, body[6:])
        cursor.advance()
        condition = parse_condition(cursor, indent + 2)

        if not _at_keyword(cursor, indent, "THEN:"):
            cursor.fail("while_then", "recursive WHILE needs THEN")

        cursor.advance()
        children = parse_steps(cursor, indent + 4)

    else:
        if " LIMIT " not in body:
            cursor.fail("while", "WHILE needs condition LIMIT positive-integer")

        condition_text, limit_text = body.rsplit(" LIMIT ", 1)
        limit = _while_limit(cursor, limit_text)
        condition = parse_compare(condition_text, cursor.path, number)
        cursor.advance()
        children = parse_steps(cursor, indent + 2)

    return While(condition=condition, limit=limit, steps=children)


def _parse_par(cursor: Cursor, indent: int) -> Par:
    cursor.advance()
    return Par(steps=parse_steps(cursor, indent + 2))


def _parse_step(cursor: Cursor, indent: int, text: str) -> Step:
    number = cursor.line_number

    if text.startswith("ACT TOOL "):
        return _parse_tool_act(cursor, text, number)

    if text.startswith("ACT "):
        return _parse_act(cursor, text, number)

    if text.startswith("SET "):
        return _parse_set(cursor, text, number)

    if text.startswith("EMIT "):
        return _parse_emit(cursor, text, number)

    if (text.startswith("IF ") and text.endswith(":")) or text == "IF:":
        return _parse_if(cursor, indent, text, number)

    if text.startswith("CALL "):
        return _parse_call(cursor, text, number)

    if text.startswith("FAIL "):
        return _parse_fail(cursor, text, number)

    if text.startswith("ASSERT ") or text == "ASSERT:":
        return _parse_assert(cursor, indent, text, number)

    if text.startswith("FOREACH ") and text.endswith(":"):
        return _parse_foreach(cursor, indent, text, number)

    if text.startswith("WHILE ") and text.endswith(":"):
        return _parse_while(cursor, indent, text, number)

    if text == "PAR:":
        return _parse_par(cursor, indent)

    if text == "JOIN":
        cursor.advance()
        return Join()

    cursor.fail("unknown_step", f"unknown process step {text}")


def parse_steps(
    cursor: Cursor,
    indent: int,
    stop: AbstractSet[str] | None = None,
) -> list[Step]:
    """Parse one ordered step sequence at the cursor."""
    steps: list[Step] = []
    stop = stop or frozenset()

    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue

        actual = cursor.indentation()

        if actual < indent:
            break

        if actual > indent:
            cursor.fail("step_indent", f"step needs {indent} spaces")

        line = cursor.peek()
        if line is None:
            break

        text = line[indent:]

        if text in stop:
            break

        steps.append(_parse_step(cursor, indent, text))

    return steps


__all__ = [
    "parse_steps",
]
