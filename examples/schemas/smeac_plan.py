"""Author the ported SMEAC plan format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import AtLeast, Instruction, Lines, Node, NonEmpty, OneOf, Schema, Type, parse, render, resolve, where

smeac_plan_schema = Schema(
    id="smeac-plan",
    name="SMEAC Plan",
    purpose="Structure a planning brief covering situation, mission, execution phases, logistics, and command.",
    template=(
        "# <PLAN_TITLE>\n"
        "\n"
        "Prepared: <TIMESTAMP>\n"
        "Classification: <CLASSIFICATION>\n"
        "\n"
        "## 1. Situation\n"
        "\n"
        "### Operating Environment\n"
        "<OPERATING_ENVIRONMENT>\n"
        "\n"
        "### Current State\n"
        "<CURRENT_STATE>\n"
        "\n"
        "### Challenges\n"
        "- <OBSTACLE>: <OBSTACLE_ASSESSMENT>\n"
        "...\n"
        "\n"
        "### Supporting Factors\n"
        "- Higher intent: <HIGHER_INTENT>\n"
        "- Adjacent efforts: <ADJACENT_EFFORTS>\n"
        "- Supporting resources: <SUPPORTING_RESOURCES>\n"
        "\n"
        "### Assumptions\n"
        "- <ASSUMPTION>\n"
        "...\n"
        "\n"
        "### Constraints and Limitations\n"
        "- Constraint: <CONSTRAINT>\n"
        "- Limitation: <LIMITATION>\n"
        "...\n"
        "\n"
        "## 2. Mission\n"
        "\n"
        "<MISSION_STATEMENT>\n"
        "\n"
        "Task: <TASK>\n"
        "Purpose: <PURPOSE>\n"
        "End state: <END_STATE>\n"
        "\n"
        "## 3. Execution\n"
        "\n"
        "Intent: <LEADERS_INTENT>\n"
        "Concept of operations: <CONCEPT_OF_OPERATIONS>\n"
        "\n"
        "### Phase <PHASE_NUMBER>: <PHASE_NAME>\n"
        "- Objective: <PHASE_OBJECTIVE>\n"
        "- Key task: <PHASE_TASK>\n"
        "  ...\n"
        "- Success criteria: <PHASE_SUCCESS_CRITERIA>\n"
        "- Transition trigger: <TRANSITION_TRIGGER>\n"
        "...\n"
        "\n"
        "### Coordinating Instructions\n"
        "- Timeline: <TIMELINE>\n"
        "- Boundaries: <BOUNDARIES>\n"
        "- Operating guidelines: <OPERATING_GUIDELINES>\n"
        "- Risk mitigation: <RISK_MITIGATION>\n"
        "\n"
        "### Contingencies\n"
        "- If <CONTINGENCY_CONDITION> then <CONTINGENCY_ACTION>\n"
        "...\n"
        "\n"
        "## 4. Admin and Logistics\n"
        "\n"
        "| Resource | Quantity | Source | Status |\n"
        "| --- | --- | --- | --- |\n"
        "| <RESOURCE_NAME> | <RESOURCE_QUANTITY> | <RESOURCE_SOURCE> | <RESOURCE_STATUS> |\n"
        "...\n"
        "\n"
        "Supply: <SUPPLY_PLAN>\n"
        "Transportation: <TRANSPORTATION_PLAN>\n"
        "Sustainment: <SUSTAINMENT_PLAN>\n"
        "Rollback: <ROLLBACK_PLAN>\n"
        "\n"
        "## 5. Command and Signal\n"
        "\n"
        "1. <PRIMARY_LEAD>\n"
        "2. <SUCCESSOR_LEAD>\n"
        "...\n"
        "\n"
        "| Channel | Medium | Purpose | Cadence |\n"
        "| --- | --- | --- | --- |\n"
        "| <CHANNEL_NAME> | <CHANNEL_MEDIUM> | <CHANNEL_PURPOSE> | <CHANNEL_CADENCE> |\n"
        "...\n"
        "\n"
        "Reporting: <REPORTING_REQUIREMENT>\n"
        "...\n"
        "\n"
        "| Decision | Authority | Escalation |\n"
        "| --- | --- | --- |\n"
        "| <DECISION_TYPE> | <DECISION_AUTHORITY> | <ESCALATION_AUTHORITY> |\n"
        "...\n"
        "\n"
        "### Acknowledgement\n"
        "All parties MUST acknowledge receipt and understanding of this plan."
    ),
    where=[
        where("PLAN_TITLE", Type(of="string"), NonEmpty(), description="one concise name for the plan or operation"),
        where("TIMESTAMP", Type(of="datetime"), description="when the plan was prepared"),
        where("CLASSIFICATION", Type(of="string"), OneOf(values=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]), description="the handling classification"),
        where("OPERATING_ENVIRONMENT", Type(of="string"), NonEmpty(), description="one to three sentences on the domain and scope of operations"),
        where("CURRENT_STATE", Type(of="string"), NonEmpty(), description="one to three sentences of factual current assessment"),
        where("OBSTACLE", Type(of="string"), NonEmpty(), description="the name of a challenge, competitor, blocker, or risk"),
        where("OBSTACLE_ASSESSMENT", Type(of="string"), NonEmpty(), description="impact, likelihood, and probable course of the obstacle"),
        where("HIGHER_INTENT", Type(of="string"), NonEmpty(), description="the overarching goal this plan supports"),
        where("ADJACENT_EFFORTS", Type(of="string"), NonEmpty(), description="related parallel initiatives and their relevance"),
        where("SUPPORTING_RESOURCES", Type(of="string"), NonEmpty(), description="available assets, teams, tools, or capabilities"),
        where("ASSUMPTION", Type(of="string"), NonEmpty(), description="one condition assumed true, validated before or during execution"),
        where("CONSTRAINT", Type(of="string"), NonEmpty(), description="one must or must-not restriction imposed by leadership or policy"),
        where("LIMITATION", Type(of="string"), NonEmpty(), description="one capability or resource shortcoming that restricts options"),
        where("MISSION_STATEMENT", Type(of="string"), Lines(min=1, max=1), description="one present-tense active-voice sentence answering who, what, when, where, and why"),
        where("TASK", Type(of="string"), NonEmpty(), description="the specific measurable time-bound action"),
        where("PURPOSE", Type(of="string"), NonEmpty(), description="why the task matters and its link to higher intent"),
        where("END_STATE", Type(of="string"), NonEmpty(), description="the desired conditions when the mission is complete"),
        where("LEADERS_INTENT", Type(of="string"), NonEmpty(), description="two to four sentences on purpose, key tasks, and end state in the leader's own framing"),
        where("CONCEPT_OF_OPERATIONS", Type(of="string"), NonEmpty(), description="two to five sentences on how the phases combine"),
        where("PHASE_NUMBER", Type(of="integer"), AtLeast(value=1), description="the sequential phase number"),
        where("PHASE_NAME", Type(of="string"), NonEmpty(), description="one short descriptive phase name"),
        where("PHASE_OBJECTIVE", Type(of="string"), NonEmpty(), description="what the phase aims to achieve"),
        where("PHASE_TASK", Type(of="string"), NonEmpty(), description="one discrete assignable task within the phase"),
        where("PHASE_SUCCESS_CRITERIA", Type(of="string"), NonEmpty(), description="measurable conditions that end the phase"),
        where("TRANSITION_TRIGGER", Type(of="string"), NonEmpty(), description="the event that signals the next phase, mission complete for the last phase"),
        where("TIMELINE", Type(of="string"), NonEmpty(), description="key dates, deadlines, or time windows"),
        where("BOUNDARIES", Type(of="string"), NonEmpty(), description="scope limits and deconfliction lines"),
        where("OPERATING_GUIDELINES", Type(of="string"), NonEmpty(), description="guidelines governing actions, decisions, and interactions"),
        where("RISK_MITIGATION", Type(of="string"), NonEmpty(), description="identified risks and their mitigations"),
        where("CONTINGENCY_CONDITION", Type(of="string"), NonEmpty(), description="one specific adverse event or deviation"),
        where("CONTINGENCY_ACTION", Type(of="string"), NonEmpty(), description="the prescribed response to the condition"),
        where("RESOURCE_NAME", Type(of="string"), NonEmpty(), description="the name or type of the resource"),
        where("RESOURCE_QUANTITY", Type(of="string"), NonEmpty(), description="the amount or count required"),
        where("RESOURCE_SOURCE", Type(of="string"), NonEmpty(), description="where the resource comes from"),
        where("RESOURCE_STATUS", Type(of="string"), OneOf(values=["AVAILABLE", "REQUESTED", "PENDING", "AT_RISK", "UNAVAILABLE"]), description="the provisioning status"),
        where("SUPPLY_PLAN", Type(of="string"), NonEmpty(), description="one to three sentences on how consumable resources are sourced and distributed"),
        where("TRANSPORTATION_PLAN", Type(of="string"), NonEmpty(), description="one to three sentences on how assets and deliverables move between stages"),
        where("SUSTAINMENT_PLAN", Type(of="string"), NonEmpty(), description="one to three sentences on how the operation is maintained over its duration"),
        where("ROLLBACK_PLAN", Type(of="string"), NonEmpty(), description="one to three sentences on how to revert or recover if execution fails"),
        where("PRIMARY_LEAD", Type(of="string"), NonEmpty(), description="the name and role of the primary decision maker"),
        where("SUCCESSOR_LEAD", Type(of="string"), NonEmpty(), description="the name and role of the next in line"),
        where("CHANNEL_NAME", Type(of="string"), NonEmpty(), description="the identifier for the communication channel"),
        where("CHANNEL_MEDIUM", Type(of="string"), NonEmpty(), description="the medium of communication"),
        where("CHANNEL_PURPOSE", Type(of="string"), NonEmpty(), description="what the channel is used for"),
        where("CHANNEL_CADENCE", Type(of="string"), NonEmpty(), description="the frequency of communication"),
        where("REPORTING_REQUIREMENT", Type(of="string"), NonEmpty(), description="one expected report, metric, or status update"),
        where("DECISION_TYPE", Type(of="string"), NonEmpty(), description="the category of decision"),
        where("DECISION_AUTHORITY", Type(of="string"), NonEmpty(), description="who has authority for this decision"),
        where("ESCALATION_AUTHORITY", Type(of="string"), NonEmpty(), description="who to escalate to when the authority is unavailable"),
    ],
)

smeac_plan_node = Node(
    instructions=[Instruction(id="repeat-marker", body="A ... line in a template marks repetition of the pattern above it.")],
    schemas=[smeac_plan_schema],
)

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the authored SMEAC plan node."""
    rendered = render(smeac_plan_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("SMEAC plan example changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
