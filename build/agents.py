"""Generate the five-file exploration bundle; never install or launch a native host."""

from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Node, parse, render, resolve
from examples.parallel_exploration import example, explorer
from build.generated import write_generated

PACKAGE = ROOT / "generated" / "oak.agents"
ADAPTOR_SOURCE = ROOT / ".agents" / "adaptors" / "codex" / "adaptor.oak.md"
NATIVE_PATH = "parallel_exploration/codex/.codex/agents/oak-explorer.toml"
NATIVE_NAME = "oak-explorer"
NATIVE_DESCRIPTION = "Read-only repository exploration with revision-bound findings, file evidence, coverage and gaps."


def adaptor_node() -> Node:
    """Load the maintained declarative mapping, not generated delivery content."""
    for path in (ADAPTOR_SOURCE, *ADAPTOR_SOURCE.parents):
        if path.is_symlink():
            raise ValueError("Codex adaptor source cannot traverse a symbolic link")
        if path == ROOT:
            break
    node = parse(ADAPTOR_SOURCE.read_text(encoding="utf-8"))
    if any((node.instructions, node.state, node.triggers, node.processes, node.interfaces)):
        raise ValueError("Codex adaptor must contain constants and schemas only")
    resolve(node)
    return node


def _toml_text(text: str) -> str:
    """Prefer readable literal strings, with JSON-compatible basic-string escaping."""
    if "'''" not in text and not any(ord(char) < 32 and char not in "\t\n" or ord(char) == 127 for char in text):
        return "'''\n" + text + "'''"
    return json.dumps(text, ensure_ascii=False).replace("\x7f", "\\u007f")


def native_agent(instructions: str, defaults: Mapping[str, object]) -> str:
    """Serialize this native artifact contract and check lossless TOML decoding."""
    if (set(defaults) != {"sandbox_mode", "approval_policy", "web_search", "agents"}
            or any(not isinstance(defaults[key], str) for key in ("sandbox_mode", "approval_policy", "web_search"))
            or not isinstance(defaults["agents"], dict) or set(defaults["agents"]) != {"enabled"}
            or not isinstance(defaults["agents"]["enabled"], bool)):
        raise ValueError("Codex defaults need three text settings and one agents.enabled boolean")
    metadata = {"name": NATIVE_NAME, "description": NATIVE_DESCRIPTION, "developer_instructions": instructions}
    lines = ["# Generated from OAK. Configuration defaults are not enforcement evidence."]
    lines.extend((f"name = {json.dumps(NATIVE_NAME)}", f"description = {json.dumps(NATIVE_DESCRIPTION)}",
                  f"developer_instructions = {_toml_text(instructions)}"))
    lines.extend(f"{name} = {json.dumps(defaults[name])}" for name in ("sandbox_mode", "approval_policy", "web_search"))
    lines.extend(("", "[agents]", "enabled = " + json.dumps(defaults["agents"]["enabled"]), ""))
    text = "\n".join(lines)
    if tomllib.loads(text) != {**metadata, **defaults}:
        raise ValueError("native TOML did not preserve the exact agent contract")
    return text


def artifacts() -> dict[Path, str]:
    """Derive every delivered path from maintained sources in one operation."""
    adaptor = adaptor_node()
    defaults = next(entry.value for entry in adaptor.constants if entry.id == "native-defaults")
    if not isinstance(defaults, dict):
        raise ValueError("Codex native-defaults must be an object")
    worker = explorer.build()
    return {
        PACKAGE / "parallel_exploration/coordinator.oak.md": example.build(),
        PACKAGE / "parallel_exploration/explorer.oak.md": worker,
        PACKAGE / "parallel_exploration/sample.oak.md": render(example.sample()),
        PACKAGE / NATIVE_PATH: native_agent(worker, defaults),
        PACKAGE / "adaptors/codex/adaptor.oak.md": render(adaptor) + "\n",
    }


def write() -> Path:
    write_generated(artifacts(), root=ROOT / "generated", owned=PACKAGE)
    return PACKAGE


if __name__ == "__main__":
    print(f"wrote {write()}")
