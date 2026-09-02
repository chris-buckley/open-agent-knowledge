"""Author one leaf worker that proves a candidate OAK successor."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    BindingValue,
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
    parse,
    render,
    resolve,
    where,
)

SCHEMA_SUCCESSOR_VERIFICATION_REQUEST = "schema.successor-verification-request"
SCHEMA_SUCCESSOR_PROOF = "schema.successor-proof"
PROCESS_VERIFY_SUCCESSOR = "process.verify-successor"
INTERFACE_VERIFICATION_REQUEST_INPUT = "interface.verification-request-input"
INTERFACE_PROOF_OUTPUT = "interface.proof-output"

TOOL_OAK_VERIFY_SUCCESSOR = "oak.verify-successor"
EVENT_SUCCESSOR_VERIFICATION_REQUESTED = "A successor verification is requested."

PLACEHOLDER_CURRENT_OAK = "CURRENT_OAK"
PLACEHOLDER_CANDIDATE_OAK = "CANDIDATE_OAK"
PLACEHOLDER_AMENDMENT = "AMENDMENT"
PLACEHOLDER_PROTECTED_INVARIANTS = "PROTECTED_INVARIANTS"
PLACEHOLDER_VALID = "VALID"
PLACEHOLDER_PARSES = "PARSES"
PLACEHOLDER_RESOLVES = "RESOLVES"
PLACEHOLDER_CANONICAL = "CANONICAL"
PLACEHOLDER_INVARIANTS_PRESERVED = "INVARIANTS_PRESERVED"
PLACEHOLDER_SCOPE_EXACT = "SCOPE_EXACT"
PLACEHOLDER_PROOF = "PROOF"

REQUEST_PLACEHOLDERS = (
    PLACEHOLDER_CURRENT_OAK,
    PLACEHOLDER_CANDIDATE_OAK,
    PLACEHOLDER_AMENDMENT,
    PLACEHOLDER_PROTECTED_INVARIANTS,
)
PROOF_PLACEHOLDERS = (
    PLACEHOLDER_VALID,
    PLACEHOLDER_PARSES,
    PLACEHOLDER_RESOLVES,
    PLACEHOLDER_CANONICAL,
    PLACEHOLDER_INVARIANTS_PRESERVED,
    PLACEHOLDER_SCOPE_EXACT,
    PLACEHOLDER_PROOF,
)

successor_verifier_instructions = [
    Instruction(
        id="verify-independently",
        body="Verify the candidate independently from the compiler that produced it.",
    ),
    Instruction(
        id="require-canonical",
        body="Require the candidate to parse, resolve, and round-trip canonically.",
    ),
    Instruction(
        id="preserve-invariants",
        body="Require every protected invariant and current instruction to remain true.",
    ),
    Instruction(
        id="enforce-scope",
        body="Require the candidate change to equal the accepted amendment exactly.",
    ),
    Instruction(
        id="forbid-publication",
        body="Do not alter, ratify, or publish the candidate.",
    ),
]

successor_verification_request_schema = Schema(
    id="successor-verification-request",
    name="Successor Verification Request",
    purpose="Carry the current and candidate OAK documents with their governing amendment.",
    template=(
        "Current OAK: <CURRENT_OAK>\n"
        "Candidate OAK: <CANDIDATE_OAK>\n"
        "Amendment: <AMENDMENT>\n"
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
            PLACEHOLDER_CANDIDATE_OAK,
            Type(of="string"),
            NonEmpty(),
            description="the proposed canonical successor document",
        ),
        where(
            PLACEHOLDER_AMENDMENT,
            Type(of="string"),
            NonEmpty(),
            description="the exact accepted amendment",
        ),
        where(
            PLACEHOLDER_PROTECTED_INVARIANTS,
            Type(of="string"),
            NonEmpty(),
            description="the invariants every successor must preserve",
        ),
    ],
)

successor_proof_schema = Schema(
    id="successor-proof",
    name="Successor Proof",
    purpose="Carry the independent machine-verifiable proof for one candidate successor.",
    template=(
        "Valid: <VALID>\n"
        "Parses: <PARSES>\n"
        "Resolves: <RESOLVES>\n"
        "Canonical: <CANONICAL>\n"
        "Invariants preserved: <INVARIANTS_PRESERVED>\n"
        "Scope exact: <SCOPE_EXACT>\n"
        "Proof: <PROOF>"
    ),
    where=[
        where(
            PLACEHOLDER_VALID,
            Type(of="boolean"),
            description="whether every required proof check passed",
        ),
        where(
            PLACEHOLDER_PARSES,
            Type(of="boolean"),
            description="whether the candidate parses as one OAK document",
        ),
        where(
            PLACEHOLDER_RESOLVES,
            Type(of="boolean"),
            description="whether every candidate target resolves",
        ),
        where(
            PLACEHOLDER_CANONICAL,
            Type(of="boolean"),
            description="whether parsing and rendering reproduces the candidate exactly",
        ),
        where(
            PLACEHOLDER_INVARIANTS_PRESERVED,
            Type(of="boolean"),
            description="whether the protected invariants remain true",
        ),
        where(
            PLACEHOLDER_SCOPE_EXACT,
            Type(of="boolean"),
            description="whether the amendment explains the complete candidate change",
        ),
        where(
            PLACEHOLDER_PROOF,
            Type(of="string"),
            NonEmpty(),
            description="the concise evidence for the proof checks",
        ),
    ],
)

successor_verification_requested_trigger = Trigger(
    id="successor-verification-requested",
    event=EVENT_SUCCESSOR_VERIFICATION_REQUESTED,
    source=INTERFACE_VERIFICATION_REQUEST_INPUT,
    process=PROCESS_VERIFY_SUCCESSOR,
    seed=[
        ValueBinding(
            placeholder=placeholder,
            value=InterfaceValue(
                interface=INTERFACE_VERIFICATION_REQUEST_INPUT,
                placeholder=placeholder,
            ),
        )
        for placeholder in REQUEST_PLACEHOLDERS
    ],
)

verify_successor_process = Process(
    id="verify-successor",
    name="Verify successor",
    input=SCHEMA_SUCCESSOR_VERIFICATION_REQUEST,
    output=SCHEMA_SUCCESSOR_PROOF,
    steps=[
        ACT.tool(
            TOOL_OAK_VERIFY_SUCCESSOR,
            (
                "Verify <CANDIDATE_OAK> against <CURRENT_OAK>, <AMENDMENT>, "
                "and <PROTECTED_INVARIANTS>, then produce <VALID>, <PARSES>, "
                "<RESOLVES>, <CANONICAL>, <INVARIANTS_PRESERVED>, "
                "<SCOPE_EXACT>, and <PROOF>."
            ),
            input=SCHEMA_SUCCESSOR_VERIFICATION_REQUEST,
            output=SCHEMA_SUCCESSOR_PROOF,
            inputs=[
                ValueBinding(
                    placeholder=placeholder,
                    value=BindingValue(binding=placeholder),
                )
                for placeholder in REQUEST_PLACEHOLDERS
            ],
            outputs=list(PROOF_PLACEHOLDERS),
        ),
        Emit(
            interface=INTERFACE_PROOF_OUTPUT,
            bindings=[
                ValueBinding(
                    placeholder=placeholder,
                    value=BindingValue(binding=placeholder),
                )
                for placeholder in PROOF_PLACEHOLDERS
            ],
        ),
    ],
)

verification_request_input_interface = Interface(
    id="verification-request-input",
    direction="in",
    schema=SCHEMA_SUCCESSOR_VERIFICATION_REQUEST,
    description="The candidate and governance context supplied by the coordinator.",
)

proof_output_interface = Interface(
    id="proof-output",
    direction="out",
    schema=SCHEMA_SUCCESSOR_PROOF,
    description="The independent proof returned to the successor coordinator.",
)

successor_verifier_node = Node(
    instructions=successor_verifier_instructions,
    schemas=[
        successor_verification_request_schema,
        successor_proof_schema,
    ],
    triggers=[
        successor_verification_requested_trigger,
    ],
    processes=[
        verify_successor_process,
    ],
    interfaces=[
        verification_request_input_interface,
        proof_output_interface,
    ],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the successor verifier."""
    rendered = render(successor_verifier_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("successor verifier changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
