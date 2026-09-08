"""Build the portable authoring skill and fuse its exact documents into an agent."""

from __future__ import annotations

import importlib.util
from types import ModuleType
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from oak import Node, render
from oak.rules import AUTHORING_GUIDANCE as GUIDANCE_SOURCE
from oak.surface import SURFACES as SURFACE_SOURCE
from build.authoring_guides import TEMPLATE_DIRECTORIES, TEMPLATE_ENTRY, knowledge_nodes, teaching_examples
from build.authoring_agent import entry_node
from build.authoring_platforms import (CODEX_SOURCE, CLAUDE_SOURCE, resource_node, profile,
                                       codex_authoring, claude_authoring)
from build.ebnf import grammar
from build.fusion import fuse
from build.generated import write_generated

PACKAGE = ROOT / "generated" / "oak-authoring.skill"
SCRIPT = PACKAGE / "scripts" / "validate.py"
VALIDATOR_SOURCE = ROOT / "build" / "authoring_validator.py"
TARGET = ROOT / "generated" / "oak-authoring.oak.md"
ENTRY = "SKILL.oak.md"  # Virtual identity for the OAK body beneath skill metadata.


def validator_module() -> ModuleType:
    """Read the helper's version and immutable validator identity without running it."""
    spec = importlib.util.spec_from_file_location("oak_authoring_validator", VALIDATOR_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing optional validator helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skill_documents() -> dict[str, str]:
    """The exact OAK material shared by progressive loading and agent fusion."""
    validator = validator_module()
    nodes = knowledge_nodes(VALIDATOR_SOURCE.read_text(encoding="utf-8"), validator.SKILL_VERSION, validator.REVISION)
    return {ENTRY: render(entry_node()),
            **{path: render(node) for path, node in nodes.items()}}


def tree(documents: dict[str, str] | None = None) -> Node:
    return fuse(documents if documents is not None else skill_documents(), entry=ENTRY)


def authoring() -> str:
    return render(tree()) + "\n"


def artifacts() -> dict[Path, str]:
    validator = validator_module()
    shared = skill_documents()
    metadata = {
        "name": "oak-authoring",
        "description": "Create, read, update or delete OAK directly or through optional guided intent development. Preserve supplied meaning, choose justified parts and schema shapes, and show the evolving draft. No installation is needed; programmatic validation is optional and dependency installation needs separate consent.",
        "metadata": {"version": validator.SKILL_VERSION, "oak-revision": validator.REVISION,
                     "validator-sha256": validator.SOURCE_SHA256},
    }
    frontmatter = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n\n"
    standalone = render(tree(shared)) + "\n"
    return {
        SCRIPT: VALIDATOR_SOURCE.read_text(encoding="utf-8"),
        PACKAGE / "SKILL.md": frontmatter + shared[ENTRY] + "\n",
        **{PACKAGE / path: text + "\n" for path, text in shared.items() if path != ENTRY},
        **{PACKAGE / path: text + "\n" for path, text in teaching_examples().items()},
        PACKAGE / "references" / "oak.ebnf": grammar(),
        PACKAGE / "_template" / "SKILL.md": TEMPLATE_ENTRY,
        **{PACKAGE / "_template" / path / ".gitkeep": "" for path in TEMPLATE_DIRECTORIES},
        PACKAGE / "platforms/codex/templates/.codex/agents/oak-authoring.toml":
            codex_authoring(standalone, profile(resource_node(CODEX_SOURCE), "authoring-profile")),
        PACKAGE / "platforms/claude/templates/.claude/agents/oak-authoring.md":
            claude_authoring(standalone, profile(resource_node(CLAUDE_SOURCE), "authoring-profile")),
        TARGET: standalone,
    }


def write() -> Path:
    """Generate products and prune only this generator's owned document paths."""
    write_generated(artifacts(), root=ROOT / "generated", owned=PACKAGE)
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
