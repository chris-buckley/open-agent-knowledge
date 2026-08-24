"""Generate the OAK authoring prompt."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Act, Instruction, Process, Root, Schema, Trigger, render

from build.examples import MODELS, model_examples, model_schema

PRD = ROOT / "docs" / "PRD.md"
TARGET = ROOT / "outputs" / "prompt.md"
_CONSTRAINT = re.compile(r"^[0-9]+\. (.+)$")
_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _slug(name: str) -> str:
    return _BOUNDARY.sub("-", name).lower()


def _constraints() -> list[str]:
    source = PRD.read_text(encoding="utf-8")
    try:
        body = source.split("## Constraints\n", 1)[1].split("\n## ", 1)[0]
    except IndexError as error:
        raise RuntimeError("docs/PRD.md has no Constraints section") from error

    result = []
    for line in body.splitlines():
        match = _CONSTRAINT.fullmatch(line)
        if match:
            result.append(match.group(1))

    if not result:
        raise RuntimeError("docs/PRD.md has no numbered constraints")
    return result


def _safe(text: str) -> str:
    return text.replace("<", "\\u003C").replace(">", "\\u003E")


def _model_schema(model: type) -> Schema:
    schema = model_schema(model)
    title = schema.get("title")
    description = schema.get("description")

    if not isinstance(title, str) or not title:
        raise RuntimeError(f"{model.__name__} has no title")
    if not isinstance(description, str) or not description:
        raise RuntimeError(f"{model.__name__} has no description")

    fields = []
    for name, field in model.model_fields.items():
        if not field.description:
            raise RuntimeError(f"{model.__name__}.{name} has no description")
        fields.append(
            f"{field.title or name.replace('_', ' ').title()}: "
            f"{field.description}"
        )

    examples = json.dumps(
        model_examples(model),
        ensure_ascii=False,
        indent=2,
    )
    template = "\n".join(
        (
            title,
            description,
            "Fields:",
            *(f"- {item}" for item in fields),
            "Examples:",
            examples,
        )
    )

    return Schema(
        id=_slug(model.__name__),
        name=title,
        purpose=description,
        template=_safe(template),
    )


def tree() -> Root:
    """Return the model-authored prompt tree."""
    return Root(
        id="oak-authoring-prompt",
        instructions=[
            Instruction(
                id=f"constraint-{index}",
                body=text,
            )
            for index, text in enumerate(_constraints(), 1)
        ],
        schemas=[_model_schema(model) for model in MODELS],
        triggers=[
            Trigger(
                id="write-oak-trigger",
                when="A model arrives to write OAK.",
                process="write-oak",
            )
        ],
        processes=[
            Process(
                id="write-oak",
                name="Write OAK",
                steps=[
                    Act(
                        instruction="Write OAK from the supplied models."
                    )
                ],
            )
        ],
    )


def prompt() -> str:
    """Return the generated authoring prompt."""
    return render(tree()) + "\n"


def write() -> Path:
    """Write the generated authoring prompt snapshot."""
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        prompt(),
        encoding="utf-8",
        newline="\n",
    )
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
