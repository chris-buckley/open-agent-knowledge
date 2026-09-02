"""Author the adapted task reviewer prompt as one directly authored OAK node."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    BindingValue,
    Call,
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

SCHEMA_REVIEW_REQUEST = "schema.review-request"
SCHEMA_REVIEW_EVIDENCE = "schema.review-evidence"
SCHEMA_COMPLIANCE_REQUEST = "schema.compliance-request"
SCHEMA_COMPLIANCE = "schema.compliance"
SCHEMA_ASSESSMENT = "schema.assessment"
SCHEMA_TASK_REVIEW = "schema.task-review"
PROCESS_READ_EVIDENCE = "process.read-evidence"
PROCESS_VALIDATE_COMPLIANCE = "process.validate-compliance"
PROCESS_ASSESS_EVIDENCE = "process.assess-evidence"
PROCESS_REVIEW_TASK = "process.review-task"
INTERFACE_REVIEW_REQUEST_INPUT = "interface.review-request-input"
INTERFACE_TASK_REVIEW_OUTPUT = "interface.task-review-output"

PLACEHOLDER_TASK_BRIEF = "TASK_BRIEF"
PLACEHOLDER_IMPLEMENTATION_REPORT = "IMPLEMENTATION_REPORT"
PLACEHOLDER_DIFF = "DIFF"
PLACEHOLDER_EVIDENCE = "EVIDENCE"
PLACEHOLDER_SPEC_COMPLIANCE = "SPEC_COMPLIANCE"
PLACEHOLDER_STRENGTHS = "STRENGTHS"
PLACEHOLDER_ISSUES = "ISSUES"
PLACEHOLDER_ASSESSMENT = "ASSESSMENT"

task_reviewer_instructions = [
    Instruction(id=slug, body=body)
    for slug, body in (
        ("limit-scope", "Review only the scope defined by the supplied task brief."),
        ("read-package", "Read the task brief, implementation report, and diff once before assessment."),
        ("remain-readonly", "Remain read-only and do not modify the implementation."),
        ("forbid-delegation", "Do not delegate review work to subagents."),
        ("treat-claims", "Treat the implementation report as a claim that requires diff evidence."),
        ("skip-suites", "Do not rerun broad test suites during the task-scoped review."),
        ("separate-checks", "Check specification compliance and implementation quality separately."),
        ("classify-issues", "Classify every issue by severity and explain its evidence."),
        ("report-assessment", "Report specification compliance, strengths, issues, and an overall assessment."),
    )
]

review_request_schema = Schema(
    id="review-request",
    name="Review Request",
    purpose="Carry one task-scoped review package.",
    template="Task brief: <TASK_BRIEF>\nImplementation report: <IMPLEMENTATION_REPORT>\nDiff: <DIFF>",
    where=[
        where(PLACEHOLDER_TASK_BRIEF, Type(of="string"), NonEmpty(), description="the accepted implementation scope"),
        where(PLACEHOLDER_IMPLEMENTATION_REPORT, Type(of="string"), NonEmpty(), description="the implementer's completion claim"),
        where(PLACEHOLDER_DIFF, Type(of="string"), NonEmpty(), description="the exact code changes under review"),
    ],
)

review_evidence_schema = Schema(
    id="review-evidence",
    name="Review Evidence",
    purpose="Carry the inspected evidence for one task-scoped review.",
    template="<EVIDENCE>",
    where=[where(PLACEHOLDER_EVIDENCE, Type(of="string"), NonEmpty(), description="the inspected review evidence")],
)

compliance_request_schema = Schema(
    id="compliance-request",
    name="Compliance Request",
    purpose="Carry the evidence and the brief for one compliance check.",
    template="Evidence: <EVIDENCE>\nTask brief: <TASK_BRIEF>",
    where=[
        where(PLACEHOLDER_EVIDENCE, Type(of="string"), NonEmpty(), description="the inspected review evidence"),
        where(PLACEHOLDER_TASK_BRIEF, Type(of="string"), NonEmpty(), description="the accepted implementation scope"),
    ],
)

compliance_schema = Schema(
    id="compliance",
    name="Compliance",
    purpose="Carry the requirement-by-requirement compliance result.",
    template="<SPEC_COMPLIANCE>",
    where=[where(PLACEHOLDER_SPEC_COMPLIANCE, Type(of="string"), NonEmpty(), description="the requirement-by-requirement result")],
)

assessment_schema = Schema(
    id="assessment",
    name="Assessment",
    purpose="Carry the evidence-based quality assessment.",
    template="Strengths: <STRENGTHS>\nIssues: <ISSUES>\nAssessment: <ASSESSMENT>",
    where=[
        where(PLACEHOLDER_STRENGTHS, Type(of="string"), NonEmpty(), description="the strongest implementation qualities"),
        where(PLACEHOLDER_ISSUES, Type(of="string"), NonEmpty(), description="the evidenced issues with severity"),
        where(PLACEHOLDER_ASSESSMENT, Type(of="string"), NonEmpty(), description="the overall task-scoped verdict"),
    ],
)

task_review_schema = Schema(
    id="task-review",
    name="Task Review",
    purpose="Carry one evidence-based task review.",
    template="Specification compliance: <SPEC_COMPLIANCE>\nStrengths: <STRENGTHS>\nIssues: <ISSUES>\nAssessment: <ASSESSMENT>",
    where=[
        where(PLACEHOLDER_SPEC_COMPLIANCE, Type(of="string"), NonEmpty(), description="the requirement-by-requirement result"),
        where(PLACEHOLDER_STRENGTHS, Type(of="string"), NonEmpty(), description="the strongest implementation qualities"),
        where(PLACEHOLDER_ISSUES, Type(of="string"), NonEmpty(), description="the evidenced issues with severity"),
        where(PLACEHOLDER_ASSESSMENT, Type(of="string"), NonEmpty(), description="the overall task-scoped verdict"),
    ],
)

review_requested_trigger = Trigger(
    id="review-requested",
    event="A task review is requested.",
    source=INTERFACE_REVIEW_REQUEST_INPUT,
    process=PROCESS_REVIEW_TASK,
    seed=[
        ValueBinding(placeholder=PLACEHOLDER_TASK_BRIEF, value=InterfaceValue(interface=INTERFACE_REVIEW_REQUEST_INPUT, placeholder=PLACEHOLDER_TASK_BRIEF)),
        ValueBinding(placeholder=PLACEHOLDER_IMPLEMENTATION_REPORT, value=InterfaceValue(interface=INTERFACE_REVIEW_REQUEST_INPUT, placeholder=PLACEHOLDER_IMPLEMENTATION_REPORT)),
        ValueBinding(placeholder=PLACEHOLDER_DIFF, value=InterfaceValue(interface=INTERFACE_REVIEW_REQUEST_INPUT, placeholder=PLACEHOLDER_DIFF)),
    ],
)

read_evidence_process = Process(
    id="read-evidence",
    name="Read evidence",
    input=SCHEMA_REVIEW_REQUEST,
    output=SCHEMA_REVIEW_EVIDENCE,
    steps=[
        ACT(
            "Inspect <TASK_BRIEF>, <IMPLEMENTATION_REPORT>, and <DIFF> once and produce <EVIDENCE>.",
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_TASK_BRIEF, value=BindingValue(binding=PLACEHOLDER_TASK_BRIEF)),
                ValueBinding(placeholder=PLACEHOLDER_IMPLEMENTATION_REPORT, value=BindingValue(binding=PLACEHOLDER_IMPLEMENTATION_REPORT)),
                ValueBinding(placeholder=PLACEHOLDER_DIFF, value=BindingValue(binding=PLACEHOLDER_DIFF)),
            ],
            outputs=[PLACEHOLDER_EVIDENCE],
        ),
    ],
)

validate_compliance_process = Process(
    id="validate-compliance",
    name="Validate compliance",
    input=SCHEMA_COMPLIANCE_REQUEST,
    output=SCHEMA_COMPLIANCE,
    steps=[
        ACT(
            "Compare <EVIDENCE> with <TASK_BRIEF> and produce <SPEC_COMPLIANCE>.",
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_EVIDENCE, value=BindingValue(binding=PLACEHOLDER_EVIDENCE)),
                ValueBinding(placeholder=PLACEHOLDER_TASK_BRIEF, value=BindingValue(binding=PLACEHOLDER_TASK_BRIEF)),
            ],
            outputs=[PLACEHOLDER_SPEC_COMPLIANCE],
        ),
    ],
)

assess_evidence_process = Process(
    id="assess-evidence",
    name="Assess evidence",
    input=SCHEMA_REVIEW_EVIDENCE,
    output=SCHEMA_ASSESSMENT,
    steps=[
        ACT(
            "Assess <EVIDENCE> and produce <STRENGTHS>, <ISSUES>, and <ASSESSMENT>.",
            inputs=[ValueBinding(placeholder=PLACEHOLDER_EVIDENCE, value=BindingValue(binding=PLACEHOLDER_EVIDENCE))],
            outputs=[PLACEHOLDER_STRENGTHS, PLACEHOLDER_ISSUES, PLACEHOLDER_ASSESSMENT],
        ),
    ],
)

review_task_process = Process(
    id="review-task",
    name="Review task",
    input=SCHEMA_REVIEW_REQUEST,
    steps=[
        Call(
            process=PROCESS_READ_EVIDENCE,
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_TASK_BRIEF, value=BindingValue(binding=PLACEHOLDER_TASK_BRIEF)),
                ValueBinding(placeholder=PLACEHOLDER_IMPLEMENTATION_REPORT, value=BindingValue(binding=PLACEHOLDER_IMPLEMENTATION_REPORT)),
                ValueBinding(placeholder=PLACEHOLDER_DIFF, value=BindingValue(binding=PLACEHOLDER_DIFF)),
            ],
            outputs=[PLACEHOLDER_EVIDENCE],
        ),
        Call(
            process=PROCESS_VALIDATE_COMPLIANCE,
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_EVIDENCE, value=BindingValue(binding=PLACEHOLDER_EVIDENCE)),
                ValueBinding(placeholder=PLACEHOLDER_TASK_BRIEF, value=BindingValue(binding=PLACEHOLDER_TASK_BRIEF)),
            ],
            outputs=[PLACEHOLDER_SPEC_COMPLIANCE],
        ),
        Call(
            process=PROCESS_ASSESS_EVIDENCE,
            inputs=[ValueBinding(placeholder=PLACEHOLDER_EVIDENCE, value=BindingValue(binding=PLACEHOLDER_EVIDENCE))],
            outputs=[PLACEHOLDER_STRENGTHS, PLACEHOLDER_ISSUES, PLACEHOLDER_ASSESSMENT],
        ),
        Emit(
            interface=INTERFACE_TASK_REVIEW_OUTPUT,
            bindings=[
                ValueBinding(placeholder=PLACEHOLDER_SPEC_COMPLIANCE, value=BindingValue(binding=PLACEHOLDER_SPEC_COMPLIANCE)),
                ValueBinding(placeholder=PLACEHOLDER_STRENGTHS, value=BindingValue(binding=PLACEHOLDER_STRENGTHS)),
                ValueBinding(placeholder=PLACEHOLDER_ISSUES, value=BindingValue(binding=PLACEHOLDER_ISSUES)),
                ValueBinding(placeholder=PLACEHOLDER_ASSESSMENT, value=BindingValue(binding=PLACEHOLDER_ASSESSMENT)),
            ],
        ),
    ],
)

review_request_input_interface = Interface(
    id="review-request-input",
    direction="in",
    schema=SCHEMA_REVIEW_REQUEST,
    description="The brief, report, and diff supplied to the reviewer.",
)

task_review_output_interface = Interface(
    id="task-review-output",
    direction="out",
    schema=SCHEMA_TASK_REVIEW,
    description="The task-scoped review returned to the caller.",
)

task_reviewer_node = Node(
    instructions=task_reviewer_instructions,
    schemas=[
        review_request_schema,
        review_evidence_schema,
        compliance_request_schema,
        compliance_schema,
        assessment_schema,
        task_review_schema,
    ],
    triggers=[review_requested_trigger],
    processes=[
        read_evidence_process,
        validate_compliance_process,
        assess_evidence_process,
        review_task_process,
    ],
    interfaces=[review_request_input_interface, task_review_output_interface],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the authored task reviewer node."""
    rendered = render(task_reviewer_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("task reviewer example changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
