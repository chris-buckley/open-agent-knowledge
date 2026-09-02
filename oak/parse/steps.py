"""Process step parsing with one shared source cursor."""

from __future__ import annotations

import json

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


def parse_steps(
    cursor: Cursor,
    indent: int,
    stop: set[str] | None = None,
) -> list[Step]:
    """Parse one ordered step sequence at the cursor."""
    result: list[Step] = []
    stop = stop or set()

    while not cursor.at_end:
        if cursor.peek() == "":
            cursor.advance()
            continue

        number = cursor.line_number
        actual = cursor.indentation()

        if actual < indent:
            break

        if actual > indent:
            cursor.fail(
                "step_indent",
                f"step needs {indent} spaces",
            )

        line = cursor.peek()
        if line is None:
            break

        text = line[indent:]

        if text in stop:
            break

        act_input: str | None = None
        act_output: str | None = None

        if text.startswith("ACT TOOL "):
            rest = text[len("ACT TOOL ") :]

            try:
                decoder = json.JSONDecoder()
                tool, consumed = decoder.raw_decode(rest)
            except json.JSONDecodeError as error:
                cursor.fail(
                    "act_tool",
                    str(error),
                )

            if not isinstance(tool, str):
                cursor.fail(
                    "act_tool",
                    "ACT TOOL needs one JSON string and colon",
                )

            remainder = rest[consumed:]
            attributes = parse_act_attributes(remainder)

            if attributes is not None:
                act_input, act_output, body = attributes
            elif remainder.startswith(": "):
                body = remainder[2:]
            else:
                cursor.fail(
                    "act_tool",
                    "ACT TOOL needs one JSON string and colon",
                )

        elif text.startswith("ACT "):
            tool = None
            attributes = parse_act_attributes(text[3:])

            if attributes is not None:
                act_input, act_output, body = attributes
            else:
                body = text[4:]

        else:
            body = None

        if body is not None:
            position = len(body)
            parsed = None

            while parsed is None:
                position = body.rfind(
                    " (",
                    0,
                    position,
                )

                if position == -1:
                    cursor.fail(
                        "act_suffix",
                        "ACT needs one (bindings) suffix",
                    )

                parsed = parse_suffix(
                    body[position + 1 :]
                )

            bindings, outputs = parsed
            result.append(
                Act(
                    tool=tool,
                    input=act_input,
                    output=act_output,
                    instruction=body[:position],
                    inputs=parse_suffix_bindings(
                        bindings,
                        cursor.path,
                        number,
                    ),
                    outputs=outputs,
                )
            )
            cursor.advance()
            continue

        if text.startswith("SET "):
            body = text[4:]

            if " = " not in body:
                cursor.fail(
                    "set",
                    "SET needs target = value",
                )

            target, value = body.split(
                " = ",
                1,
            )
            result.append(
                Set(
                    state=target,
                    value=parse_value(
                        value,
                        cursor.path,
                        number,
                    ),
                )
            )
            cursor.advance()
            continue

        if text.startswith("EMIT "):
            target, _, remainder = text[5:].partition(" ")
            parsed = parse_suffix(remainder)

            if parsed is None:
                cursor.fail(
                    "emit_suffix",
                    "EMIT needs target (bindings)",
                )

            bindings, outputs = parsed

            if outputs:
                cursor.fail(
                    "emit_suffix",
                    "EMIT takes no outputs",
                )

            result.append(
                Emit(
                    interface=target,
                    bindings=parse_suffix_bindings(
                        bindings,
                        cursor.path,
                        number,
                    ),
                )
            )
            cursor.advance()
            continue

        if text.startswith("IF ") and text.endswith(":"):
            condition = parse_compare(
                text[3:-1],
                cursor.path,
                number,
            )
            cursor.advance()

        elif text == "IF:":
            cursor.advance()
            condition = parse_condition(
                cursor,
                indent + 2,
            )

        else:
            condition = None

        if condition is not None:
            if (
                cursor.at_end
                or cursor.indentation() != indent + 2
                or cursor.peek()[indent + 2 :] != "THEN:"
            ):
                cursor.fail(
                    "if_then",
                    "IF needs THEN",
                )

            cursor.advance()
            then = parse_steps(
                cursor,
                indent + 4,
                {"ELSE:"},
            )
            otherwise = None

            if (
                not cursor.at_end
                and cursor.indentation() == indent + 2
                and cursor.peek()[indent + 2 :] == "ELSE:"
            ):
                cursor.advance()
                otherwise = parse_steps(
                    cursor,
                    indent + 4,
                )

            result.append(
                If(
                    condition=condition,
                    then=then,
                    otherwise=otherwise,
                )
            )
            continue

        if text.startswith("CALL "):
            target, _, remainder = text[5:].partition(" ")
            parsed = parse_suffix(remainder)

            if parsed is None:
                cursor.fail(
                    "call_suffix",
                    "CALL needs target (bindings)",
                )

            bindings, outputs = parsed
            result.append(
                Call(
                    process=target,
                    inputs=parse_suffix_bindings(
                        bindings,
                        cursor.path,
                        number,
                    ),
                    outputs=outputs,
                )
            )
            cursor.advance()
            continue

        if text.startswith("FAIL "):
            message = parse_json_value(
                text[5:],
                cursor.path,
                number,
            )

            if not isinstance(message, str):
                cursor.fail(
                    "fail_message",
                    "FAIL message must be a JSON string",
                )

            result.append(
                Fail(message=message)
            )
            cursor.advance()
            continue

        if text.startswith("ASSERT "):
            condition = parse_compare(
                text[7:],
                cursor.path,
                number,
            )
            cursor.advance()

        elif text == "ASSERT:":
            cursor.advance()
            condition = parse_condition(
                cursor,
                indent + 2,
            )

        else:
            condition = None

        if condition is not None:
            message = None

            if (
                not cursor.at_end
                and cursor.indentation() == indent + 2
                and cursor.peek()[indent + 2 :].startswith("MESSAGE ")
            ):
                raw = parse_json_value(
                    cursor.peek()[indent + 10 :],
                    cursor.path,
                    cursor.line_number,
                )

                if not isinstance(raw, str):
                    cursor.fail(
                        "assert_message",
                        "MESSAGE must be a JSON string",
                    )

                message = raw
                cursor.advance()

            result.append(
                Assert(
                    condition=condition,
                    message=message,
                )
            )
            continue

        if text.startswith("FOREACH ") and text.endswith(":"):
            body = text[8:-1]

            if " IN " not in body:
                cursor.fail(
                    "foreach",
                    "FOREACH needs binding IN value",
                )

            binding, value = body.split(
                " IN ",
                1,
            )
            cursor.advance()
            children = parse_steps(
                cursor,
                indent + 2,
            )
            result.append(
                Foreach(
                    binding=binding,
                    value=parse_value(
                        value,
                        cursor.path,
                        number,
                    ),
                    steps=children,
                )
            )
            continue

        if text.startswith("WHILE ") and text.endswith(":"):
            body = text[6:-1]

            if body.startswith("LIMIT "):
                limit_text = body[6:]

                if (
                    not limit_text.isdigit()
                    or int(limit_text) < 1
                ):
                    cursor.fail(
                        "while_limit",
                        "WHILE LIMIT must be a positive integer",
                    )

                cursor.advance()
                condition = parse_condition(
                    cursor,
                    indent + 2,
                )

                if (
                    cursor.at_end
                    or cursor.indentation() != indent + 2
                    or cursor.peek()[indent + 2 :] != "THEN:"
                ):
                    cursor.fail(
                        "while_then",
                        "recursive WHILE needs THEN",
                    )

                cursor.advance()
                children = parse_steps(
                    cursor,
                    indent + 4,
                )

            else:
                if " LIMIT " not in body:
                    cursor.fail(
                        "while",
                        "WHILE needs condition LIMIT positive-integer",
                    )

                condition_text, limit_text = body.rsplit(
                    " LIMIT ",
                    1,
                )

                if (
                    not limit_text.isdigit()
                    or int(limit_text) < 1
                ):
                    cursor.fail(
                        "while_limit",
                        "WHILE LIMIT must be a positive integer",
                    )

                condition = parse_compare(
                    condition_text,
                    cursor.path,
                    number,
                )
                cursor.advance()
                children = parse_steps(
                    cursor,
                    indent + 2,
                )

            result.append(
                While(
                    condition=condition,
                    limit=int(limit_text),
                    steps=children,
                )
            )
            continue

        if text == "PAR:":
            cursor.advance()
            children = parse_steps(
                cursor,
                indent + 2,
            )
            result.append(
                Par(steps=children)
            )
            continue

        if text == "JOIN":
            result.append(Join())
            cursor.advance()
            continue

        cursor.fail(
            "unknown_step",
            f"unknown process step {text}",
        )

    return result


__all__ = [
    "parse_steps",
]
