"""Author one proof-carrying OAK successor machine and its two leaf workers."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Arrival,
    Assert,
    AtLeast,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    LiteralValue,
    Node,
    NonEmpty,
    OakParseError,
    OneOf,
    Process,
    ResolutionError,
    Schema,
    Set,
    State,
    StateValue,
    ToolContract,
    Trigger,
    Type,
    ValueBinding,
    Where,
    execute,
    parse,
    render,
    resolve,
    where,
)
from examples.agents.bindings import interface_bindings, local_bindings
from examples.agents.amendment_reviewer import (
    INTERFACE_REVIEW_REQUEST_INPUT as WORKER_REVIEW_REQUEST_INPUT,
    REVIEW_PLACEHOLDERS,
    REQUEST_PLACEHOLDERS as REVIEW_REQUEST_PLACEHOLDERS,
    amendment_reviewer_node,
)
from examples.agents.successor_verifier import (
    INTERFACE_VERIFICATION_REQUEST_INPUT as WORKER_VERIFICATION_REQUEST_INPUT,
    PROOF_PLACEHOLDERS,
    REQUEST_PLACEHOLDERS as VERIFICATION_REQUEST_PLACEHOLDERS,
    SCHEMA_SUCCESSOR_PROOF,
    SCHEMA_SUCCESSOR_VERIFICATION_REQUEST,
    TOOL_OAK_VERIFY_SUCCESSOR,
    successor_verifier_node,
)

SCHEMA_REVIEWER_REQUEST = "amendment_reviewer.oak.md#schema.amendment-review-request"
SCHEMA_REVIEWER_RESULT = "amendment_reviewer.oak.md#schema.amendment-review"
SCHEMA_VERIFIER_REQUEST = "successor_verifier.oak.md#schema.successor-verification-request"
SCHEMA_VERIFIER_RESULT = "successor_verifier.oak.md#schema.successor-proof"
SCHEMA_GOVERNANCE = "schema.governance"
SCHEMA_AMENDMENT_PROPOSAL = "schema.amendment-proposal"
SCHEMA_AMENDMENT_CYCLE = "schema.amendment-cycle"
SCHEMA_EVIDENCE_SUPPLEMENT = "schema.evidence-supplement"
SCHEMA_ACCEPTED_AMENDMENT = "schema.accepted-amendment"
SCHEMA_CANDIDATE_SUCCESSOR = "schema.candidate-successor"
SCHEMA_SUCCESSOR_PUBLICATION = "schema.successor-publication"

CONSTANT_CURRENT_OAK = "constant.current-oak"
CONSTANT_PROTECTED_INVARIANTS = "constant.protected-invariants"
STATE_CURRENT_REVISION = "state.current-revision"
STATE_REVIEW_STATUS = "state.review-status"
STATE_PENDING_AMENDMENT_ID = "state.pending-amendment-id"
STATE_PENDING_AMENDMENT = "state.pending-amendment"
STATE_PENDING_RATIONALE = "state.pending-rationale"

PROCESS_DISPATCH_REVIEW = "process.dispatch-review"
PROCESS_DISPATCH_VERIFICATION = "process.dispatch-verification"
PROCESS_GOVERN_SUCCESSION = "process.govern-succession"

INTERFACE_AMENDMENT_INPUT = "interface.amendment-input"
INTERFACE_EVIDENCE_INPUT = "interface.evidence-input"
INTERFACE_REVIEW_OUTCOME_OUTPUT = "interface.review-outcome-output"
INTERFACE_SUCCESSOR_OUTPUT = "interface.successor-output"

TOOL_AGENT_AMENDMENT_REVIEWER = "agent.amendment-reviewer"
TOOL_AGENT_SUCCESSOR_VERIFIER = "agent.successor-verifier"
TOOL_OAK_COMPILE_SUCCESSOR = "oak.compile-successor"

EVENT_AMENDMENT_PROPOSED = "An amendment is proposed."
EVENT_EVIDENCE_SUPPLIED = "Evidence for the pending amendment is supplied."

PLACEHOLDER_CURRENT_OAK = "CURRENT_OAK"
PLACEHOLDER_PROTECTED_INVARIANTS = "PROTECTED_INVARIANTS"
PLACEHOLDER_REVISION = "REVISION"
PLACEHOLDER_STATUS = "STATUS"
PLACEHOLDER_AMENDMENT_ID = "AMENDMENT_ID"
PLACEHOLDER_AMENDMENT = "AMENDMENT"
PLACEHOLDER_RATIONALE = "RATIONALE"
PLACEHOLDER_EVIDENCE = "EVIDENCE"
PLACEHOLDER_RESUME = "RESUME"
PLACEHOLDER_DECISION = "DECISION"
PLACEHOLDER_REVIEW_FINDINGS = "REVIEW_FINDINGS"
PLACEHOLDER_EVIDENCE_REQUEST = "EVIDENCE_REQUEST"
PLACEHOLDER_CURRENT_REVISION = "CURRENT_REVISION"
PLACEHOLDER_PRIOR_REVISION = "PRIOR_REVISION"
PLACEHOLDER_NEXT_REVISION = "NEXT_REVISION"
PLACEHOLDER_CANDIDATE_OAK = "CANDIDATE_OAK"
PLACEHOLDER_VALID = "VALID"
PLACEHOLDER_PARSES = "PARSES"
PLACEHOLDER_RESOLVES = "RESOLVES"
PLACEHOLDER_CANONICAL = "CANONICAL"
PLACEHOLDER_INVARIANTS_PRESERVED = "INVARIANTS_PRESERVED"
PLACEHOLDER_SCOPE_EXACT = "SCOPE_EXACT"
PLACEHOLDER_PROOF = "PROOF"

AMENDMENT_PROPOSAL_PLACEHOLDERS = (
    PLACEHOLDER_AMENDMENT_ID,
    PLACEHOLDER_AMENDMENT,
    PLACEHOLDER_RATIONALE,
    PLACEHOLDER_EVIDENCE,
)
ACCEPTED_AMENDMENT_PLACEHOLDERS = (
    PLACEHOLDER_CURRENT_OAK,
    PLACEHOLDER_CURRENT_REVISION,
    PLACEHOLDER_AMENDMENT_ID,
    PLACEHOLDER_AMENDMENT,
    PLACEHOLDER_RATIONALE,
    PLACEHOLDER_REVIEW_FINDINGS,
    PLACEHOLDER_PROTECTED_INVARIANTS,
)

STATUS_IDLE = "idle"
STATUS_REVIEWING = "reviewing"
STATUS_NEEDS_EVIDENCE = "needs-evidence"
STATUS_REJECTED = "rejected"
STATUS_RATIFIED = "ratified"
DECISION_ACCEPT = "accept"
DECISION_REJECT = "reject"
DECISION_NEEDS_EVIDENCE = "needs-evidence"

preserve_one_node_instruction = Instruction(
    id="preserve-one-node",
    body="Preserve exactly one node in every OAK document.",
)
preserve_seven_parts_instruction = Instruction(
    id="preserve-seven-parts",
    body="Preserve the closed seven-part OAK structure.",
)
constitution_node = Node(
    instructions=[preserve_one_node_instruction, preserve_seven_parts_instruction],
)
CURRENT_OAK_TEXT = render(constitution_node)
PROTECTED_INVARIANTS_TEXT = (
    "One OAK document contains exactly one node.\n"
    "The seven OAK parts remain closed.\n"
    "Every published successor parses, resolves, and round-trips canonically."
)

protect_current_instruction = Instruction(
    id="protect-current",
    body="Treat the current OAK document as immutable.",
)
require_proof_instruction = Instruction(
    id="require-proof",
    body="Never publish a successor without a valid independent proof.",
)
preserve_invariants_instruction = Instruction(
    id="preserve-invariants",
    body="Preserve every protected invariant across succession.",
)
request_evidence_instruction = Instruction(
    id="request-evidence",
    body="Request evidence instead of guessing when review support is incomplete.",
)
separate_authority_instruction = Instruction(
    id="separate-authority",
    body="Keep review, compilation, verification, ratification, and publication separate.",
)
successor_instructions = [
    protect_current_instruction,
    require_proof_instruction,
    preserve_invariants_instruction,
    request_evidence_instruction,
    separate_authority_instruction,
]


def required_text(placeholder: str, description: str) -> Where:
    return where(placeholder, Type(of="string"), NonEmpty(), description=description)


def text_value(placeholder: str, description: str) -> Where:
    return where(placeholder, Type(of="string"), description=description)


governance_schema = Schema(
    id="governance",
    name="Governance",
    purpose="Constrain the immutable and persistent values that govern succession.",
    template=(
        "Current OAK: <CURRENT_OAK>\n"
        "Protected invariants: <PROTECTED_INVARIANTS>\n"
        "Revision: <REVISION>\n"
        "Status: <STATUS>\n"
        "Pending amendment id: <AMENDMENT_ID>\n"
        "Pending amendment: <AMENDMENT>\n"
        "Pending rationale: <RATIONALE>"
    ),
    where=[
        required_text(PLACEHOLDER_CURRENT_OAK, "the current canonical OAK document"),
        required_text(PLACEHOLDER_PROTECTED_INVARIANTS, "the invariants every successor must preserve"),
        where(PLACEHOLDER_REVISION, Type(of="integer"), AtLeast(value=1), description="the current positive revision"),
        where(
            PLACEHOLDER_STATUS,
            Type(of="string"),
            OneOf(values=[STATUS_IDLE, STATUS_REVIEWING, STATUS_NEEDS_EVIDENCE, STATUS_REJECTED, STATUS_RATIFIED]),
            description="the persistent succession status",
        ),
        text_value(PLACEHOLDER_AMENDMENT_ID, "the pending amendment identifier, empty before a proposal"),
        text_value(PLACEHOLDER_AMENDMENT, "the pending amendment, empty before a proposal"),
        text_value(PLACEHOLDER_RATIONALE, "the pending rationale, empty before a proposal"),
    ],
)

amendment_proposal_schema = Schema(
    id="amendment-proposal",
    name="Amendment Proposal",
    purpose="Carry one amendment proposal into the successor machine.",
    template=(
        "Amendment id: <AMENDMENT_ID>\n"
        "Amendment: <AMENDMENT>\n"
        "Rationale: <RATIONALE>\n"
        "Evidence: <EVIDENCE>"
    ),
    where=[
        required_text(PLACEHOLDER_AMENDMENT_ID, "the stable amendment identifier"),
        required_text(PLACEHOLDER_AMENDMENT, "the exact proposed change"),
        required_text(PLACEHOLDER_RATIONALE, "why the proposed change is needed"),
        text_value(PLACEHOLDER_EVIDENCE, "the supplied evidence, empty when none is available"),
    ],
)

amendment_cycle_schema = Schema(
    id="amendment-cycle",
    name="Amendment Cycle",
    purpose="Carry one new or resumed amendment through succession.",
    template=(
        "Amendment id: <AMENDMENT_ID>\n"
        "Amendment: <AMENDMENT>\n"
        "Rationale: <RATIONALE>\n"
        "Evidence: <EVIDENCE>\n"
        "Resume: <RESUME>"
    ),
    where=[
        required_text(PLACEHOLDER_AMENDMENT_ID, "the stable amendment identifier"),
        required_text(PLACEHOLDER_AMENDMENT, "the exact proposed change"),
        required_text(PLACEHOLDER_RATIONALE, "why the proposed change is needed"),
        text_value(PLACEHOLDER_EVIDENCE, "the supplied review evidence, empty when absent"),
        where(PLACEHOLDER_RESUME, Type(of="boolean"), description="whether this cycle resumes a pending amendment"),
    ],
)

evidence_supplement_schema = Schema(
    id="evidence-supplement",
    name="Evidence Supplement",
    purpose="Carry evidence for the amendment retained in state.",
    template="Amendment id: <AMENDMENT_ID>\nEvidence: <EVIDENCE>",
    where=[
        required_text(PLACEHOLDER_AMENDMENT_ID, "the pending amendment identifier"),
        required_text(PLACEHOLDER_EVIDENCE, "the evidence supplied for the pending amendment"),
    ],
)

accepted_amendment_schema = Schema(
    id="accepted-amendment",
    name="Accepted Amendment",
    purpose="Carry the independently reviewed amendment into compilation.",
    template=(
        "Current OAK: <CURRENT_OAK>\n"
        "Current revision: <CURRENT_REVISION>\n"
        "Amendment id: <AMENDMENT_ID>\n"
        "Amendment: <AMENDMENT>\n"
        "Rationale: <RATIONALE>\n"
        "Review findings: <REVIEW_FINDINGS>\n"
        "Protected invariants: <PROTECTED_INVARIANTS>"
    ),
    where=[
        required_text(PLACEHOLDER_CURRENT_OAK, "the current canonical OAK document"),
        where(PLACEHOLDER_CURRENT_REVISION, Type(of="integer"), AtLeast(value=1), description="the revision being succeeded"),
        required_text(PLACEHOLDER_AMENDMENT_ID, "the accepted amendment identifier"),
        required_text(PLACEHOLDER_AMENDMENT, "the exact accepted amendment"),
        required_text(PLACEHOLDER_RATIONALE, "why the amendment is needed"),
        required_text(PLACEHOLDER_REVIEW_FINDINGS, "the independent findings that support compilation"),
        required_text(PLACEHOLDER_PROTECTED_INVARIANTS, "the invariants the compiler must preserve"),
    ],
)

candidate_successor_schema = Schema(
    id="candidate-successor",
    name="Candidate Successor",
    purpose="Carry the compiled candidate before independent verification.",
    template="<CANDIDATE_OAK>",
    where=[required_text(PLACEHOLDER_CANDIDATE_OAK, "the compiled candidate OAK document")],
)

successor_publication_schema = Schema(
    id="successor-publication",
    name="Successor Publication",
    purpose="Publish one canonical successor only together with its amendment and proof.",
    template=(
        "Decision: <DECISION>\n"
        "Prior revision: <PRIOR_REVISION>\n"
        "Next revision: <NEXT_REVISION>\n"
        "Amendment id: <AMENDMENT_ID>\n"
        "Amendment: <AMENDMENT>\n"
        "Rationale: <RATIONALE>\n"
        "Successor OAK: <CANDIDATE_OAK>\n"
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
            PLACEHOLDER_DECISION,
            Type(of="string"),
            OneOf(values=[DECISION_ACCEPT]),
            description="the ratified amendment decision",
        ),
        where(PLACEHOLDER_PRIOR_REVISION, Type(of="integer"), AtLeast(value=1), description="the revision that the successor replaces"),
        where(PLACEHOLDER_NEXT_REVISION, Type(of="integer"), AtLeast(value=2), description="the published successor revision"),
        required_text(PLACEHOLDER_AMENDMENT_ID, "the ratified amendment identifier"),
        required_text(PLACEHOLDER_AMENDMENT, "the exact amendment implemented by the successor"),
        required_text(PLACEHOLDER_RATIONALE, "why the amendment was accepted"),
        required_text(PLACEHOLDER_CANDIDATE_OAK, "the canonical successor OAK document"),
        *[
            where(name, Type(of="boolean"), OneOf(values=[True]), description=description)
            for name, description in (
                (PLACEHOLDER_VALID, "whether every required proof check passed"),
                (PLACEHOLDER_PARSES, "whether the successor parses as one OAK document"),
                (PLACEHOLDER_RESOLVES, "whether every successor target resolves"),
                (PLACEHOLDER_CANONICAL, "whether the successor round-trips exactly"),
                (PLACEHOLDER_INVARIANTS_PRESERVED, "whether every protected invariant remains true"),
                (PLACEHOLDER_SCOPE_EXACT, "whether the amendment explains the complete change"),
            )
        ],
        required_text(PLACEHOLDER_PROOF, "the independent evidence carried with the successor"),
    ],
)

current_oak_constant = Constant(
    id="current-oak",
    form="text",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_CURRENT_OAK,
    value=CURRENT_OAK_TEXT,
)
protected_invariants_constant = Constant(
    id="protected-invariants",
    form="text",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_PROTECTED_INVARIANTS,
    value=PROTECTED_INVARIANTS_TEXT,
)
current_revision_state = State(
    id="current-revision",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_REVISION,
    value=13,
)
review_status_state = State(
    id="review-status",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_STATUS,
    value=STATUS_IDLE,
)
pending_amendment_id_state = State(
    id="pending-amendment-id",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_AMENDMENT_ID,
    value="",
)
pending_amendment_state = State(
    id="pending-amendment",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_AMENDMENT,
    value="",
)
pending_rationale_state = State(
    id="pending-rationale",
    schema=SCHEMA_GOVERNANCE,
    placeholder=PLACEHOLDER_RATIONALE,
    value="",
)

amendment_proposed_trigger = Trigger(
    id="amendment-proposed",
    event=EVENT_AMENDMENT_PROPOSED,
    source=INTERFACE_AMENDMENT_INPUT,
    process=PROCESS_GOVERN_SUCCESSION,
    seed=[
        *interface_bindings(INTERFACE_AMENDMENT_INPUT, AMENDMENT_PROPOSAL_PLACEHOLDERS),
        ValueBinding(placeholder=PLACEHOLDER_RESUME, value=LiteralValue(value=False)),
    ],
)

evidence_supplied_trigger = Trigger(
    id="evidence-supplied",
    event=EVENT_EVIDENCE_SUPPLIED,
    source=INTERFACE_EVIDENCE_INPUT,
    guard=Compare(
        left=StateValue(state=STATE_REVIEW_STATUS),
        operator="equals",
        right=LiteralValue(value=STATUS_NEEDS_EVIDENCE),
    ),
    process=PROCESS_GOVERN_SUCCESSION,
    seed=[
        ValueBinding(
            placeholder=PLACEHOLDER_AMENDMENT_ID,
            value=InterfaceValue(interface=INTERFACE_EVIDENCE_INPUT, placeholder=PLACEHOLDER_AMENDMENT_ID),
        ),
        ValueBinding(placeholder=PLACEHOLDER_AMENDMENT, value=StateValue(state=STATE_PENDING_AMENDMENT)),
        ValueBinding(placeholder=PLACEHOLDER_RATIONALE, value=StateValue(state=STATE_PENDING_RATIONALE)),
        ValueBinding(
            placeholder=PLACEHOLDER_EVIDENCE,
            value=InterfaceValue(interface=INTERFACE_EVIDENCE_INPUT, placeholder=PLACEHOLDER_EVIDENCE),
        ),
        ValueBinding(placeholder=PLACEHOLDER_RESUME, value=LiteralValue(value=True)),
    ],
)

dispatch_review_process = Process(
    id="dispatch-review",
    name="Dispatch review",
    input=SCHEMA_REVIEWER_REQUEST,
    output=SCHEMA_REVIEWER_RESULT,
    steps=[
        ACT.tool(
            TOOL_AGENT_AMENDMENT_REVIEWER,
            (
                "For <AMENDMENT_ID>, challenge <AMENDMENT> with <RATIONALE> and "
                "<EVIDENCE> against <CURRENT_OAK> and "
                "<PROTECTED_INVARIANTS>, then produce "
                "<DECISION>, <REVIEW_FINDINGS>, and <EVIDENCE_REQUEST>."
            ),
            input=SCHEMA_REVIEWER_REQUEST,
            output=SCHEMA_REVIEWER_RESULT,
            inputs=local_bindings(REVIEW_REQUEST_PLACEHOLDERS),
            outputs=list(REVIEW_PLACEHOLDERS),
        )
    ],
)

dispatch_verification_process = Process(
    id="dispatch-verification",
    name="Dispatch verification",
    input=SCHEMA_VERIFIER_REQUEST,
    output=SCHEMA_VERIFIER_RESULT,
    steps=[
        ACT.tool(
            TOOL_AGENT_SUCCESSOR_VERIFIER,
            (
                "Verify <CANDIDATE_OAK> against <CURRENT_OAK>, <AMENDMENT>, "
                "and <PROTECTED_INVARIANTS>, then produce <VALID>, <PARSES>, "
                "<RESOLVES>, <CANONICAL>, <INVARIANTS_PRESERVED>, "
                "<SCOPE_EXACT>, and <PROOF>."
            ),
            input=SCHEMA_VERIFIER_REQUEST,
            output=SCHEMA_VERIFIER_RESULT,
            inputs=local_bindings(VERIFICATION_REQUEST_PLACEHOLDERS),
            outputs=list(PROOF_PLACEHOLDERS),
        )
    ],
)

govern_succession_process = Process(
    id="govern-succession",
    name="Govern succession",
    input=SCHEMA_AMENDMENT_CYCLE,
    steps=[
        If(
            condition=Compare(
                left=BindingValue(binding=PLACEHOLDER_RESUME),
                operator="equals",
                right=LiteralValue(value=True),
            ),
            then=[
                Assert(
                    condition=Compare(
                        left=BindingValue(binding=PLACEHOLDER_AMENDMENT_ID),
                        operator="equals",
                        right=StateValue(state=STATE_PENDING_AMENDMENT_ID),
                    ),
                    message="The evidence does not match the pending amendment.",
                )
            ],
        ),
        Set(state=STATE_PENDING_AMENDMENT_ID, value=BindingValue(binding=PLACEHOLDER_AMENDMENT_ID)),
        Set(state=STATE_PENDING_AMENDMENT, value=BindingValue(binding=PLACEHOLDER_AMENDMENT)),
        Set(state=STATE_PENDING_RATIONALE, value=BindingValue(binding=PLACEHOLDER_RATIONALE)),
        Set(state=STATE_REVIEW_STATUS, value=LiteralValue(value=STATUS_REVIEWING)),
        Call(
            process=PROCESS_DISPATCH_REVIEW,
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_CURRENT_OAK, value=ConstantValue(constant=CONSTANT_CURRENT_OAK)),
                ValueBinding(placeholder=PLACEHOLDER_AMENDMENT_ID, value=BindingValue(binding=PLACEHOLDER_AMENDMENT_ID)),
                ValueBinding(placeholder=PLACEHOLDER_AMENDMENT, value=BindingValue(binding=PLACEHOLDER_AMENDMENT)),
                ValueBinding(placeholder=PLACEHOLDER_RATIONALE, value=BindingValue(binding=PLACEHOLDER_RATIONALE)),
                ValueBinding(placeholder=PLACEHOLDER_EVIDENCE, value=BindingValue(binding=PLACEHOLDER_EVIDENCE)),
                ValueBinding(
                    placeholder=PLACEHOLDER_PROTECTED_INVARIANTS,
                    value=ConstantValue(constant=CONSTANT_PROTECTED_INVARIANTS),
                ),
            ],
            outputs=list(REVIEW_PLACEHOLDERS),
        ),
        If(
            condition=Compare(
                left=BindingValue(binding=PLACEHOLDER_DECISION),
                operator="equals",
                right=LiteralValue(value=DECISION_ACCEPT),
            ),
            then=[
                ACT.tool(
                    TOOL_OAK_COMPILE_SUCCESSOR,
                    (
                        "Apply <AMENDMENT_ID>: <AMENDMENT> with <RATIONALE> and "
                        "<REVIEW_FINDINGS> to <CURRENT_OAK> at <CURRENT_REVISION> "
                        "while preserving <PROTECTED_INVARIANTS>, then produce "
                        "<CANDIDATE_OAK>."
                    ),
                    input=SCHEMA_ACCEPTED_AMENDMENT,
                    output=SCHEMA_CANDIDATE_SUCCESSOR,
                    inputs=[
                        ValueBinding(
                            placeholder=PLACEHOLDER_CURRENT_OAK,
                            value=ConstantValue(constant=CONSTANT_CURRENT_OAK),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_CURRENT_REVISION,
                            value=StateValue(state=STATE_CURRENT_REVISION),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_AMENDMENT_ID,
                            value=BindingValue(binding=PLACEHOLDER_AMENDMENT_ID),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_AMENDMENT,
                            value=BindingValue(binding=PLACEHOLDER_AMENDMENT),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_RATIONALE,
                            value=BindingValue(binding=PLACEHOLDER_RATIONALE),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_REVIEW_FINDINGS,
                            value=BindingValue(binding=PLACEHOLDER_REVIEW_FINDINGS),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_PROTECTED_INVARIANTS,
                            value=ConstantValue(constant=CONSTANT_PROTECTED_INVARIANTS),
                        ),
                    ],
                    outputs=[PLACEHOLDER_CANDIDATE_OAK],
                ),
                Call(
                    process=PROCESS_DISPATCH_VERIFICATION,
                    inputs=[
                        ValueBinding(
                            placeholder=PLACEHOLDER_CURRENT_OAK,
                            value=ConstantValue(constant=CONSTANT_CURRENT_OAK),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_CANDIDATE_OAK,
                            value=BindingValue(binding=PLACEHOLDER_CANDIDATE_OAK),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_AMENDMENT,
                            value=BindingValue(binding=PLACEHOLDER_AMENDMENT),
                        ),
                        ValueBinding(
                            placeholder=PLACEHOLDER_PROTECTED_INVARIANTS,
                            value=ConstantValue(constant=CONSTANT_PROTECTED_INVARIANTS),
                        ),
                    ],
                    outputs=list(PROOF_PLACEHOLDERS),
                ),
                *[
                    Assert(
                        condition=Compare(
                            left=BindingValue(binding=placeholder),
                            operator="equals",
                            right=LiteralValue(value=True),
                        ),
                        message=message,
                    )
                    for placeholder, message in (
                        (PLACEHOLDER_VALID, "The successor proof is not valid."),
                        (PLACEHOLDER_PARSES, "The successor does not parse."),
                        (PLACEHOLDER_RESOLVES, "The successor does not resolve."),
                        (PLACEHOLDER_CANONICAL, "The successor is not canonical."),
                        (PLACEHOLDER_INVARIANTS_PRESERVED, "The successor breaks a protected invariant."),
                        (PLACEHOLDER_SCOPE_EXACT, "The successor contains an unexplained change."),
                    )
                ],
                ACT(
                    "Advance <CURRENT_REVISION> and produce <PRIOR_REVISION> and <NEXT_REVISION>.",
                    inputs=[
                        ValueBinding(
                            placeholder=PLACEHOLDER_CURRENT_REVISION,
                            value=StateValue(state=STATE_CURRENT_REVISION),
                        )
                    ],
                    outputs=[PLACEHOLDER_PRIOR_REVISION, PLACEHOLDER_NEXT_REVISION],
                ),
                Set(state=STATE_CURRENT_REVISION, value=BindingValue(binding=PLACEHOLDER_NEXT_REVISION)),
                Set(state=STATE_REVIEW_STATUS, value=LiteralValue(value=STATUS_RATIFIED)),
                Emit(
                    interface=INTERFACE_SUCCESSOR_OUTPUT,
                    bindings=[
                        ValueBinding(placeholder=PLACEHOLDER_DECISION, value=BindingValue(binding=PLACEHOLDER_DECISION)),
                        ValueBinding(placeholder=PLACEHOLDER_AMENDMENT_ID, value=BindingValue(binding=PLACEHOLDER_AMENDMENT_ID)),
                        ValueBinding(placeholder=PLACEHOLDER_AMENDMENT, value=BindingValue(binding=PLACEHOLDER_AMENDMENT)),
                        ValueBinding(placeholder=PLACEHOLDER_RATIONALE, value=BindingValue(binding=PLACEHOLDER_RATIONALE)),
                        *local_bindings(
                            (
                                PLACEHOLDER_PRIOR_REVISION,
                                PLACEHOLDER_NEXT_REVISION,
                                PLACEHOLDER_CANDIDATE_OAK,
                                *PROOF_PLACEHOLDERS,
                            )
                        ),
                    ],
                ),
            ],
            otherwise=[
                If(
                    condition=Compare(
                        left=BindingValue(binding=PLACEHOLDER_DECISION),
                        operator="equals",
                        right=LiteralValue(value=DECISION_NEEDS_EVIDENCE),
                    ),
                    then=[
                        Set(
                            state=STATE_REVIEW_STATUS,
                            value=LiteralValue(value=STATUS_NEEDS_EVIDENCE),
                        )
                    ],
                    otherwise=[
                        Set(
                            state=STATE_REVIEW_STATUS,
                            value=LiteralValue(value=STATUS_REJECTED),
                        )
                    ],
                ),
                Emit(
                    interface=INTERFACE_REVIEW_OUTCOME_OUTPUT,
                    bindings=local_bindings(REVIEW_PLACEHOLDERS),
                ),
            ],
        ),
    ],
)

amendment_input_interface = Interface(
    id="amendment-input",
    direction="in",
    schema=SCHEMA_AMENDMENT_PROPOSAL,
    description="The proposed amendment, rationale, and available evidence.",
)
evidence_input_interface = Interface(
    id="evidence-input",
    direction="in",
    schema=SCHEMA_EVIDENCE_SUPPLEMENT,
    description="The evidence supplied for the amendment retained in state.",
)
review_outcome_output_interface = Interface(
    id="review-outcome-output",
    direction="out",
    schema=SCHEMA_REVIEWER_RESULT,
    description="The independent decision returned when succession does not proceed.",
)
successor_output_interface = Interface(
    id="successor-output",
    direction="out",
    schema=SCHEMA_SUCCESSOR_PUBLICATION,
    description="The canonical successor published only together with its proof.",
)

successor_node = Node(
    instructions=successor_instructions,
    constants=[current_oak_constant, protected_invariants_constant],
    schemas=[
        governance_schema,
        amendment_proposal_schema,
        amendment_cycle_schema,
        evidence_supplement_schema,
        accepted_amendment_schema,
        candidate_successor_schema,
        successor_publication_schema,
    ],
    state=[
        current_revision_state,
        review_status_state,
        pending_amendment_id_state,
        pending_amendment_state,
        pending_rationale_state,
    ],
    triggers=[amendment_proposed_trigger, evidence_supplied_trigger],
    processes=[
        dispatch_review_process,
        dispatch_verification_process,
        govern_succession_process,
    ],
    interfaces=[
        amendment_input_interface,
        evidence_input_interface,
        review_outcome_output_interface,
        successor_output_interface,
    ],
)

TARGET = Path(__file__).with_suffix(".oak.md")
SOURCE = "examples/agents/successor.oak.md"
AMENDMENT_REVIEWER_SOURCE = "examples/agents/amendment_reviewer.oak.md"
SUCCESSOR_VERIFIER_SOURCE = "examples/agents/successor_verifier.oak.md"

AMENDMENT_VALUES = {
    PLACEHOLDER_AMENDMENT_ID: "proof-carrying-successors",
    PLACEHOLDER_AMENDMENT: "Require every successor publication to include a canonical verification proof.",
    PLACEHOLDER_RATIONALE: "Knowledge must justify its replacement before it becomes current.",
    PLACEHOLDER_EVIDENCE: "",
}
EVIDENCE_VALUES = {
    PLACEHOLDER_AMENDMENT_ID: AMENDMENT_VALUES[PLACEHOLDER_AMENDMENT_ID],
    PLACEHOLDER_EVIDENCE: (
        "The candidate passes parsing, resolution, canonical round-trip, "
        "invariant preservation, and exact-scope checks."
    ),
}
INITIAL_STATE = {
    STATE_CURRENT_REVISION: 13,
    STATE_REVIEW_STATUS: STATUS_IDLE,
    STATE_PENDING_AMENDMENT_ID: "",
    STATE_PENDING_AMENDMENT: "",
    STATE_PENDING_RATIONALE: "",
}


def _review_amendment_act(_step, values):
    evidence = values[PLACEHOLDER_EVIDENCE].strip()
    amendment = values[PLACEHOLDER_AMENDMENT].lower()
    if not evidence:
        return {
            PLACEHOLDER_DECISION: DECISION_NEEDS_EVIDENCE,
            PLACEHOLDER_REVIEW_FINDINGS: "The amendment is coherent, but no verification evidence supports ratification.",
            PLACEHOLDER_EVIDENCE_REQUEST: "Provide parse, resolve, canonical round-trip, invariant, and exact-scope evidence.",
        }
    if "remove" in amendment and "seven" in amendment:
        return {
            PLACEHOLDER_DECISION: DECISION_REJECT,
            PLACEHOLDER_REVIEW_FINDINGS: "The amendment would break the protected seven-part structure.",
            PLACEHOLDER_EVIDENCE_REQUEST: "",
        }
    return {
        PLACEHOLDER_DECISION: DECISION_ACCEPT,
        PLACEHOLDER_REVIEW_FINDINGS: "The evidence supports one exact invariant-preserving amendment.",
        PLACEHOLDER_EVIDENCE_REQUEST: "",
    }


def _amendment_reviewer_agent(_step, values):
    completed = execute(
        amendment_reviewer_node,
        Arrival(
            source=WORKER_REVIEW_REQUEST_INPUT,
            interfaces={WORKER_REVIEW_REQUEST_INPUT: dict(values)},
        ),
        {},
        act=_review_amendment_act,
    )
    return dict(completed.emissions[0].values)


def _compile_successor_tool(_step, values):
    current = parse(values[PLACEHOLDER_CURRENT_OAK])
    candidate = Node(
        instructions=[
            *current.instructions,
            Instruction(id="successor-amendment", body=values[PLACEHOLDER_AMENDMENT]),
        ],
        constants=list(current.constants),
        schemas=list(current.schemas),
        state=list(current.state),
        triggers=list(current.triggers),
        processes=list(current.processes),
        interfaces=list(current.interfaces),
    )
    return {PLACEHOLDER_CANDIDATE_OAK: render(candidate)}


def _verify_successor_tool(_step, values):
    current_text = values[PLACEHOLDER_CURRENT_OAK]
    candidate_text = values[PLACEHOLDER_CANDIDATE_OAK]
    amendment = values[PLACEHOLDER_AMENDMENT]
    protected = values[PLACEHOLDER_PROTECTED_INVARIANTS]
    current = candidate = None
    parses = resolves = canonical = False
    try:
        current, candidate = parse(current_text), parse(candidate_text)
        parses = True
    except OakParseError:
        pass
    if candidate is not None:
        try:
            resolve(candidate)
            resolves = True
        except ResolutionError:
            pass
        canonical = render(candidate) == candidate_text
    invariants_preserved = scope_exact = False
    if current is not None and candidate is not None:
        current_bodies = [item.body for item in current.instructions]
        candidate_bodies = [item.body for item in candidate.instructions]
        closed_parts = tuple(candidate.model_dump()) == (
            "instructions",
            "constants",
            "schemas",
            "state",
            "triggers",
            "processes",
            "interfaces",
        )
        invariants_preserved = (
            bool(protected.strip())
            and parses
            and resolves
            and canonical
            and closed_parts
            and candidate_bodies[: len(current_bodies)] == current_bodies
        )
        scope_exact = (
            candidate_bodies == [*current_bodies, amendment]
            and current.model_dump(exclude={"instructions"})
            == candidate.model_dump(exclude={"instructions"})
        )
    valid = all((parses, resolves, canonical, invariants_preserved, scope_exact))
    proof = (
        f"parses={str(parses).lower()}; resolves={str(resolves).lower()}; "
        f"canonical={str(canonical).lower()}; "
        f"invariants-preserved={str(invariants_preserved).lower()}; "
        f"scope-exact={str(scope_exact).lower()}"
    )
    return {
        PLACEHOLDER_VALID: valid,
        PLACEHOLDER_PARSES: parses,
        PLACEHOLDER_RESOLVES: resolves,
        PLACEHOLDER_CANONICAL: canonical,
        PLACEHOLDER_INVARIANTS_PRESERVED: invariants_preserved,
        PLACEHOLDER_SCOPE_EXACT: scope_exact,
        PLACEHOLDER_PROOF: proof,
    }


def _successor_verifier_agent(_step, values):
    completed = execute(
        successor_verifier_node,
        Arrival(
            source=WORKER_VERIFICATION_REQUEST_INPUT,
            interfaces={WORKER_VERIFICATION_REQUEST_INPUT: dict(values)},
        ),
        {},
        tools={
            TOOL_OAK_VERIFY_SUCCESSOR: ToolContract(
                _verify_successor_tool,
                frozenset(VERIFICATION_REQUEST_PLACEHOLDERS),
                frozenset(PROOF_PLACEHOLDERS),
                input=SCHEMA_SUCCESSOR_VERIFICATION_REQUEST,
                output=SCHEMA_SUCCESSOR_PROOF,
            )
        },
    )
    return dict(completed.emissions[0].values)


def _advance_revision_act(step, values):
    if step.outputs != [PLACEHOLDER_PRIOR_REVISION, PLACEHOLDER_NEXT_REVISION]:
        raise RuntimeError("unexpected coordinator ACT")
    current = values[PLACEHOLDER_CURRENT_REVISION]
    return {
        PLACEHOLDER_PRIOR_REVISION: current,
        PLACEHOLDER_NEXT_REVISION: current + 1,
    }


def _load_document(path: str) -> Node | None:
    if path == AMENDMENT_REVIEWER_SOURCE:
        return amendment_reviewer_node
    if path == SUCCESSOR_VERIFIER_SOURCE:
        return successor_verifier_node
    return None


def _tool_registry() -> dict[str, ToolContract]:
    return {
        TOOL_AGENT_AMENDMENT_REVIEWER: ToolContract(
            _amendment_reviewer_agent,
            frozenset(REVIEW_REQUEST_PLACEHOLDERS),
            frozenset(REVIEW_PLACEHOLDERS),
            input=SCHEMA_REVIEWER_REQUEST,
            output=SCHEMA_REVIEWER_RESULT,
        ),
        TOOL_AGENT_SUCCESSOR_VERIFIER: ToolContract(
            _successor_verifier_agent,
            frozenset(VERIFICATION_REQUEST_PLACEHOLDERS),
            frozenset(PROOF_PLACEHOLDERS),
            input=SCHEMA_VERIFIER_REQUEST,
            output=SCHEMA_VERIFIER_RESULT,
        ),
        TOOL_OAK_COMPILE_SUCCESSOR: ToolContract(
            _compile_successor_tool,
            frozenset(ACCEPTED_AMENDMENT_PLACEHOLDERS),
            frozenset({PLACEHOLDER_CANDIDATE_OAK}),
            input=SCHEMA_ACCEPTED_AMENDMENT,
            output=SCHEMA_CANDIDATE_SUCCESSOR,
        ),
        TOOL_OAK_VERIFY_SUCCESSOR: ToolContract(
            _verify_successor_tool,
            frozenset(VERIFICATION_REQUEST_PLACEHOLDERS),
            frozenset(PROOF_PLACEHOLDERS),
            input=SCHEMA_SUCCESSOR_VERIFICATION_REQUEST,
            output=SCHEMA_SUCCESSOR_PROOF,
        ),
    }


def build() -> str:
    """Prove a two-arrival succession and return canonical coordinator OAK."""
    rendered = render(successor_node)
    parsed = parse(rendered)
    resolve(parsed, source=SOURCE, load=_load_document)
    if render(parsed) != rendered:
        raise RuntimeError("successor machine changed during render and parse")

    review = execute(
        parsed,
        Arrival(
            source=INTERFACE_AMENDMENT_INPUT,
            interfaces={INTERFACE_AMENDMENT_INPUT: dict(AMENDMENT_VALUES)},
        ),
        INITIAL_STATE,
        act=_advance_revision_act,
        tools=_tool_registry(),
        source=SOURCE,
        load=_load_document,
    )
    if not (
        review.state[STATE_REVIEW_STATUS] == STATUS_NEEDS_EVIDENCE
        and review.state[STATE_CURRENT_REVISION] == 13
        and len(review.emissions) == 1
        and review.emissions[0].interface == INTERFACE_REVIEW_OUTCOME_OUTPUT
    ):
        raise RuntimeError("the first arrival did not request evidence")

    succession = execute(
        parsed,
        Arrival(
            source=INTERFACE_EVIDENCE_INPUT,
            interfaces={INTERFACE_EVIDENCE_INPUT: dict(EVIDENCE_VALUES)},
        ),
        review.state,
        act=_advance_revision_act,
        tools=_tool_registry(),
        source=SOURCE,
        load=_load_document,
    )
    if not (
        succession.state[STATE_REVIEW_STATUS] == STATUS_RATIFIED
        and succession.state[STATE_CURRENT_REVISION] == 14
        and len(succession.emissions) == 1
        and succession.emissions[0].interface == INTERFACE_SUCCESSOR_OUTPUT
    ):
        raise RuntimeError("the second arrival did not publish one successor")

    published = dict(succession.emissions[0].values)
    if not (
        published[PLACEHOLDER_DECISION] == DECISION_ACCEPT
        and published[PLACEHOLDER_PRIOR_REVISION] == 13
        and published[PLACEHOLDER_NEXT_REVISION] == 14
        and all(
            published[name] is True
            for name in (
                PLACEHOLDER_VALID,
                PLACEHOLDER_PARSES,
                PLACEHOLDER_RESOLVES,
                PLACEHOLDER_CANONICAL,
                PLACEHOLDER_INVARIANTS_PRESERVED,
                PLACEHOLDER_SCOPE_EXACT,
            )
        )
        and published[PLACEHOLDER_PROOF]
    ):
        raise RuntimeError("the successor was published without its proof")

    candidate = published[PLACEHOLDER_CANDIDATE_OAK]
    resolved_candidate = parse(candidate)
    resolve(resolved_candidate)
    if render(resolved_candidate) != candidate:
        raise RuntimeError("the published successor is not canonical")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
