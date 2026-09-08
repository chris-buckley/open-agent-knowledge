"""Generate the five-file exploration bundle; never install or launch a native host."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import render
from examples.parallel_exploration import example, explorer
from build.generated import write_generated
from build.authoring_platforms import CODEX_SOURCE, adaptor_node, native_agent, NATIVE_NAME, NATIVE_DESCRIPTION

PACKAGE = ROOT / "generated" / "oak.agents"
ADAPTOR_SOURCE = ROOT / CODEX_SOURCE
NATIVE_PATH = "parallel_exploration/codex/.codex/agents/oak-explorer.toml"


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
