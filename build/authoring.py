"""Generate the compact single-shot OAK authoring document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build.ebnf import grammar
from examples.schemas.shape_gallery import prompt_examples
from oak import (
    ACT,
    BindingValue,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    Instruction,
    Interface,
    LiteralValue,
    Node,
    NonEmpty,
    OneOf,
    Process,
    Schema,
    Set,
    State,
    StateValue,
    Trigger,
    Type,
    ValueBinding,
    render,
    where,
)
from oak.rules import AUTHORING_GUIDANCE

from oak.rules import AUTHORING_GUIDANCE as GUIDANCE_SOURCE
from oak.surface import SURFACES as SURFACE_SOURCE

TARGET = ROOT / "outputs" / "authoring.md"

ARCHITECTURE_CAPSULE = """One UTF-8 OAK document contains one idless node.
The node has only instructions, constants, schemas, state, triggers, processes, and interfaces.
Schemas define reusable information shapes independently of boundaries and processes.
Constants are fixed, state persists across arrivals, process bindings are local, and interfaces carry complete boundary instances.
Target paths connect documents into a graph; local state and interface operations stay in the active document.
Triggers route outside occurrences; CALL composes internal process work.
OAK text is the default authored render; JSON-LD is the interchange render.
The host owns tools, credentials, transport, model selection, external side effects, persistence, and deployment."""


def canonical_example() -> str:
    """Return one compact example that exercises all seven parts."""
    request_schema = Schema(
        id="support-request",
        name="Support Request",
        purpose="Carry one support request into classification.",
        template="Message: <MESSAGE>",
        where=[
            where(
                "MESSAGE",
                Type(of="string"),
                NonEmpty(),
                description="the support request text",
            )
        ],
    )
    result_schema = Schema(
        id="support-result",
        name="Support Result",
        purpose="Carry one classified support request.",
        template="## <PRIORITY>\n\n<SUMMARY>",
        where=[
            where(
                "PRIORITY",
                Type(of="string"),
                OneOf(values=["urgent", "normal"]),
                description="the assigned urgency",
            ),
            where(
                "SUMMARY",
                Type(of="string"),
                NonEmpty(),
                description="the concise request summary",
            ),
        ],
    )
    workflow_schema = Schema(
        id="workflow-state",
        name="Workflow State",
        purpose="Constrain the persistent classification state.",
        template="Status: <STATUS>",
        where=[
            where(
                "STATUS",
                Type(of="string"),
                OneOf(values=["idle", "running"]),
                description="the current workflow status",
            )
        ],
    )
    node = Node(
        instructions=[
            Instruction(
                id="classify-support-request",
                body="Classify each support request by urgency.",
            )
        ],
        constants=[
            Constant(
                id="urgent-terms",
                value=["outage", "security"],
            )
        ],
        schemas=[request_schema, result_schema, workflow_schema],
        state=[
            State(
                id="review-status",
                schema="schema.workflow-state",
                placeholder="STATUS",
                value="idle",
            )
        ],
        triggers=[
            Trigger(
                id="support-requested",
                event="A support request is supplied.",
                source="interface.request",
                guard=Compare(
                    left=StateValue(state="state.review-status"),
                    operator="equals",
                    right=LiteralValue(value="idle"),
                ),
                process="process.classify-request",
            )
        ],
        processes=[
            Process(
                id="classify-request",
                name="Classify request",
                input="schema.support-request",
                output="schema.support-result",
                steps=[
                    Set(
                        state="state.review-status",
                        value=LiteralValue(value="running"),
                    ),
                    ACT(
                        (
                            "Classify <MESSAGE> using <URGENT_TERMS>, "
                            "then produce <PRIORITY> and <SUMMARY>."
                        ),
                        output="schema.support-result",
                        inputs=[
                            ValueBinding(
                                placeholder="MESSAGE",
                                value=BindingValue(binding="MESSAGE"),
                            ),
                            ValueBinding(
                                placeholder="URGENT_TERMS",
                                value=ConstantValue(
                                    constant="constant.urgent-terms"
                                ),
                            ),
                        ],
                        outputs=["PRIORITY", "SUMMARY"],
                    ),
                    Emit(interface="interface.result"),
                    Set(
                        state="state.review-status",
                        value=LiteralValue(value="idle"),
                    ),
                ],
            )
        ],
        interfaces=[
            Interface(
                id="request",
                flow="receives",
                schema="schema.support-request",
            ),
            Interface(
                id="result",
                flow="emits",
                schema="schema.support-result",
            ),
        ],
    )
    return render(node, grouping="xml")


def tree() -> Node:
    """Return the model-authored single-shot authoring document."""
    oak_document_schema = Schema(
        id="oak-document",
        name="OAK Document",
        purpose="Carry the one valid OAK document written from the supplied source.",
        template="<OAK>",
        where=[
            where(
                "OAK",
                Type(of="string"),
                NonEmpty(),
                description="the complete valid OAK document",
            )
        ],
    )
    return Node(
        instructions=[
            Instruction(
                id=guidance.id,
                body=guidance.instruction,
            )
            for guidance in AUTHORING_GUIDANCE
        ],
        constants=[
            Constant(
                id="architecture-capsule",
                form="text",
                value=ARCHITECTURE_CAPSULE,
            ),
            Constant(
                id="oak-ebnf",
                form="text",
                value=grammar(groupings=("xml",)).rstrip("\n"),
            ),
            Constant(
                id="schema-examples",
                form="text",
                value=prompt_examples(),
            ),
            Constant(
                id="canonical-oak",
                form="text",
                value=canonical_example(),
            ),
        ],
        schemas=[oak_document_schema],
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
                output="schema.oak-document",
                steps=[
                    ACT(
                        "Use <EXAMPLES> to choose suitable schema shapes and derive <DRAFT> from the supplied source.",
                        inputs=[ValueBinding(placeholder="EXAMPLES", value=ConstantValue(constant="constant.schema-examples"))],
                        outputs=["DRAFT"],
                    ),
                    ACT(
                        (
                            "Validate <DRAFT> against the supplied architecture, "
                            "grammar, example, and OAK contracts, then produce <OAK>."
                        ),
                        inputs=[
                            ValueBinding(
                                placeholder="DRAFT",
                                value=BindingValue(binding="DRAFT"),
                            )
                        ],
                        outputs=["OAK"],
                    ),
                    Emit(interface="interface.oak-document-output"),
                ],
            )
        ],
        interfaces=[
            Interface(
                id="oak-document-output",
                flow="emits",
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
