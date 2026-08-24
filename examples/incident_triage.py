"""Author one agent-facing OAK tree and write its render."""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    Act,
    BindingValue,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    LiteralValue,
    MaxChars,
    NonEmpty,
    OneOf,
    Process,
    Root,
    Schema,
    Set,
    State,
    StateValue,
    Trigger,
    Type,
    ValueBinding,
    render,
    where,
)

incident_report = Schema(
    id="incident-report",
    name="Incident Report",
    purpose="Describe the incident evidence supplied for triage.",
    template="""Summary: <SUMMARY>
Impact: <IMPACT>""",
    where=[
        where(
            "SUMMARY",
            Type(of="string"),
            NonEmpty(),
            description="observed incident evidence",
        ),
        where(
            "IMPACT",
            Type(of="string"),
            OneOf(values=["low", "medium", "high"]),
            description="reported impact",
        ),
    ],
)

triage_decision = Schema(
    id="triage-decision",
    name="Triage Decision",
    purpose="Return one evidence-based incident decision.",
    template="""Severity: <SEVERITY>
Rationale: <RATIONALE>
Next action: <NEXT_ACTION>
Policy: <POLICY>""",
    where=[
        where(
            "SEVERITY",
            Type(of="string"),
            OneOf(values=["low", "medium", "high", "critical"]),
            description="assigned severity",
        ),
        where(
            "RATIONALE",
            Type(of="string"),
            NonEmpty(),
            MaxChars(n=240),
            description="brief evidence-based reason",
        ),
        where(
            "NEXT_ACTION",
            Type(of="string"),
            NonEmpty(),
            description="one immediate action",
        ),
        where(
            "POLICY",
            Type(of="string"),
            NonEmpty(),
            description="policy applied to the decision",
        ),
    ],
)

root = Root(
    id="root",
    instructions=[
        Instruction(
            id="evidence",
            body="Use only evidence present in the incident report.",
        )
    ],
    constants=[
        Constant(
            id="escalation-policy",
            value="Escalate critical incidents immediately.",
        )
    ],
    schemas=[incident_report, triage_decision],
    state=[State(id="status", value="ready")],
    triggers=[
        Trigger(
            id="triage-trigger",
            given=Condition(
                left=StateValue(state="status"),
                operator="equals",
                right=LiteralValue(value="ready"),
            ),
            when="An incident report arrives for triage.",
            process="triage",
        )
    ],
    processes=[
        Process(
            id="triage",
            name="Triage incident",
            steps=[
                Act(
                    instruction=(
                        "Classify <SUMMARY> with <IMPACT> under <POLICY>, "
                        "then produce <SEVERITY>, <RATIONALE>, and "
                        "<NEXT_ACTION>."
                    ),
                    inputs=[
                        ValueBinding(
                            placeholder="SUMMARY",
                            value=InterfaceValue(
                                interface="report",
                                placeholder="SUMMARY",
                            ),
                        ),
                        ValueBinding(
                            placeholder="IMPACT",
                            value=InterfaceValue(
                                interface="report",
                                placeholder="IMPACT",
                            ),
                        ),
                        ValueBinding(
                            placeholder="POLICY",
                            value=ConstantValue(
                                constant="escalation-policy"
                            ),
                        ),
                    ],
                    outputs=["SEVERITY", "RATIONALE", "NEXT_ACTION"],
                ),
                If(
                    condition=Condition(
                        left=BindingValue(binding="SEVERITY"),
                        operator="equals",
                        right=LiteralValue(value="critical"),
                    ),
                    then=[
                        Set(
                            state="status",
                            value=LiteralValue(value="escalated"),
                        )
                    ],
                    otherwise=[
                        Set(
                            state="status",
                            value=LiteralValue(value="triaged"),
                        )
                    ],
                ),
                Emit(
                    interface="decision",
                    bindings=[
                        ValueBinding(
                            placeholder="SEVERITY",
                            value=BindingValue(binding="SEVERITY"),
                        ),
                        ValueBinding(
                            placeholder="RATIONALE",
                            value=BindingValue(binding="RATIONALE"),
                        ),
                        ValueBinding(
                            placeholder="NEXT_ACTION",
                            value=BindingValue(binding="NEXT_ACTION"),
                        ),
                        ValueBinding(
                            placeholder="POLICY",
                            value=ConstantValue(
                                constant="escalation-policy"
                            ),
                        ),
                    ],
                ),
            ],
        )
    ],
    interfaces=[
        Interface(
            id="report",
            direction="in",
            schema="incident-report",
            description="The report supplied for incident triage.",
        ),
        Interface(
            id="decision",
            direction="out",
            schema="triage-decision",
            description="The triage decision returned to the caller.",
        ),
    ],
)

target = pathlib.Path(__file__).with_name("incident_triage.oak.md")
target.write_text(
    render(root) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"wrote {target}")
