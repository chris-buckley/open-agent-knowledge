"""Author the ported code map format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import AtLeast, Node, NonEmpty, Regex, Schema, SchemaBindingError, Type, parse, render, resolve, where
from examples.schemas.repeat_marker import repeat_marker_instruction

PLACEHOLDER_AREA_TITLE = "AREA_TITLE"
PLACEHOLDER_SHORT_DESC = "SHORT_DESC"
PLACEHOLDER_REPO_NAME = "REPO_NAME"
PLACEHOLDER_REL_PATH = "REL_PATH"
PLACEHOLDER_LINE_FROM = "LINE_FROM"
PLACEHOLDER_LINE_TO = "LINE_TO"
PLACEHOLDER_LANG = "LANG"
PLACEHOLDER_SNIPPET = "SNIPPET"

code_map_schema = Schema(
    id="code-map",
    name="Code Map",
    purpose="Display relevant code snippets with links to their source lines.",
    template=(
        "<AREA_TITLE>\n"
        "> [<SHORT_DESC>](<REPO_NAME>/<REL_PATH>#L<LINE_FROM>-L<LINE_TO>)\n"
        "```<LANG>\n"
        "<SNIPPET>\n"
        "```\n"
        "\n"
        "..."
    ),
    where=[
        where(PLACEHOLDER_AREA_TITLE, Type(of="string"), NonEmpty(), description="the title of the area being described"),
        where(PLACEHOLDER_SHORT_DESC, Type(of="string"), NonEmpty(), description="one short description of the code snippet"),
        where(PLACEHOLDER_REPO_NAME, Type(of="string"), Regex(pattern="^[A-Za-z0-9._\\-]+$"), description="one path segment naming the repository"),
        where(PLACEHOLDER_REL_PATH, Type(of="path"), Regex(pattern="^[A-Za-z0-9._\\-][A-Za-z0-9._/\\-]*$"), description="the repository-relative file path without parent traversal"),
        where(PLACEHOLDER_LINE_FROM, Type(of="integer"), AtLeast(value=1), description="the first snippet line number"),
        where(PLACEHOLDER_LINE_TO, Type(of="integer"), AtLeast(value=PLACEHOLDER_LINE_FROM), description="the last snippet line number"),
        where(PLACEHOLDER_LANG, Type(of="string"), NonEmpty(), description="one code language name for GitHub-flavored Markdown"),
        where(PLACEHOLDER_SNIPPET, Type(of="string"), NonEmpty(), description="the code lines from LINE_FROM to LINE_TO, each prefixed with its source line number"),
    ],
)

code_map_node = Node(
    instructions=[repeat_marker_instruction],
    schemas=[code_map_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")

_ACCEPTED_BINDING = {
    PLACEHOLDER_AREA_TITLE: "Part rendering",
    PLACEHOLDER_SHORT_DESC: "the part filter",
    PLACEHOLDER_REPO_NAME: "open-agent-knowledge",
    PLACEHOLDER_REL_PATH: "oak/render/oak/groupings.py",
    PLACEHOLDER_LINE_FROM: 66,
    PLACEHOLDER_LINE_TO: 75,
    PLACEHOLDER_LANG: "python",
    PLACEHOLDER_SNIPPET: "66: def _node_xml(node):",
}
_REJECTED_BINDINGS = ((PLACEHOLDER_LINE_TO, 1),)


def build() -> str:
    """Render, parse, resolve, round-trip, and bind the authored code map node."""
    rendered = render(code_map_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("code map example changed during render and parse")
    schema = parsed.schemas[0]
    schema.bind(_ACCEPTED_BINDING)
    for placeholder, value in _REJECTED_BINDINGS:
        try:
            schema.bind({**_ACCEPTED_BINDING, placeholder: value})
        except SchemaBindingError:
            continue
        raise RuntimeError(f"code map accepted an invalid {placeholder}")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
