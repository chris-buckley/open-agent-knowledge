"""The restricted text syntax tree that emits regex patterns and EBNF."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol


class Syntax(Protocol):
    """One text syntax expression."""

    def regex(self) -> str:
        """Return the unanchored regular expression body."""

    def ebnf(self) -> str:
        """Return the EBNF expression."""


def _escape_regex(text: str) -> str:
    return "".join("\\" + char if char in r"\\.^$|?*+()[]{}" else char for char in text)


@dataclass(frozen=True, slots=True)
class LiteralText:
    """One literal string."""

    value: str

    def regex(self) -> str:
        return _escape_regex(self.value)

    def ebnf(self) -> str:
        return json.dumps(self.value, ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class CharacterClass:
    """One authored regular-expression character class body."""

    source: str

    def regex(self) -> str:
        return f"[{self.source}]"

    def ebnf(self) -> str:
        return f"? [{self.source}] ?"


@dataclass(frozen=True, slots=True)
class Sequence:
    """Expressions that occur in order."""

    items: tuple[Syntax, ...]

    def regex(self) -> str:
        return "".join(item.regex() for item in self.items)

    def ebnf(self) -> str:
        return ", ".join(item.ebnf() for item in self.items) or '""'


@dataclass(frozen=True, slots=True)
class Choice:
    """One expression selected from a closed set."""

    items: tuple[Syntax, ...]

    def regex(self) -> str:
        return "(?:" + "|".join(item.regex() for item in self.items) + ")"

    def ebnf(self) -> str:
        return "( " + " | ".join(item.ebnf() for item in self.items) + " )"


@dataclass(frozen=True, slots=True)
class Optional:
    """An expression that occurs zero or one time."""

    item: Syntax

    def regex(self) -> str:
        return f"(?:{self.item.regex()})?"

    def ebnf(self) -> str:
        return f"[ {self.item.ebnf()} ]"


@dataclass(frozen=True, slots=True)
class Repeat:
    """An expression repeated inside inclusive bounds."""

    item: Syntax
    minimum: int = 0
    maximum: int | None = None

    def __post_init__(self) -> None:
        if self.minimum < 0:
            raise ValueError("repeat minimum must be non-negative")
        if self.maximum is not None and self.maximum < self.minimum:
            raise ValueError("repeat maximum must not be below minimum")

    def regex(self) -> str:
        body = f"(?:{self.item.regex()})"
        if self.minimum == 0 and self.maximum is None:
            return body + "*"
        if self.minimum == 1 and self.maximum is None:
            return body + "+"
        if self.minimum == 0 and self.maximum == 1:
            return body + "?"
        if self.maximum == self.minimum:
            return body + f"{{{self.minimum}}}"
        if self.maximum is None:
            return body + f"{{{self.minimum},}}"
        return body + f"{{{self.minimum},{self.maximum}}}"

    def ebnf(self) -> str:
        item = self.item.ebnf()
        required = ", ".join(item for _ in range(self.minimum))
        if self.maximum == self.minimum:
            return required or '""'
        if self.maximum is None:
            repeated = f"{{ {item} }}"
            return f"{required}, {repeated}" if required else repeated
        optional_count = self.maximum - self.minimum
        suffix = ", ".join(f"[ {item} ]" for _ in range(optional_count))
        if required and suffix:
            return f"{required}, {suffix}"
        return required or suffix or '""'


@dataclass(frozen=True, slots=True)
class NamedReference:
    """A named rule embedded in regex and referenced by name in EBNF."""

    rule: Rule

    def regex(self) -> str:
        return self.rule.expression.regex()

    def ebnf(self) -> str:
        return self.rule.name


@dataclass(frozen=True, slots=True)
class Rule:
    """One named whole-value text syntax."""

    name: str
    expression: Syntax

    @property
    def body(self) -> str:
        """The unanchored regular-expression body."""
        return self.expression.regex()

    @property
    def pattern(self) -> str:
        """The whole-value regular-expression pattern."""
        return f"^{self.body}$"

    @property
    def production(self) -> str:
        """The EBNF production."""
        return f"{self.name} = {self.expression.ebnf()} ;"

    def reference(self) -> NamedReference:
        """A reference to this rule."""
        return NamedReference(self)
