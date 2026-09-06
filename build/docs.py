"""Generate one self-writing OAK document per authorable model."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build.surfaces import (
    AUTHORABLE_MODELS,
    model_schema,
    slug,
    surface_example,
    surface_grammar,
    surface_schema,
)
from oak import Constant, Instruction, Node, Process, render
from oak.rules import RULES
from oak.surface.registry import surfaces_for_model

from oak.rules import RULES as RULE_SOURCE
from oak.surface import SURFACES as SURFACE_SOURCE

TARGET = ROOT / "outputs" / "docs"


def _filename(model: type) -> str:
    return slug(model.__name__) + ".md"


def document(model: type) -> str:
    """Return one generated model document as markdown-grouped OAK."""
    metadata = model_schema(model)
    title = metadata.get("title")
    description = metadata.get("description")
    if not isinstance(title, str) or not title:
        raise RuntimeError(f"{model.__name__} has no title")
    if not isinstance(description, str) or not description:
        raise RuntimeError(f"{model.__name__} has no description")
    surfaces = surfaces_for_model(model)
    if not surfaces:
        raise RuntimeError(f"{model.__name__} has no surface")
    matching_rules = [rule for rule in RULES if model.__name__ in rule.models]
    node = Node(
        instructions=[
            Instruction(id="definition", body=f"{title}: {description}"),
            *[
                Instruction(id=f"rule-{index}", body=rule.instruction)
                for index, rule in enumerate(matching_rules, 1)
            ],
        ],
        constants=[
            *([migration_note()] if model is Process else []),
            *[
                Constant(id=f"example-{index}", value=surface_example(surface))
                for index, surface in enumerate(surfaces, 1)
            ],
            Constant(id="syntax-reference", value="outputs/oak.ebnf"),
            Constant(
                id="grammar",
                form="text",
                value="\n".join(surface_grammar(surface) for surface in surfaces),
            ),
        ],
        schemas=[surface_schema(surface) for surface in surfaces],
    )
    return render(node, grouping="xml") + "\n"


def migration_note() -> Constant:
    """Keep the breaking Python and interchange migration in one generated owner."""
    return Constant(
        id="statement-body-migration",
        value={
            "python": "Import Statement instead of Step. Process, Foreach, While, and Par take body instead of steps. If keeps then and otherwise. StatementModel, iter_statements, statement_values, and statements modules replace the corresponding step names without forwarding aliases.",
            "models": "Model dumps and JSON Schema use ordinary body arrays. Old steps fields, including mixed steps/body input, are rejected.",
            "json-ld": "Process, Foreach, While, and Par encode body as an explicit @list object. Instruction.body remains a string with no global list container. The ordered then term replaces thenSteps; otherwise is unchanged.",
            "unchanged": "OAK keywords, grouping delimiters, literal JSON keys, operation kinds, schema identities, execution scope, and stable diagnostic codes are unchanged. This is not Python or JSON-LD wire compatibility.",
        },
    )


def documents() -> dict[str, str]:
    """Return every generated authoring model document."""
    return {_filename(model): document(model) for model in AUTHORABLE_MODELS}


def write() -> Path:
    """Write the generated documentation snapshot."""
    TARGET.mkdir(parents=True, exist_ok=True)
    for stale in TARGET.glob("*.md"):
        stale.unlink()
    for name, text in documents().items():
        (TARGET / name).write_text(text, encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
