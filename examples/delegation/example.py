"""Author one coordinator that dispatches the task reviewer as its worker agent."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Arrival,
    Call,
    Emit,
    Instruction,
    Interface,
    Node,
    Process,
    ToolContract,
    Trigger,
    execute,
    parse,
    render,
    resolve,
)
if __package__:
    from examples.bindings import local_bindings
else:
    from bindings import local_bindings
if __package__:
    from .task_reviewer import (
        INTERFACE_REVIEW_REQUEST_INPUT as WORKER_REVIEW_REQUEST_INPUT,
        PLACEHOLDER_ASSESSMENT,
        PLACEHOLDER_DIFF,
        PLACEHOLDER_EVIDENCE,
        PLACEHOLDER_IMPLEMENTATION_REPORT,
        PLACEHOLDER_ISSUES,
        PLACEHOLDER_SPEC_COMPLIANCE,
        PLACEHOLDER_STRENGTHS,
        PLACEHOLDER_TASK_BRIEF,
        task_reviewer_node,
    )
else:
    from task_reviewer import (
        INTERFACE_REVIEW_REQUEST_INPUT as WORKER_REVIEW_REQUEST_INPUT,
        PLACEHOLDER_ASSESSMENT,
        PLACEHOLDER_DIFF,
        PLACEHOLDER_EVIDENCE,
        PLACEHOLDER_IMPLEMENTATION_REPORT,
        PLACEHOLDER_ISSUES,
        PLACEHOLDER_SPEC_COMPLIANCE,
        PLACEHOLDER_STRENGTHS,
        PLACEHOLDER_TASK_BRIEF,
        task_reviewer_node,
    )

SCHEMA_WORKER_REQUEST = "task_reviewer.oak.md#schema.review-request"
SCHEMA_WORKER_RESULT = "task_reviewer.oak.md#schema.task-review"
PROCESS_DISPATCH_REVIEW = "process.dispatch-review"
PROCESS_DELEGATE_REVIEW = "process.delegate-review"
INTERFACE_REVIEW_REQUEST_INPUT = "interface.review-request"
INTERFACE_TASK_REVIEW_OUTPUT = "interface.task-review"

TOOL_AGENT_REVIEWER = "agent.reviewer"
WORKER_DOCUMENT = "examples/delegation/task_reviewer.oak.md"
EVENT_DELEGATION_REQUESTED = "Delegate the task review."

SOURCE = "examples/delegation/example.oak.md"

REQUEST_PLACEHOLDERS = (PLACEHOLDER_TASK_BRIEF, PLACEHOLDER_IMPLEMENTATION_REPORT, PLACEHOLDER_DIFF)
RESULT_PLACEHOLDERS = (
    PLACEHOLDER_SPEC_COMPLIANCE,
    PLACEHOLDER_STRENGTHS,
    PLACEHOLDER_ISSUES,
    PLACEHOLDER_ASSESSMENT,
)

preserve_result_instruction = Instruction(
    id="preserve-result",
    body="Return the worker task review unchanged.",
)
delegation_instructions = [preserve_result_instruction]

delegation_requested_trigger = Trigger(
    id="delegation-requested",
    event=EVENT_DELEGATION_REQUESTED,
    source=INTERFACE_REVIEW_REQUEST_INPUT,
    process=PROCESS_DELEGATE_REVIEW,
)

dispatch_review_process = Process(
    id="dispatch-review",
    name="Dispatch review",
    input=SCHEMA_WORKER_REQUEST,
    output=SCHEMA_WORKER_RESULT,
    steps=[
        ACT.tool(
            TOOL_AGENT_REVIEWER,
            "Review <TASK_BRIEF>, <IMPLEMENTATION_REPORT>, and <DIFF> in one worker agent and produce <SPEC_COMPLIANCE>, <STRENGTHS>, <ISSUES>, and <ASSESSMENT>.",
            input=SCHEMA_WORKER_REQUEST,
            output=SCHEMA_WORKER_RESULT,
            inputs=local_bindings(REQUEST_PLACEHOLDERS),
            outputs=list(RESULT_PLACEHOLDERS),
        ),
    ],
)

delegate_review_process = Process(
    id="delegate-review",
    name="Delegate review",
    input=SCHEMA_WORKER_REQUEST,
    steps=[
        Call(
            process=PROCESS_DISPATCH_REVIEW,
            inputs=local_bindings(REQUEST_PLACEHOLDERS),
            outputs=list(RESULT_PLACEHOLDERS),
        ),
        Emit(interface=INTERFACE_TASK_REVIEW_OUTPUT),
    ],
)

review_request_input_interface = Interface(
    id="review-request",
    flow="receives",
    schema=SCHEMA_WORKER_REQUEST,
    description="The review request the coordinator forwards to the worker.",
)

task_review_output_interface = Interface(
    id="task-review",
    flow="emits",
    schema=SCHEMA_WORKER_RESULT,
    description="The worker task review returned to the caller.",
)

delegation_node = Node(
    instructions=delegation_instructions,
    triggers=[delegation_requested_trigger],
    processes=[dispatch_review_process, delegate_review_process],
    interfaces=[review_request_input_interface, task_review_output_interface],
)

TARGET = Path(__file__).with_suffix(".oak.md")

REQUEST_VALUES = {
    PLACEHOLDER_TASK_BRIEF: "Add one bounded while to the growth example.",
    PLACEHOLDER_IMPLEMENTATION_REPORT: "Added the while and regenerated the snapshot.",
    PLACEHOLDER_DIFF: "examples/agents/compound_growth.py: +12 -2",
}


def _worker_act(step, _values):
    if step.outputs == [PLACEHOLDER_EVIDENCE]:
        return {PLACEHOLDER_EVIDENCE: "The diff matches the report."}
    if step.outputs == [PLACEHOLDER_SPEC_COMPLIANCE]:
        return {PLACEHOLDER_SPEC_COMPLIANCE: "Every requirement is met."}
    return {
        PLACEHOLDER_STRENGTHS: "Small bounded change.",
        PLACEHOLDER_ISSUES: "None found.",
        PLACEHOLDER_ASSESSMENT: "Accept.",
    }


def _reviewer_agent(_step, values):
    completed = execute(
        task_reviewer_node,
        Arrival(
            interface=WORKER_REVIEW_REQUEST_INPUT,
            values=dict(values),
        ),
        {},
        act=_worker_act,
    )
    return dict(completed.emissions[0].values)


def _load_worker(path: str) -> Node | None:
    return task_reviewer_node if path == WORKER_DOCUMENT else None


def build() -> str:
    """Render, parse, resolve across the worker, execute the dispatch, and round-trip."""
    rendered = render(delegation_node)
    parsed = parse(rendered)
    resolve(parsed, source=SOURCE, load=_load_worker)
    if render(parsed) != rendered:
        raise RuntimeError("delegation example changed during render and parse")
    completed = execute(
        parsed,
        Arrival(
            interface=INTERFACE_REVIEW_REQUEST_INPUT,
            values=dict(REQUEST_VALUES),
        ),
        {},
        tools={
            TOOL_AGENT_REVIEWER: ToolContract(
                _reviewer_agent,
                frozenset(REQUEST_PLACEHOLDERS),
                frozenset(RESULT_PLACEHOLDERS),
                input=SCHEMA_WORKER_REQUEST,
                output=SCHEMA_WORKER_RESULT,
            )
        },
        source=SOURCE,
        load=_load_worker,
    )
    expected_review = _reviewer_agent(None, REQUEST_VALUES)
    if len(completed.emissions) != 1 or dict(completed.emissions[0].values) != expected_review:
        raise RuntimeError("delegation did not return the worker task review unchanged")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
