"""Author the adapted implementer prompt as one directly authored OAK node."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __package__:
    from examples.bindings import local_bindings
else:
    from bindings import local_bindings

from oak import (
    ACT,
    Assert,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    If,
    Instruction,
    Interface,
    LiteralValue,
    Node,
    NonEmpty,
    OneOf,
    Process,
    Regex,
    Schema,
    Trigger,
    Type,
    ValueBinding,
    parse,
    render,
    resolve,
    where,
)

if __package__:
    from examples.schemas.verification import VERIFICATION_FIELDS, verification_node, verification_schema
else:
    # Detached demonstration: consume the bundled contract, not repository sources.
    verification_node = parse(Path(__file__).with_name("verification.oak.md").read_text(encoding="utf-8"))
    verification_schema = verification_node.schemas[0]
    VERIFICATION_FIELDS = tuple(clause.placeholder for clause in verification_schema.where)

SCHEMA_TASK_REQUEST = "schema.task-request"
SCHEMA_IMPLEMENTATION_PLAN = "schema.implementation-plan"
SCHEMA_CHANGESET = "schema.changeset"
SCHEMA_VERIFICATION = "verification.oak.md#schema.verification"
SCHEMA_CANDIDATE = "schema.candidate"
CONSTANT_REQUIRED_CHECK = "constant.required-check"
PROCESS_SNAPSHOT_CHANGESET = "process.snapshot-changeset"
SCHEMA_PLANNED_CHANGESET = "schema.planned-changeset"
SCHEMA_REVIEW_FINDINGS = "schema.review-findings"
SCHEMA_REVIEWED_CHANGESET = "schema.reviewed-changeset"
SCHEMA_COMPLETION = "schema.completion"
SCHEMA_VERIFIED_CHANGESET = "schema.verified-changeset"
SCHEMA_COMMIT = "schema.commit"
SCHEMA_IMPLEMENTATION_REPORT = "schema.implementation-report"
SCHEMA_ESCALATION = "schema.escalation"
CONSTANT_COMMIT_CONVENTION = "constant.commit-convention"
PROCESS_PLAN_TASK = "process.plan-task"
PROCESS_IMPLEMENT_PLAN = "process.implement-plan"
PROCESS_TEST_CHANGESET = "process.test-changeset"
PROCESS_REVIEW_CHANGESET = "process.review-changeset"
PROCESS_APPLY_FINDINGS = "process.apply-findings"
PROCESS_COMMIT_CHANGESET = "process.commit-changeset"
PROCESS_IMPLEMENT_TASK = "process.implement-task"
INTERFACE_TASK_REQUEST_INPUT = "interface.task-request-input"
INTERFACE_IMPLEMENTATION_REPORT_OUTPUT = "interface.implementation-report-output"
INTERFACE_ESCALATION_OUTPUT = "interface.escalation-output"

PLACEHOLDER_TASK_BRIEF = "TASK_BRIEF"
PLACEHOLDER_CONTEXT = "CONTEXT"
PLACEHOLDER_DRAFT_PLAN = "DRAFT_PLAN"
PLACEHOLDER_QUESTIONS = "QUESTIONS"
PLACEHOLDER_PLAN = "PLAN"
PLACEHOLDER_CHANGESET = "CHANGESET"
PLACEHOLDER_REVISED_CHANGESET = "REVISED_CHANGESET"
PLACEHOLDER_CANDIDATE = "CANDIDATE"
PLACEHOLDER_REVISION = "REVISION"
PLACEHOLDER_COMMITTED_REVISION = "COMMITTED_REVISION"
PLACEHOLDER_FINDINGS = "FINDINGS"
PLACEHOLDER_SUMMARY = "SUMMARY"
PLACEHOLDER_STATUS = "STATUS"
PLACEHOLDER_COMMIT = "COMMIT"
PLACEHOLDER_COMMIT_CONVENTION = "COMMIT_CONVENTION"

STATUS_COMPLETE = "complete"
STATUS_BLOCKED = "blocked"

PLAN_WHERE = where(
    PLACEHOLDER_PLAN,
    Type(of="string"),
    NonEmpty(),
    description="the ready implementation plan",
)
CHANGESET_WHERE = where(
    PLACEHOLDER_CHANGESET,
    Type(of="string"),
    NonEmpty(),
    description="the implemented code changes",
)
CANDIDATE_WHERE = where(
    PLACEHOLDER_CANDIDATE, Type(of="string"), NonEmpty(),
    description="the host-owned immutable snapshot to verify and commit",
)
REVISION_WHERE = where(
    PLACEHOLDER_REVISION, Type(of="string"), Regex(pattern="^[0-9a-f]{64}$"),
    description="the snapshot SHA-256 digest computed by the host",
)
REVISED_CHANGESET_WHERE = where(
    PLACEHOLDER_REVISED_CHANGESET, Type(of="string"), NonEmpty(),
    description="the work after applying review findings",
)
COMMITTED_REVISION_WHERE = where(
    PLACEHOLDER_COMMITTED_REVISION, Type(of="string"), Regex(pattern="^[0-9a-f]{64}$"),
    description="the snapshot digest actually committed by the host",
)
FINDINGS_WHERE = where(
    PLACEHOLDER_FINDINGS,
    Type(of="string"),
    NonEmpty(),
    description="the self-review findings",
)
SUMMARY_WHERE = where(
    PLACEHOLDER_SUMMARY,
    Type(of="string"),
    NonEmpty(),
    description="the implemented changes",
)
STATUS_WHERE = where(
    PLACEHOLDER_STATUS,
    Type(of="string"),
    OneOf(values=[STATUS_COMPLETE, STATUS_BLOCKED]),
    description="the completion status",
)
COMPLETE_STATUS_WHERE = where(
    PLACEHOLDER_STATUS,
    Type(of="string"),
    OneOf(values=[STATUS_COMPLETE]),
    description="the complete status",
)
BLOCKED_STATUS_WHERE = where(
    PLACEHOLDER_STATUS,
    Type(of="string"),
    OneOf(values=[STATUS_BLOCKED]),
    description="the blocked status",
)
BLOCKED_SUMMARY_WHERE = where(
    PLACEHOLDER_SUMMARY,
    Type(of="string"),
    NonEmpty(),
    description="the work state when blocked",
)
COMMIT_WHERE = where(
    PLACEHOLDER_COMMIT,
    Type(of="string"),
    Regex(pattern="^[0-9a-f]{7,40}$"),
    description="the resulting commit hash",
)

implementer_instructions = [
    Instruction(id=slug, body=body)
    for slug, body in (
        ("read-brief", "Read the task brief and supplied context before implementation."),
        ("ask-questions", "Ask focused questions before implementation when a requirement is unclear."),
        ("preserve-scope", "Implement only the requested scope and preserve exact requirements."),
        ("forbid-delegation", "Do not delegate implementation to subagents."),
        ("organize-code", "Keep code organized around clear responsibilities."),
        ("escalate-limits", "Escalate when the task exceeds the available evidence or capability."),
        ("verify-changes", "Run relevant tests and verification before completion."),
        ("review-changes", "Review the completed changes against the task before reporting."),
        ("report-evidence", "Report status, changes, verification, commit, and review findings."),
    )
]

task_request_schema = Schema(
    id="task-request",
    name="Task Request",
    purpose="Carry one implementation task and its working context.",
    template="Task brief: <TASK_BRIEF>\nContext: <CONTEXT>",
    where=[
        where(PLACEHOLDER_TASK_BRIEF, Type(of="string"), NonEmpty(), description="the exact requested implementation"),
        where(PLACEHOLDER_CONTEXT, Type(of="string"), NonEmpty(), description="the supplied repository and task context"),
    ],
)

implementation_plan_schema = Schema(
    id="implementation-plan",
    name="Implementation Plan",
    purpose="Carry one implementation plan with its questions resolved.",
    template="<PLAN>",
    where=[PLAN_WHERE],
)

changeset_schema = Schema(
    id="changeset",
    name="Changeset",
    purpose="Carry the implemented code changes.",
    template="<CHANGESET>",
    where=[CHANGESET_WHERE],
)

candidate_schema = Schema(
    id="candidate", name="Candidate", purpose="Carry one host-created immutable work snapshot.",
    template="Candidate: <CANDIDATE>\nRevision: <REVISION>",
    where=[CANDIDATE_WHERE, REVISION_WHERE],
)

planned_changeset_schema = Schema(
    id="planned-changeset",
    name="Planned Changeset",
    purpose="Carry the implemented changes with the plan they must satisfy.",
    template="Plan: <PLAN>\nChangeset: <CHANGESET>",
    where=[PLAN_WHERE, CHANGESET_WHERE],
)

review_findings_schema = Schema(
    id="review-findings",
    name="Review Findings",
    purpose="Carry the self-review findings for one changeset.",
    template="<FINDINGS>",
    where=[FINDINGS_WHERE],
)

reviewed_changeset_schema = Schema(
    id="reviewed-changeset",
    name="Reviewed Changeset",
    purpose="Carry the implemented changes with the findings to apply.",
    template="Changeset: <CHANGESET>\nFindings: <FINDINGS>",
    where=[CHANGESET_WHERE, FINDINGS_WHERE],
)

completion_schema = Schema(
    id="completion", name="Completion",
    purpose="Carry the revised work and status after findings are applied.",
    template="Status: <STATUS>\nSummary: <SUMMARY>\nRevised changeset: <REVISED_CHANGESET>",
    where=[STATUS_WHERE, SUMMARY_WHERE, REVISED_CHANGESET_WHERE],
)

verified_changeset_schema = Schema(
    id="verified-changeset", name="Verified Changeset",
    purpose="Carry one candidate with revision-linked verification and its commit convention.",
    template=("Candidate: <CANDIDATE>\nRevision: <REVISION>\n"
              + verification_schema.template + "\nCommit convention: <COMMIT_CONVENTION>"),
    where=[CANDIDATE_WHERE, REVISION_WHERE, *verification_schema.where,
           where(PLACEHOLDER_COMMIT_CONVENTION, Type(of="string"), NonEmpty(),
                 description="the required commit message convention")],
)

commit_schema = Schema(
    id="commit", name="Commit", purpose="Identify the commit and the exact snapshot it contains.",
    template="Commit: <COMMIT>\nCommitted revision: <COMMITTED_REVISION>",
    where=[COMMIT_WHERE, COMMITTED_REVISION_WHERE],
)

implementation_report_schema = Schema(
    id="implementation-report", name="Implementation Report",
    purpose="Carry the completed implementer report and exact verification subject.",
    template=("Status: <STATUS>\nSummary: <SUMMARY>\nCandidate: <CANDIDATE>\nRevision: <REVISION>\n"
              + verification_schema.template + "\nCommit: <COMMIT>\nFindings: <FINDINGS>"),
    where=[COMPLETE_STATUS_WHERE, SUMMARY_WHERE, CANDIDATE_WHERE, REVISION_WHERE,
           *verification_schema.where, COMMIT_WHERE, FINDINGS_WHERE],
)

escalation_schema = Schema(
    id="escalation",
    name="Escalation",
    purpose="Carry the blocked outcome and its findings to the caller.",
    template="Status: <STATUS>\nSummary: <SUMMARY>\nFindings: <FINDINGS>",
    where=[BLOCKED_STATUS_WHERE, BLOCKED_SUMMARY_WHERE, FINDINGS_WHERE],
)

commit_convention_constant = Constant(
    id="commit-convention",
    value="type(scope): imperative summary",
)

required_check_constant = Constant(
    id="required-check", schema=SCHEMA_VERIFICATION, placeholder="CHECK", value="implementation-checks-v1",
)

implementation_requested_trigger = Trigger(
    id="implementation-requested",
    event="An implementation task arrives.",
    source=INTERFACE_TASK_REQUEST_INPUT,
    process=PROCESS_IMPLEMENT_TASK,
)

task_brief_value = BindingValue(binding=PLACEHOLDER_TASK_BRIEF)

task_brief_binding = ValueBinding(placeholder=PLACEHOLDER_TASK_BRIEF, value=task_brief_value)

context_value = BindingValue(binding=PLACEHOLDER_CONTEXT)

context_binding = ValueBinding(placeholder=PLACEHOLDER_CONTEXT, value=context_value)

draft_plan_text = "Read <TASK_BRIEF> with <CONTEXT> and produce <DRAFT_PLAN> and <QUESTIONS>."

draft_plan_action = ACT(
    draft_plan_text,
    inputs=[task_brief_binding, context_binding],
    outputs=[PLACEHOLDER_DRAFT_PLAN, PLACEHOLDER_QUESTIONS],
)

questions_value = BindingValue(binding=PLACEHOLDER_QUESTIONS)

questions_binding = ValueBinding(placeholder=PLACEHOLDER_QUESTIONS, value=questions_value)

draft_plan_value = BindingValue(binding=PLACEHOLDER_DRAFT_PLAN)

draft_plan_binding = ValueBinding(placeholder=PLACEHOLDER_DRAFT_PLAN, value=draft_plan_value)

resolve_plan_text = "Resolve <QUESTIONS> into <DRAFT_PLAN> and produce <PLAN>."

resolve_plan_action = ACT(
    resolve_plan_text,
    inputs=[questions_binding, draft_plan_binding],
    outputs=[PLACEHOLDER_PLAN],
)

plan_task_process = Process(
    id="plan-task",
    name="Plan task",
    input=SCHEMA_TASK_REQUEST,
    output=SCHEMA_IMPLEMENTATION_PLAN,
    body=[draft_plan_action, resolve_plan_action],
)

plan_value = BindingValue(binding=PLACEHOLDER_PLAN)

plan_binding = ValueBinding(placeholder=PLACEHOLDER_PLAN, value=plan_value)

implement_plan_text = "Implement <PLAN> exactly and produce <CHANGESET>."

implement_plan_action = ACT(
    implement_plan_text,
    inputs=[plan_binding],
    outputs=[PLACEHOLDER_CHANGESET],
)

implement_plan_process = Process(
    id="implement-plan",
    name="Implement plan",
    input=SCHEMA_IMPLEMENTATION_PLAN,
    output=SCHEMA_CHANGESET,
    body=[implement_plan_action],
)

snapshot_text = (
    'Freeze <CHANGESET>, including all verification-relevant inputs, as immutable <CANDIDATE> and compute '
    'its SHA-256 <REVISION>.'
)

snapshot_action = ACT.tool(
    "changes.snapshot",
    snapshot_text,
    input=SCHEMA_CHANGESET,
    output=SCHEMA_CANDIDATE,
    inputs=local_bindings([PLACEHOLDER_CHANGESET]),
    outputs=[PLACEHOLDER_CANDIDATE, PLACEHOLDER_REVISION],
)

snapshot_changeset_process = Process(
    id="snapshot-changeset",
    name="Snapshot changeset",
    input=SCHEMA_CHANGESET,
    output=SCHEMA_CANDIDATE,
    body=[snapshot_action],
)

verify_changeset_text = (
    'Inspect immutable <CANDIDATE> requested at <REVISION>; run the versioned implementation checks and '
    'record actual <VERIFIED_SUBJECT>, <VERIFIED_REVISION>, <CHECK>, <PASSED>, and <EVIDENCE>.'
)

verify_changeset_action = ACT.tool(
    "checks.verify-changeset",
    verify_changeset_text,
    input=SCHEMA_CANDIDATE,
    output=SCHEMA_VERIFICATION,
    inputs=local_bindings([PLACEHOLDER_CANDIDATE, PLACEHOLDER_REVISION]),
    outputs=list(VERIFICATION_FIELDS),
)

test_changeset_process = Process(
    id="test-changeset",
    name="Test changeset",
    input=SCHEMA_CANDIDATE,
    output=SCHEMA_VERIFICATION,
    body=[verify_changeset_action],
)

changeset_value = BindingValue(binding=PLACEHOLDER_CHANGESET)

changeset_binding = ValueBinding(placeholder=PLACEHOLDER_CHANGESET, value=changeset_value)

review_changeset_text = "Review <CHANGESET> against <PLAN> and produce <FINDINGS>."

review_changeset_action = ACT(
    review_changeset_text,
    inputs=[changeset_binding, plan_binding],
    outputs=[PLACEHOLDER_FINDINGS],
)

review_changeset_process = Process(
    id="review-changeset",
    name="Review changeset",
    input=SCHEMA_PLANNED_CHANGESET,
    output=SCHEMA_REVIEW_FINDINGS,
    body=[review_changeset_action],
)

apply_findings_text = "Apply <FINDINGS> to <CHANGESET> and produce <REVISED_CHANGESET>, <SUMMARY>, and <STATUS>."

apply_findings_action = ACT(
    apply_findings_text,
    inputs=local_bindings([PLACEHOLDER_FINDINGS, PLACEHOLDER_CHANGESET]),
    outputs=[PLACEHOLDER_REVISED_CHANGESET, PLACEHOLDER_SUMMARY, PLACEHOLDER_STATUS],
)

apply_findings_process = Process(
    id="apply-findings",
    name="Apply findings",
    input=SCHEMA_REVIEWED_CHANGESET,
    output=SCHEMA_COMPLETION,
    body=[apply_findings_action],
)

verified_subject_value = BindingValue(binding="VERIFIED_SUBJECT")

candidate_value = BindingValue(binding=PLACEHOLDER_CANDIDATE)

verified_subject_condition = Compare(left=verified_subject_value, operator="equals", right=candidate_value)

assert_verified_subject = Assert(
    condition=verified_subject_condition,
    message="The evidence belongs to another candidate.",
)

verified_revision_value = BindingValue(binding="VERIFIED_REVISION")

revision_value = BindingValue(binding=PLACEHOLDER_REVISION)

verified_revision_condition = Compare(left=verified_revision_value, operator="equals", right=revision_value)

assert_verified_revision = Assert(
    condition=verified_revision_condition,
    message="The evidence belongs to another revision.",
)

check_value = BindingValue(binding="CHECK")

required_check_value = ConstantValue(constant=CONSTANT_REQUIRED_CHECK)

check_condition = Compare(left=check_value, operator="equals", right=required_check_value)

assert_check = Assert(condition=check_condition, message="The evidence does not cover the required checks.")

passed_value = BindingValue(binding="PASSED")

required_pass_value = LiteralValue(value=True)

passed_condition = Compare(left=passed_value, operator="equals", right=required_pass_value)

assert_passed = Assert(condition=passed_condition, message="The required checks failed.")

commit_verified_text = (
    'Reject drift before any side effect; commit exactly immutable <CANDIDATE> at <REVISION> with '
    '<COMMIT_CONVENTION> using <VERIFIED_SUBJECT>, <VERIFIED_REVISION>, <CHECK>, <PASSED>, and '
    '<EVIDENCE>, then return <COMMIT> and <COMMITTED_REVISION>.'
)

commit_verified_action = ACT.tool(
    "changes.commit-verified",
    commit_verified_text,
    input=SCHEMA_VERIFIED_CHANGESET,
    output=SCHEMA_COMMIT,
    inputs=local_bindings(
        [PLACEHOLDER_CANDIDATE, PLACEHOLDER_REVISION, *VERIFICATION_FIELDS, PLACEHOLDER_COMMIT_CONVENTION],
    ),
    outputs=[PLACEHOLDER_COMMIT, PLACEHOLDER_COMMITTED_REVISION],
)

committed_revision_value = BindingValue(binding=PLACEHOLDER_COMMITTED_REVISION)

committed_revision_condition = Compare(left=committed_revision_value, operator="equals", right=revision_value)

assert_committed_revision = Assert(
    condition=committed_revision_condition,
    message="The host committed a different revision; external effects cannot be rolled back by OAK.",
)

commit_changeset_process = Process(
    id="commit-changeset",
    name="Commit changeset",
    input=SCHEMA_VERIFIED_CHANGESET,
    output=SCHEMA_COMMIT,
    body=[
        assert_verified_subject,
        assert_verified_revision,
        assert_check,
        assert_passed,
        commit_verified_action,
        assert_committed_revision,
    ],
)

plan_task_call = Call(
    process=PROCESS_PLAN_TASK,
    inputs=local_bindings([PLACEHOLDER_TASK_BRIEF, PLACEHOLDER_CONTEXT]),
    outputs=[PLACEHOLDER_PLAN],
)

implement_plan_call = Call(
    process=PROCESS_IMPLEMENT_PLAN,
    inputs=local_bindings([PLACEHOLDER_PLAN]),
    outputs=[PLACEHOLDER_CHANGESET],
)

review_changeset_call = Call(
    process=PROCESS_REVIEW_CHANGESET,
    inputs=local_bindings([PLACEHOLDER_PLAN, PLACEHOLDER_CHANGESET]),
    outputs=[PLACEHOLDER_FINDINGS],
)

apply_findings_call = Call(
    process=PROCESS_APPLY_FINDINGS,
    inputs=local_bindings([PLACEHOLDER_CHANGESET, PLACEHOLDER_FINDINGS]),
    outputs=[PLACEHOLDER_REVISED_CHANGESET, PLACEHOLDER_SUMMARY, PLACEHOLDER_STATUS],
)

status_value = BindingValue(binding=PLACEHOLDER_STATUS)

blocked_status_value = LiteralValue(value=STATUS_BLOCKED)

implementation_blocked = Compare(left=status_value, operator="equals", right=blocked_status_value)

emit_escalation = Emit(
    interface=INTERFACE_ESCALATION_OUTPUT,
    bindings=local_bindings([PLACEHOLDER_STATUS, PLACEHOLDER_SUMMARY, PLACEHOLDER_FINDINGS]),
)

revised_changeset_value = BindingValue(binding=PLACEHOLDER_REVISED_CHANGESET)

revised_changeset_binding = ValueBinding(placeholder=PLACEHOLDER_CHANGESET, value=revised_changeset_value)

snapshot_changeset_call = Call(
    process=PROCESS_SNAPSHOT_CHANGESET,
    inputs=[revised_changeset_binding],
    outputs=[PLACEHOLDER_CANDIDATE, PLACEHOLDER_REVISION],
)

test_changeset_call = Call(
    process=PROCESS_TEST_CHANGESET,
    inputs=local_bindings([PLACEHOLDER_CANDIDATE, PLACEHOLDER_REVISION]),
    outputs=list(VERIFICATION_FIELDS),
)

commit_convention_value = ConstantValue(constant=CONSTANT_COMMIT_CONVENTION)

commit_convention_binding = ValueBinding(
    placeholder=PLACEHOLDER_COMMIT_CONVENTION,
    value=commit_convention_value,
)

commit_changeset_call = Call(
    process=PROCESS_COMMIT_CHANGESET,
    inputs=[
        *local_bindings([PLACEHOLDER_CANDIDATE, PLACEHOLDER_REVISION, *VERIFICATION_FIELDS]),
        commit_convention_binding,
    ],
    outputs=[PLACEHOLDER_COMMIT, PLACEHOLDER_COMMITTED_REVISION],
)

emit_implementation_report = Emit(
    interface=INTERFACE_IMPLEMENTATION_REPORT_OUTPUT,
    bindings=local_bindings(
        [
            PLACEHOLDER_STATUS,
            PLACEHOLDER_SUMMARY,
            PLACEHOLDER_CANDIDATE,
            PLACEHOLDER_REVISION,
            *VERIFICATION_FIELDS,
            PLACEHOLDER_COMMIT,
            PLACEHOLDER_FINDINGS,
        ],
    ),
)

route_implementation = If(
    condition=implementation_blocked,
    then=[emit_escalation],
    otherwise=[snapshot_changeset_call, test_changeset_call, commit_changeset_call, emit_implementation_report],
)

implement_task_process = Process(
    id="implement-task",
    name="Implement task",
    input=SCHEMA_TASK_REQUEST,
    body=[plan_task_call, implement_plan_call, review_changeset_call, apply_findings_call, route_implementation],
)

task_request_input_interface = Interface(
    id="task-request-input",
    flow="receives",
    schema=SCHEMA_TASK_REQUEST,
    description="The task and context supplied to the implementer.",
)

implementation_report_output_interface = Interface(
    id="implementation-report-output",
    flow="emits",
    schema=SCHEMA_IMPLEMENTATION_REPORT,
    description="The implementer's final status and evidence.",
)

escalation_output_interface = Interface(
    id="escalation-output",
    flow="emits",
    schema=SCHEMA_ESCALATION,
    description="The blocked outcome returned instead of a commit.",
)

implementer_node = Node(
    instructions=implementer_instructions,
    constants=[commit_convention_constant, required_check_constant],
    schemas=[
        task_request_schema,
        implementation_plan_schema,
        changeset_schema,
        candidate_schema,
        planned_changeset_schema,
        review_findings_schema,
        reviewed_changeset_schema,
        completion_schema,
        verified_changeset_schema,
        commit_schema,
        implementation_report_schema,
        escalation_schema,
    ],
    triggers=[implementation_requested_trigger],
    processes=[
        plan_task_process,
        implement_plan_process,
        snapshot_changeset_process,
        test_changeset_process,
        review_changeset_process,
        apply_findings_process,
        commit_changeset_process,
        implement_task_process,
    ],
    interfaces=[task_request_input_interface, implementation_report_output_interface, escalation_output_interface],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def load_document(path: str) -> Node | None:
    """Supply only the explicitly shared verification document."""
    return verification_node if path == "examples/implementer/verification.oak.md" else None


def build() -> str:
    """Render, parse, resolve, and round-trip the authored implementer node."""
    rendered = render(implementer_node)
    parsed = parse(rendered)
    resolve(parsed, source="examples/implementer/example.oak.md", load=load_document)
    if render(parsed) != rendered:
        raise RuntimeError("implementer example changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
