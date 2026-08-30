"""Build, render, parse, resolve, and execute one directly authored OAK node."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Arrival,
    BindingValue,
    Compare,
    LiteralValue,
    Node,
    Process,
    Set,
    State,
    StateValue,
    ToolContract,
    Trigger,
    ValueBinding,
    While,
    execute,
    parse,
    render,
    resolve,
)

STATE_JOB_ID = "state.job-id"
STATE_CURRENT_JOB_STATUS = "state.current-job-status"
PROCESS_WAIT_JOB = "process.wait-job"

PLACEHOLDER_JOB_ID = "JOB_ID"
PLACEHOLDER_STATUS = "STATUS"

job_id_state = State(id="job-id", value="job-123")
current_job_status_state = State(id="current-job-status", value="pending")

job_waiting_trigger = Trigger(
    id="job-waiting",
    when="Wait for the job.",
    then=PROCESS_WAIT_JOB,
)

read_job_status_act = ACT.tool(
    "jobs.status",
    "Read <JOB_ID> and produce <STATUS>.",
    inputs=[
        ValueBinding(
            placeholder=PLACEHOLDER_JOB_ID,
            value=StateValue(state=STATE_JOB_ID),
        )
    ],
    outputs=[PLACEHOLDER_STATUS],
)

wait_job_process = Process(
    id="wait-job",
    name="Wait job",
    steps=[
        While(
            condition=Compare(
                left=StateValue(state=STATE_CURRENT_JOB_STATUS),
                operator="not_equals",
                right=LiteralValue(value="complete"),
            ),
            limit=3,
            steps=[
                read_job_status_act,
                Set(
                    state=STATE_CURRENT_JOB_STATUS,
                    value=BindingValue(binding=PLACEHOLDER_STATUS),
                ),
            ],
        ),
        ACT("Confirm that the job is complete."),
    ],
)

job_node = Node(
    state=[job_id_state, current_job_status_state],
    triggers=[job_waiting_trigger],
    processes=[wait_job_process],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def _status_tool():
    calls = 0

    def handler(_step, _values):
        nonlocal calls
        calls += 1
        return {"STATUS": "complete" if calls >= 2 else "pending"}

    return handler


def build() -> str:
    """Validate every working path and return canonical OAK text."""
    rendered = render(job_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("authoring example changed during render and parse")
    result = execute(
        parsed,
        Arrival(when="Wait for the job."),
        {STATE_JOB_ID: "job-123", STATE_CURRENT_JOB_STATUS: "pending"},
        act=lambda _step, _values: {},
        tools={
            "jobs.status": ToolContract(
                _status_tool(),
                frozenset({PLACEHOLDER_JOB_ID}),
                frozenset({PLACEHOLDER_STATUS}),
            )
        },
    )
    if result.state[STATE_CURRENT_JOB_STATUS] != "complete":
        raise RuntimeError("authoring example execution did not complete the job")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
