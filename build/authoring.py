"""Generate the single-shot OAK authoring document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build.ebnf import grammar
from build.surfaces import all_surface_schemas, surface_example
from oak import (
    ACT,
    BindingValue,
    Call,
    Constant,
    Emit,
    Instruction,
    Interface,
    InterfaceValue,
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
from oak.render.oak.groupings import process_xml
from oak.rules import AUTHORING_GUIDANCE, RULES
from oak.surface import SURFACES

from oak.rules import RULES as RULE_SOURCE
from oak.surface import SURFACES as SURFACE_SOURCE

TARGET = ROOT / "outputs" / "authoring.md"


def _orchestrator_example() -> str:
    """Render one decomposed trigger-selected orchestrator of calls and emits."""
    orchestrator = Process(
        id="implement-task",
        name="Implement task",
        steps=[
            Call(
                process="process.plan-task",
                inputs=[
                    ValueBinding(placeholder="TASK_BRIEF", value=InterfaceValue(interface="interface.task-request-input", placeholder="TASK_BRIEF")),
                    ValueBinding(placeholder="CONTEXT", value=InterfaceValue(interface="interface.task-request-input", placeholder="CONTEXT")),
                ],
                outputs=["PLAN"],
            ),
            Call(
                process="process.implement-plan",
                inputs=[ValueBinding(placeholder="PLAN", value=BindingValue(binding="PLAN"))],
                outputs=["CHANGESET"],
            ),
            Call(
                process="process.test-changeset",
                inputs=[ValueBinding(placeholder="CHANGESET", value=BindingValue(binding="CHANGESET"))],
                outputs=["TESTS"],
            ),
            Call(
                process="process.review-changeset",
                inputs=[
                    ValueBinding(placeholder="PLAN", value=BindingValue(binding="PLAN")),
                    ValueBinding(placeholder="CHANGESET", value=BindingValue(binding="CHANGESET")),
                ],
                outputs=["FINDINGS"],
            ),
            Emit(
                interface="interface.implementation-report-output",
                bindings=[
                    ValueBinding(placeholder="CHANGESET", value=BindingValue(binding="CHANGESET")),
                    ValueBinding(placeholder="TESTS", value=BindingValue(binding="TESTS")),
                    ValueBinding(placeholder="FINDINGS", value=BindingValue(binding="FINDINGS")),
                ],
            ),
        ],
    )
    return process_xml(orchestrator)


def tree() -> Node:
    """Return the model-authored single-shot authoring document."""
    oak_document_schema = Schema(
        id="oak-document",
        name="OAK Document",
        purpose="Carry the one valid OAK document written from the supplied source.",
        template="<OAK>",
        where=[where("OAK", Type(of="string"), NonEmpty(), description="the complete valid OAK document")],
    )
    instructions = [
        *[
            Instruction(id=guidance.id, body=guidance.instruction)
            for guidance in AUTHORING_GUIDANCE
        ],
        *[
            Instruction(
                id="enforce-" + rule.code.replace("_", ""),
                body=rule.instruction,
            )
            for rule in RULES
        ],
    ]
    return Node(
        instructions=instructions,
        constants=[
            Constant(id="oak-ebnf", form="text", value=grammar(groupings=("xml",)).rstrip("\n")),
            Constant(id="canonical-oak", form="text", value=surface_example(next(surface for surface in SURFACES if surface.id == "node"))),
            Constant(id="orchestrator-example", form="text", value=_orchestrator_example()),
        ],
        schemas=[*all_surface_schemas(), oak_document_schema],
        triggers=[
            Trigger(
                id="source-supplied",
                event="Any source material is supplied with this prompt.",
                process="process.write-oak",
            )
        ],
        processes=[
            Process(
                id="write-oak",
                name="Write OAK",
                steps=[
                    ACT(
                        "Derive <DRAFT> from the complete supplied source.",
                        outputs=["DRAFT"],
                    ),
                    ACT(
                        "Validate <DRAFT> against every supplied OAK contract and produce <OAK>.",
                        inputs=[ValueBinding(placeholder="DRAFT", value=BindingValue(binding="DRAFT"))],
                        outputs=["OAK"],
                    ),
                    Emit(
                        interface="interface.oak-document-output",
                        bindings=[ValueBinding(placeholder="OAK", value=BindingValue(binding="OAK"))],
                    ),
                ],
            )
        ],
        interfaces=[
            Interface(
                id="oak-document-output",
                direction="out",
                schema="schema.oak-document",
                description="The sole OAK document returned to the caller.",
            )
        ],
    )


def authoring() -> str:
    """Return the generated single-shot authoring document."""
    return render(tree(), grouping="xml") + "\n"


def write() -> Path:
    """Write the generated authoring snapshot."""
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(authoring(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
