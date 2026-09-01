"""Author the ported hierarchical outline format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Instruction, Node, NonEmpty, Schema, SchemaBindingError, Regex, Type, parse, render, resolve, where

hierarchical_outline_schema = Schema(
    id="hierarchical-outline",
    name="Hierarchical Outline",
    purpose="Generate a semantic numbered outline of at most three levels, one space of indentation per level.",
    template=(
        "## <OUTLINE_TITLE>\n"
        "\n"
        "<LEVEL_1_NUMBER> <STATEMENT>\n"
        " <LEVEL_2_NUMBER> <STATEMENT>\n"
        "  <LEVEL_3_NUMBER> <STATEMENT>\n"
        "\n"
        "..."
    ),
    where=[
        where("OUTLINE_TITLE", Type(of="string"), NonEmpty(), description="the title for the outline"),
        where("LEVEL_1_NUMBER", Type(of="string"), Regex(pattern="^[0-9]+$"), description="the level one number"),
        where("LEVEL_2_NUMBER", Type(of="string"), Regex(pattern="^[0-9]+\\.[0-9]+$"), description="the level two number"),
        where("LEVEL_3_NUMBER", Type(of="string"), Regex(pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$"), examples=["1.1.1", "1.1.2"], description="the level three number at the maximum depth"),
        where("STATEMENT", Type(of="string"), NonEmpty(), description="one atomic statement without obvious content"),
    ],
)

hierarchical_outline_node = Node(
    instructions=[Instruction(id="repeat-marker", body="A ... line in a template marks repetition of the pattern above it.")],
    schemas=[hierarchical_outline_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {
    "OUTLINE_TITLE": "Plan",
    "LEVEL_1_NUMBER": "1",
    "LEVEL_2_NUMBER": "1.1",
    "LEVEL_3_NUMBER": "1.1.1",
    "STATEMENT": "Define the goal.",
}
_REJECTED_BINDINGS = (("LEVEL_1_NUMBER", "one"),)


def build() -> str:
    """Render, parse, resolve, round-trip, and bind the authored hierarchical outline node."""
    rendered = render(hierarchical_outline_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("hierarchical outline example changed during render and parse")
    schema = parsed.schemas[0]
    schema.bind(_ACCEPTED_BINDING)
    for placeholder, value in _REJECTED_BINDINGS:
        try:
            schema.bind({**_ACCEPTED_BINDING, placeholder: value})
        except SchemaBindingError:
            continue
        raise RuntimeError(f"hierarchical outline accepted an invalid {placeholder}")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
