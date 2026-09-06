"""Process-value, condition, step, and process surface descriptors."""

from __future__ import annotations

from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Not,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.statements import (
    Act,
    Assert,
    Call,
    Emit,
    Fail,
    Foreach,
    If,
    Join,
    Par,
    Set,
    While,
)
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    LiteralValue,
    StateValue,
    ValueBinding,
)
from oak.surface.model import _NON_EMPTY, _PRESENT, _surface

PROCESS_SURFACES = (
    _surface(
        "value-literal",
        LiteralValue,
        "<VALUE>",
        rendered=("value",),
        fixed=("source",),
    ),
    _surface(
        "value-constant",
        ConstantValue,
        "$<CONSTANT>",
        rendered=("constant",),
        fixed=("source",),
    ),
    _surface(
        "value-state",
        StateValue,
        "$<STATE>",
        rendered=("state",),
        fixed=("source",),
    ),
    _surface(
        "value-binding",
        BindingValue,
        "$<BINDING>",
        rendered=("binding",),
        fixed=("source",),
    ),
    _surface(
        "value-binding-line",
        ValueBinding,
        "<PLACEHOLDER>=<VALUE>",
        rendered=(
            "placeholder",
            "value",
        ),
    ),
    _surface(
        "condition-compare",
        Compare,
        "<LEFT> <OPERATOR> <RIGHT>",
        rendered=(
            "left",
            "operator",
            "right",
        ),
        fixed=("kind",),
    ),
    _surface(
        "condition-all",
        All,
        "ALL(<CONDITIONS>)",
        rendered=("conditions",),
        fixed=("kind",),
    ),
    _surface(
        "condition-any",
        Any,
        "ANY(<CONDITIONS>)",
        rendered=("conditions",),
        fixed=("kind",),
    ),
    _surface(
        "condition-not",
        Not,
        "NOT(<CONDITION>)",
        rendered=("condition",),
        fixed=("kind",),
    ),
    _surface(
        "act-native",
        Act,
        'ACT input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS>',
        rendered=(
            "input",
            "output",
            "instruction",
            "inputs",
            "outputs",
        ),
        fixed=("kind",),
        omitted=("tool",),
        when=(("tool", None),),
    ),
    _surface(
        "act-tool",
        Act,
        'ACT TOOL "<TOOL>" input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS>',
        rendered=(
            "tool",
            "input",
            "output",
            "instruction",
            "inputs",
            "outputs",
        ),
        fixed=("kind",),
        when=(("tool", _PRESENT),),
    ),
    _surface(
        "statement-set",
        Set,
        "SET <STATE> = <VALUE>",
        rendered=(
            "state",
            "value",
        ),
        fixed=("kind",),
    ),
    _surface(
        "statement-emit-inferred",
        Emit,
        "EMIT <INTERFACE>",
        rendered=("interface",),
        fixed=("kind", "bindings"),
        when=(("bindings", []),),
    ),
    _surface(
        "statement-emit-explicit",
        Emit,
        "EMIT <INTERFACE> (<BINDINGS>)",
        rendered=(
            "interface",
            "bindings",
        ),
        fixed=("kind",),
        when=(("bindings", _NON_EMPTY),),
    ),
    _surface(
        "statement-if",
        If,
        "IF <CONDITION>:\n  <THEN>\nELSE:\n  <OTHERWISE>",
        rendered=(
            "condition",
            "then",
            "otherwise",
        ),
        fixed=("kind",),
    ),
    _surface(
        "statement-call",
        Call,
        "CALL <PROCESS> (<INPUTS>) -> <OUTPUTS>",
        rendered=(
            "process",
            "inputs",
            "outputs",
        ),
        fixed=("kind",),
    ),
    _surface(
        "statement-fail",
        Fail,
        "FAIL <MESSAGE>",
        rendered=("message",),
        fixed=("kind",),
    ),
    _surface(
        "statement-assert",
        Assert,
        "ASSERT <CONDITION>\n  MESSAGE <MESSAGE>",
        rendered=(
            "condition",
            "message",
        ),
        fixed=("kind",),
    ),
    _surface(
        "statement-foreach",
        Foreach,
        "FOREACH <BINDING> IN <VALUE>:\n  <BODY>",
        rendered=(
            "binding",
            "value",
            "body",
        ),
        fixed=("kind",),
    ),
    _surface(
        "statement-while",
        While,
        "WHILE <CONDITION> LIMIT <LIMIT>:\n  <BODY>",
        rendered=(
            "condition",
            "limit",
            "body",
        ),
        fixed=("kind",),
    ),
    _surface(
        "statement-par",
        Par,
        "PAR:\n  <BODY>",
        rendered=("body",),
        fixed=("kind",),
    ),
    _surface(
        "statement-join",
        Join,
        "JOIN",
        fixed=("kind",),
    ),
    _surface(
        "process",
        Process,
        '<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">\n<BODY>\n</process>',
        rendered=(
            "id",
            "name",
            "input",
            "output",
            "body",
        ),
        fixed=("part",),
        part="processes",
        tag="process",
    ),
)

__all__ = [
    "PROCESS_SURFACES",
]
