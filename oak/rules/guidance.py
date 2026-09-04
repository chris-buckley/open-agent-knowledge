"""Compact ordered guidance for mapping source knowledge into OAK."""

from oak.rules.model import GuidanceRule

AUTHORING_GUIDANCE = (
    GuidanceRule(
        "treat-context",
        "Treat the complete supplied host context as the source, regardless of modality.",
    ),
    GuidanceRule(
        "map-instructions",
        "Map directives, policies, interpretation rules, and required behaviour to instructions.",
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
        "map-state",
        "Map values that persist and can change across arrivals to state.",
    ),
    GuidanceRule(
        "map-triggers",
        "Map outside events, receive sources, state guards, and selected work to triggers.",
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
        "Check the draft against the supplied grammar, example, and every stated OAK contract.",
    ),
    GuidanceRule(
        "write-document",
        "Produce exactly one valid OAK document.",
    ),
    GuidanceRule(
        "emit-document",
        "Emit the final OAK document as the sole response.",
    ),
)

__all__ = ["AUTHORING_GUIDANCE"]
