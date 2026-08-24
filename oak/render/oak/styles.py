"""Named wording profiles for natural-language OAK fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from oak.node.model import Node

StyleName = Literal["authored", "asd-ste100-9"]
ASD_STE100_EDITION = "Issue 9, January 2025"

_SUBSTITUTIONS = (
    (
        re.compile(r"\bin order to\b", re.IGNORECASE),
        "to",
    ),
    (
        re.compile(r"\bprior to\b", re.IGNORECASE),
        "before",
    ),
    (
        re.compile(r"\bsubsequent to\b", re.IGNORECASE),
        "after",
    ),
    (
        re.compile(r"\butilizes\b", re.IGNORECASE),
        "uses",
    ),
    (
        re.compile(r"\butilized\b", re.IGNORECASE),
        "used",
    ),
    (
        re.compile(r"\butilizing\b", re.IGNORECASE),
        "using",
    ),
    (
        re.compile(r"\butilize\b", re.IGNORECASE),
        "use",
    ),
    (
        re.compile(r"\bcommences\b", re.IGNORECASE),
        "starts",
    ),
    (
        re.compile(r"\bcommenced\b", re.IGNORECASE),
        "started",
    ),
    (
        re.compile(r"\bcommencing\b", re.IGNORECASE),
        "starting",
    ),
    (
        re.compile(r"\bcommence\b", re.IGNORECASE),
        "start",
    ),
    (
        re.compile(r"\bterminates\b", re.IGNORECASE),
        "stops",
    ),
    (
        re.compile(r"\bterminated\b", re.IGNORECASE),
        "stopped",
    ),
    (
        re.compile(r"\bterminating\b", re.IGNORECASE),
        "stopping",
    ),
    (
        re.compile(r"\bterminate\b", re.IGNORECASE),
        "stop",
    ),
)

_PROHIBITED = tuple(
    pattern
    for pattern, _replacement in _SUBSTITUTIONS
)
_WORD = re.compile(
    r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"
)
_SENTENCE_END = re.compile(
    r"[.!?](?=\s|$)"
)


@dataclass(frozen=True, slots=True)
class StyleFailure:
    """One controlled-style validation failure."""

    path: str
    code: str
    message: str

    def __str__(self) -> str:
        return (
            f"[{self.code}] "
            f"{self.path}: "
            f"{self.message}"
        )


class StyleError(ValueError):
    """Every failure from one controlled-style render."""

    code = "controlled_style_invalid"

    def __init__(
        self,
        failures: list[StyleFailure],
    ) -> None:
        self.failures = tuple(failures)
        super().__init__(
            "\n".join(
                str(failure)
                for failure in self.failures
            )
        )


def _case(
    source: str,
    replacement: str,
) -> str:
    if source.isupper():
        return replacement.upper()

    if source[:1].isupper():
        return (
            replacement[:1].upper()
            + replacement[1:]
        )

    return replacement


def _rewrite(text: str) -> str:
    for pattern, replacement in _SUBSTITUTIONS:
        text = pattern.sub(
            lambda match: _case(
                match.group(0),
                replacement,
            ),
            text,
        )

    return text


def _validate(
    path: str,
    text: str,
) -> list[StyleFailure]:
    failures: list[StyleFailure] = []

    if "\n" in text or "\r" in text:
        failures.append(
            StyleFailure(
                path,
                "ste_line_count",
                "text must be one line",
            )
        )

    if len(_WORD.findall(text)) > 20:
        failures.append(
            StyleFailure(
                path,
                "ste_sentence_length",
                "text must contain at most 20 words",
            )
        )

    if len(_SENTENCE_END.findall(text)) > 1:
        failures.append(
            StyleFailure(
                path,
                "ste_sentence_count",
                "text must contain at most one sentence",
            )
        )

    for pattern in _PROHIBITED:
        if pattern.search(text):
            failures.append(
                StyleFailure(
                    path,
                    "ste_prohibited_term",
                    f"text contains {pattern.pattern}",
                )
            )

    return failures


def _style_steps(
    steps: list[dict[str, object]],
    path: str,
    failures: list[StyleFailure],
) -> None:
    for index, step in enumerate(steps):
        step_path = f"{path}.{index}"
        kind = step.get("kind")

        if kind == "act":
            text = _rewrite(
                str(step["instruction"])
            )
            step["instruction"] = text
            failures.extend(
                _validate(
                    f"{step_path}.instruction",
                    text,
                )
            )

        elif kind == "fail":
            text = _rewrite(
                str(step["message"])
            )
            step["message"] = text
            failures.extend(
                _validate(
                    f"{step_path}.message",
                    text,
                )
            )

        elif kind == "if":
            then = step.get("then")
            if isinstance(then, list):
                _style_steps(
                    then,
                    f"{step_path}.then",
                    failures,
                )

            otherwise = step.get("otherwise")
            if isinstance(otherwise, list):
                _style_steps(
                    otherwise,
                    f"{step_path}.otherwise",
                    failures,
                )


def _style_node(
    data: dict[str, object],
    path: str,
    failures: list[StyleFailure],
) -> None:
    instructions = data.get("instructions")
    if isinstance(instructions, list):
        for index, instruction in enumerate(
            instructions
        ):
            if not isinstance(instruction, dict):
                continue

            text = _rewrite(
                str(instruction["body"])
            )
            instruction["body"] = text
            failures.extend(
                _validate(
                    (
                        f"{path}.instructions."
                        f"{index}.body"
                    ),
                    text,
                )
            )

    triggers = data.get("triggers")
    if isinstance(triggers, list):
        for index, trigger in enumerate(
            triggers
        ):
            if not isinstance(trigger, dict):
                continue

            text = _rewrite(
                str(trigger["when"])
            )
            trigger["when"] = text
            failures.extend(
                _validate(
                    (
                        f"{path}.triggers."
                        f"{index}.when"
                    ),
                    text,
                )
            )

    processes = data.get("processes")
    if isinstance(processes, list):
        for index, process in enumerate(
            processes
        ):
            if not isinstance(process, dict):
                continue

            steps = process.get("steps")
            if isinstance(steps, list):
                _style_steps(
                    steps,
                    (
                        f"{path}.processes."
                        f"{index}.steps"
                    ),
                    failures,
                )

    children = data.get("children")
    if isinstance(children, list):
        for index, child in enumerate(children):
            if isinstance(child, dict):
                _style_node(
                    child,
                    f"{path}.children.{index}",
                    failures,
                )


def styled_node(
    node: Node,
    style: StyleName = "authored",
) -> Node:
    """Return a render-only copy with one wording profile."""
    if style == "authored":
        return node

    if style != "asd-ste100-9":
        raise ValueError(
            f"unknown OAK style {style}"
        )

    data = node.model_dump(
        mode="python",
        by_alias=True,
    )
    failures: list[StyleFailure] = []

    _style_node(
        data,
        node.id,
        failures,
    )

    if failures:
        raise StyleError(failures)

    return type(node).model_validate(data)
