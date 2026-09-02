"""Author the ported documentation index format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Node, NonEmpty, Schema, Type, parse, render, resolve, where
from examples.schemas.repeat_marker import repeat_marker_instruction

docs_index_schema = Schema(
    id="docs-index",
    name="Documentation Index",
    purpose="Map documentation hierarchically for navigation: groups contain pages, pages contain headings.",
    template=(
        "# <PROJECT_TITLE> Documentation Map\n"
        "\n"
        "> Fetch the complete documentation index at: <INDEX_URL>\n"
        "> Last updated: <TIMESTAMP>\n"
        "\n"
        "## <GROUP_NAME>\n"
        "\n"
        "### [<PAGE_TITLE>](<PAGE_URL>)\n"
        "* <HEADING_TEXT>\n"
        "  * <SUBHEADING_TEXT>\n"
        "\n"
        "..."
    ),
    where=[
        where("PROJECT_TITLE", Type(of="string"), NonEmpty(), description="the name of the project or documentation set"),
        where("INDEX_URL", Type(of="uri"), description="the URL where this index can be fetched"),
        where("TIMESTAMP", Type(of="datetime"), description="when the index was generated"),
        where("GROUP_NAME", Type(of="string"), NonEmpty(), description="the documentation section name"),
        where("PAGE_TITLE", Type(of="string"), NonEmpty(), description="the title of the documentation page"),
        where("PAGE_URL", Type(of="uri"), description="the link to the documentation page"),
        where("HEADING_TEXT", Type(of="string"), NonEmpty(), description="one heading from the page"),
        where("SUBHEADING_TEXT", Type(of="string"), NonEmpty(), description="one nested heading under its parent"),
    ],
)

docs_index_node = Node(
    instructions=[repeat_marker_instruction],
    schemas=[docs_index_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the authored documentation index node."""
    rendered = render(docs_index_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("documentation index example changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
