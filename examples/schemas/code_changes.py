"""Author the ported code changes format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Node, NonEmpty, Regex, Schema, SchemaBindingError, Type, parse, render, resolve, where
from examples.schemas.repeat_marker import repeat_marker_instruction

PLACEHOLDER_CHANGE_TITLE = "CHANGE_TITLE"
PLACEHOLDER_CHANGE_DESCRIPTION = "CHANGE_DESCRIPTION"
PLACEHOLDER_FILE_PATH = "FILE_PATH"
PLACEHOLDER_LANG = "LANG"
PLACEHOLDER_COMPLETE_CODE = "COMPLETE_CODE"

code_changes_schema = Schema(
    id="code-changes",
    name="Code Changes",
    purpose="Display updated and new files with complete code, one block per file separated by a rule.",
    template=(
        "## <CHANGE_TITLE>\n"
        "\n"
        "<CHANGE_DESCRIPTION>\n"
        "File: <FILE_PATH>\n"
        "```<LANG>\n"
        "<COMPLETE_CODE>\n"
        "```\n"
        "\n"
        "---\n"
        "\n"
        "..."
    ),
    where=[
        where(PLACEHOLDER_CHANGE_TITLE, Type(of="string"), NonEmpty(), description="the title for the set of changes"),
        where(PLACEHOLDER_CHANGE_DESCRIPTION, Type(of="string"), NonEmpty(), description="one terse present-voice description of the change, never changelog style"),
        where(PLACEHOLDER_FILE_PATH, Type(of="path"), Regex(pattern="^[A-Za-z0-9._\\-][A-Za-z0-9._/\\-]*$"), description="the repository-relative file path without parent traversal"),
        where(PLACEHOLDER_LANG, Type(of="string"), NonEmpty(), description="one code language name for GitHub-flavored Markdown"),
        where(PLACEHOLDER_COMPLETE_CODE, Type(of="string"), NonEmpty(), description="the complete file contents with terse present-voice comments"),
    ],
)

code_changes_node = Node(
    instructions=[repeat_marker_instruction],
    schemas=[code_changes_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {
    PLACEHOLDER_CHANGE_TITLE: "Omit empty parts",
    PLACEHOLDER_CHANGE_DESCRIPTION: "The render skips empty parts.",
    PLACEHOLDER_FILE_PATH: "oak/render/oak/groupings.py",
    PLACEHOLDER_LANG: "python",
    PLACEHOLDER_COMPLETE_CODE: "def _node_xml(node): ...",
}
_REJECTED_BINDINGS = (
    (PLACEHOLDER_CHANGE_TITLE, ""),
    (PLACEHOLDER_FILE_PATH, "/etc/passwd"),
)


def build() -> str:
    """Render, parse, resolve, round-trip, and bind the authored code changes node."""
    rendered = render(code_changes_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("code changes example changed during render and parse")
    schema = parsed.schemas[0]
    schema.bind(_ACCEPTED_BINDING)
    for placeholder, value in _REJECTED_BINDINGS:
        try:
            schema.bind({**_ACCEPTED_BINDING, placeholder: value})
        except SchemaBindingError:
            continue
        raise RuntimeError(f"code changes accepted an invalid {placeholder}")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
