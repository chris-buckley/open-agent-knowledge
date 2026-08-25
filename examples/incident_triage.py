"""Author one agent-facing OAK document and write its render."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import cast

from pydantic import BaseModel

from oak import (
    Act,
    All,
    Assert,
    BindingValue,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    LiteralValue,
    MaxChars,
    Node,
    NonEmpty,
    OneOf,
    Process,
    Schema,
    Set,
    State,
    StateValue,
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

    @staticmethod
    def max_chars(n):
        return MaxChars(n=n)

    @staticmethod
    def one_of(*values):
        return OneOf(values=list(values))


def value(item) -> Value:
    return cast(Value, item) if isinstance(item, BaseModel) else LiteralValue(value=item)


def iface(target, placeholder):
    return InterfaceValue(interface=target, placeholder=placeholder)


def constant(target):
    return ConstantValue(constant=target)


def state(target):
    return StateValue(state=target)


def binding(name):
    return BindingValue(binding=name)


def eq(left, right):
    return Compare(left=value(left), operator="equals", right=value(right))


def ne(left, right):
    return Compare(left=value(left), operator="not_equals", right=value(right))


def all_(*conditions):
    return All(conditions=list(conditions))


def if_(condition, then, otherwise=None):
    return If(condition=condition, then=then, otherwise=otherwise)


def set_(target, item):
    return Set(state=target, value=value(item))


def emit(target, **bindings):
    return Emit(
        interface=target,
        bindings=[ValueBinding(placeholder=key, value=value(item)) for key, item in bindings.items()],
    )


CONSTANT_ESCALATION_POLICY = "constant.escalation-policy"
SCHEMA_INCIDENT_REPORT = "schema.incident-report"
SCHEMA_TRIAGE_DECISION = "schema.triage-decision"
INTERFACE_REPORT = "interface.report"
INTERFACE_DECISION = "interface.decision"
STATE_STATUS = "state.status"
PROCESS_TRIAGE = "process.triage"
SEVERITY_CRITICAL = "critical"
STATUS_READY = "ready"
STATUS_ESCALATED = "escalated"
STATUS_TRIAGED = "triaged"

incident_report_schema = Schema(
    id="incident-report",
    name="Incident Report",
    purpose="Describe the incident evidence supplied for triage.",
    template="""Summary: <SUMMARY>
Impact: <IMPACT>""",
    where=[
        where("SUMMARY", Constraint.STRING, Constraint.NON_EMPTY, description="observed incident evidence"),
        where("IMPACT", Constraint.STRING, Constraint.one_of("low", "medium", "high"), description="reported impact"),
    ],
)

triage_decision_schema = Schema(
    id="triage-decision",
    name="Triage Decision",
    purpose="Return one evidence-based incident decision.",
    template="""Severity: <SEVERITY>
Rationale: <RATIONALE>
Next action: <NEXT_ACTION>
Policy: <POLICY>""",
    where=[
        where("SEVERITY", Constraint.STRING, Constraint.one_of("low", "medium", "high", "critical"), description="assigned severity"),
        where("RATIONALE", Constraint.STRING, Constraint.NON_EMPTY, Constraint.max_chars(240), description="brief evidence-based reason"),
        where("NEXT_ACTION", Constraint.STRING, Constraint.NON_EMPTY, description="one immediate action"),
        where("POLICY", Constraint.STRING, Constraint.NON_EMPTY, description="policy applied to the decision"),
    ],
)

triage_incident_process = Process(
    id="triage",
    name="Triage incident",
    steps=[
        Act(
            instruction="Classify <SUMMARY> with <IMPACT> under <POLICY>, then produce <SEVERITY>, <RATIONALE>, and <NEXT_ACTION>.",
            inputs=[
                ValueBinding(placeholder="SUMMARY", value=iface(INTERFACE_REPORT, "SUMMARY")),
                ValueBinding(placeholder="IMPACT", value=iface(INTERFACE_REPORT, "IMPACT")),
                ValueBinding(placeholder="POLICY", value=constant(CONSTANT_ESCALATION_POLICY)),
            ],
            outputs=["SEVERITY", "RATIONALE", "NEXT_ACTION"],
        ),
        Assert(
            condition=all_(
                ne(binding("SEVERITY"), ""),
                ne(binding("RATIONALE"), ""),
            ),
            message="The triage result must not be empty.",
        ),
        if_(
            eq(binding("SEVERITY"), SEVERITY_CRITICAL),
            then=[set_(STATE_STATUS, STATUS_ESCALATED)],
            otherwise=[set_(STATE_STATUS, STATUS_TRIAGED)],
        ),
        emit(
            INTERFACE_DECISION,
            SEVERITY=binding("SEVERITY"),
            RATIONALE=binding("RATIONALE"),
            NEXT_ACTION=binding("NEXT_ACTION"),
            POLICY=constant(CONSTANT_ESCALATION_POLICY),
        ),
    ],
)

on_report_trigger = Trigger(
    id="triage-trigger",
    given=eq(state(STATE_STATUS), STATUS_READY),
    when="An incident report arrives for triage.",
    then=PROCESS_TRIAGE,
)

report_interface = Interface(
    id="report",
    direction="in",
    schema=SCHEMA_INCIDENT_REPORT,
    description="The report supplied for incident triage.",
)

decision_interface = Interface(
    id="decision",
    direction="out",
    schema=SCHEMA_TRIAGE_DECISION,
    description="The triage decision returned to the caller.",
)

node = Node(
    instructions=[Instruction(id="evidence", body="Use only evidence present in the incident report.")],
    constants=[Constant(id="escalation-policy", value="Escalate critical incidents immediately.")],
    schemas=[incident_report_schema, triage_decision_schema],
    state=[State(id="status", value=STATUS_READY)],
    triggers=[on_report_trigger],
    processes=[triage_incident_process],
    interfaces=[report_interface, decision_interface],
)

target = Path(__file__).with_name("incident_triage.oak.md")
resolve(node, source=target.as_posix())
target.write_text(render(node) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target}")
