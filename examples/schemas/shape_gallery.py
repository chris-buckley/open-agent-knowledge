"""Four fixed-cardinality OAK shapes and their populated text examples.

These are ordinary schemas, not schema kinds or a new format registry.
The fixture helper substitutes already validated values once. It is not a
production Markdown renderer, escaping engine, or repeated-instance facility.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Constant, Lines, Node, NonEmpty, Regex, Schema, Type, parse, render, resolve, schema_xml, where
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX

PLACEHOLDER_CRITERION = "CRITERION"
PLACEHOLDER_CURRENT = "CURRENT"
PLACEHOLDER_PROPOSED = "PROPOSED"
PLACEHOLDER_DECISION = "DECISION"
PLACEHOLDER_RATIONALE = "RATIONALE"
PLACEHOLDER_GOAL = "GOAL"
PLACEHOLDER_STEP = "STEP"
PLACEHOLDER_CHECK = "CHECK"
PLACEHOLDER_FILE_PATH = "FILE_PATH"
PLACEHOLDER_CODE = "CODE"

comparison_schema = Schema(
    id="option-comparison", name="Option Comparison",
    purpose="Compare current and proposed behaviour for one criterion.",
    template=(
        "| Criterion | Current | Proposed |\n"
        "| --- | --- | --- |\n"
        "| <CRITERION> | <CURRENT> | <PROPOSED> |"
    ),
    where=[
        where(name, Type(of="string"), Regex(pattern=r"^[^|\r\n]+$"))
        for name in (PLACEHOLDER_CRITERION, PLACEHOLDER_CURRENT, PLACEHOLDER_PROPOSED)
    ],
)

decision_schema = Schema(
    id="decision-brief", name="Decision Brief",
    purpose="State one decision and explain its rationale.",
    template="## Decision\n<DECISION>\n\n### Rationale\n<RATIONALE>",
    where=[
        where(PLACEHOLDER_DECISION, Type(of="string"), NonEmpty()),
        where(PLACEHOLDER_RATIONALE, Type(of="string"), NonEmpty()),
    ],
)

outline_schema = Schema(
    id="work-outline", name="Work Outline",
    purpose="Nest one implementation step and its check beneath one goal.",
    template="1. <GOAL>\n   1. <STEP>\n      1. <CHECK>",
    where=[
        where(name, Type(of="string"), NonEmpty(), Lines(min=1, max=1))
        for name in (PLACEHOLDER_GOAL, PLACEHOLDER_STEP, PLACEHOLDER_CHECK)
    ],
)

file_schema = Schema(
    id="code-file", name="Code File",
    purpose="Present one Python file with its complete source.",
    template="### <FILE_PATH>\n\n```python\n<CODE>\n```",
    where=[
        where(PLACEHOLDER_FILE_PATH, Type(of="path"), Regex(pattern=r"^[A-Za-z0-9_./\-]+$")),
        where(PLACEHOLDER_CODE, Type(of="string"), NonEmpty()),
    ],
)

SHAPES = (comparison_schema, decision_schema, outline_schema, file_schema)
SAMPLE_BINDINGS = {
    comparison_schema.id: {
        PLACEHOLDER_CRITERION: "Blank title",
        PLACEHOLDER_CURRENT: "Accepted",
        PLACEHOLDER_PROPOSED: "Rejected",
    },
    decision_schema.id: {
        PLACEHOLDER_DECISION: "Reject blank titles.",
        PLACEHOLDER_RATIONALE: "A title must identify the task.",
    },
    outline_schema.id: {
        PLACEHOLDER_GOAL: "Require meaningful titles.",
        PLACEHOLDER_STEP: "Check the stripped title.",
        PLACEHOLDER_CHECK: "Test empty, whitespace, and valid titles.",
    },
    file_schema.id: {
        PLACEHOLDER_FILE_PATH: "title.py",
        PLACEHOLDER_CODE: 'def valid_title(title: str) -> bool:\n    return bool(title.strip())',
    },
}

EXPECTED_INSTANCES = {
    comparison_schema.id: "| Criterion | Current | Proposed |\n| --- | --- | --- |\n| Blank title | Accepted | Rejected |",
    decision_schema.id: "## Decision\nReject blank titles.\n\n### Rationale\nA title must identify the task.",
    outline_schema.id: "1. Require meaningful titles.\n   1. Check the stripped title.\n      1. Test empty, whitespace, and valid titles.",
    file_schema.id: "### title.py\n\n```python\ndef valid_title(title: str) -> bool:\n    return bool(title.strip())\n```",
}

_TOKEN = re.compile(f"<({PLACEHOLDER_SYNTAX.body})>")
TARGET = Path(__file__).with_suffix(".oak.md")


def populate_example(schema: Schema, values: Mapping[str, object]) -> str:
    """Fill these text fixtures once, after binding validation, without escaping."""
    schema.bind(values)
    text_values = {name: value for name, value in values.items() if isinstance(value, str)}
    if len(text_values) != len(values):
        raise TypeError("the shape examples require text values")
    return _TOKEN.sub(lambda match: text_values[match.group(1)], schema.template)


def prompt_examples() -> str:
    """Pair compact OAK schema definitions with their populated instances."""
    pairs = []
    for schema in SHAPES:
        compact = Schema(id=schema.id, template=schema.template, where=schema.where)
        instance = populate_example(schema, SAMPLE_BINDINGS[schema.id])
        pairs.append(schema_xml(compact) + "\nPopulated instance:\n" + instance)
    return "Fixed-cardinality examples; choose or combine shapes as needed.\n\n" + "\n\n".join(pairs)


shape_gallery_node = Node(
    constants=[
        Constant(id=schema.id + "-instance", form="text", value=EXPECTED_INSTANCES[schema.id])
        for schema in SHAPES
    ],
    schemas=[comparison_schema, decision_schema, outline_schema, file_schema],
)


def build() -> str:
    """Validate values and exact populated examples, then round-trip the OAK."""
    for schema in SHAPES:
        if populate_example(schema, SAMPLE_BINDINGS[schema.id]) != EXPECTED_INSTANCES[schema.id]:
            raise RuntimeError(f"populated {schema.id} differs from its expected layout")
    text = render(shape_gallery_node)
    for grouping in ("xml", "markdown"):
        grouped = render(shape_gallery_node, grouping=grouping)
        parsed = parse(grouped)
        resolve(parsed)
        if render(parsed, grouping=grouping) != grouped:
            raise RuntimeError(f"shape gallery did not round-trip through {grouping}")
    return text


def write() -> Path:
    """Write the canonical sibling OAK document."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
