"""Author the ported error format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Lines, MaxChars, Node, Schema, SchemaBindingError, Type, parse, render, resolve, where

error_schema = Schema(
    id="error",
    name="Error",
    purpose="Carry one single-line reason when a requested shape cannot be produced.",
    template="Error: <REASON>",
    where=[
        where(
            "REASON",
            Type(of="string"),
            Lines(min=1, max=1),
            MaxChars(n=160),
            description="why the requested shape cannot be produced",
        ),
    ],
)

error_node = Node(schemas=[error_schema])

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {"REASON": "the source names no schema"}
_REJECTED_BINDINGS = (
    ("REASON", "line one\nline two"),
    ("REASON", "r" * 200),
)


def build() -> str:
    """Render, parse, resolve, round-trip, and bind the authored error node."""
    rendered = render(error_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("error example changed during render and parse")
    schema = parsed.schemas[0]
    schema.bind(_ACCEPTED_BINDING)
    for placeholder, value in _REJECTED_BINDINGS:
        try:
            schema.bind({**_ACCEPTED_BINDING, placeholder: value})
        except SchemaBindingError:
            continue
        raise RuntimeError(f"error accepted an invalid {placeholder}")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
