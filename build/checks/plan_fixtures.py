"""Fixed SMEAC examples, independent of the schema and plan checker."""

CURRENT_TREE = """project/
└── source.py                              # Existing source"""
PLANNED_TREE = """project/
├── source.py                              # [modify] Use the new helper
└── helper.py                              # [add] Own the shared operation"""

DIRECTORY_EXAMPLE = """### Directory Changes

Baseline: inspected fixture revision abc123.
Legend: [add] new; [modify] changed; [move from PATH] relocated; [remove] deleted; [keep] unchanged context; [check] verify and change only if needed.
Current:
```text
project/
└── source.py                              # Existing source
```
Planned:
```text
project/
├── source.py                              # [modify] Use the new helper
└── helper.py                              # [add] Own the shared operation
```
Ownership: source.py owns the call; helper.py owns the operation. Neither is generated.
Verification: compare the actual changed paths and inspected diff with this view.
"""

MOVE_CURRENT = """project/
├── old.py                                 # Existing implementation
└── obsolete.txt                           # Obsolete notes"""
MOVE_PLANNED = """project/
├── new.py                                 # [move from old.py] Same implementation
└── obsolete.txt                           # [remove] Superseded notes stay visible"""
MOVE_EXAMPLE = DIRECTORY_EXAMPLE.replace(CURRENT_TREE, MOVE_CURRENT).replace(PLANNED_TREE, MOVE_PLANNED).replace(
    "source.py owns the call; helper.py owns the operation. Neither is generated.",
    "new.py inherits old.py's ownership; obsolete.txt is removed without replacement.",
)
NO_CHANGE_EXAMPLE = DIRECTORY_EXAMPLE.replace(
    "inspected fixture revision abc123.", "fixture revision abc123; this is a review-only decision, so no files change.",
).replace(CURRENT_TREE, "No directory or file changes.").replace(
    PLANNED_TREE, "No directory or file changes.",
).replace(
    "source.py owns the call; helper.py owns the operation. Neither is generated.", "No changed source or output ownership.",
)
UNKNOWN_EXAMPLE = DIRECTORY_EXAMPLE.replace(
    "inspected fixture revision abc123.", "Unknown: the operator has not supplied a repository snapshot.",
).replace(CURRENT_TREE, "Unknown: no observed directory tree is available.").replace(
    PLANNED_TREE,
    "project/\n└── source.py                              # [check] Verify existence and ownership before editing",
).replace(
    "source.py owns the call; helper.py owns the operation. Neither is generated.",
    "Confirm source.py's owner before editing; no generated output is assumed.",
)
DIRECTORY_EXAMPLES = (DIRECTORY_EXAMPLE, MOVE_EXAMPLE, NO_CHANGE_EXAMPLE, UNKNOWN_EXAMPLE)

# A single fully populated brief. Repetition markers remain the existing inert notation.
PLAN_VALUES: dict[str, str | int] = {
    "PLAN_TITLE": "Extract a shared operation",
    "TIMESTAMP": "2026-09-07T13:00:00Z",
    "CLASSIFICATION": "PUBLIC",
    "OPERATING_ENVIRONMENT": "A local Python project with one source file.",
    "CURRENT_STATE": "The same operation is repeated in source.py.",
    "OBSTACLE": "Behaviour drift",
    "OBSTACLE_ASSESSMENT": "Moving the operation could change its result; compare fixed examples.",
    "HIGHER_INTENT": "Keep one owner for the shared operation.",
    "ADJACENT_EFFORTS": "No competing change is active in the fixture.",
    "SUPPORTING_RESOURCES": "Source, fixed examples and a local interpreter.",
    "ASSUMPTION": "The supplied abc123 snapshot is the agreed input.",
    "CONSTRAINT": "Preserve the existing input/output contract.",
    "LIMITATION": "This is an inert planning specimen, not executed project work.",
    "MISSION_STATEMENT": "The author extracts the shared operation in the fixture project during this change to remove duplication.",
    "TASK": "Extract and verify the shared operation at abc123.",
    "PURPOSE": "Keep fixes in one implementation.",
    "END_STATE": "source.py uses helper.py without changing behaviour.",
    "DIRECTORY_BASELINE": "inspected fixture revision abc123.",
    "DIRECTORY_CURRENT": CURRENT_TREE,
    "DIRECTORY_PLANNED": PLANNED_TREE,
    "DIRECTORY_OWNERSHIP": "source.py owns the call; helper.py owns the operation. Neither is generated.",
    "DIRECTORY_VERIFICATION": "compare the actual changed paths and inspected diff with this view.",
    "COMPARISON_ID": "E01",
    "COMPARISON_NAME": "One shared operation",
    "COMPARISON_AUTHORITY": "required",
    "COMPARISON_CURRENT": "Repeated operation bodies in source.py.",
    "COMPARISON_DESIRED": "One helper.py implementation with unchanged results.",
    "COMPARISON_ACCEPTANCE": "Both call sites return the same fixed examples.",
    "LEADERS_INTENT": "Preserve behaviour and make ownership clear.",
    "CONCEPT_OF_OPERATIONS": "Read the source, extract the operation and verify both callers.",
    "PHASE_NUMBER": 1,
    "PHASE_NAME": "Extract the operation",
    "PHASE_OBJECTIVE": "Remove duplication without changing behaviour.",
    "PHASE_TASK": "P01.01 Extract the helper and verify both callers.",
    "PHASE_SUCCESS_CRITERIA": "E01 passes and the final directory view matches the diff.",
    "TRANSITION_TRIGGER": "The reviewed change is ready for operator approval.",
    "TIMELINE": "One approved local change.",
    "BOUNDARIES": "Only the two illustrated source files.",
    "OPERATING_GUIDELINES": "Inspect and preserve the public contract.",
    "RISK_MITIGATION": "Keep independent expected results for both callers.",
    "CONTINGENCY_CONDITION": "a result changes",
    "CONTINGENCY_ACTION": "correct the implementation and recheck both callers.",
    "RESOURCE_NAME": "Local source snapshot",
    "RESOURCE_QUANTITY": "One",
    "RESOURCE_SOURCE": "The fixture operator",
    "RESOURCE_STATUS": "AVAILABLE",
    "SUPPLY_PLAN": "Use the supplied source and existing interpreter.",
    "TRANSPORTATION_PLAN": "Return changed files to the operator.",
    "SUSTAINMENT_PLAN": "Keep one helper and fixed regression examples.",
    "ROLLBACK_PLAN": "Correct with a new change; preserve history.",
    "PRIMARY_LEAD": "Operator: scope and publication authority.",
    "SUCCESSOR_LEAD": "Author: implementation and evidence.",
    "CHANNEL_NAME": "Review",
    "CHANNEL_MEDIUM": "Versioned plan",
    "CHANNEL_PURPOSE": "Record scope and observed checks.",
    "CHANNEL_CADENCE": "At phase completion.",
    "REPORTING_REQUIREMENT": "Distinguish actual results from this inert specimen.",
    "DECISION_TYPE": "Accept the change",
    "DECISION_AUTHORITY": "Operator",
    "ESCALATION_AUTHORITY": "Operator for scope changes.",
}
