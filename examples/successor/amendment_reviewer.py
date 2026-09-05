"""Author one leaf worker that challenges a proposed OAK amendment."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Emit,
    Instruction,
    Interface,
    Node,
    NonEmpty,
    OneOf,
    Process,
    Schema,
    Trigger,
    Type,
    parse,
    render,
    resolve,
    where,
)
if __package__:
    from examples.bindings import local_bindings
else:
    from bindings import local_bindings

SCHEMA_AMENDMENT_REVIEW_REQUEST = "schema.amendment-review-request"
SCHEMA_AMENDMENT_REVIEW = "schema.amendment-review"
PROCESS_REVIEW_AMENDMENT = "process.review-amendment"
INTERFACE_REVIEW_REQUEST_INPUT = "interface.review-request"
INTERFACE_REVIEW_OUTPUT = "interface.review-result"

EVENT_AMENDMENT_REVIEW_REQUESTED = "An amendment review is requested."

PLACEHOLDER_CURRENT_OAK = "CURRENT_OAK"
PLACEHOLDER_AMENDMENT_ID = "AMENDMENT_ID"
PLACEHOLDER_AMENDMENT = "AMENDMENT"
PLACEHOLDER_RATIONALE = "RATIONALE"
PLACEHOLDER_EVIDENCE = "EVIDENCE"
PLACEHOLDER_PROTECTED_INVARIANTS = "PROTECTED_INVARIANTS"
PLACEHOLDER_DECISION = "DECISION"
PLACEHOLDER_REVIEW_FINDINGS = "REVIEW_FINDINGS"
PLACEHOLDER_EVIDENCE_REQUEST = "EVIDENCE_REQUEST"

REQUEST_PLACEHOLDERS = (
    PLACEHOLDER_CURRENT_OAK,
    PLACEHOLDER_AMENDMENT_ID,
    PLACEHOLDER_AMENDMENT,
    PLACEHOLDER_RATIONALE,
    PLACEHOLDER_EVIDENCE,
    PLACEHOLDER_PROTECTED_INVARIANTS,
)
REVIEW_PLACEHOLDERS = (
    PLACEHOLDER_DECISION,
    PLACEHOLDER_REVIEW_FINDINGS,
    PLACEHOLDER_EVIDENCE_REQUEST,
)

challenge_amendment_instruction = Instruction(
    id="challenge-amendment",
    body="Challenge the amendment against the supplied evidence and protected invariants.",
)
preserve_current_instruction = Instruction(
    id="preserve-current",
    body="Treat the current OAK document and protected invariants as read-only.",
)
request_evidence_instruction = Instruction(
    id="request-evidence",
    body="Request evidence when the amendment cannot yet be justified.",
)
reject_breach_instruction = Instruction(
    id="reject-breach",
    body="Reject an amendment that breaks a protected invariant.",
)
forbid_publication_instruction = Instruction(
    id="forbid-publication",
    body="Do not compile, ratify, or publish a successor.",
)
amendment_reviewer_instructions = [
    challenge_amendment_instruction,
    preserve_current_instruction,
    request_evidence_instruction,
    reject_breach_instruction,
    forbid_publication_instruction,
]

amendment_review_request_schema = Schema(
    id="amendment-review-request",
    name="Amendment Review Request",
    purpose="Carry one proposed amendment and the evidence needed to challenge it.",
    template=(
        "Current OAK: <CURRENT_OAK>\n"
        "Amendment id: <AMENDMENT_ID>\n"
        "Amendment: <AMENDMENT>\n"
        "Rationale: <RATIONALE>\n"
        "Evidence: <EVIDENCE>\n"
        "Protected invariants: <PROTECTED_INVARIANTS>"
    ),
    where=[
        where(
            PLACEHOLDER_CURRENT_OAK,
            Type(of="string"),
            NonEmpty(),
            description="the current canonical OAK document",
        ),
        where(
            PLACEHOLDER_AMENDMENT_ID,
            Type(of="string"),
            NonEmpty(),
            description="the stable amendment identifier",
        ),
        where(
            PLACEHOLDER_AMENDMENT,
            Type(of="string"),
            NonEmpty(),
            description="the exact proposed change",
        ),
        where(
            PLACEHOLDER_RATIONALE,
            Type(of="string"),
            NonEmpty(),
            description="why the proposed change is needed",
        ),
        where(
            PLACEHOLDER_EVIDENCE,
            Type(of="string"),
            description="the supplied implementation or validation evidence, empty when absent",
        ),
        where(
            PLACEHOLDER_PROTECTED_INVARIANTS,
            Type(of="string"),
            NonEmpty(),
            description="the invariants every successor must preserve",
        ),
    ],
)

amendment_review_schema = Schema(
    id="amendment-review",
    name="Amendment Review",
    purpose="Carry the independent decision and evidence request for one amendment.",
    template=(
        "Decision: <DECISION>\n"
        "Findings: <REVIEW_FINDINGS>\n"
        "Evidence request: <EVIDENCE_REQUEST>"
    ),
    where=[
        where(
            PLACEHOLDER_DECISION,
            Type(of="string"),
            OneOf(values=["accept", "reject", "needs-evidence"]),
            description="the independent amendment decision",
        ),
        where(
            PLACEHOLDER_REVIEW_FINDINGS,
            Type(of="string"),
            NonEmpty(),
            description="the evidence-based review findings",
        ),
        where(
            PLACEHOLDER_EVIDENCE_REQUEST,
            Type(of="string"),
            description="the missing evidence request, empty when none is needed",
        ),
    ],
)

amendment_review_requested_trigger = Trigger(
    id="amendment-review-requested",
    event=EVENT_AMENDMENT_REVIEW_REQUESTED,
    source=INTERFACE_REVIEW_REQUEST_INPUT,
    process=PROCESS_REVIEW_AMENDMENT,
)

review_amendment_process = Process(
    id="review-amendment",
    name="Review amendment",
    input=SCHEMA_AMENDMENT_REVIEW_REQUEST,
    output=SCHEMA_AMENDMENT_REVIEW,
    steps=[
        ACT(
            (
                "For <AMENDMENT_ID>, challenge <AMENDMENT> with <RATIONALE> and "
                "<EVIDENCE> against <CURRENT_OAK> and "
                "<PROTECTED_INVARIANTS>, then produce "
                "<DECISION>, <REVIEW_FINDINGS>, and <EVIDENCE_REQUEST>."
            ),
            input=SCHEMA_AMENDMENT_REVIEW_REQUEST,
            output=SCHEMA_AMENDMENT_REVIEW,
            inputs=local_bindings(REQUEST_PLACEHOLDERS),
            outputs=list(REVIEW_PLACEHOLDERS),
        ),
        Emit(interface=INTERFACE_REVIEW_OUTPUT),
    ],
)

review_request_input_interface = Interface(
    id="review-request",
    flow="receives",
    schema=SCHEMA_AMENDMENT_REVIEW_REQUEST,
    description="The amendment package supplied by the successor coordinator.",
)

review_output_interface = Interface(
    id="review-result",
    flow="emits",
    schema=SCHEMA_AMENDMENT_REVIEW,
    description="The independent amendment decision returned to the coordinator.",
)

amendment_reviewer_node = Node(
    instructions=amendment_reviewer_instructions,
    schemas=[
        amendment_review_request_schema,
        amendment_review_schema,
    ],
    triggers=[
        amendment_review_requested_trigger,
    ],
    processes=[
        review_amendment_process,
    ],
    interfaces=[
        review_request_input_interface,
        review_output_interface,
    ],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the amendment reviewer."""
    rendered = render(amendment_reviewer_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("amendment reviewer changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
