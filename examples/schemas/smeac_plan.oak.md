<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="smeac-plan" name="SMEAC Plan" purpose="Structure a planning brief covering situation, mission, execution phases, logistics, and command.">
# <PLAN_TITLE>

Prepared: <TIMESTAMP>
Classification: <CLASSIFICATION>

## 1. Situation

### Operating Environment
<OPERATING_ENVIRONMENT>

### Current State
<CURRENT_STATE>

### Challenges
- <OBSTACLE>: <OBSTACLE_ASSESSMENT>
...

### Supporting Factors
- Higher intent: <HIGHER_INTENT>
- Adjacent efforts: <ADJACENT_EFFORTS>
- Supporting resources: <SUPPORTING_RESOURCES>

### Assumptions
- <ASSUMPTION>
...

### Constraints and Limitations
- Constraint: <CONSTRAINT>
- Limitation: <LIMITATION>
...

## 2. Mission

<MISSION_STATEMENT>

Task: <TASK>
Purpose: <PURPOSE>
End state: <END_STATE>

## 3. Execution

Intent: <LEADERS_INTENT>
Concept of operations: <CONCEPT_OF_OPERATIONS>

### Phase <PHASE_NUMBER>: <PHASE_NAME>
Objective: <PHASE_OBJECTIVE>
- [ ] Key task: <PHASE_TASK>
  ...
Success criteria: <PHASE_SUCCESS_CRITERIA>
Transition trigger: <TRANSITION_TRIGGER>
...

### Coordinating Instructions
- Timeline: <TIMELINE>
- Boundaries: <BOUNDARIES>
- Operating guidelines: <OPERATING_GUIDELINES>
- Risk mitigation: <RISK_MITIGATION>

### Contingencies
- If <CONTINGENCY_CONDITION> then <CONTINGENCY_ACTION>
...

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| <RESOURCE_NAME> | <RESOURCE_QUANTITY> | <RESOURCE_SOURCE> | <RESOURCE_STATUS> |
...

Supply: <SUPPLY_PLAN>
Transportation: <TRANSPORTATION_PLAN>
Sustainment: <SUSTAINMENT_PLAN>
Rollback: <ROLLBACK_PLAN>

## 5. Command and Signal

1. <PRIMARY_LEAD>
2. <SUCCESSOR_LEAD>
...

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| <CHANNEL_NAME> | <CHANNEL_MEDIUM> | <CHANNEL_PURPOSE> | <CHANNEL_CADENCE> |
...

Reporting: <REPORTING_REQUIREMENT>
...

| Decision | Authority | Escalation |
| --- | --- | --- |
| <DECISION_TYPE> | <DECISION_AUTHORITY> | <ESCALATION_AUTHORITY> |
...

### Acknowledgement
All parties MUST acknowledge receipt and understanding of this plan.

WHERE:
- <PLAN_TITLE> is string; is non-empty; one concise name for the plan or operation.
- <TIMESTAMP> is datetime; when the plan was prepared.
- <CLASSIFICATION> is string; is one of `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`; the handling classification.
- <OPERATING_ENVIRONMENT> is string; is non-empty; one to three sentences on the domain and scope of operations.
- <CURRENT_STATE> is string; is non-empty; one to three sentences of factual current assessment.
- <OBSTACLE> is string; is non-empty; the name of a challenge, competitor, blocker, or risk.
- <OBSTACLE_ASSESSMENT> is string; is non-empty; impact, likelihood, and probable course of the obstacle.
- <HIGHER_INTENT> is string; is non-empty; the overarching goal this plan supports.
- <ADJACENT_EFFORTS> is string; is non-empty; related parallel initiatives and their relevance.
- <SUPPORTING_RESOURCES> is string; is non-empty; available assets, teams, tools, or capabilities.
- <ASSUMPTION> is string; is non-empty; one condition assumed true, validated before or during execution.
- <CONSTRAINT> is string; is non-empty; one must or must-not restriction imposed by leadership or policy.
- <LIMITATION> is string; is non-empty; one capability or resource shortcoming that restricts options.
- <MISSION_STATEMENT> is string; is one line; one present-tense active-voice sentence answering who, what, when, where, and why.
- <TASK> is string; is non-empty; the specific measurable time-bound action.
- <PURPOSE> is string; is non-empty; why the task matters and its link to higher intent.
- <END_STATE> is string; is non-empty; the desired conditions when the mission is complete.
- <LEADERS_INTENT> is string; is non-empty; two to four sentences on purpose, key tasks, and end state in the leader's own framing.
- <CONCEPT_OF_OPERATIONS> is string; is non-empty; two to five sentences on how the phases combine.
- <PHASE_NUMBER> is integer; is at least 1; the sequential phase number.
- <PHASE_NAME> is string; is non-empty; one short descriptive phase name.
- <PHASE_OBJECTIVE> is string; is non-empty; what the phase aims to achieve.
- <PHASE_TASK> is string; is non-empty; one discrete assignable task within the phase.
- <PHASE_SUCCESS_CRITERIA> is string; is non-empty; measurable conditions that end the phase.
- <TRANSITION_TRIGGER> is string; is non-empty; the event that signals the next phase, mission complete for the last phase.
- <TIMELINE> is string; is non-empty; key dates, deadlines, or time windows.
- <BOUNDARIES> is string; is non-empty; scope limits and deconfliction lines.
- <OPERATING_GUIDELINES> is string; is non-empty; guidelines governing actions, decisions, and interactions.
- <RISK_MITIGATION> is string; is non-empty; identified risks and their mitigations.
- <CONTINGENCY_CONDITION> is string; is non-empty; one specific adverse event or deviation.
- <CONTINGENCY_ACTION> is string; is non-empty; the prescribed response to the condition.
- <RESOURCE_NAME> is string; is non-empty; the name or type of the resource.
- <RESOURCE_QUANTITY> is string; is non-empty; the amount or count required.
- <RESOURCE_SOURCE> is string; is non-empty; where the resource comes from.
- <RESOURCE_STATUS> is string; is one of `AVAILABLE`, `REQUESTED`, `PENDING`, `AT_RISK`, `UNAVAILABLE`; the provisioning status.
- <SUPPLY_PLAN> is string; is non-empty; one to three sentences on how consumable resources are sourced and distributed.
- <TRANSPORTATION_PLAN> is string; is non-empty; one to three sentences on how assets and deliverables move between stages.
- <SUSTAINMENT_PLAN> is string; is non-empty; one to three sentences on how the operation is maintained over its duration.
- <ROLLBACK_PLAN> is string; is non-empty; one to three sentences on how to revert or recover if execution fails.
- <PRIMARY_LEAD> is string; is non-empty; the name and role of the primary decision maker.
- <SUCCESSOR_LEAD> is string; is non-empty; the name and role of the next in line.
- <CHANNEL_NAME> is string; is non-empty; the identifier for the communication channel.
- <CHANNEL_MEDIUM> is string; is non-empty; the medium of communication.
- <CHANNEL_PURPOSE> is string; is non-empty; what the channel is used for.
- <CHANNEL_CADENCE> is string; is non-empty; the frequency of communication.
- <REPORTING_REQUIREMENT> is string; is non-empty; one expected report, metric, or status update.
- <DECISION_TYPE> is string; is non-empty; the category of decision.
- <DECISION_AUTHORITY> is string; is non-empty; who has authority for this decision.
- <ESCALATION_AUTHORITY> is string; is non-empty; who to escalate to when the authority is unavailable.
</schema>
</schemas>