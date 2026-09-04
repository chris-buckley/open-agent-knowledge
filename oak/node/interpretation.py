"""Built-in OAK interpretation instructions shared by parsing and rendering."""

from oak.node.parts.interfaces import INTERFACE_FLOWS

REFERENCE_INSTRUCTION = (
    "$ reads a value; local targets start with their part; relative targets "
    "start with a document path; a bare $NAME is local to the running process; "
    "SET, CALL, EMIT, and trigger facts omit $."
)

PART_INSTRUCTIONS = (
    ("constants", "Constants hold values that do not change while the knowledge runs."),
    ("schemas", "Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot."),
    ("state", "State holds values that persist and can change while processes run."),
    ("triggers", "Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work."),
    ("processes", "Each process is the exact ordered way to do one task; follow its typed steps from top to bottom."),
)

CONTROL_INSTRUCTION = (
    "Conditions are typed trees; ALL, ANY, and NOT compose comparisons; "
    "ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN."
)

CONTRACT_INSTRUCTION = (
    "Process input schemas seed local bindings, process output schemas validate successful outputs, "
    "and CALL binds inputs and promotes declared outputs."
)

ACT_SCHEMA_INSTRUCTION = (
    "ACT input and output schemas validate resolved inputs before invocation "
    "and produced outputs before promotion."
)

TRIGGER_SEED_INSTRUCTION = (
    "Event-backed trigger seeds fill the selected process input schema; "
    "each seeded value validates before the process runs."
)

TRIGGER_SOURCE_INSTRUCTION = (
    "A source-backed trigger supplies the received instance as the selected process input."
)

INFERRED_EMIT_INSTRUCTION = (
    "EMIT without bindings fills the target schema from same-named visible process bindings."
)

INTERFACE_DESCRIPTION_INSTRUCTION = (
    "Text after `: ` states boundary meaning absent from the interface schema."
)

TYPED_ENTRY_INSTRUCTION = (
    "AS binds one constant or state value to one schema placeholder; "
    "the value must satisfy that placeholder at resolution and before each state write commits."
)

BUILT_IN_INSTRUCTIONS = frozenset(
    (
        REFERENCE_INSTRUCTION,
        CONTROL_INSTRUCTION,
        CONTRACT_INSTRUCTION,
        ACT_SCHEMA_INSTRUCTION,
        TRIGGER_SEED_INSTRUCTION,
        TRIGGER_SOURCE_INSTRUCTION,
        INFERRED_EMIT_INSTRUCTION,
        INTERFACE_DESCRIPTION_INSTRUCTION,
        TYPED_ENTRY_INSTRUCTION,
        *(definition.instruction for definition in INTERFACE_FLOWS),
        *(text for _field, text in PART_INSTRUCTIONS),
    )
)


__all__ = [
    "ACT_SCHEMA_INSTRUCTION",
    "BUILT_IN_INSTRUCTIONS",
    "CONTRACT_INSTRUCTION",
    "CONTROL_INSTRUCTION",
    "INFERRED_EMIT_INSTRUCTION",
    "INTERFACE_DESCRIPTION_INSTRUCTION",
    "PART_INSTRUCTIONS",
    "REFERENCE_INSTRUCTION",
    "TRIGGER_SEED_INSTRUCTION",
    "TRIGGER_SOURCE_INSTRUCTION",
    "TYPED_ENTRY_INSTRUCTION",
]
