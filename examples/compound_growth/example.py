"""Two host-driven growth cycles with persistent state and bounded local work.

The arithmetic adapter computes real fixture values; reflection is deterministic,
not model inference. The demonstration runs exactly two arrivals, not an endless
host scheduler. It also checks failure after staged writes without promising
rollback of external effects. Regenerate with the repository module command;
run a detached copy with `python example.py` and an installed OAK runtime.
"""

from __future__ import annotations

from pathlib import Path
import sys
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Arrival,
    AtLeast,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    ExecutionError,
    Instruction,
    Interface,
    Node,
    NonEmpty,
    Process,
    Schema,
    Set,
    State,
    StateValue,
    ToolContract,
    Trigger,
    Type,
    ValueBinding,
    While,
    execute,
    parse,
    render,
    resolve,
    where,
)

CONSTANT_GROWTH_RATE = "constant.growth-rate"
CONSTANT_REFLECTION_STEP = "constant.reflection-step"
SCHEMA_SCALING = "schema.scaling"
SCHEMA_SCALED_BALANCE = "schema.scaled-balance"
SCHEMA_GROWTH_TARGET = "schema.growth-target"
SCHEMA_REFLECTION = "schema.reflection"
STATE_CURRENT_BALANCE = "state.current-balance"
STATE_REFLECTION_TARGET = "state.reflection-target"
PROCESS_SCALE_BALANCE = "process.scale-balance"
PROCESS_GROW_BALANCE = "process.grow-balance"
INTERFACE_REFLECTION_OUTPUT = "interface.reflection-output"

TOOL_MATH_MULTIPLY = "math.multiply"
EVENT_GROWTH_REQUESTED = "Continue growing the balance."

PLACEHOLDER_BALANCE = "BALANCE"
PLACEHOLDER_FACTOR = "FACTOR"
PLACEHOLDER_SCALED_BALANCE = "SCALED_BALANCE"
PLACEHOLDER_TARGET = "TARGET"
PLACEHOLDER_REFLECTION = "REFLECTION"

run_continuously_instruction = Instruction(
    id="run-continuously",
    body="Run this machine continuously: after each cycle commits, apply the same arrival again.",
)
growth_instructions = [run_continuously_instruction]

growth_rate_constant = Constant(
    id="growth-rate",
    schema=SCHEMA_SCALING,
    placeholder=PLACEHOLDER_FACTOR,
    value=1.05,
)
reflection_step_constant = Constant(
    id="reflection-step",
    schema=SCHEMA_SCALING,
    placeholder=PLACEHOLDER_FACTOR,
    value=8,
)

scaling_schema = Schema(
    id="scaling",
    name="Scaling",
    purpose="Carry one balance and the factor to scale it by.",
    template="Balance: <BALANCE>\nFactor: <FACTOR>",
    where=[
        where(PLACEHOLDER_BALANCE, Type(of="number"), AtLeast(value=0), description="the non-negative balance to scale"),
        where(PLACEHOLDER_FACTOR, Type(of="number"), AtLeast(value=1), description="the multiplication factor"),
    ],
)

scaled_balance_schema = Schema(
    id="scaled-balance",
    name="Scaled Balance",
    purpose="Carry the balance after one multiplication.",
    template="<SCALED_BALANCE>",
    where=[where(PLACEHOLDER_SCALED_BALANCE, Type(of="number"), description="the balance after one multiplication")],
)

growth_target_schema = Schema(
    id="growth-target",
    name="Growth Target",
    purpose="Carry the balance one growth cycle must reach.",
    template="Target: <TARGET>",
    where=[where(PLACEHOLDER_TARGET, Type(of="number"), AtLeast(value=0), description="the balance the cycle must reach")],
)

reflection_schema = Schema(
    id="reflection",
    name="Reflection",
    purpose="Carry one growth reflection for the chat.",
    template="Balance: <BALANCE>\nReflection: <REFLECTION>",
    where=[
        where(PLACEHOLDER_BALANCE, Type(of="number"), description="the balance at the end of the cycle"),
        where(PLACEHOLDER_REFLECTION, Type(of="string"), NonEmpty(), description="the reflection on this growth cycle"),
    ],
)

current_balance_state = State(
    id="current-balance",
    schema=SCHEMA_SCALING,
    placeholder=PLACEHOLDER_BALANCE,
    value=100,
)
reflection_target_state = State(
    id="reflection-target",
    schema=SCHEMA_SCALING,
    placeholder=PLACEHOLDER_BALANCE,
    value=800,
)

growth_requested_trigger = Trigger(
    id="growth-requested",
    event=EVENT_GROWTH_REQUESTED,
    process=PROCESS_GROW_BALANCE,
    seed=[
        ValueBinding(placeholder=PLACEHOLDER_TARGET, value=StateValue(state=STATE_REFLECTION_TARGET)),
    ],
)

scale_balance_process = Process(
    id="scale-balance",
    name="Scale balance",
    input=SCHEMA_SCALING,
    output=SCHEMA_SCALED_BALANCE,
    steps=[
        ACT.tool(
            TOOL_MATH_MULTIPLY,
            "Multiply <BALANCE> by <FACTOR> and round to 2 decimals to produce <SCALED_BALANCE>.",
            input=SCHEMA_SCALING,
            output=SCHEMA_SCALED_BALANCE,
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_BALANCE, value=BindingValue(binding=PLACEHOLDER_BALANCE)),
                ValueBinding(placeholder=PLACEHOLDER_FACTOR, value=BindingValue(binding=PLACEHOLDER_FACTOR)),
            ],
            outputs=[PLACEHOLDER_SCALED_BALANCE],
        ),
    ],
)

grow_balance_process = Process(
    id="grow-balance",
    name="Grow balance",
    input=SCHEMA_GROWTH_TARGET,
    steps=[
        While(
            condition=Compare(
                left=StateValue(state=STATE_CURRENT_BALANCE),
                operator="less_than",
                right=BindingValue(binding=PLACEHOLDER_TARGET),
            ),
            limit=60,
            steps=[
                Call(
                    process=PROCESS_SCALE_BALANCE,
                    inputs=[
                        ValueBinding(placeholder=PLACEHOLDER_BALANCE, value=StateValue(state=STATE_CURRENT_BALANCE)),
                        ValueBinding(placeholder=PLACEHOLDER_FACTOR, value=ConstantValue(constant=CONSTANT_GROWTH_RATE)),
                    ],
                    outputs=[PLACEHOLDER_SCALED_BALANCE],
                ),
                Set(state=STATE_CURRENT_BALANCE, value=BindingValue(binding=PLACEHOLDER_SCALED_BALANCE)),
            ],
        ),
        ACT(
            "Reflect on <BALANCE> reaching <TARGET> and produce <REFLECTION>.",
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_BALANCE, value=StateValue(state=STATE_CURRENT_BALANCE)),
                ValueBinding(placeholder=PLACEHOLDER_TARGET, value=BindingValue(binding=PLACEHOLDER_TARGET)),
            ],
            outputs=[PLACEHOLDER_REFLECTION],
        ),
        Call(
            process=PROCESS_SCALE_BALANCE,
            inputs=[
                ValueBinding(placeholder=PLACEHOLDER_BALANCE, value=StateValue(state=STATE_REFLECTION_TARGET)),
                ValueBinding(placeholder=PLACEHOLDER_FACTOR, value=ConstantValue(constant=CONSTANT_REFLECTION_STEP)),
            ],
            outputs=[PLACEHOLDER_SCALED_BALANCE],
        ),
        Set(state=STATE_REFLECTION_TARGET, value=BindingValue(binding=PLACEHOLDER_SCALED_BALANCE)),
        Emit(
            interface=INTERFACE_REFLECTION_OUTPUT,
            bindings=[
                ValueBinding(placeholder=PLACEHOLDER_BALANCE, value=StateValue(state=STATE_CURRENT_BALANCE)),
                ValueBinding(placeholder=PLACEHOLDER_REFLECTION, value=BindingValue(binding=PLACEHOLDER_REFLECTION)),
            ],
        ),
    ],
)

reflection_output_interface = Interface(
    id="reflection-output",
    flow="emits",
    schema=SCHEMA_REFLECTION,
    description="The reflection written to the chat before the next cycle starts.",
)

growth_node = Node(
    instructions=growth_instructions,
    constants=[growth_rate_constant, reflection_step_constant],
    schemas=[scaling_schema, scaled_balance_schema, growth_target_schema, reflection_schema],
    state=[current_balance_state, reflection_target_state],
    triggers=[growth_requested_trigger],
    processes=[scale_balance_process, grow_balance_process],
    interfaces=[reflection_output_interface],
)

TARGET = Path(__file__).with_suffix(".oak.md")


EXPECTED_STATES = [
    {"state.current-balance": 815.04, "state.reflection-target": 6400},
    {"state.current-balance": 6642.28, "state.reflection-target": 51200},
]
EXPECTED_EMISSIONS = [
    {"BALANCE": 815.04, "REFLECTION": "Balance 815.04 passed target 800."},
    {"BALANCE": 6642.28, "REFLECTION": "Balance 6642.28 passed target 6400."},
]


def sample() -> Node:
    """Supply inert, complete fixture input and expected outputs from this source."""
    return Node(constants=[
        Constant(id="arrival", value={"event": EVENT_GROWTH_REQUESTED, "count": 2}),
        Constant(id="initial-state", value={STATE_CURRENT_BALANCE: 100, STATE_REFLECTION_TARGET: 800}),
        Constant(id="expected-states", value=EXPECTED_STATES),
        Constant(id="expected-emissions", value=EXPECTED_EMISSIONS),
        Constant(id="failure", value="A reflection failure after staged growth leaves caller state unchanged and returns no committed result. Host calls are not rolled back."),
        Constant(id="host", value="Exact math.multiply arithmetic and deterministic reflection; two fixture arrivals, not an automatic infinite scheduler."),
    ])


def _multiply_tool(_step, values):
    return {PLACEHOLDER_SCALED_BALANCE: round(values[PLACEHOLDER_BALANCE] * values[PLACEHOLDER_FACTOR], 2)}


def _reflect_act(_step, values):
    return {PLACEHOLDER_REFLECTION: f"Balance {values[PLACEHOLDER_BALANCE]} passed target {values[PLACEHOLDER_TARGET]}."}


def build() -> str:
    """Validate every working path across two host cycles and return canonical OAK text."""
    rendered = render(growth_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("compound growth example changed during render and parse")
    tools = {
        TOOL_MATH_MULTIPLY: ToolContract(
            _multiply_tool,
            frozenset({PLACEHOLDER_BALANCE, PLACEHOLDER_FACTOR}),
            frozenset({PLACEHOLDER_SCALED_BALANCE}),
            input=SCHEMA_SCALING,
            output=SCHEMA_SCALED_BALANCE,
        )
    }
    initial = {STATE_CURRENT_BALANCE: 100, STATE_REFLECTION_TARGET: 800}
    state = dict(initial)
    observed_states = []
    emissions = []
    for _cycle in range(2):
        before_cycle = dict(state)
        cycle_execution = execute(
            parsed,
            Arrival(event=EVENT_GROWTH_REQUESTED),
            state,
            act=_reflect_act,
            tools=tools,
        )
        if state != before_cycle:
            raise RuntimeError("successful execution mutated caller state")
        state = dict(cycle_execution.state)
        observed_states.append(state)
        emissions.extend(cycle_execution.emissions)
    if len(emissions) != 2:
        raise RuntimeError("compound growth did not emit one reflection per cycle")
    if not (
        emissions[0].values[PLACEHOLDER_BALANCE] >= 800
        and emissions[1].values[PLACEHOLDER_BALANCE] >= emissions[0].values[PLACEHOLDER_BALANCE] * 8
    ):
        raise RuntimeError("compound growth cycles did not build the balance")
    if observed_states != EXPECTED_STATES or [dict(item.values) for item in emissions] != EXPECTED_EMISSIONS:
        raise RuntimeError("growth fixture changed its exact states or emissions")
    # The host has already been called and state has been staged when reflection fails.
    # OAK must discard its staged values; those host calls are not undone.
    caller = dict(initial)
    caller_before = deepcopy(caller)
    host_calls = []
    def fail_reflection(_step, values):
        host_calls.append(dict(values))
        raise ValueError("fixture reflection failure after growth")
    try:
        execute(parsed, Arrival(event=EVENT_GROWTH_REQUESTED), caller, act=fail_reflection, tools=tools)
    except ExecutionError as error:
        if error.code != "act_failed":
            raise
    else:
        raise RuntimeError("the failing host was accepted")
    if caller != caller_before or not host_calls or host_calls[0][PLACEHOLDER_BALANCE] != 815.04:
        raise RuntimeError("failure did not preserve the transaction boundary")
    retry = execute(parsed, Arrival(event=EVENT_GROWTH_REQUESTED), caller, act=_reflect_act, tools=tools)
    if dict(retry.state) != EXPECTED_STATES[0] or len(retry.emissions) != 1:
        raise RuntimeError("failed execution leaked staged state or emissions")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
