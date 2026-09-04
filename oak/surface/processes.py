"""Process-value, condition, step, and process surface descriptors."""

from __future__ import annotations

from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Not,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import (
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
        "ALL:\n  <CONDITIONS>",
        rendered=("conditions",),
        fixed=("kind",),
    ),
    _surface(
        "condition-any",
        Any,
        "ANY:\n  <CONDITIONS>",
        rendered=("conditions",),
        fixed=("kind",),
    ),
    _surface(
        "condition-not",
        Not,
        "NOT:\n  <CONDITION>",
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
        "step-set",
        Set,
        "SET <STATE> = <VALUE>",
        rendered=(
            "state",
            "value",
        ),
        fixed=("kind",),
    ),
    _surface(
        "step-emit-inferred",
        Emit,
        "EMIT <INTERFACE>",
        rendered=("interface",),
        fixed=("kind", "bindings"),
        when=(("bindings", []),),
    ),
    _surface(
        "step-emit-explicit",
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
        "step-if",
        If,
        "IF <CONDITION>:\nTHEN:\n  <THEN>\nELSE:\n  <OTHERWISE>",
        rendered=(
            "condition",
            "then",
            "otherwise",
        ),
        fixed=("kind",),
    ),
    _surface(
        "step-call",
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
        "step-fail",
        Fail,
        "FAIL <MESSAGE>",
        rendered=("message",),
        fixed=("kind",),
    ),
    _surface(
        "step-assert",
        Assert,
        "ASSERT <CONDITION>\nMESSAGE <MESSAGE>",
        rendered=(
            "condition",
            "message",
        ),
        fixed=("kind",),
    ),
    _surface(
        "step-foreach",
        Foreach,
        "FOREACH <BINDING> IN <VALUE>:\n  <STEPS>",
        rendered=(
            "binding",
            "value",
            "steps",
        ),
        fixed=("kind",),
    ),
    _surface(
        "step-while",
        While,
        "WHILE <CONDITION> LIMIT <LIMIT>:\n  <STEPS>",
        rendered=(
            "condition",
            "limit",
            "steps",
        ),
        fixed=("kind",),
    ),
    _surface(
        "step-par",
        Par,
        "PAR:\n  <STEPS>",
        rendered=("steps",),
        fixed=("kind",),
    ),
    _surface(
        "step-join",
        Join,
        "JOIN",
        fixed=("kind",),
    ),
    _surface(
        "process",
        Process,
        '<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">\n<STEPS>\n</process>',
        rendered=(
            "id",
            "name",
            "input",
            "output",
            "steps",
        ),
        fixed=("part",),
        part="processes",
        tag="process",
    ),
)

__all__ = [
    "PROCESS_SURFACES",
]
