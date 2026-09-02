"""Compose one GitHub Copilot CLI custom agent file around one rendered OAK document."""

from __future__ import annotations

import json


def frontmatter(name: str, description: str, tools: list[str]) -> str:
    """Return the Copilot CLI agent frontmatter: the name, one-line description, and exact tool allowlist."""
    lines = ["---", f"name: {name}", f"description: {json.dumps(description)}", "tools:"]
    lines.extend(f"  - {tool}" for tool in tools)
    lines.extend(["---", "", ""])
    return "\n".join(lines)


def agent_text(header: str, rendered: str) -> str:
    """Return one agent file: the frontmatter, then the OAK document as the whole prompt."""
    return header + rendered + "\n"
