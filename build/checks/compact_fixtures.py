"""Contracted Python fixtures for plan 0006's twelve authored-syntax specimens."""

from __future__ import annotations

from dataclasses import dataclass

from oak import (
    ACT, All, Any, Assert, BindingValue, Call, Compare, Constant, Emit, Fail,
    If, Interface, LiteralValue, Node, NonEmpty, Not, Process, Schema, Set,
    State, StateValue, Trigger, Type, ValueBinding, While, render, where,
)
from oak.node.parts.processes.steps import Step


def read(name: str) -> StateValue:
    return StateValue(state="state." + name)


def literal(value: object) -> LiteralValue:
    return LiteralValue(value=value)


def compare(name: str, value: object = True, operator: str = "equals") -> Compare:
    return Compare(left=read(name), operator=operator, right=literal(value))


def call(name: str) -> Call:
    return Call(process="process." + name)


def put(name: str, value: object) -> Set:
    return Set(state="state." + name, value=literal(value))


def binding(name: str, value: object) -> ValueBinding:
    return ValueBinding(placeholder=name, value=value)


def below_target() -> Compare:
    return Compare(left=read("balance"), operator="less_than", right=BindingValue(binding="TARGET"))


def specimen_node(steps: list[Step], trigger: Trigger | None = None, *, growth: bool = False) -> Node:
    """Every specimen has real local schemas, targets, state, and process inputs."""
    return Node(
        constants=[Constant(id="approval", value=True)],
        schemas=[
            Schema(id="authoring-request", template="<SOURCE>\n<VALIDATE>", where=[
                where("SOURCE", Type(of="string")), where("VALIDATE", Type(of="boolean")),
            ]),
            Schema(id="growth-request", template="<TARGET>", where=[where("TARGET", Type(of="number"))]),
            Schema(id="message", template="<TEXT>\n<DATA>", where=[
                where("TEXT", Type(of="string")), where("DATA", NonEmpty()),
            ]),
            Schema(id="progress", template="<NEXT>", where=[where("NEXT", Type(of="number"))]),
        ],
        state=[State(id=name, value=value) for name, value in (
            ("ready", True), ("approved", True), ("override", False), ("blocked", False),
            ("status", "ready"), ("balance", 0), ("reflection-target", 2),
            ("note", "a is less than b, (hold)"), ("result", ""),
        )],
        triggers=[trigger or Trigger(
            id="run-requested", event="Run the specimen.", process="process.run",
            seed=[binding("TARGET", read("reflection-target"))] if growth else [],
        )],
        processes=[
            Process(id="run", name="Run specimen", input="schema.growth-request" if growth else None, steps=steps),
            Process(id="publish", name="Publish document", steps=[put("result", "published")]),
            Process(id="review", name="Review document", steps=[put("result", "reviewed")]),
            Process(id="author-document", name="Author document", input="schema.authoring-request", steps=[
                Emit(interface="interface.authored-output"),
            ]),
            Process(id="grow-once", name="Grow balance", steps=[
                ACT("Grow <BALANCE> into <NEXT>.", inputs=[binding("BALANCE", read("balance"))], outputs=["NEXT"]),
                Set(state="state.balance", value=BindingValue(binding="NEXT")),
                Emit(interface="interface.progress-output"),
            ]),
            Process(id="grow-balance", name="Grow balance", input="schema.growth-request", steps=[
                While(condition=below_target(), limit=10, steps=[call("grow-once")]),
            ]),
            Process(id="inspect", name="Inspect message", input="schema.message", steps=[
                Emit(interface="interface.message-output"),
            ]),
        ],
        interfaces=[
            Interface(id="authoring-input", flow="receives", schema="schema.authoring-request"),
            Interface(id="authored-output", flow="emits", schema="schema.authoring-request"),
            Interface(id="message-output", flow="emits", schema="schema.message"),
            Interface(id="progress-output", flow="emits", schema="schema.progress"),
        ],
    )


@dataclass(frozen=True)
class Specimen:
    identifier: str
    steps: tuple[Step, ...]
    process_text: str | None = None
    trigger: Trigger | None = None
    trigger_text: str | None = None
    growth: bool = False

    def node(self) -> Node:
        return specimen_node(list(self.steps), self.trigger, growth=self.growth)

    def text(self) -> str:
        """Inject the reviewed spelling into an otherwise contracted XML document."""
        text = render(self.node())
        if self.process_text is not None:
            start = text.index('\n', text.index('<process id="run"')) + 1
            end = text.index('</process>', start)
            text = text[:start] + self.process_text + '\n' + text[end:]
        if self.trigger_text is not None:
            start = text.index('<triggers>\n') + len('<triggers>\n')
            end = text.index('</triggers>', start)
            text = text[:start] + self.trigger_text + '\n' + text[end:]
        return text


_SOURCE_TRIGGER = Trigger(
    id="request-received", event="A complete OAK authoring request is received.",
    source="interface.authoring-input", process="process.author-document",
)
_GUARDED_TRIGGER = _SOURCE_TRIGGER.model_copy(update={
    "guard": All(conditions=[compare("ready"), compare("approved")]),
})
_GROWTH_TRIGGER = Trigger(
    id="growth-requested", event="Continue growing the balance.", process="process.grow-balance",
    seed=[binding("TARGET", read("reflection-target"))],
)
_MESSAGE_TRIGGER = Trigger(
    id="message-received", event='Received "go, now" (draft): x=y; #tag.', process="process.inspect",
    seed=[binding("TEXT", literal("a equals b, (c)")), binding("DATA", literal({"items": ["x,y", "(z)"]}))],
)

SPECIMENS = (
    Specimen("S01", (If(condition=compare("ready"), then=[call("publish")]),),
        'IF $state.ready equals true:\n  CALL process.publish ()'),
    Specimen("S02", (If(condition=compare("status", "ready"), then=[put("status", "complete")], otherwise=[Fail(message="The state is not ready.")]),),
        'IF $state.status equals "ready":\n  SET state.status = "complete"\nELSE:\n  FAIL "The state is not ready."'),
    Specimen("S03", (If(condition=All(conditions=[compare("ready"), compare("approved")]), then=[call("publish")], otherwise=[call("review")]),),
        'IF ALL($state.ready equals true, $state.approved equals true):\n  CALL process.publish ()\nELSE:\n  CALL process.review ()'),
    Specimen("S04", (If(condition=All(conditions=[compare("ready"), Not(condition=compare("blocked"))]), then=[call("publish")]),),
        'IF ALL($state.ready equals true, NOT($state.blocked equals true)):\n  CALL process.publish ()'),
    Specimen("S05", (
        If(condition=Any(conditions=[compare("ready"), compare("override")]), then=[call("publish")]),
        If(condition=All(conditions=[compare("ready"), Any(conditions=[compare("approved"), compare("override")]), Not(condition=compare("blocked"))]), then=[call("publish")]),
    ), 'IF ANY($state.ready equals true, $state.override equals true):\n  CALL process.publish ()\n\nIF ALL(\n  $state.ready equals true,\n  ANY($state.approved equals true, $state.override equals true),\n  NOT($state.blocked equals true),\n):\n  CALL process.publish ()'),
    Specimen("S06", (If(condition=compare("ready"), then=[
        If(condition=compare("approved"), then=[call("publish")], otherwise=[call("review")]),
    ], otherwise=[Fail(message="The state is not ready.")]),),
        'IF $state.ready equals true:\n  IF $state.approved equals true:\n    CALL process.publish ()\n  ELSE:\n    CALL process.review ()\nELSE:\n  FAIL "The state is not ready."'),
    Specimen("S07", (
        While(condition=below_target(), limit=10, steps=[call("grow-once")]),
        While(condition=All(conditions=[below_target(), Not(condition=compare("blocked"))]), limit=10, steps=[call("grow-once")]),
    ), 'WHILE $state.balance is less than $TARGET LIMIT 10:\n  CALL process.grow-once ()\n\nWHILE ALL($state.balance is less than $TARGET, NOT($state.blocked equals true)) LIMIT 10:\n  CALL process.grow-once ()', growth=True),
    Specimen("S08", (put("result", "unused"),), trigger=_SOURCE_TRIGGER,
        trigger_text='request-received(event="A complete OAK authoring request is received.", source=interface.authoring-input, process=process.author-document)'),
    Specimen("S09", (put("result", "unused"),), trigger=_GUARDED_TRIGGER,
        trigger_text='request-received(\n  event="A complete OAK authoring request is received.",\n  source=interface.authoring-input,\n  guard=ALL($state.ready equals true, $state.approved equals true),\n  process=process.author-document,\n)'),
    Specimen("S10", (put("result", "unused"),), trigger=_GROWTH_TRIGGER,
        trigger_text='growth-requested(event="Continue growing the balance.", process=process.grow-balance, seed=(TARGET=$state.reflection-target))'),
    Specimen("S11", (If(condition=compare("note", "a is less than b, (hold)"), then=[call("review")]),),
        'IF $state.note equals "a is less than b, (hold)":\n  CALL process.review ()', trigger=_MESSAGE_TRIGGER,
        trigger_text='message-received(\n  event="Received \\"go, now\\" (draft): x=y; #tag.",\n  process=process.inspect,\n  seed=(TEXT="a equals b, (c)", DATA={"items": ["x,y", "(z)"]}),\n)'.replace('\\\\"', '\\"')),
    Specimen("S12", (Assert(condition=All(conditions=[compare("ready"), Not(condition=compare("blocked"))]), message="Ready and unblocked state is required."),),
        'ASSERT ALL($state.ready equals true, NOT($state.blocked equals true))\n  MESSAGE "Ready and unblocked state is required."'),
)
