"""Author the ported code changes format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Instruction, Node, NonEmpty, Regex, Schema, SchemaBindingError, Type, parse, render, resolve, where

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
        where("CHANGE_TITLE", Type(of="string"), NonEmpty(), description="the title for the set of changes"),
        where("CHANGE_DESCRIPTION", Type(of="string"), NonEmpty(), description="one terse present-voice description of the change, never changelog style"),
        where("FILE_PATH", Type(of="path"), Regex(pattern="^[A-Za-z0-9._\\-][A-Za-z0-9._/\\-]*$"), description="the repository-relative file path without parent traversal"),
        where("LANG", Type(of="string"), NonEmpty(), description="one code language name for GitHub-flavored Markdown"),
        where("COMPLETE_CODE", Type(of="string"), NonEmpty(), description="the complete file contents with terse present-voice comments"),
    ],
)

code_changes_node = Node(
    instructions=[Instruction(id="repeat-marker", body="A ... line in a template marks repetition of the pattern above it.")],
    schemas=[code_changes_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {
    "CHANGE_TITLE": "Omit empty parts",
    "CHANGE_DESCRIPTION": "The render skips empty parts.",
    "FILE_PATH": "oak/render/oak/groupings.py",
    "LANG": "python",
    "COMPLETE_CODE": "def _node_xml(node): ...",
}
_REJECTED_BINDINGS = (
    ("CHANGE_TITLE", ""),
    ("FILE_PATH", "/etc/passwd"),
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
