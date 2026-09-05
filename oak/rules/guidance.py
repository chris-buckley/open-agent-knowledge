"""Compact ordered guidance for mapping source knowledge into OAK."""

from oak.rules.model import GuidanceRule

AUTHORING_GUIDANCE = (
    GuidanceRule(
        "treat-context",
        "Treat the complete supplied host context as the source, regardless of modality.",
    ),
    GuidanceRule(
        "map-instructions",
        "Author instructions last; include only meaning that schemas, constants, state, interfaces, triggers, and processes cannot express.",
    ),
    GuidanceRule(
        "map-constants",
        "Map stable values needed during use to constants.",
    ),
    GuidanceRule(
        "map-schemas",
        "Map reusable information shapes and contracts to schemas.",
    ),
    GuidanceRule(
        "choose-schema-shape",
        "Choose schema templates by information relationships: tables for comparison, outlines for hierarchy, sections for explanation, and fenced blocks for code; use lists only for list-shaped information.",
    ),
    GuidanceRule(
        "preserve-schema-shape",
        "Preserve requested layouts; the demonstrated shapes are examples, not a closed catalogue or a reason to force every schema into labelled fields.",
    ),
    GuidanceRule(
        "separate-template-instance",
        "Keep templates and WHERE constraints in schema definitions; populated outputs fill its slots rather than copying the schema definition.",
    ),
    GuidanceRule(
        "respect-schema-cardinality",
        "A binding supplies one value per placeholder; repeated names reuse that value, and an ellipsis alone does not create independently typed rows or sections.",
    ),
    GuidanceRule(
        "map-state",
        "Map values that persist and can change across arrivals to state.",
    ),
    GuidanceRule(
        "map-triggers",
        "Map outside events, receive sources, state guards, and selected work to triggers.",
    ),
    GuidanceRule(
        "declare-triggers",
        "Declare each trigger once with named fields; omit unused fields and keep source payloads separate from event seeds.",
    ),
    GuidanceRule(
        "compose-conditions",
        "Use the same explicit recursive condition structure for branches, loop conditions, assertions, and guards; preserve child order and bounded-loop failures.",
    ),
    GuidanceRule(
        "separate-layout",
        "Use delimiter continuation for long expressions and indentation for ordered action suites; follow the shared grammar instead of inventing another layout dialect.",
    ),
    GuidanceRule(
        "map-processes",
        "Map ordered local work to processes.",
    ),
    GuidanceRule(
        "map-interfaces",
        "Map complete document-boundary crossings to one-way interfaces.",
    ),
    GuidanceRule(
        "omit-unjustified",
        "Omit every part and entry that the source does not justify.",
    ),
    GuidanceRule(
        "avoid-invention",
        "Do not invent state, triggers, processes, interfaces, tools, or relative paths.",
    ),
    GuidanceRule(
        "preserve-node",
        "Write one idless node using only the seven parts in canonical order.",
    ),
    GuidanceRule(
        "separate-lifetimes",
        "Use constants for fixed values, state for values across arrivals, process bindings for local values, and interfaces for boundary instances.",
    ),
    GuidanceRule(
        "reuse-domain",
        "Use the shortest unambiguous names and reuse one exact domain noun across parts.",
    ),
    GuidanceRule(
        "name-process",
        "Start each process id with an exact base-form action verb and name the result it establishes.",
    ),
    GuidanceRule(
        "contract-work",
        "Give reusable process phases input and output schemas when their values need contracts.",
    ),
    GuidanceRule(
        "compose-work",
        "Keep multi-phase entry processes as orchestrators that compose reusable processes with `CALL`.",
    ),
    GuidanceRule(
        "keep-local-values",
        "Keep pipeline values in process bindings and use state only for values that must survive an arrival.",
    ),
    GuidanceRule(
        "route-receive",
        "Route each receive interface through one source-backed trigger into a process with the same resolved input schema.",
    ),
    GuidanceRule(
        "use-native-act",
        "Use plain `ACT` when the interpreter performs the work with native capabilities.",
    ),
    GuidanceRule(
        "use-exact-tool",
        "Use `ACT TOOL` only for one exact tool name copied from the supplied registry.",
    ),
    GuidanceRule(
        "keep-host-boundary",
        "Keep tool implementations, handlers, transport, credentials, model selection, and server configuration in the host.",
    ),
    GuidanceRule(
        "parallelize-tools",
        "Use `PAR` and `JOIN` only for independent exact tool actions.",
    ),
    GuidanceRule(
        "delegate-document",
        "Model a delegated agent as its own typed OAK document and dispatch it through an exact host tool contract.",
    ),
    GuidanceRule(
        "bind-values",
        "Bind constants, state, processes, actions, and interfaces to schemas where values must validate.",
    ),
    GuidanceRule(
        "emit-complete",
        "Emit one complete schema instance and use inferred `EMIT` only when same-named visible bindings satisfy it.",
    ),
    GuidanceRule(
        "validate-draft",
        "Review the draft against the grammar, populated examples, and OAK contracts; run programmatic validation only when requested and report whether it actually ran.",
    ),
    GuidanceRule(
        "write-document",
        "Produce exactly one valid OAK document.",
    ),
    GuidanceRule(
        "emit-document",
        "Return the final OAK document and, when validation is requested, an honest validation result outside the authored document.",
    ),
)

__all__ = ["AUTHORING_GUIDANCE"]
