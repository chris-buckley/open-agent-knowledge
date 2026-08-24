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
    StateValue,
    Trigger,
    Type,
    ValueBinding,
    node_xml,
    where,
)

command_line = Schema(
    id="command-line",
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
    id="terminal-output",
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
    id="root",
    instructions=[
        Instruction(
            id="exact-command",
            body="Treat each command as an exact string.",
        )
    ],
    schemas=[
        command_line,
        terminal_output,
    ],
    state=[
        State(
            id="mode",
            value="open",
        )
    ],
    triggers=[
        Trigger(
            id="command",
            given=Condition(
                left=StateValue(
                    state="mode",
                ),
                operator="equals",
                right=LiteralValue(
                    value="open",
                ),
            ),
            when="A command line arrives.",
            process="route",
        )
    ],
    processes=[
        Process(
            id="route",
            name="Route command",
            steps=[
                If(
                    condition=Condition(
                        left=InterfaceValue(
                            interface="stdin",
                            placeholder="COMMAND",
                        ),
                        operator="equals",
                        right=LiteralValue(
                            value="pwd",
                        ),
                    ),
                    then=[
                        Call(
                            process="pwd",
                        )
                    ],
                    otherwise=[
                        If(
                            condition=Condition(
                                left=InterfaceValue(
                                    interface="stdin",
                                    placeholder="COMMAND",
                                ),
                                operator="equals",
                                right=LiteralValue(
                                    value="exit",
                                ),
                            ),
                            then=[
                                Call(
                                    process="exit",
                                )
                            ],
                            otherwise=[
                                Fail(
                                    message="Unknown shell command.",
                                )
                            ],
                        )
                    ],
                )
            ],
        ),
        Process(
            id="pwd",
            name="Run pwd",
            steps=[
                Emit(
                    interface="stdout",
                    bindings=[
                        ValueBinding(
                            placeholder="OUTPUT",
                            value=LiteralValue(
                                value="/oak",
                            ),
                        )
                    ],
                )
            ],
        ),
        Process(
            id="exit",
            name="Run exit",
            steps=[
                Emit(
                    interface="stdout",
                    bindings=[
                        ValueBinding(
                            placeholder="OUTPUT",
                            value=LiteralValue(
                                value="logout",
                            ),
                        )
                    ],
                ),
                Set(
                    state="mode",
                    value=LiteralValue(
                        value="closed",
                    ),
                ),
            ],
        ),
    ],
    interfaces=[
        Interface(
            id="stdin",
            direction="in",
            schema="command-line",
            description="The command line the user types.",
        ),
        Interface(
            id="stdout",
            direction="out",
            schema="terminal-output",
            description="The line the shell prints.",
        ),
    ],
)

target = pathlib.Path(__file__).with_name(
    "shell.oak.md"
)
target.write_text(
    node_xml(root) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"wrote {target}")
