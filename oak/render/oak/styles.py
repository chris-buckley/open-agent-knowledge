"""Named wording profiles for natural-language OAK fields."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from oak.node.model import Node
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Fail,
    Foreach,
    If,
    Par,
    Step,
    While,
)

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

    def __init__(self, failures: Sequence[StyleFailure]) -> None:
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


def _style_failures(path: str, text: str) -> list[StyleFailure]:
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


def _styled_text(text: str, path: str, failures: list[StyleFailure]) -> str:
    rewritten = _rewrite(text)
    failures.extend(_style_failures(path, rewritten))
    return rewritten


def _styled_steps(
    steps: Sequence[Step],
    path: str,
    failures: list[StyleFailure],
) -> list[Step]:
    styled: list[Step] = []

    for index, step in enumerate(steps):
        step_path = f"{path}.{index}"

        match step:
            case Act():
                instruction = _styled_text(step.instruction, f"{step_path}.instruction", failures)
                styled.append(step.model_copy(update={"instruction": instruction}))

            case Fail():
                message = _styled_text(step.message, f"{step_path}.message", failures)
                styled.append(step.model_copy(update={"message": message}))

            case Assert() if step.message is not None:
                message = _styled_text(step.message, f"{step_path}.message", failures)
                styled.append(step.model_copy(update={"message": message}))

            case If():
                then = _styled_steps(step.then, f"{step_path}.then", failures)
                otherwise = (
                    None
                    if step.otherwise is None
                    else _styled_steps(step.otherwise, f"{step_path}.otherwise", failures)
                )
                styled.append(step.model_copy(update={"then": then, "otherwise": otherwise}))

            case Foreach() | While() | Par():
                children = _styled_steps(step.steps, f"{step_path}.steps", failures)
                styled.append(step.model_copy(update={"steps": children}))

            case _:
                styled.append(step)

    return styled


def styled_node(node: Node, style: StyleName = "authored") -> Node:
    """Return a render-only copy with one wording profile."""
    if style == "authored":
        return node
    if style != "asd-ste100-9":
        raise ValueError(f"unknown OAK style {style}")
    failures: list[StyleFailure] = []
    instructions = [
        instruction.model_copy(
            update={"body": _styled_text(instruction.body, f"instructions.{index}.body", failures)}
        )
        for index, instruction in enumerate(node.instructions)
    ]
    triggers = [
        trigger.model_copy(
            update={"event": _styled_text(trigger.event, f"triggers.{index}.event", failures)}
        )
        for index, trigger in enumerate(node.triggers)
    ]
    processes = [
        process.model_copy(
            update={"steps": _styled_steps(process.steps, f"processes.{index}.steps", failures)}
        )
        for index, process in enumerate(node.processes)
    ]
    if failures:
        raise StyleError(failures)
    styled = node.model_copy(
        update={"instructions": instructions, "triggers": triggers, "processes": processes}
    )
    return Node.model_validate(styled.model_dump(mode="python", by_alias=True))
