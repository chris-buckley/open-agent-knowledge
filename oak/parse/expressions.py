"""Recursive OAK expressions with physical source locations and JSON boundaries.

Only the grammar consumes punctuation. JSONDecoder owns strings, arrays, and
objects; OAK owns condition groups and named lists. Prose is never tokenized.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import NoReturn, TypeVar

from pydantic import TypeAdapter, ValidationError

from oak.node.parts.processes.conditions import All, Any, Compare, Condition, Not
from oak.node.parts.processes.operators import OPERATOR_PHRASES
from oak.node.parts.processes.targets import InterfaceTarget, ProcessTarget, StateTarget
from oak.node.parts.processes.values import (
    BindingValue, ConstantValue, LiteralValue, StateValue, Value, ValueBinding,
)
from oak.parse.cursor import Cursor
from oak.parse.errors import fail
from oak.surface.syntax import CONDITION_GROUPS
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX

T = TypeVar("T")
_NAME = re.compile(r"[A-Za-z0-9._/#-]+")
_PLACEHOLDER = re.compile(PLACEHOLDER_SYNTAX.body)
_SLUG = re.compile(SLUG_ID_SYNTAX.body)
_TARGETS = {
    "interface": TypeAdapter(InterfaceTarget),
    "process": TypeAdapter(ProcessTarget),
    "state": TypeAdapter(StateTarget),
}
_JSON = json.JSONDecoder()


@dataclass(slots=True)
class ExpressionReader:
    """A character cursor; embedded newlines retain their original line numbers."""

    source: str
    path: str
    first_line: int
    position: int = 0
    depth: int = 0

    @classmethod
    def at(cls, cursor: Cursor, first: str) -> ExpressionReader:
        """Start at a known expression boundary, never at arbitrary ACT prose."""
        return cls(
            "\n".join((first, *cursor.lines[cursor.index + 1 :])),
            cursor.path,
            cursor.line_number,
        )

    def line_at(self, position: int | None = None) -> int:
        return self.first_line + self.source.count(
            "\n", 0, self.position if position is None else position,
        )

    def fail(self, code: str, message: str, position: int | None = None) -> NoReturn:
        fail(code, self.path, self.line_at(position), message)

    def checked(self, make: Callable[[], T], position: int | None = None) -> T:
        """Attach model validation failures to the expression that supplied them."""
        try:
            return make()
        except ValidationError as error:
            detail = error.errors(include_url=False, include_context=False)[0]
            self.fail(str(detail["type"]), detail["msg"], position)

    def skip(self) -> None:
        whitespace = " \n" if self.depth else " "
        while self.position < len(self.source) and self.source[self.position] in whitespace:
            self.position += 1
        if self.source.startswith("\t", self.position):
            self.fail("tab", "structural tabs are not allowed")

    def space(self) -> None:
        start = self.position
        self.skip()
        if self.position == start:
            self.fail("expression_space", "expected whitespace between tokens")

    def take(self, token: str) -> bool:
        self.skip()
        if not self.source.startswith(token, self.position):
            return False
        self.position += len(token)
        return True

    def expect(self, token: str) -> None:
        if not self.take(token):
            self.fail("expression_token", f"expected {token!r}")

    def name(self, pattern: re.Pattern[str] = _NAME, label: str = "name") -> str:
        self.skip()
        match = pattern.match(self.source, self.position)
        if match is None:
            self.fail("expression_name", f"expected one {label}")
        self.position = match.end()
        return match.group()

    def slug(self) -> str:
        return self.name(_SLUG, "lower-kebab identifier")

    def placeholder(self) -> str:
        return self.name(_PLACEHOLDER, "upper-snake placeholder")

    def target(self, part: str) -> str:
        self.skip()
        start = self.position
        text = self.name(label=f"bare {part} target")
        return self.checked(lambda: _TARGETS[part].validate_python(text), start)

    def json(self) -> object:
        self.skip()
        try:
            value, self.position = _JSON.raw_decode(self.source, self.position)
        except json.JSONDecodeError as error:
            self.fail("invalid_json", error.msg, error.pos)
        return value

    def string(self) -> str:
        self.skip()
        start = self.position
        value = self.json()
        if not isinstance(value, str):
            self.fail("expression_string", "expected one JSON string", start)
        return value

    def value(self) -> Value:
        self.skip()
        start = self.position
        if self.take("$"):
            if self.position == len(self.source) or self.source[self.position].isspace():
                self.fail("value_reference", "the value target must immediately follow $")
            target = self.name(label="value reference")
            if target.startswith("state."):
                return self.checked(lambda: StateValue(state=target), start)
            if target.startswith("constant.") or "#constant." in target:
                return self.checked(lambda: ConstantValue(constant=target), start)
            return self.checked(lambda: BindingValue(binding=target), start)
        value = self.json()
        return self.checked(lambda: LiteralValue(value=value), start)

    def enclosed(self, item: Callable[[], T]) -> list[T]:
        """Parse one OAK list with nested continuation and an optional trailing comma."""
        self.expect("(")
        self.depth += 1
        try:
            items: list[T] = []
            if self.take(")"):
                return items
            while True:
                items.append(item())
                if self.take(")"):
                    return items
                self.expect(",")
                if self.take(")"):
                    return items
        finally:
            self.depth -= 1

    def condition(self) -> Condition:
        self.skip()
        start = self.position
        for word in CONDITION_GROUPS:
            # A group name is a complete token, not a prefix of a value.
            if re.match(rf"{word}(?=\s|\()", self.source[self.position :]):
                self.position += len(word)
                children = self.enclosed(self.condition)
                if word == "NOT":
                    if len(children) != 1:
                        self.fail("condition_not_arity", "NOT needs exactly one condition", start)
                    return Not(condition=children[0])
                model = All if word == "ALL" else Any
                return self.checked(lambda: model(conditions=children), start)
        left = self.value()
        self.space()
        for phrase, operator in OPERATOR_PHRASES:
            token = phrase.strip()
            if self.source.startswith(token, self.position):
                self.position += len(token)
                self.space()
                right = self.value()
                return Compare(left=left, operator=operator, right=right)
        self.fail("condition_compare", "condition needs one comparison operator")

    def binding(self) -> ValueBinding:
        self.skip()
        start = self.position
        placeholder = self.placeholder()
        self.expect("=")
        previous = self.path
        self.path += "." + placeholder
        try:
            value = self.value()
            return self.checked(lambda: ValueBinding(placeholder=placeholder, value=value), start)
        finally:
            self.path = previous

    def bindings(self) -> list[ValueBinding]:
        seen: set[str] = set()

        def item() -> ValueBinding:
            self.skip()
            start = self.position
            binding = self.binding()
            if binding.placeholder in seen:
                self.fail("duplicate_binding", f"duplicate binding {binding.placeholder}", start)
            seen.add(binding.placeholder)
            return binding

        return self.enclosed(item)

    def suffix(self) -> tuple[list[ValueBinding], list[str]]:
        bindings = self.bindings()
        outputs: list[str] = []
        if self.take("->"):
            outputs.append(self.placeholder())
            while self.take(","):
                outputs.append(self.placeholder())
        return bindings, outputs

    def finish(self, cursor: Cursor | None = None) -> None:
        """Finish exactly one logical statement, then advance its physical cursor."""
        self.skip()
        if self.position < len(self.source) and self.source[self.position] != "\n":
            self.fail("expression_trailing", "unexpected text after the expression")
        if cursor is None:
            if self.source[self.position :].strip():
                self.fail("expression_trailing", "unexpected text after the expression")
        else:
            cursor.advance(self.source.count("\n", 0, self.position) + 1)
