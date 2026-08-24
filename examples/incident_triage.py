"""Author one agent-facing OAK tree and write its render."""

import pathlib

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
    Trigger,
    Type,
    ValueBinding,
    node_xml,
    where,
)

incident_report = Schema(
    id="oak:schema/incident-report",
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
    id="oak:schema/triage-decision",
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
    id="oak:root",
    instructions=[
        Instruction(
            id="oak:instruction/evidence",
            body="Use only evidence present in the incident report.",
        )
    ],
    constants=[
        Constant(
            id="oak:constant/escalation-policy",
            name="ESCALATION_POLICY",
            value="Escalate critical incidents immediately.",
        )
    ],
    schemas=[incident_report, triage_decision],
    state=[
        State(
            id="oak:state/status",
            name="STATUS",
            value="ready",
        )
    ],
    triggers=[
        Trigger(
            id="oak:trigger/triage",
            when="An incident report arrives for triage.",
            process="oak:process/triage",
        )
    ],
    processes=[
        Process(
            id="oak:process/triage",
            name="Triage an incident",
            steps=[
                Act(
                    instruction="Classify <SUMMARY> with <IMPACT> under <POLICY>, then produce <SEVERITY>, <RATIONALE>, and <NEXT_ACTION>.",
                    inputs=[
                        ValueBinding(
                            placeholder="SUMMARY",
                            value=InterfaceValue(
                                interface="oak:interface/report",
                                placeholder="SUMMARY",
                            ),
                        ),
                        ValueBinding(
                            placeholder="IMPACT",
                            value=InterfaceValue(
                                interface="oak:interface/report",
                                placeholder="IMPACT",
                            ),
                        ),
                        ValueBinding(
                            placeholder="POLICY",
                            value=ConstantValue(
                                constant="oak:constant/escalation-policy"
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
                            state="oak:state/status",
                            value=LiteralValue(value="escalated"),
                        )
                    ],
                    otherwise=[
                        Set(
                            state="oak:state/status",
                            value=LiteralValue(value="triaged"),
                        )
                    ],
                ),
                Emit(
                    interface="oak:interface/decision",
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
                                constant="oak:constant/escalation-policy"
                            ),
                        ),
                    ],
                ),
            ],
        )
    ],
    interfaces=[
        Interface(
            id="oak:interface/report",
            direction="in",
            schema="oak:schema/incident-report",
            description="The report supplied for incident triage.",
        ),
        Interface(
            id="oak:interface/decision",
            direction="out",
            schema="oak:schema/triage-decision",
            description="The triage decision returned to the caller.",
        ),
    ],
)

target = pathlib.Path(__file__).with_name("incident_triage.oak.md")
target.write_text(node_xml(root) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target}")
