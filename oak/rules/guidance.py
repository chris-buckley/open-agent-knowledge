"""Ordered instructions for mapping source knowledge into OAK."""

from oak.rules.model import GuidanceRule

SOURCE_GUIDANCE = (
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
        "Map reusable information shapes and output contracts to schemas.",
    ),
    GuidanceRule(
        "map-state",
        "Map values that can change while the knowledge runs to state.",
    ),
    GuidanceRule(
        "map-triggers",
        "Map arrival events, receive sources, state guards, and selected processes to triggers.",
    ),
    GuidanceRule(
        "map-processes",
        "Map ordered ways to perform tasks to processes.",
    ),
    GuidanceRule(
        "map-interfaces",
        "Map verifiable document-boundary crossings to interfaces.",
    ),
    GuidanceRule(
        "omit-part",
        "Omit a part when the source provides no justified entry.",
    ),
    GuidanceRule(
        "avoid-invention",
        "Do not invent state, triggers, processes, interfaces, or relative paths.",
    ),
    GuidanceRule(
        "write-document",
        "Write exactly one valid OAK document containing one node.",
    ),
    GuidanceRule(
        "emit-document",
        "Emit the final OAK document as the sole response.",
    ),
)

ENTRY_ID_GUIDANCE = (
    GuidanceRule(
        "allow-brevity",
        "Do not require a minimum word count for an entry id.",
    ),
    GuidanceRule(
        "form-process",
        "Use `<verb>-<object>[-<outcome-or-context>]` for process ids.",
    ),
    GuidanceRule(
        "start-process",
        "Start each process id with an exact base-form action verb.",
    ),
    GuidanceRule(
        "form-instruction",
        "Use `<verb>-<object>` for instruction ids.",
    ),
    GuidanceRule(
        "name-structure",
        "Use noun phrases for constant, schema, state, and interface ids.",
    ),
    GuidanceRule(
        "phrase-trigger",
        "Use circumstance phrases for trigger ids.",
    ),
)

NAMING_GUIDANCE = (
    GuidanceRule(
        "name-result",
        "Name each reusable process for what it establishes, not how it works.",
    ),
    GuidanceRule(
        "name-queryprocess",
        "Name each query process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<query-action>_<object>` and a non-mutating action (is|has|find|read) (e.g. `find-document` and `Find document`).",
    ),
    GuidanceRule(
        "name-commandprocess",
        "Name each command process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<command-action>_<object>` and expose the state change (create|write|publish|delete) (e.g. `publish-report` and `Publish report`).",
    ),
    GuidanceRule(
        "name-combinedprocess",
        "Name each combined process with matching `SlugId` and two-word `ProcessName` forms that place its mutating action first and use the semantic structure `<command-action>_<object>[_if_<condition>]` (e.g. `create-folder-if-missing` and `Create folder-if-missing`).",
    ),
    GuidanceRule(
        "name-verificationprocess",
        "Name each verification process with matching `SlugId` and `ProcessName` forms that use the semantic structure `(test|validate|prove)_<object>[_<condition>][_<outcome>]` (e.g. `validate-candidate` and `Validate candidate`).",
    ),
    GuidanceRule(
        "define-logprocess",
        "Define each required log event as a reusable process with the semantic structure `log_<object>_<event>` (e.g. `log-artifact-published` and `Log artifact-published`).",
    ),
    GuidanceRule(
        "perform-logging",
        "Perform interpreter-native logging with plain `ACT`.",
    ),
    GuidanceRule(
        "select-logtool",
        "Use `ACT TOOL` only when one exact registered logging tool must perform the logging operation.",
    ),
    GuidanceRule(
        "reuse-logging",
        "Reuse a logging process from other processes with `CALL`.",
    ),
    GuidanceRule(
        "name-value",
        "Name each value with the semantic structure `<role>_<object>_<kind-or-unit>` using a `SlugId` for a constant or state entry and a `Placeholder` for a schema or process binding (e.g. `source-document-file` and `SOURCE_DOCUMENT_FILE`).",
    ),
    GuidanceRule(
        "name-collection",
        "Name each collection with the semantic structure `<contents>_<shape>` (e.g. `report-names` as a `SlugId` or `REPORT_NAMES` as a `Placeholder`).",
    ),
    GuidanceRule(
        "name-boolean",
        "Name each boolean as a positive condition or control (e.g. `is-ready` as a `SlugId` or `IS_READY` as a `Placeholder`).",
    ),
    GuidanceRule(
        "name-quantity",
        "Name each quantity with the semantic structure `[<context>_]<quantity>_<unit>` (e.g. `poll-interval-seconds` as a `SlugId` or `POLL_INTERVAL_SECONDS` as a `Placeholder`).",
    ),
    GuidanceRule(
        "name-identifier",
        "Name each identifier value with the semantic structure `<object>_id` (e.g. `document-id` as a `SlugId` or `DOCUMENT_ID` as a `Placeholder`).",
    ),
    GuidanceRule(
        "name-mapping",
        "Name each mapping with the semantic structure `<key>_to_<value>` (e.g. `filename-to-document-id` as a `SlugId` or `FILENAME_TO_DOCUMENT_ID` as a `Placeholder`).",
    ),
    GuidanceRule(
        "represent-lifetime",
        "Represent each variable-like value by its source and lifetime: `CONSTANT` for fixed values, `STATE` for mutable values, a process binding for local immutable values, and an `INTERFACE` binding for boundary values (e.g. `$constant.max-retries`, `$state.current-candidate`, or `$CANDIDATE`).",
    ),
    GuidanceRule(
        "reuse-domain",
        "Use the shortest unambiguous name that states purpose or result and reuses one exact domain noun across every part, including verification processes (e.g. schema `candidate`, state `current-candidate`, process `validate-candidate`, and interface `verified-candidate-output`; do not rename `candidate` as `option` or `proposal`).",
    ),
    GuidanceRule(
        "replace-generics",
        "Replace generic nouns and vague process verbs with exact domain terms that state purpose or action (e.g. replace (data|item|result|value|config|response|path) with (candidate|verification-step|verified-candidate|retry-limit|validation-rules|review-feedback|source-document-file), and replace (handle|process|manage|do) with (validate|publish|archive|verify)).",
    ),
)

DECOMPOSITION_GUIDANCE = (
    GuidanceRule(
        "decompose-phases",
        "Decompose each multi-phase task into one process per phase.",
    ),
    GuidanceRule(
        "contract-phase",
        "Give each phase process one input schema and one output schema.",
    ),
    GuidanceRule(
        "name-contractschema",
        "Name each contract schema as the information shape it carries.",
    ),
    GuidanceRule(
        "orchestrate-trigger",
        "Keep each multi-phase trigger-selected process an orchestrator of calls and emits.",
    ),
    GuidanceRule(
        "restrict-phaseemit",
        "Do not emit from a phase process.",
    ),
    GuidanceRule(
        "restrict-state",
        "Keep pipeline values in call contracts; use state only for values that persist between arrivals.",
    ),
)

ACT_GUIDANCE = (
    GuidanceRule(
        "treat-default",
        "Treat plain `ACT` as the default action form.",
    ),
    GuidanceRule(
        "use-native",
        "Use plain `ACT` when the interpreter performs the instruction with its native capabilities.",
    ),
    GuidanceRule(
        "interpret-missingtool",
        "No `ACT.tool` means interpreter-native work.",
    ),
    GuidanceRule(
        "use-exacttool",
        "Use `ACT TOOL` only when one exact registered tool must perform the instruction.",
    ),
    GuidanceRule(
        "omit-tool",
        "Omit `ACT TOOL` when the interpreter may choose how to perform the instruction.",
    ),
    GuidanceRule(
        "copy-tool",
        "Copy each tool name from the supplied exact tool registry.",
    ),
    GuidanceRule(
        "preserve-tool",
        "Preserve each tool name verbatim.",
    ),
    GuidanceRule(
        "avoid-toolguess",
        "Do not invent, normalize, or infer a tool name.",
    ),
    GuidanceRule(
        "use-call",
        "Use `CALL` to run another OAK process.",
    ),
    GuidanceRule(
        "avoid-toolcall",
        "Do not use `ACT TOOL` to run an OAK process.",
    ),
    GuidanceRule(
        "keep-implementation",
        "Keep tool implementations, handlers, transport, credentials, server configuration, and aliases outside the OAK document.",
    ),
    GuidanceRule(
        "prefer-tool",
        "Prefer `ACT TOOL` when stable tool selection, contract validation, auditability, or controlled side effects matter.",
    ),
    GuidanceRule(
        "fix-registry",
        "An exact tool name fixes which registry entry is selected.",
    ),
    GuidanceRule(
        "allow-variance",
        "An exact tool name does not guarantee deterministic output.",
    ),
    GuidanceRule(
        "require-determinism",
        "Require the selected tool itself to provide deterministic behaviour when deterministic output is required.",
    ),
    GuidanceRule(
        "expose-native",
        "Expose plain `ACT` as `ACT(instruction, ...)` in direct Python authoring.",
    ),
    GuidanceRule(
        "expose-tool",
        "Expose named `ACT TOOL` as `ACT.tool(name, instruction, ...)` in direct Python authoring.",
    ),
    GuidanceRule(
        "accept-schemas",
        "Accept `input` and `output` schema targets in both authoring helpers.",
    ),
    GuidanceRule(
        "return-act",
        "Make `ACT(...)` and `ACT.tool(...)` return the existing `Act` model.",
    ),
    GuidanceRule(
        "keep-kind",
        "Keep `ACT(...)` and `ACT.tool(...)` as one `act` process step kind.",
    ),
    GuidanceRule(
        "omit-infer",
        "Do not expose `ACT.infer`.",
    ),
    GuidanceRule(
        "omit-use",
        "Do not expose `ACT.use`.",
    ),
    GuidanceRule(
        "avoid-helper",
        "Add no second helper for interpreter-native work.",
    ),
)

TYPED_BINDING_GUIDANCE = (
    GuidanceRule(
        "bind-entry",
        "Bind a constant or state value to one schema placeholder with `AS` when a schema constrains it.",
    ),
    GuidanceRule(
        "type-act",
        "Give an act input and output schema targets when its values must validate at the action boundary.",
    ),
    GuidanceRule(
        "seed-trigger",
        "Seed an event-selected typed process through trigger seeds, one binding per input schema placeholder.",
    ),
)

DELEGATION_GUIDANCE = (
    GuidanceRule(
        "model-worker",
        "Model each subagent as one worker OAK document with one RECEIVES interface and one EMITS interface.",
    ),
    GuidanceRule(
        "treat-contracts",
        "Treat the worker receive schema as the request contract and its emit schema as the result contract.",
    ),
    GuidanceRule(
        "type-dispatch",
        "Type each dispatch process with relative targets to the worker request and result schemas as its input and output schemas.",
    ),
    GuidanceRule(
        "dispatch-worker",
        "Dispatch each worker inside its dispatch process with one exact tool name from the supplied registry.",
    ),
    GuidanceRule(
        "prefer-portable-name",
        "Prefer one registered portable `agent.<worker>` contract when the host permits registration.",
    ),
    GuidanceRule(
        "use-native-name",
        "Use the native runner name verbatim when the host does not permit registration.",
    ),
    GuidanceRule(
        "mirror-contract",
        "Give each agent tool contract the worker request placeholders as inputs and the worker result placeholders as outputs.",
    ),
    GuidanceRule(
        "type-dispatch-act",
        "Give each agent dispatch act and contract the worker request and result schemas as input and output targets.",
    ),
    GuidanceRule(
        "keep-invocation",
        "Keep agent invocation, model selection, and transport in the host registry, outside the OAK document.",
    ),
    GuidanceRule(
        "restrict-workers",
        "Treat the supplied registry as the worker allowlist.",
    ),
    GuidanceRule(
        "parallelize-workers",
        "Run parallel workers as `PAR` children, one exact agent tool act per worker.",
    ),
    GuidanceRule(
        "limit-depth",
        "Keep delegation depth at one: each worker returns its result to the coordinator and dispatches no workers.",
    ),
    GuidanceRule(
        "avoid-worker-call",
        "Do not dispatch a worker with `CALL`.",
    ),
    GuidanceRule(
        "compose-call",
        "`CALL` composes processes inside one interpreter and one transaction.",
    ),
    GuidanceRule(
        "separate-interpreter",
        "Treat each dispatch as separate-interpreter host work, not as running an OAK process with `ACT TOOL`.",
    ),
    GuidanceRule(
        "treat-worker-effects",
        "Treat committed worker effects as external tool effects that the coordinator transaction cannot roll back.",
    ),
)

AUTHORING_GUIDANCE = (
    *SOURCE_GUIDANCE,
    *ENTRY_ID_GUIDANCE,
    *NAMING_GUIDANCE,
    *DECOMPOSITION_GUIDANCE,
    *ACT_GUIDANCE,
    *TYPED_BINDING_GUIDANCE,
    *DELEGATION_GUIDANCE,
)

__all__ = [
    "ACT_GUIDANCE",
    "AUTHORING_GUIDANCE",
    "DECOMPOSITION_GUIDANCE",
    "DELEGATION_GUIDANCE",
    "ENTRY_ID_GUIDANCE",
    "NAMING_GUIDANCE",
    "SOURCE_GUIDANCE",
    "TYPED_BINDING_GUIDANCE",
]
