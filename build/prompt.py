"""Generate the single-shot OAK authoring prompt."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build.ebnf import grammar
from build.surfaces import all_surface_schemas, surface_example
from oak import (
    Act,
    BindingValue,
    Constant,
    Emit,
    Instruction,
    Interface,
    Node,
    NonEmpty,
    Process,
    Schema,
    Trigger,
    Type,
    ValueBinding,
    render,
    where,
)
from oak.rules import RULES
from oak.surface import SURFACES

from oak.rules import RULES as RULE_SOURCE
from oak.surface import SURFACES as SURFACE_SOURCE

TARGET = ROOT / "outputs" / "prompt.md"

_SOURCE_RULES = (
    "Treat the complete supplied host context as the source, regardless of modality.",
    "Map directives, policies, interpretation rules, and required behaviour to instructions.",
    "Map stable values needed during use to constants.",
    "Map reusable information shapes and output contracts to schemas.",
    "Map values that can change while the knowledge runs to state.",
    "Map arrival reasons, state guards, and selected processes to triggers.",
    "Map ordered ways to perform tasks to processes.",
    "Map verifiable document-boundary crossings to interfaces.",
    "Leave a part empty when the source provides no justified entry.",
    "Do not invent state, triggers, processes, interfaces, or relative paths.",
    "Write exactly one valid OAK document containing one node.",
    "Emit the final OAK document as the sole response.",
)


def tree() -> Node:
    """Return the model-authored single-shot prompt document."""
    result_schema = Schema(
        id="oak-result",
        name="OAK Result",
        purpose="Carry the one valid OAK document written from the supplied source.",
        template="<OAK>",
        where=[where("OAK", Type(of="string"), NonEmpty(), description="the complete valid OAK document")],
    )
    instructions = [
        *[Instruction(id=f"source-rule-{index}", body=text) for index, text in enumerate(_SOURCE_RULES, 1)],
        *[Instruction(id=f"authoring-rule-{index}", body=rule.instruction) for index, rule in enumerate(RULES, 1)],
    ]
    return Node(
        instructions=instructions,
        constants=[
            Constant(id="oak-ebnf", form="text", value=grammar().rstrip("\n")),
            Constant(id="canonical-oak", form="text", value=surface_example(next(surface for surface in SURFACES if surface.id == "node"))),
        ],
        schemas=[*all_surface_schemas(), result_schema],
        triggers=[
            Trigger(
                id="write-oak-trigger",
                given=True,
                when="Any source material is supplied with this prompt.",
                then="process.write-oak",
            )
        ],
        processes=[
            Process(
                id="write-oak",
                name="Write OAK",
                steps=[
                    Act(
                        instruction="Derive <DRAFT> from the complete supplied source.",
                        outputs=["DRAFT"],
                    ),
                    Act(
                        instruction="Validate <DRAFT> against every supplied OAK contract and produce <OAK>.",
                        inputs=[ValueBinding(placeholder="DRAFT", value=BindingValue(binding="DRAFT"))],
                        outputs=["OAK"],
                    ),
                    Emit(
                        interface="interface.result",
                        bindings=[ValueBinding(placeholder="OAK", value=BindingValue(binding="OAK"))],
                    ),
                ],
            )
        ],
        interfaces=[
            Interface(
                id="result",
                direction="out",
                schema="schema.oak-result",
                description="The sole OAK document returned to the caller.",
            )
        ],
    )


def prompt() -> str:
    """Return the generated single-shot prompt."""
    return render(tree(), grouping="xml") + "\n"


def write() -> Path:
    """Write the generated authoring prompt snapshot."""
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(prompt(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
