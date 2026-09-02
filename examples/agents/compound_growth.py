"""Author one endless grow-and-reflect machine with schema-bound constants, state, trigger seeds, and tool contracts."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
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

growth_instructions = [
    Instruction(
        id="run-continuously",
        body="Run this machine continuously: after each cycle commits, apply the same arrival again.",
    )
]

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
    direction="out",
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
    state = {STATE_CURRENT_BALANCE: 100, STATE_REFLECTION_TARGET: 800}
    emissions = []
    for _cycle in range(2):
        result = execute(
            parsed,
            Arrival(event=EVENT_GROWTH_REQUESTED),
            state,
            act=_reflect_act,
            tools=tools,
        )
        state = dict(result.state)
        emissions.extend(result.emissions)
    if len(emissions) != 2:
        raise RuntimeError("compound growth did not emit one reflection per cycle")
    if not (
        emissions[0].values[PLACEHOLDER_BALANCE] >= 800
        and emissions[1].values[PLACEHOLDER_BALANCE] >= emissions[0].values[PLACEHOLDER_BALANCE] * 8
    ):
        raise RuntimeError("compound growth cycles did not build the balance")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
