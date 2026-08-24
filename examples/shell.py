"""Author one closed OAK state machine and write its render."""

import pathlib

from oak import (
    Call,
    Condition,
    Fail,
    If,
    Instruction,
    LiteralValue,
    Process,
    Root,
    Set,
    State,
    StateValue,
    Trigger,
    node_xml,
)

root = Root(
    id="oak:root",
    instructions=[
        Instruction(
            id="oak:instruction/exact-command",
            body="Treat each command as an exact string.",
        )
    ],
    state=[
        State(
            id="oak:state/mode",
            name="MODE",
            value="open",
        ),
        State(
            id="oak:state/command",
            name="COMMAND",
            value="pwd",
        ),
        State(
            id="oak:state/output",
            name="OUTPUT",
            value="",
        ),
    ],
    triggers=[
        Trigger(
            id="oak:trigger/open",
            when="The shell mode is open.",
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
                        left=StateValue(state="oak:state/command"),
                        operator="equals",
                        right=LiteralValue(value="pwd"),
                    ),
                    then=[Call(process="oak:process/pwd")],
                    otherwise=[
                        If(
                            condition=Condition(
                                left=StateValue(state="oak:state/command"),
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
                Set(
                    state="oak:state/output",
                    value=LiteralValue(value="/oak"),
                ),
                Set(
                    state="oak:state/command",
                    value=LiteralValue(value="exit"),
                ),
            ],
        ),
        Process(
            id="oak:process/exit",
            name="Run exit",
            steps=[
                Set(
                    state="oak:state/output",
                    value=LiteralValue(value="logout"),
                ),
                Set(
                    state="oak:state/mode",
                    value=LiteralValue(value="closed"),
                ),
            ],
        ),
    ],
)

target = pathlib.Path(__file__).with_name("shell.oak.md")
target.write_text(node_xml(root) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target}")
