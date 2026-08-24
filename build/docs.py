"""Generate one markdown document per model."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build.examples import MODELS, field_examples, model_examples, model_schema

TARGET = ROOT / "outputs" / "docs"
_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _filename(model: type) -> str:
    return _BOUNDARY.sub("-", model.__name__).lower() + ".md"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def document(model: type) -> str:
    """Return one generated model document."""
    schema = model_schema(model)
    title = schema.get("title")
    description = schema.get("description")

    if not isinstance(title, str) or not title:
        raise RuntimeError(f"{model.__name__} has no title")
    if not isinstance(description, str) or not description:
        raise RuntimeError(f"{model.__name__} has no description")

    lines = [
        f"# {title}",
        "",
        description,
        "",
        "## Examples",
        "",
        "```json",
        _json(model_examples(model)),
        "```",
        "",
        "## Fields",
    ]

    for name, field in model.model_fields.items():
        if not field.description:
            raise RuntimeError(f"{model.__name__}.{name} has no description")

        lines.extend(
            (
                "",
                f"### {field.title or name.replace('_', ' ').title()}",
                "",
                f"`{name}`",
                "",
                field.description,
                "",
                "```json",
                _json(field_examples(model, name)),
                "```",
            )
        )

    return "\n".join(lines) + "\n"


def documents() -> dict[str, str]:
    """Return every generated model document."""
    return {
        _filename(model): document(model)
        for model in MODELS
    }


def write() -> Path:
    """Write the generated documentation snapshot."""
    TARGET.mkdir(parents=True, exist_ok=True)
    for stale in TARGET.glob("*.md"):
        stale.unlink()

    for name, text in documents().items():
        (TARGET / name).write_text(
            text,
            encoding="utf-8",
            newline="\n",
        )

    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
