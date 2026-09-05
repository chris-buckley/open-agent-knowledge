"""Build the portable authoring skill and fuse its exact documents into an agent."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from oak import Node, render
from oak.rules import AUTHORING_GUIDANCE as GUIDANCE_SOURCE
from oak.surface import SURFACES as SURFACE_SOURCE
from build.authoring_guides import entry_node, knowledge_nodes, teaching_examples
from build.ebnf import grammar
from build.fusion import fuse

PACKAGE = ROOT / "skills" / "oak-authoring"
SCRIPT = PACKAGE / "scripts" / "validate.py"
TARGET = ROOT / "outputs" / "oak-authoring.oak.md"
ENTRY = "SKILL.oak.md"  # Virtual identity for the OAK body beneath skill metadata.


def validator_module():
    """Read the helper's version and immutable validator identity without running it."""
    spec = importlib.util.spec_from_file_location("oak_authoring_validator", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing optional validator helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skill_documents() -> dict[str, str]:
    """The exact OAK material shared by progressive loading and agent fusion."""
    validator = validator_module()
    nodes = knowledge_nodes(SCRIPT.read_text(encoding="utf-8"), validator.SKILL_VERSION, validator.REVISION)
    return {ENTRY: render(entry_node(), grouping="markdown"),
            **{path: render(node, grouping="markdown") for path, node in nodes.items()}}


def tree(documents: dict[str, str] | None = None) -> Node:
    return fuse(documents if documents is not None else skill_documents(), entry=ENTRY)


def authoring() -> str:
    return render(tree(), grouping="markdown") + "\n"


def artifacts() -> dict[Path, str]:
    validator = validator_module()
    shared = skill_documents()
    metadata = {
        "name": "oak-authoring",
        "description": "Author, review, or revise Open Agent Knowledge (OAK) documents from supplied knowledge. Choose justified parts and schema shapes with populated examples. Use when writing OAK; no installation is needed. Programmatic validation is optional and installation requires separate permission.",
        "metadata": {"version": validator.SKILL_VERSION, "oak-revision": validator.REVISION,
                     "validator-sha256": validator.SOURCE_SHA256},
    }
    frontmatter = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n\n"
    return {
        PACKAGE / "SKILL.md": frontmatter + shared[ENTRY] + "\n",
        **{PACKAGE / path: text + "\n" for path, text in shared.items() if path != ENTRY},
        **{PACKAGE / path: text + "\n" for path, text in teaching_examples().items()},
        PACKAGE / "references" / "10-oak.ebnf": grammar(),
        TARGET: render(tree(shared), grouping="markdown") + "\n",
    }


def write() -> Path:
    """Generate products and prune only this generator's owned document paths."""
    expected = artifacts()
    for path in (PACKAGE / "references").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".ebnf"} and path not in expected:
            path.unlink()
    for path in sorted((PACKAGE / "references").rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    (ROOT / "outputs" / "authoring.md").unlink(missing_ok=True)
    for path, text in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
