"""Two fixed facts; no process, mutable state, boundary, or host action is needed.

Regenerate in the repository: python -m examples.fixed_knowledge.example
Detached demonstration: python example.py with the declared OAK runtime installed.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from oak import Constant, Node, parse, render, resolve

service_name_constant = Constant(id="service-name", value="Task board")
title_limit_constant = Constant(id="title-limit", value=120)
knowledge_node = Node(constants=[service_name_constant, title_limit_constant])
TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    text = render(knowledge_node)
    for grouping in ("xml", "markdown"):
        grouped = render(knowledge_node, grouping=grouping)
        parsed = parse(grouped)
        resolve(parsed)
        if render(parsed, grouping=grouping) != grouped:
            raise RuntimeError("fixed knowledge changed during round-trip")
    return text


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
