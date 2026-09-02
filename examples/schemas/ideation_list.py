"""Author the ported ideation list format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import AtLeast, AtMost, Lines, Node, NonEmpty, Schema, SchemaBindingError, Type, parse, render, resolve, where
from examples.schemas.repeat_marker import repeat_marker_instruction

PLACEHOLDER_TASK_TITLE = "TASK_TITLE"
PLACEHOLDER_IDEA_COUNT = "IDEA_COUNT"
PLACEHOLDER_IDEA_NUMBER = "IDEA_NUMBER"
PLACEHOLDER_IDEA_TITLE = "IDEA_TITLE"
PLACEHOLDER_IDEA_SUMMARY = "IDEA_SUMMARY"
PLACEHOLDER_IDEA_DETAILS = "IDEA_DETAILS"

ideation_list_schema = Schema(
    id="ideation-list",
    name="Ideation List",
    purpose="Generate structured brainstorming ideas for a given task, one block per idea separated by a rule.",
    template=(
        "## <TASK_TITLE>\n"
        "\n"
        "Ideas: <IDEA_COUNT>\n"
        "\n"
        "[<IDEA_NUMBER>] <IDEA_TITLE>\n"
        "Summary: <IDEA_SUMMARY>\n"
        "Details: <IDEA_DETAILS>\n"
        "\n"
        "---\n"
        "\n"
        "..."
    ),
    where=[
        where(PLACEHOLDER_TASK_TITLE, Type(of="string"), NonEmpty(), description="the task or topic for ideation"),
        where(PLACEHOLDER_IDEA_COUNT, Type(of="integer"), AtLeast(value=1), description="the total number of ideas, the list holds exactly this many"),
        where(PLACEHOLDER_IDEA_NUMBER, Type(of="integer"), AtLeast(value=1), AtMost(value=PLACEHOLDER_IDEA_COUNT), description="the sequential idea number"),
        where(PLACEHOLDER_IDEA_TITLE, Type(of="string"), NonEmpty(), description="one short present-tense active-voice title"),
        where(PLACEHOLDER_IDEA_SUMMARY, Type(of="string"), Lines(min=1, max=1), description="one present-tense active-voice sentence"),
        where(PLACEHOLDER_IDEA_DETAILS, Type(of="string"), NonEmpty(), description="two to four conceptual sentences without implementation, code, or pseudo-code"),
    ],
)

ideation_list_node = Node(
    instructions=[repeat_marker_instruction],
    schemas=[ideation_list_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {
    PLACEHOLDER_TASK_TITLE: "Reduce render tokens",
    PLACEHOLDER_IDEA_COUNT: 3,
    PLACEHOLDER_IDEA_NUMBER: 2,
    PLACEHOLDER_IDEA_TITLE: "Omit empty parts",
    PLACEHOLDER_IDEA_SUMMARY: "The render skips a part with no entries.",
    PLACEHOLDER_IDEA_DETAILS: "The parser treats a missing part as empty. The document shrinks.",
}
_REJECTED_BINDINGS = (
    (PLACEHOLDER_IDEA_COUNT, 0),
    (PLACEHOLDER_IDEA_NUMBER, 9),
)


def build() -> str:
    """Render, parse, resolve, round-trip, and bind the authored ideation list node."""
    rendered = render(ideation_list_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("ideation list example changed during render and parse")
    schema = parsed.schemas[0]
    schema.bind(_ACCEPTED_BINDING)
    for placeholder, value in _REJECTED_BINDINGS:
        try:
            schema.bind({**_ACCEPTED_BINDING, placeholder: value})
        except SchemaBindingError:
            continue
        raise RuntimeError(f"ideation list accepted an invalid {placeholder}")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
