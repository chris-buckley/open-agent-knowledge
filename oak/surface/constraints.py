"""Constraint and Where authored-surface descriptors."""

from __future__ import annotations

from oak.node.parts.schemas.constraints import (
    AtLeast,
    AtMost,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Type,
)
from oak.node.parts.schemas.model import Where
from oak.surface.model import _surface

CONSTRAINT_SURFACES = (
    _surface(
        "constraint-type",
        Type,
        "is <OF>",
        rendered=("of",),
        fixed=("kind",),
    ),
    _surface(
        "constraint-one-of",
        OneOf,
        "is one of <VALUES>",
        rendered=("values",),
        fixed=("kind",),
    ),
    _surface(
        "constraint-regex",
        Regex,
        "matches `<PATTERN>`",
        rendered=("pattern",),
        fixed=("kind",),
    ),
    _surface(
        "constraint-non-empty",
        NonEmpty,
        "is non-empty",
        fixed=("kind",),
    ),
    _surface(
        "constraint-max-chars",
        MaxChars,
        "is at most <N> characters",
        rendered=("n",),
        fixed=("kind",),
    ),
    _surface(
        "constraint-lines",
        Lines,
        "has <MIN> to <MAX> lines",
        rendered=(
            "min",
            "max",
        ),
        fixed=("kind",),
    ),
    _surface(
        "constraint-list-of",
        ListOf,
        "is a list of <ITEM> joined by `<SEPARATOR>`",
        rendered=(
            "item",
            "separator",
        ),
        fixed=("kind",),
    ),
    _surface(
        "constraint-at-least",
        AtLeast,
        "is at least <VALUE>",
        rendered=("value",),
        fixed=("kind",),
    ),
    _surface(
        "constraint-at-most",
        AtMost,
        "is at most <VALUE>",
        rendered=("value",),
        fixed=("kind",),
    ),
    _surface(
        "where",
        Where,
        "- <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>.",
        rendered=(
            "placeholder",
            "constraints",
            "examples",
            "description",
        ),
    ),
)

__all__ = [
    "CONSTRAINT_SURFACES",
]
