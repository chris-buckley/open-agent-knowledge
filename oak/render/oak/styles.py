"""Named wording profiles for natural-language OAK fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from oak.node.model import Node

StyleName = Literal["authored", "asd-ste100-9"]
ASD_STE100_EDITION = "Issue 9, January 2025"

_SUBSTITUTIONS = (
    (re.compile(r"\bin order to\b", re.IGNORECASE), "to"),
    (re.compile(r"\bprior to\b", re.IGNORECASE), "before"),
    (re.compile(r"\bsubsequent to\b", re.IGNORECASE), "after"),
    (re.compile(r"\butilizes\b", re.IGNORECASE), "uses"),
    (re.compile(r"\butilized\b", re.IGNORECASE), "used"),
    (re.compile(r"\butilizing\b", re.IGNORECASE), "using"),
    (re.compile(r"\butilize\b", re.IGNORECASE), "use"),
    (re.compile(r"\bcommences\b", re.IGNORECASE), "starts"),
    (re.compile(r"\bcommenced\b", re.IGNORECASE), "started"),
    (re.compile(r"\bcommencing\b", re.IGNORECASE), "starting"),
    (re.compile(r"\bcommence\b", re.IGNORECASE), "start"),
    (re.compile(r"\bterminates\b", re.IGNORECASE), "stops"),
    (re.compile(r"\bterminated\b", re.IGNORECASE), "stopped"),
    (re.compile(r"\bterminating\b", re.IGNORECASE), "stopping"),
    (re.compile(r"\bterminate\b", re.IGNORECASE), "stop"),
)
_PROHIBITED = tuple(pattern for pattern, _replacement in _SUBSTITUTIONS)
_WORD = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
_SENTENCE_END = re.compile(r"[.!?](?=\s|$)")


@dataclass(frozen=True, slots=True)
class StyleFailure:
    """One controlled-style failure at one rendered text path."""

    path: str
    code: str
    message: str
    def __str__(self) -> str:
        return f"[{self.code}] {self.path}: {self.message}"


class StyleError(ValueError):
    """Every failure collected while applying one controlled style."""

    code = "controlled_style_invalid"
    def __init__(self, failures: list[StyleFailure]) -> None:
        self.failures = tuple(failures)
        super().__init__("\n".join(str(failure) for failure in self.failures))


def _case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _rewrite(text: str) -> str:
    for pattern, replacement in _SUBSTITUTIONS:
        text = pattern.sub(lambda match: _case(match.group(0), replacement), text)
    return text


def _validate(path: str, text: str) -> list[StyleFailure]:
    failures: list[StyleFailure] = []
    if "\n" in text or "\r" in text:
        failures.append(StyleFailure(path, "ste_line_count", "text must be one line"))
    if len(_WORD.findall(text)) > 20:
        failures.append(StyleFailure(path, "ste_sentence_length", "text must contain at most 20 words"))
    if len(_SENTENCE_END.findall(text)) > 1:
        failures.append(StyleFailure(path, "ste_sentence_count", "text must contain at most one sentence"))
    for pattern in _PROHIBITED:
        if pattern.search(text):
            failures.append(StyleFailure(path, "ste_prohibited_term", f"text contains {pattern.pattern}"))
    return failures


def _style_steps(steps: list[dict[str, object]], path: str, failures: list[StyleFailure]) -> None:
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        step_path = f"{path}.{index}"
        kind = step.get("kind")
        if kind == "act":
            text = _rewrite(str(step["instruction"])); step["instruction"] = text
            failures.extend(_validate(f"{step_path}.instruction", text))
        elif kind == "fail":
            text = _rewrite(str(step["message"])); step["message"] = text
            failures.extend(_validate(f"{step_path}.message", text))
        elif kind == "assert" and step.get("message") is not None:
            text = _rewrite(str(step["message"])); step["message"] = text
            failures.extend(_validate(f"{step_path}.message", text))
        if kind == "if":
            _style_steps(step.get("then", []), f"{step_path}.then", failures)  # type: ignore[arg-type]
            _style_steps(step.get("otherwise") or [], f"{step_path}.otherwise", failures)  # type: ignore[arg-type]
        elif kind in {"foreach", "while"}:
            _style_steps(step.get("steps", []), f"{step_path}.steps", failures)  # type: ignore[arg-type]
        elif kind == "par":
            _style_steps(step.get("steps", []), f"{step_path}.steps", failures)  # type: ignore[arg-type]


def styled_node(node: Node, style: StyleName = "authored") -> Node:
    """Return a render-only copy with one wording profile."""
    if style == "authored":
        return node
    if style != "asd-ste100-9":
        raise ValueError(f"unknown OAK style {style}")
    data = node.model_dump(mode="python", by_alias=True)
    failures: list[StyleFailure] = []
    for index, instruction in enumerate(data.get("instructions", [])):
        text = _rewrite(str(instruction["body"])); instruction["body"] = text
        failures.extend(_validate(f"instructions.{index}.body", text))
    for index, trigger in enumerate(data.get("triggers", [])):
        text = _rewrite(str(trigger["event"])); trigger["event"] = text
        failures.extend(_validate(f"triggers.{index}.event", text))
    for index, process in enumerate(data.get("processes", [])):
        _style_steps(process.get("steps", []), f"processes.{index}.steps", failures)
    if failures:
        raise StyleError(failures)
    return Node.model_validate(data)
