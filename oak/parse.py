"""Parse one XML- or markdown-grouped OAK document into one Node."""

from __future__ import annotations

import csv
import html
import io
import json
import re
from dataclasses import dataclass
from typing import Iterable, Literal

import yaml
from pydantic import ValidationError

from oak.node import Node
from oak.node.interpretation import BUILT_IN_INSTRUCTIONS
from oak.node.parts import (
    Act,
    All,
    Any,
    Assert,
    AtLeast,
    AtMost,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    Foreach,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    Join,
    Lines,
    ListOf,
    LiteralValue,
    MaxChars,
    NonEmpty,
    Not,
    OneOf,
    Par,
    Process,
    Regex,
    Schema,
    Set,
    State,
    StateValue,
    Trigger,
    Type,
    ValueBinding,
    Where,
    While,
)
from oak.node.parts.processes.operators import OPERATOR_PHRASES
from oak.node.structure import PART_ORDER
from oak.surface import entry_surface
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX

GroupingName = Literal["xml", "markdown"]

_AS_CLAUSE = r"(?: AS ([^ :]+?)\.(" + PLACEHOLDER_SYNTAX.body + r"))?"

_BLOCK_CONSTANT_OPEN = re.compile(
    r"^([a-z][a-z0-9]*(?:-[a-z0-9]+)*)" + _AS_CLAUSE + r": (TEXT|JSON|CSV|YAML)<<$"
)


@dataclass(frozen=True, slots=True)
class ParseFailure:
    """One stable OAK parse failure."""

    code: str
    path: str
    line: int | None
    message: str

    def __str__(self) -> str:
        location = self.path
        if self.line is not None:
            location += f":{self.line}"
        return f"[{self.code}] {location}: {self.message}"


class OakParseError(ValueError):
    """Every failure collected while parsing one OAK document."""

    code = "oak_parse_invalid"

    def __init__(self, failures: Iterable[ParseFailure]) -> None:
        self.failures = tuple(failures)
        super().__init__("\n".join(str(failure) for failure in self.failures))


class _Parse(ValueError):
    def __init__(self, code: str, path: str, line: int | None, message: str) -> None:
        self.failure = ParseFailure(code, path, line, message)
        super().__init__(str(self.failure))


def _fail(code: str, path: str, line: int | None, message: str) -> None:
    raise _Parse(code, path, line, message)


def _source_text(source: str | bytes) -> str:
    if isinstance(source, bytes):
        try:
            source = source.decode("utf-8")
        except UnicodeDecodeError as error:
            raise OakParseError((ParseFailure("invalid_utf8", "$", None, str(error)),)) from None
    return source.replace("\r\n", "\n").replace("\r", "\n")


def _infer_grouping(text: str) -> GroupingName:
    first = text.partition("\n")[0]
    if first in {f"<{part}>" for part in PART_ORDER}:
        return "xml"
    if first in {f"~~~~{part}" for part in PART_ORDER}:
        return "markdown"
    _fail("unknown_grouping", "$", 1, "document must start with one part delimiter")


def _parts(text: str, grouping: GroupingName) -> dict[str, tuple[list[str], int]]:
    lines = text.splitlines()
    index = 0
    result: dict[str, tuple[list[str], int]] = {}
    for part in PART_ORDER:
        opening = f"<{part}>" if grouping == "xml" else f"~~~~{part}"
        closing = f"</{part}>" if grouping == "xml" else "~~~~"
        position = index
        if result:
            if position < len(lines) and lines[position] == opening:
                _fail("part_separator", part, position + 1, "parts need one blank line between them")
            if position >= len(lines) or lines[position] != "":
                continue
            position += 1
        if position >= len(lines) or lines[position] != opening:
            continue
        index = position
        start = index + 2
        index += 1
        body: list[str] = []
        block: tuple[str, int] | None = None
        depth = 1
        while index < len(lines):
            line = lines[index]
            if block is None:
                if grouping == "xml":
                    if line == opening:
                        depth += 1
                    elif line == closing:
                        depth -= 1
                        if depth == 0:
                            break
                elif line == closing:
                    break
            body.append(line)
            if part == "constants":
                match = _BLOCK_CONSTANT_OPEN.fullmatch(line)
                if block is None and match is not None:
                    block = (match.group(1), index + 1)
                elif block is not None and line == ">>":
                    block = None
            index += 1
        if block is not None:
            _fail(
                "block_constant_unterminated",
                f"constants.{block[0]}",
                block[1],
                "missing >>",
            )
        if index >= len(lines):
            _fail("part_unterminated", part, start, f"missing {closing}")
        result[part] = body, start
        index += 1
    if index != len(lines):
        _fail("part_order", "$", index + 1, "parts appear once in OAK order")
    return result


def _xml_attributes(line: str, tag: str, path: str, number: int) -> dict[str, str]:
    if not line.startswith(f"<{tag}") or not line.endswith(">"):
        _fail("entry_open", path, number, f"expected <{tag}> entry")
    source = line[len(tag) + 1 : -1].strip()
    attributes: dict[str, str] = {}
    pattern = re.compile(r'([A-Za-z_][A-Za-z0-9_-]*)=("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')')
    position = 0
    for match in pattern.finditer(source):
        if source[position : match.start()].strip():
            _fail("entry_attribute", path, number, "invalid XML-like attribute syntax")
        key = match.group(1)
        raw = match.group(2)
        attributes[key] = html.unescape(raw[1:-1])
        position = match.end()
    if source[position:].strip():
        _fail("entry_attribute", path, number, "invalid XML-like attribute syntax")
    return attributes


def _markdown_attributes(line: str, tag: str, path: str, number: int) -> dict[str, str]:
    prefix = f"~~~{tag}"
    if not line.startswith(prefix):
        _fail("entry_open", path, number, f"expected {prefix}")
    tail = line[len(prefix) :]
    attributes: dict[str, str] = {}
    if not tail:
        return attributes
    if not tail.startswith(";"):
        _fail("entry_attribute", path, number, "markdown attributes must start with ;")
    for item in tail[1:].split(";"):
        if "=" not in item:
            _fail("entry_attribute", path, number, "markdown attribute needs =")
        key, raw = item.split("=", 1)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            _fail("entry_attribute", path, number, str(error))
        if not isinstance(value, str):
            _fail("entry_attribute", path, number, "markdown attribute must be a JSON string")
        attributes[key] = value
    return attributes


def _entries(
    lines: list[str],
    start: int,
    tag: str,
    grouping: GroupingName,
    path: str,
) -> list[tuple[dict[str, str], list[str], int]]:
    entry_surface(tag)
    result: list[tuple[dict[str, str], list[str], int]] = []
    index = 0
    while index < len(lines):
        if lines[index] == "":
            index += 1
            continue
        number = start + index
        attributes = (
            _xml_attributes(lines[index], tag, path, number)
            if grouping == "xml"
            else _markdown_attributes(lines[index], tag, path, number)
        )
        closing = f"</{tag}>" if grouping == "xml" else "~~~"
        index += 1
        body: list[str] = []
        depth = 1
        while index < len(lines):
            line = lines[index]
            if grouping == "xml":
                if line == f"<{tag}>" or line.startswith(f"<{tag} "):
                    depth += 1
                elif line == closing:
                    depth -= 1
                    if depth == 0:
                        break
            elif line == closing:
                break
            body.append(line)
            index += 1
        if index >= len(lines):
            _fail("entry_unterminated", path, number, f"missing {closing}")
        result.append((attributes, body, number))
        index += 1
    return result


def _instructions(lines: list[str], start: int) -> list[Instruction]:
    authored = [line for line in lines if line and line not in BUILT_IN_INSTRUCTIONS]
    return [Instruction(id=f"instruction-{index}", body=line) for index, line in enumerate(authored, 1)]


def _json_value(source: str, path: str, line: int) -> object:
    try:
        return json.loads(source)
    except json.JSONDecodeError as error:
        _fail("invalid_json", path, line, str(error))


def _csv_value(body: str, path: str, line: int) -> list[dict[str, object]]:
    try:
        rows = list(csv.DictReader(io.StringIO(body)))
    except csv.Error as error:
        _fail("invalid_csv", path, line, str(error))
    result: list[dict[str, object]] = []
    for row in rows:
        converted: dict[str, object] = {}
        for key, value in row.items():
            if key is None or value is None:
                _fail("invalid_csv", path, line, "CSV row has an absent key or value")
            try:
                converted[key] = json.loads(value)
            except json.JSONDecodeError:
                converted[key] = value
        result.append(converted)
    return result


def _named_values(lines: list[str], start: int, *, constants: bool) -> list[Constant] | list[State]:
    result: list[Constant] | list[State] = []
    index = 0
    inline = re.compile(r"^([a-z][a-z0-9]*(?:-[a-z0-9]+)*)" + _AS_CLAUSE + r": (.+)$")
    while index < len(lines):
        if lines[index] == "":
            index += 1
            continue
        number = start + index
        block_match = _BLOCK_CONSTANT_OPEN.fullmatch(lines[index])
        if block_match:
            identifier, schema_target, placeholder, form = block_match.groups()
            index += 1
            body_lines: list[str] = []
            while index < len(lines) and lines[index] != ">>":
                body_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                _fail("block_constant_unterminated", f"constants.{identifier}", number, "missing >>")
            body = "\n".join(body_lines)
            index += 1
            if not constants:
                _fail("invalid_state", "state", number, "state does not accept block values")
            if form == "TEXT":
                value: object = body
                constant_form = "text"
            elif form == "JSON":
                value = _json_value(body, f"constants.{identifier}", number)
                constant_form = "json"
            elif form == "CSV":
                value = _csv_value(body, f"constants.{identifier}", number)
                constant_form = "csv"
            else:
                try:
                    value = yaml.safe_load(body)
                except yaml.YAMLError as error:
                    _fail("invalid_yaml", f"constants.{identifier}", number, str(error))
                constant_form = "yaml"
            result.append(Constant(id=identifier, form=constant_form, schema=schema_target, placeholder=placeholder, value=value))
            continue
        inline_match = inline.fullmatch(lines[index])
        if inline_match is None:
            _fail("named_value", "constants" if constants else "state", number, "expected id: JSON")
        identifier, schema_target, placeholder, source = inline_match.groups()
        value = _json_value(source, f"{'constants' if constants else 'state'}.{identifier}", number)
        if constants:
            result.append(Constant(id=identifier, schema=schema_target, placeholder=placeholder, value=value))
        else:
            result.append(State(id=identifier, schema=schema_target, placeholder=placeholder, value=value))
        index += 1
    return result


def _constraint(source: str, path: str, line: int):
    if source.startswith("is one of "):
        values = []
        for raw in re.findall(r"`([^`]*)`", source[len("is one of ") :]):
            try:
                values.append(json.loads(raw))
            except json.JSONDecodeError:
                values.append(raw)
        return OneOf(values=values)
    if source.startswith("matches `") and source.endswith("`"):
        return Regex(pattern=source[9:-1])
    if source == "is non-empty":
        return NonEmpty()
    match = re.fullmatch(r"is at most ([0-9]+) characters", source)
    if match:
        return MaxChars(n=int(match.group(1)))
    if source == "is one line":
        return Lines(min=1, max=1)
    match = re.fullmatch(r"has ([0-9]+) lines", source)
    if match:
        value = int(match.group(1))
        return Lines(min=value, max=value)
    match = re.fullmatch(r"has ([0-9]+) to ([0-9]+) lines", source)
    if match:
        return Lines(min=int(match.group(1)), max=int(match.group(2)))
    match = re.fullmatch(r"has at most ([0-9]+) line(?:s)?", source)
    if match:
        return Lines(max=int(match.group(1)))
    match = re.fullmatch(r"has at least ([0-9]+) line(?:s)?", source)
    if match:
        return Lines(min=int(match.group(1)))
    match = re.fullmatch(r"is a list of ([a-z]+) joined by `([^`]*)`", source)
    if match:
        return ListOf(item=match.group(1), separator=match.group(2))
    if source.startswith("is at least "):
        raw = source[len("is at least ") :]
        value = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else _json_value(raw, path, line)
        return AtLeast(value=value)
    if source.startswith("is at most "):
        raw = source[len("is at most ") :]
        value = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else _json_value(raw, path, line)
        return AtMost(value=value)
    if source.startswith("is "):
        return Type(of=source[3:])
    return None


def _where(line_text: str, path: str, line: int) -> Where:
    match = re.fullmatch(r"- <([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)> (.*)\.", line_text)
    if match is None:
        _fail("where_line", path, line, "invalid WHERE line")
    placeholder, body = match.groups()
    example_match = re.search(r" \(e\.g\. (.*?)\)", body)
    examples: list[object] = []
    if example_match:
        for raw in re.findall(r"`([^`]*)`", example_match.group(1)):
            try:
                examples.append(json.loads(raw))
            except json.JSONDecodeError:
                examples.append(raw)
        body = body[: example_match.start()] + body[example_match.end() :]
    constraints = []
    description = None
    for segment in body.split("; "):
        item = _constraint(segment, path, line)
        if item is None:
            if description is not None:
                _fail("where_description", path, line, "WHERE has more than one description segment")
            description = segment
        else:
            constraints.append(item)
    if not constraints:
        _fail("where_constraint", path, line, "WHERE needs at least one constraint")
    return Where(placeholder=placeholder, constraints=constraints, examples=examples, description=description)


def _schemas(lines: list[str], start: int, grouping: GroupingName) -> list[Schema]:
    result = []
    for attributes, body_lines, number in _entries(lines, start, "schema", grouping, "schemas"):
        if "id" not in attributes:
            _fail("schema_id", "schemas", number, "schema entry needs id")
        body = "\n".join(body_lines)
        marker = "\n\nWHERE:"
        template, separator, where_text = body.rpartition(marker)
        if not separator:
            _fail("schema_where", f"schemas.{attributes['id']}", number, "schema body needs the generated WHERE separator")
        result.append(
            Schema(
                id=attributes["id"],
                name=attributes.get("name"),
                purpose=attributes.get("purpose"),
                template=template,
                where=[
                    _where(item, f"schemas.{attributes['id']}.where", number + len(template.splitlines()) + 3 + index)
                    for index, item in enumerate(where_text.splitlines())
                    if item
                ],
            )
        )
    return result


def _value(source: str, path: str, line: int):
    if not source.startswith("$"):
        return LiteralValue(value=_json_value(source, path, line))
    target = source[1:]
    if target.startswith("state."):
        return StateValue(state=target)
    if target.startswith("interface."):
        parts = target.split(".")
        if len(parts) != 3:
            _fail("interface_value", path, line, "interface value needs one placeholder")
        return InterfaceValue(interface=".".join(parts[:2]), placeholder=parts[2])
    if target.startswith("constant.") or "#constant." in target:
        return ConstantValue(constant=target)
    return BindingValue(binding=target)


def _compare(source: str, path: str, line: int) -> Compare:
    for phrase, operator in OPERATOR_PHRASES:
        if phrase in source:
            left, right = source.split(phrase, 1)
            return Compare(left=_value(left, path, line), operator=operator, right=_value(right, path, line))
    _fail("condition_compare", path, line, "condition needs one comparison operator")


def _indent(line: str, path: str, number: int) -> int:
    if "\t" in line:
        _fail("tab", path, number, "tabs are not allowed")
    return len(line) - len(line.lstrip(" "))


def _condition(lines: list[str], index: int, indent: int, path: str, start: int):
    if index >= len(lines):
        _fail("condition_missing", path, start + index, "condition is missing")
    number = start + index
    actual = _indent(lines[index], path, number)
    if actual != indent:
        _fail("condition_indent", path, number, f"condition needs {indent} spaces")
    text = lines[index][indent:]
    if text in ("ALL:", "ANY:"):
        kind = text[:-1]
        index += 1
        children = []
        while index < len(lines) and _indent(lines[index], path, start + index) >= indent + 2:
            child, index = _condition(lines, index, indent + 2, path, start)
            children.append(child)
        return (All(conditions=children) if kind == "ALL" else Any(conditions=children)), index
    if text == "NOT:":
        child, index = _condition(lines, index + 1, indent + 2, path, start)
        return Not(condition=child), index
    return _compare(text, path, number), index + 1


def _binding(source: str, path: str, line: int) -> ValueBinding:
    placeholder, separator, value = source.partition("=")
    if not separator:
        _fail("binding", path, line, "binding needs NAME=value")
    return ValueBinding(placeholder=placeholder, value=_value(value, path, line))


_SUFFIX_PLACEHOLDER_RE = re.compile(PLACEHOLDER_SYNTAX.body)


def _suffix_value(source: str, position: int) -> int | None:
    if source.startswith("$", position):
        end = position + 1
        while end < len(source) and source[end] not in ",)":
            end += 1
        return end
    try:
        _, end = json.JSONDecoder().raw_decode(source, position)
    except json.JSONDecodeError:
        return None
    return end


def _suffix(source: str) -> tuple[list[tuple[str, str]], list[str]] | None:
    """Return (bindings, outputs) when source is exactly one binding suffix."""
    if not source.startswith("("):
        return None
    bindings: list[tuple[str, str]] = []
    position = 1
    if source.startswith(")", position):
        position += 1
    else:
        while True:
            end = source.find("=", position)
            if end == -1 or _SUFFIX_PLACEHOLDER_RE.fullmatch(source, position, end) is None:
                return None
            value_start = end + 1
            value_end = _suffix_value(source, value_start)
            if value_end is None:
                return None
            bindings.append((source[position:end], source[value_start:value_end]))
            position = value_end
            if source.startswith(", ", position):
                position += 2
                continue
            if source.startswith(")", position):
                position += 1
                break
            return None
    if position == len(source):
        return bindings, []
    if not source.startswith(" -> ", position):
        return None
    outputs = source[position + 4 :].split(", ")
    if any(_SUFFIX_PLACEHOLDER_RE.fullmatch(item) is None for item in outputs):
        return None
    return bindings, outputs


_ACT_INPUT_RE = re.compile(r'^ input="([^"]+)"')
_ACT_OUTPUT_RE = re.compile(r'^ output="([^"]+)"')


def _act_attributes(source: str) -> tuple[str | None, str | None, str] | None:
    """Return (input, output, body) when source starts with act schema attributes."""
    input_target = None
    output_target = None
    rest = source
    match = _ACT_INPUT_RE.match(rest)
    if match:
        input_target = match.group(1)
        rest = rest[match.end() :]
    match = _ACT_OUTPUT_RE.match(rest)
    if match:
        output_target = match.group(1)
        rest = rest[match.end() :]
    if input_target is None and output_target is None:
        return None
    if not rest.startswith(": "):
        return None
    return input_target, output_target, rest[2:]


def _suffix_bindings(
    bindings: list[tuple[str, str]],
    path: str,
    line: int,
) -> list[ValueBinding]:
    return [
        ValueBinding(placeholder=placeholder, value=_value(value, path, line))
        for placeholder, value in bindings
    ]


def _steps(
    lines: list[str],
    index: int,
    indent: int,
    path: str,
    start: int,
    stop: set[str] | None = None,
):
    result = []
    stop = stop or set()
    while index < len(lines):
        if lines[index] == "":
            index += 1
            continue
        number = start + index
        actual = _indent(lines[index], path, number)
        if actual < indent:
            break
        if actual > indent:
            _fail("step_indent", path, number, f"step needs {indent} spaces")
        text = lines[index][indent:]
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
                _fail("act_tool", path, number, str(error))
            if not isinstance(tool, str):
                _fail("act_tool", path, number, "ACT TOOL needs one JSON string and colon")
            remainder = rest[consumed:]
            attributes = _act_attributes(remainder)
            if attributes is not None:
                act_input, act_output, body = attributes
            elif remainder.startswith(": "):
                body = remainder[2:]
            else:
                _fail("act_tool", path, number, "ACT TOOL needs one JSON string and colon")
        elif text.startswith("ACT "):
            tool = None
            attributes = _act_attributes(text[3:])
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
                position = body.rfind(" (", 0, position)
                if position == -1:
                    _fail("act_suffix", path, number, "ACT needs one (bindings) suffix")
                parsed = _suffix(body[position + 1 :])
            bindings, outputs = parsed
            result.append(
                Act(
                    tool=tool,
                    input=act_input,
                    output=act_output,
                    instruction=body[:position],
                    inputs=_suffix_bindings(bindings, path, number),
                    outputs=outputs,
                )
            )
            index += 1
            continue
        if text.startswith("SET "):
            body = text[4:]
            if " = " not in body:
                _fail("set", path, number, "SET needs target = value")
            target, value = body.split(" = ", 1)
            result.append(Set(state=target, value=_value(value, path, number)))
            index += 1
            continue
        if text.startswith("EMIT "):
            target, _, remainder = text[5:].partition(" ")
            parsed = _suffix(remainder)
            if parsed is None:
                _fail("emit_suffix", path, number, "EMIT needs target (bindings)")
            bindings, outputs = parsed
            if outputs:
                _fail("emit_suffix", path, number, "EMIT takes no outputs")
            result.append(Emit(interface=target, bindings=_suffix_bindings(bindings, path, number)))
            index += 1
            continue
        if text.startswith("IF ") and text.endswith(":"):
            condition = _compare(text[3:-1], path, number)
            index += 1
        elif text == "IF:":
            condition, index = _condition(lines, index + 1, indent + 2, path, start)
        else:
            condition = None
        if condition is not None:
            if index >= len(lines) or _indent(lines[index], path, start + index) != indent + 2 or lines[index][indent + 2 :] != "THEN:":
                _fail("if_then", path, start + index, "IF needs THEN")
            then, index = _steps(lines, index + 1, indent + 4, path, start, {"ELSE:"})
            otherwise = None
            if index < len(lines) and _indent(lines[index], path, start + index) == indent + 2 and lines[index][indent + 2 :] == "ELSE:":
                otherwise, index = _steps(lines, index + 1, indent + 4, path, start)
            result.append(If(condition=condition, then=then, otherwise=otherwise))
            continue
        if text.startswith("CALL "):
            target, _, remainder = text[5:].partition(" ")
            parsed = _suffix(remainder)
            if parsed is None:
                _fail("call_suffix", path, number, "CALL needs target (bindings)")
            bindings, outputs = parsed
            result.append(
                Call(
                    process=target,
                    inputs=_suffix_bindings(bindings, path, number),
                    outputs=outputs,
                )
            )
            index += 1
            continue
        if text.startswith("FAIL "):
            message = _json_value(text[5:], path, number)
            if not isinstance(message, str):
                _fail("fail_message", path, number, "FAIL message must be a JSON string")
            result.append(Fail(message=message))
            index += 1
            continue
        if text.startswith("ASSERT "):
            condition = _compare(text[7:], path, number)
            index += 1
        elif text == "ASSERT:":
            condition, index = _condition(lines, index + 1, indent + 2, path, start)
        else:
            condition = None
        if condition is not None:
            message = None
            if index < len(lines) and _indent(lines[index], path, start + index) == indent + 2 and lines[index][indent + 2 :].startswith("MESSAGE "):
                raw = _json_value(lines[index][indent + 10 :], path, start + index)
                if not isinstance(raw, str):
                    _fail("assert_message", path, start + index, "MESSAGE must be a JSON string")
                message = raw
                index += 1
            result.append(Assert(condition=condition, message=message))
            continue
        if text.startswith("FOREACH ") and text.endswith(":"):
            body = text[8:-1]
            if " IN " not in body:
                _fail("foreach", path, number, "FOREACH needs binding IN value")
            binding, value = body.split(" IN ", 1)
            children, index = _steps(lines, index + 1, indent + 2, path, start)
            result.append(Foreach(binding=binding, value=_value(value, path, number), steps=children))
            continue
        if text.startswith("WHILE ") and text.endswith(":"):
            body = text[6:-1]
            if body.startswith("LIMIT "):
                limit_text = body[6:]
                if not limit_text.isdigit() or int(limit_text) < 1:
                    _fail("while_limit", path, number, "WHILE LIMIT must be a positive integer")
                condition, index = _condition(
                    lines,
                    index + 1,
                    indent + 2,
                    path,
                    start,
                )
                if (
                    index >= len(lines)
                    or _indent(lines[index], path, start + index) != indent + 2
                    or lines[index][indent + 2 :] != "THEN:"
                ):
                    _fail("while_then", path, start + index, "recursive WHILE needs THEN")
                children, index = _steps(
                    lines,
                    index + 1,
                    indent + 4,
                    path,
                    start,
                )
            else:
                if " LIMIT " not in body:
                    _fail("while", path, number, "WHILE needs condition LIMIT positive-integer")
                condition_text, limit_text = body.rsplit(" LIMIT ", 1)
                if not limit_text.isdigit() or int(limit_text) < 1:
                    _fail("while_limit", path, number, "WHILE LIMIT must be a positive integer")
                condition = _compare(condition_text, path, number)
                children, index = _steps(
                    lines,
                    index + 1,
                    indent + 2,
                    path,
                    start,
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
            children, index = _steps(lines, index + 1, indent + 2, path, start)
            result.append(Par(steps=children))
            continue
        if text == "JOIN":
            result.append(Join())
            index += 1
            continue
        _fail("unknown_step", path, number, f"unknown process step {text}")
    return result, index


def _processes(lines: list[str], start: int, grouping: GroupingName) -> list[Process]:
    result = []
    for attributes, body, number in _entries(lines, start, "process", grouping, "processes"):
        if "id" not in attributes or "name" not in attributes:
            _fail("process_attributes", "processes", number, "process needs id and name")
        steps, index = _steps(body, 0, 0, f"processes.{attributes['id']}", number + 1)
        if index != len(body):
            _fail("process_trailing", f"processes.{attributes['id']}", number + index + 1, "unparsed process text")
        result.append(
            Process(
                id=attributes["id"],
                name=attributes["name"],
                input=attributes.get("input"),
                output=attributes.get("output"),
                steps=steps,
            )
        )
    return result


_TRIGGER_FACT = re.compile(
    r"^trigger\.([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\."
    r"(event|source|guard|process|seed\.(" + PLACEHOLDER_SYNTAX.body + r")) :=(.*)$"
)


def _triggers(lines: list[str], start: int) -> list[Trigger]:
    chunks: list[tuple[int, list[str]]] = []
    current: list[str] = []
    current_start = 0
    for offset, line in enumerate(lines):
        if line == "":
            if not current:
                _fail("trigger_separator", "triggers", start + offset, "one blank line separates triggers")
            chunks.append((current_start, current))
            current = []
            continue
        if not current:
            current_start = offset
        current.append(line)
    if current:
        chunks.append((current_start, current))
    elif chunks:
        _fail("trigger_separator", "triggers", start + len(lines) - 1, "one blank line separates triggers")
    result: list[Trigger] = []
    seen: set[str] = set()
    for chunk_start, chunk in chunks:
        number = start + chunk_start
        identifier: str | None = None
        event: str | None = None
        source: str | None = None
        guard: object = True
        process: str | None = None
        seed: list[ValueBinding] = []
        stage = 0
        index = 0
        while index < len(chunk):
            line_number = number + index
            match = _TRIGGER_FACT.fullmatch(chunk[index])
            if match is None:
                _fail("trigger_fact", "triggers", line_number, "trigger fact must be trigger.<id>.<fact> := <value>")
            entry_id, field, placeholder, rest = match.group(1), match.group(2), match.group(3), match.group(4)
            if identifier is None:
                if entry_id in seen:
                    _fail("trigger_fact", f"triggers.{entry_id}", line_number, "one trigger's facts stay contiguous")
                identifier = entry_id
                seen.add(entry_id)
            elif entry_id != identifier:
                _fail("trigger_fact", f"triggers.{identifier}", line_number, "one trigger's facts stay contiguous")
            path = f"triggers.{identifier}"
            if rest and (not rest.startswith(" ") or rest == " " or rest.startswith("  ")):
                _fail("trigger_fact", path, line_number, "one space follows :=")
            value = rest[1:]
            if field == "guard":
                if stage not in (1, 2):
                    _fail("trigger_order", path, line_number, "guard follows event and source")
                if value:
                    guard = _compare(value, path + ".guard", line_number)
                    index += 1
                else:
                    guard, index = _condition(chunk, index + 1, 2, path + ".guard", number)
                stage = 3
                continue
            if not value:
                _fail("trigger_fact", path, line_number, "trigger fact needs one value")
            if field == "event":
                if stage != 0:
                    _fail("trigger_order", path, line_number, "event opens one trigger")
                parsed = _json_value(value, path + ".event", line_number)
                if not isinstance(parsed, str):
                    _fail("trigger_event", path, line_number, "event must be a JSON string")
                event = parsed
                stage = 1
            elif field == "source":
                if stage != 1:
                    _fail("trigger_order", path, line_number, "source follows event")
                source = value
                stage = 2
            elif field == "process":
                if stage not in (1, 2, 3):
                    _fail("trigger_order", path, line_number, "process follows event, source, and guard")
                process = value
                stage = 4
            else:
                if stage != 4:
                    _fail("trigger_order", path, line_number, "seeds follow process")
                if any(binding.placeholder == placeholder for binding in seed):
                    _fail("trigger_seed", path, line_number, "seed placeholders are unique")
                seed.append(
                    ValueBinding(
                        placeholder=placeholder,
                        value=_value(value, path + ".seed." + placeholder, line_number),
                    )
                )
            index += 1
        if process is None:
            _fail("trigger_process", f"triggers.{identifier}", number + len(chunk), "trigger needs process")
        result.append(Trigger(id=identifier, event=event, source=source, guard=guard, process=process, seed=seed))
    return result


def _interfaces(lines: list[str], start: int, grouping: GroupingName) -> list[Interface]:
    result = []
    for attributes, body, number in _entries(lines, start, "interface", grouping, "interfaces"):
        for required in ("id", "direction", "schema"):
            if required not in attributes:
                _fail("interface_attribute", "interfaces", number, f"interface needs {required}")
        description = "\n".join(body) or None
        result.append(Interface(id=attributes["id"], direction=attributes["direction"], schema=attributes["schema"], description=description))
    return result


def _validation_failures(error: ValidationError) -> list[ParseFailure]:
    result = []
    for detail in error.errors(include_url=False, include_context=False, include_input=False):
        path = ".".join(str(part) for part in detail["loc"]) or "$"
        result.append(ParseFailure(str(detail["type"]), path, None, detail["msg"]))
    return result


def parse(source: str | bytes, *, grouping: GroupingName | None = None) -> Node:
    """Parse one OAK document and run every standalone model check."""
    text = _source_text(source)
    if not text:
        return Node()
    failures: list[ParseFailure] = []
    try:
        grouping = grouping or _infer_grouping(text)
        parts = _parts(text, grouping)
    except _Parse as error:
        raise OakParseError((error.failure,)) from None
    data: dict[str, object] = {}
    parsers = {
        "instructions": lambda body, start: _instructions(body, start),
        "constants": lambda body, start: _named_values(body, start, constants=True),
        "schemas": lambda body, start: _schemas(body, start, grouping),
        "state": lambda body, start: _named_values(body, start, constants=False),
        "triggers": lambda body, start: _triggers(body, start),
        "processes": lambda body, start: _processes(body, start, grouping),
        "interfaces": lambda body, start: _interfaces(body, start, grouping),
    }
    for part in PART_ORDER:
        if part not in parts:
            continue
        body, start = parts[part]
        try:
            data[part] = parsers[part](body, start)
        except _Parse as error:
            failures.append(error.failure)
        except ValidationError as error:
            failures.extend(_validation_failures(error))
    if failures:
        raise OakParseError(failures)
    try:
        return Node.model_validate(data)
    except ValidationError as error:
        raise OakParseError(_validation_failures(error)) from None


def parse_oak(source: str | bytes, *, grouping: GroupingName | None = None) -> Node:
    """Parse one OAK document."""
    return parse(source, grouping=grouping)
