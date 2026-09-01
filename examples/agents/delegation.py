"""Author one coordinator that dispatches the task reviewer as its worker agent."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Arrival,
    BindingValue,
    Call,
    Emit,
    Instruction,
    Interface,
    InterfaceValue,
    Node,
    Process,
    ToolContract,
    Trigger,
    ValueBinding,
    execute,
    parse,
    render,
    resolve,
)
from examples.agents.task_reviewer import task_reviewer_node

SCHEMA_WORKER_REQUEST = "task_reviewer.oak.md#schema.review-request"
SCHEMA_WORKER_RESULT = "task_reviewer.oak.md#schema.task-review"
PROCESS_DISPATCH_REVIEW = "process.dispatch-review"
PROCESS_DELEGATE_REVIEW = "process.delegate-review"
INTERFACE_REVIEW_REQUEST_INPUT = "interface.review-request-input"
INTERFACE_TASK_REVIEW_OUTPUT = "interface.task-review-output"

TOOL_AGENT_REVIEWER = "agent.reviewer"
WORKER_DOCUMENT = "examples/agents/task_reviewer.oak.md"
WORKER_ARRIVAL_WHEN = "A task review is requested."
WHEN_DELEGATION_REQUESTED = "Delegate the task review."

REQUEST_PLACEHOLDERS = ("TASK_BRIEF", "IMPLEMENTATION_REPORT", "DIFF")
RESULT_PLACEHOLDERS = ("SPEC_COMPLIANCE", "STRENGTHS", "ISSUES", "ASSESSMENT")

delegation_instructions = [
    Instruction(
        id="preserve-result",
        body="Return the worker task review unchanged.",
    )
]

delegation_requested_trigger = Trigger(
    id="delegation-requested",
    when=WHEN_DELEGATION_REQUESTED,
    then=PROCESS_DELEGATE_REVIEW,
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
            inputs=[
                ValueBinding(placeholder=placeholder, value=BindingValue(binding=placeholder))
                for placeholder in REQUEST_PLACEHOLDERS
            ],
            outputs=list(RESULT_PLACEHOLDERS),
        ),
    ],
)

delegate_review_process = Process(
    id="delegate-review",
    name="Delegate review",
    steps=[
        Call(
            process=PROCESS_DISPATCH_REVIEW,
            inputs=[
                ValueBinding(
                    placeholder=placeholder,
                    value=InterfaceValue(interface=INTERFACE_REVIEW_REQUEST_INPUT, placeholder=placeholder),
                )
                for placeholder in REQUEST_PLACEHOLDERS
            ],
            outputs=list(RESULT_PLACEHOLDERS),
        ),
        Emit(
            interface=INTERFACE_TASK_REVIEW_OUTPUT,
            bindings=[
                ValueBinding(placeholder=placeholder, value=BindingValue(binding=placeholder))
                for placeholder in RESULT_PLACEHOLDERS
            ],
        ),
    ],
)

review_request_input_interface = Interface(
    id="review-request-input",
    direction="in",
    schema=SCHEMA_WORKER_REQUEST,
    description="The review request the coordinator forwards to the worker.",
)

task_review_output_interface = Interface(
    id="task-review-output",
    direction="out",
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
    "TASK_BRIEF": "Add one bounded while to the growth example.",
    "IMPLEMENTATION_REPORT": "Added the while and regenerated the snapshot.",
    "DIFF": "examples/agents/compound_growth.py: +12 -2",
}


def _worker_act(step, _values):
    if step.outputs == ["EVIDENCE"]:
        return {"EVIDENCE": "The diff matches the report."}
    if step.outputs == ["SPEC_COMPLIANCE"]:
        return {"SPEC_COMPLIANCE": "Every requirement is met."}
    return {
        "STRENGTHS": "Small bounded change.",
        "ISSUES": "None found.",
        "ASSESSMENT": "Accept.",
    }


def _reviewer_agent(_step, values):
    completed = execute(
        task_reviewer_node,
        Arrival(
            when=WORKER_ARRIVAL_WHEN,
            interfaces={"interface.review-request-input": dict(values)},
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
    resolve(parsed, source="examples/agents/delegation.oak.md", load=_load_worker)
    if render(parsed) != rendered:
        raise RuntimeError("delegation example changed during render and parse")
    completed = execute(
        parsed,
        Arrival(
            when=WHEN_DELEGATION_REQUESTED,
            interfaces={INTERFACE_REVIEW_REQUEST_INPUT: dict(REQUEST_VALUES)},
        ),
        {},
        tools={
            TOOL_AGENT_REVIEWER: ToolContract(
                _reviewer_agent,
                frozenset(REQUEST_PLACEHOLDERS),
                frozenset(RESULT_PLACEHOLDERS),
            )
        },
        source="examples/agents/delegation.oak.md",
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
