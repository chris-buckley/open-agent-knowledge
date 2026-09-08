"""Load bounded product knowledge and serialize native artifacts without a client."""

from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
import tomllib

import yaml

from oak import Node, parse, render, resolve

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = Path("build/authoring_resources")
CATALOGUE_SOURCE = RESOURCE_ROOT / "assets/constants/artifact-kinds.oak.md"
CODEX_SOURCE = RESOURCE_ROOT / "platforms/codex/adaptor.oak.md"
CLAUDE_SOURCE = RESOURCE_ROOT / "platforms/claude/adaptor.oak.md"
RESOURCE_PATHS = (CATALOGUE_SOURCE, CODEX_SOURCE, CLAUDE_SOURCE)
NATIVE_NAME = "oak-explorer"
NATIVE_DESCRIPTION = "Read-only repository exploration with revision-bound findings, file evidence, coverage and gaps."
AUTHORING_DESCRIPTION = "Create, read, update or delete OAK; clarify intent only when useful."


def resource_node(source: Path) -> Node:
    """Read one named, canonical, self-contained declarative resource."""
    if source not in RESOURCE_PATHS:
        raise ValueError("unregistered authoring resource")
    path = ROOT / source
    for current in (path, *path.parents):
        if current.is_symlink():
            raise ValueError("authoring resource cannot traverse a symbolic link")
        if current == ROOT:
            break
    if not path.resolve().is_relative_to((ROOT / RESOURCE_ROOT).resolve()):
        raise ValueError("authoring resource escapes maintained resource root")
    text = path.read_text(encoding="utf-8")
    node = parse(text)
    if any((node.instructions, node.state, node.triggers, node.processes, node.interfaces)):
        raise ValueError("authoring resource must contain constants and schemas only")
    if render(node) + "\n" != text:
        raise ValueError("authoring resource must be canonical")
    # No loader is supplied: these three maintained resources have local closure.
    resolve(node)
    return node


def adaptor_node() -> Node:
    return resource_node(CODEX_SOURCE)


def profile(node: Node, identifier: str) -> dict[str, object]:
    """Read source-owned native metadata, rejecting a malformed profile."""
    value = next((item.value for item in node.constants if item.id == identifier), None)
    if not isinstance(value, dict):
        raise ValueError(f"{identifier} must be an object")
    return dict(value)


def _toml_text(text: str) -> str:
    """Preserve the explorer's literal/basic-string byte convention."""
    if "'''" not in text and not any(ord(char) < 32 and char not in "\t\n" or ord(char) == 127 for char in text):
        return "'''\n" + text + "'''"
    return json.dumps(text, ensure_ascii=False).replace("\x7f", "\\u007f")


def native_agent(instructions: str, defaults: Mapping[str, object]) -> str:
    """Preserve the existing explorer serializer and its separate profile."""
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


def codex_authoring(instructions: str, metadata: Mapping[str, object]) -> str:
    """Serialize the authorer's inherited profile with exactly one shared body."""
    expected = {"name": "oak-authoring", "description": AUTHORING_DESCRIPTION,
                "agents": {"enabled": False}}
    if dict(metadata) != expected or type(metadata.get("agents", {}).get("enabled")) is not bool:
        raise ValueError("invalid Codex authoring profile")
    text = "\n".join((f"name = {json.dumps(metadata['name'])}",
                       f"description = {json.dumps(metadata['description'])}",
                       f"developer_instructions = {_toml_text(instructions)}", "", "[agents]", "enabled = false", ""))
    if tomllib.loads(text) != {**metadata, "developer_instructions": instructions}:
        raise ValueError("native TOML did not preserve the exact authoring contract")
    return text


def claude_authoring(instructions: str, metadata: Mapping[str, object]) -> str:
    """Serialize frontmatter independently of the unmodified OAK body."""
    expected = {"name": "oak-authoring", "description": AUTHORING_DESCRIPTION,
                "model": "inherit", "permissionMode": "default", "disallowedTools": ["Agent"]}
    if dict(metadata) != expected:
        raise ValueError("invalid Claude authoring profile")
    header = yaml.safe_dump(dict(metadata), sort_keys=False, allow_unicode=True)
    text = "---\n" + header + "---\n\n" + instructions
    decoded, body = text[4:].split("---\n\n", 1)
    if yaml.safe_load(decoded) != expected or body != instructions:
        raise ValueError("native Markdown did not preserve the exact authoring contract")
    return text
