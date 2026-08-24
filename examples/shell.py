"""Author one OAK shell state machine and write its render."""

import pathlib

from oak import (
    Call,
    Condition,
    Emit,
    Fail,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    LiteralValue,
    NonEmpty,
    Process,
    Root,
    Schema,
    Set,
    State,
    Trigger,
    Type,
    ValueBinding,
    node_xml,
    where,
)

command_line = Schema(
    id="oak:schema/command-line",
    name="Command Line",
    purpose="Carry one command the user types.",
    template="<COMMAND>",
    where=[
        where(
            "COMMAND",
            Type(of="string"),
            NonEmpty(),
            examples=["pwd", "exit"],
            description="the exact command string",
        )
    ],
)

terminal_output = Schema(
    id="oak:schema/terminal-output",
    name="Terminal Output",
    purpose="Carry one line the shell prints.",
    template="<OUTPUT>",
    where=[
        where(
            "OUTPUT",
            Type(of="string"),
            NonEmpty(),
            examples=["/oak", "logout"],
            description="the printed line",
        )
    ],
)

root = Root(
    id="oak:root",
    instructions=[
        Instruction(
            id="oak:instruction/exact-command",
            body="Treat each command as an exact string.",
        )
    ],
    schemas=[command_line, terminal_output],
    state=[
        State(
            id="oak:state/mode",
            name="MODE",
            value="open",
        )
    ],
    triggers=[
        Trigger(
            id="oak:trigger/command",
            when="A command line arrives while the shell mode is open.",
            process="oak:process/route",
        )
    ],
    processes=[
        Process(
            id="oak:process/route",
            name="Route the current command",
            steps=[
                If(
                    condition=Condition(
                        left=InterfaceValue(
                            interface="oak:interface/stdin",
                            placeholder="COMMAND",
                        ),
                        operator="equals",
                        right=LiteralValue(value="pwd"),
                    ),
                    then=[Call(process="oak:process/pwd")],
                    otherwise=[
                        If(
                            condition=Condition(
                                left=InterfaceValue(
                                    interface="oak:interface/stdin",
                                    placeholder="COMMAND",
                                ),
                                operator="equals",
                                right=LiteralValue(value="exit"),
                            ),
                            then=[Call(process="oak:process/exit")],
                            otherwise=[
                                Fail(message="Unknown shell command.")
                            ],
                        )
                    ],
                )
            ],
        ),
        Process(
            id="oak:process/pwd",
            name="Run pwd",
            steps=[
                Emit(
                    interface="oak:interface/stdout",
                    bindings=[
                        ValueBinding(
                            placeholder="OUTPUT",
                            value=LiteralValue(value="/oak"),
                        )
                    ],
                )
            ],
        ),
        Process(
            id="oak:process/exit",
            name="Run exit",
            steps=[
                Emit(
                    interface="oak:interface/stdout",
                    bindings=[
                        ValueBinding(
                            placeholder="OUTPUT",
                            value=LiteralValue(value="logout"),
                        )
                    ],
                ),
                Set(
                    state="oak:state/mode",
                    value=LiteralValue(value="closed"),
                ),
            ],
        ),
    ],
    interfaces=[
        Interface(
            id="oak:interface/stdin",
            direction="in",
            schema="oak:schema/command-line",
            description="The command line the user types.",
        ),
        Interface(
            id="oak:interface/stdout",
            direction="out",
            schema="oak:schema/terminal-output",
            description="The line the shell prints.",
        ),
    ],
)

target = pathlib.Path(__file__).with_name("shell.oak.md")
target.write_text(node_xml(root) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target}")
