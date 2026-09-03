"""Author the ported link manifest format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Lines, Node, NonEmpty, Schema, Type, parse, render, resolve, where
from examples.schemas.repeat_marker import repeat_marker_instruction

link_manifest_schema = Schema(
    id="link-manifest",
    name="Link Manifest",
    purpose="List documentation links with descriptions for quick navigation, one entry per link.",
    template=(
        "# <MANIFEST_TITLE>\n"
        "\n"
        "- [<LINK_TITLE>](<LINK_URL>): <LINK_DESCRIPTION>\n"
        "..."
    ),
    where=[
        where("MANIFEST_TITLE", Type(of="string"), NonEmpty(), description="the title of the manifest or documentation set"),
        where("LINK_TITLE", Type(of="string"), NonEmpty(), description="the display title for the link"),
        where("LINK_URL", Type(of="uri"), description="the URL to the resource"),
        where("LINK_DESCRIPTION", Type(of="string"), Lines(min=1, max=1), description="one sentence describing the linked resource"),
    ],
)

link_manifest_node = Node(
    instructions=[repeat_marker_instruction],
    schemas=[link_manifest_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the authored link manifest node."""
    rendered = render(link_manifest_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("link manifest example changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
