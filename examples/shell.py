"""Author one OAK shell state machine and write its render."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import cast

from pydantic import BaseModel

from oak import (
    Call,
    Compare,
    Emit,
    Fail,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    LiteralValue,
    Node,
    NonEmpty,
    Process,
    Schema,
    Set,
    State,
    StateValue,
    Step,
    Trigger,
    Type,
    Value,
    ValueBinding,
    render,
    resolve,
    where,
)


class Constraint:
    """Every constraint kind behind one discoverable name."""

    STRING = Type(of="string")
    NON_EMPTY = NonEmpty()


def value(item) -> Value:
    return cast(Value, item) if isinstance(item, BaseModel) else LiteralValue(value=item)


def iface(target, placeholder):
    return InterfaceValue(interface=target, placeholder=placeholder)


def state(target):
    return StateValue(state=target)


def eq(left, right):
    return Compare(left=value(left), operator="equals", right=value(right))


def if_(condition, then, otherwise=None):
    return If(condition=condition, then=then, otherwise=otherwise)


def call(target):
    return Call(process=target)


def fail(message):
    return Fail(message=message)


def set_(target, item):
    return Set(state=target, value=value(item))


def emit(target, **bindings):
    return Emit(
        interface=target,
        bindings=[ValueBinding(placeholder=key, value=value(item)) for key, item in bindings.items()],
    )


def match_(subject, *cases, otherwise) -> list[Step]:
    steps: list[Step] = list(otherwise)
    for literal, branch in reversed(cases):
        steps = [if_(eq(subject, literal), then=branch, otherwise=steps)]
    return steps


SCHEMA_COMMAND_LINE = "schema.command-line"
SCHEMA_TERMINAL_OUTPUT = "schema.terminal-output"
INTERFACE_STDIN = "interface.stdin"
INTERFACE_STDOUT = "interface.stdout"
STATE_MODE = "state.mode"
PROCESS_ROUTE = "process.route"
PROCESS_PWD = "process.pwd"
PROCESS_EXIT = "process.exit"
PLACEHOLDER_COMMAND = "COMMAND"
CMD_PWD = "pwd"
CMD_EXIT = "exit"
MODE_OPEN = "open"
MODE_CLOSED = "closed"

command_line_schema = Schema(
    id="command-line",
    name="Command Line",
    purpose="Carry one command the user types.",
    template="<COMMAND>",
    where=[where(PLACEHOLDER_COMMAND, Constraint.STRING, Constraint.NON_EMPTY, examples=[CMD_PWD, CMD_EXIT], description="the exact command string")],
)

terminal_output_schema = Schema(
    id="terminal-output",
    name="Terminal Output",
    purpose="Carry one line the shell prints.",
    template="<OUTPUT>",
    where=[where("OUTPUT", Constraint.STRING, Constraint.NON_EMPTY, examples=["/oak", "logout"], description="the printed line")],
)

route_command_process = Process(
    id="route",
    name="Route command",
    steps=match_(
        iface(INTERFACE_STDIN, PLACEHOLDER_COMMAND),
        (CMD_PWD, [call(PROCESS_PWD)]),
        (CMD_EXIT, [call(PROCESS_EXIT)]),
        otherwise=[fail("Unknown shell command.")],
    ),
)

run_pwd_process = Process(id="pwd", name="Run pwd", steps=[emit(INTERFACE_STDOUT, OUTPUT="/oak")])

run_exit_process = Process(
    id="exit",
    name="Run exit",
    steps=[emit(INTERFACE_STDOUT, OUTPUT="logout"), set_(STATE_MODE, MODE_CLOSED)],
)

on_command_trigger = Trigger(
    id="command",
    given=eq(state(STATE_MODE), MODE_OPEN),
    when="A command line arrives.",
    then=PROCESS_ROUTE,
)

stdin_interface = Interface(
    id="stdin",
    direction="in",
    schema=SCHEMA_COMMAND_LINE,
    description="The command line the user types.",
)

stdout_interface = Interface(
    id="stdout",
    direction="out",
    schema=SCHEMA_TERMINAL_OUTPUT,
    description="The line the shell prints.",
)

node = Node(
    instructions=[Instruction(id="exact-command", body="Treat each command as an exact string.")],
    schemas=[command_line_schema, terminal_output_schema],
    state=[State(id="mode", value=MODE_OPEN)],
    triggers=[on_command_trigger],
    processes=[route_command_process, run_pwd_process, run_exit_process],
    interfaces=[stdin_interface, stdout_interface],
)

target = Path(__file__).with_name("shell.oak.md")
resolve(node, source=target.as_posix())
target.write_text(render(node) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target}")
