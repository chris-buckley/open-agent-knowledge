"""Stable authoring rules shared by validation and generated outputs."""

from dataclasses import dataclass

from pydantic_core import PydanticCustomError


@dataclass(frozen=True, slots=True)
class AuthoringRule:
    """One stable validator instruction."""

    code: str
    instruction: str
    models: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GuidanceRule:
    """One generated instruction for authoring OAK."""

    id: str
    instruction: str


_RULES = (
    AuthoringRule("duplicate_id", "Use each entry id once in one OAK document.", ("Node",)),
    AuthoringRule("missing_reference_target", "Target an entry that exists in the current OAK document.", ("Node",)),
    AuthoringRule("wrong_reference_target_type", "Target the part required by the typed reference field.", ("Node",)),
    AuthoringRule("invalid_document_path", "Use a relative POSIX document path ending in .oak.md without a scheme, query, or extra fragment.", ("TargetPath",)),
    AuthoringRule("external_reference_without_source", "Supply the referencing document path before resolving a relative target.", ("TargetPath",)),
    AuthoringRule("external_document_missing", "Make every reachable relative document available through the explicit loader.", ("TargetPath",)),
    AuthoringRule("external_entry_missing", "Make every resolved fragment target exist in its document.", ("TargetPath",)),
    AuthoringRule("external_state_reference", "Read and write state only in the active OAK document.", ("StateValue", "Set")),
    AuthoringRule("external_interface_reference", "Read and emit interfaces only in the active OAK document.", ("InterfaceValue", "Emit")),
    AuthoringRule("cross_document_process_call_cycle", "Keep the resolved process call graph acyclic.", ("Call",)),
    AuthoringRule("interface_direction_mismatch", "Read only in or inout interfaces and emit only out or inout interfaces.", ("InterfaceValue", "Emit")),
    AuthoringRule("unknown_interface_placeholder", "Read a placeholder present in the interface schema.", ("InterfaceValue",)),
    AuthoringRule("emit_schema_binding_mismatch", "Bind every interface schema placeholder exactly once when emitting.", ("Emit",)),
    AuthoringRule("invalid_static_schema_binding", "Make every statically known emission satisfy its interface schema.", ("Emit",)),
    AuthoringRule("process_call_cycle", "Keep the local process call graph acyclic.", ("Call",)),
    AuthoringRule("call_contract_mismatch", "Match each call's inputs and outputs to the called process schemas.", ("Call",)),
    AuthoringRule("process_output_binding_mismatch", "Make every process output schema placeholder visible after successful completion.", ("Process",)),
    AuthoringRule("trigger_process_input", "Select only a process without an input schema from a trigger.", ("Trigger",)),
    AuthoringRule("dead_process_branch", "Remove a process branch that cannot run.", ("If", "While")),
    AuthoringRule("unreachable_process_step", "Remove a process step after a path that always fails.", ("Process",)),
    AuthoringRule("condition_group_too_short", "Give each ALL or ANY condition at least two children.", ("All", "Any")),
    AuthoringRule("ordered_comparison_type_mismatch", "Order only two numbers or two strings without coercion.", ("Compare",)),
    AuthoringRule("trigger_guard_missing_state", "Give every non-true trigger guard at least one state read.", ("Trigger",)),
    AuthoringRule("invalid_trigger_guard_value", "Do not read an interface or local binding in a trigger guard.", ("Trigger",)),
    AuthoringRule("overlapping_trigger_guards", "Make equal trigger WHEN values provably disjoint.", ("Trigger",)),
    AuthoringRule("assertion_always_fails", "Remove or repair an assertion that is statically false.", ("Assert",)),
    AuthoringRule("redundant_assertion", "Remove an assertion that is statically true.", ("Assert",)),
    AuthoringRule("foreach_source_not_list", "Give FOREACH a value that resolves to a JSON list.", ("Foreach",)),
    AuthoringRule("foreach_binding_redefined", "Use a new loop binding that does not shadow a visible binding.", ("Foreach",)),
    AuthoringRule("parallel_step_not_tool_act", "Put only exact named-tool acts inside PAR.", ("Par",)),
    AuthoringRule("parallel_output_collision", "Give every PAR child a distinct output binding.", ("Par",)),
    AuthoringRule("join_without_par", "Put JOIN immediately after one PAR.", ("Join",)),
    AuthoringRule("parallel_join_missing", "Follow a final PAR with JOIN.", ("Par",)),
    AuthoringRule("parallel_join_not_adjacent", "Put no step between PAR and JOIN.", ("Par", "Join")),
    AuthoringRule("unknown_tool", "Name a tool exposed by the supplied exact tool registry.", ("Act",)),
    AuthoringRule("tool_contract_mismatch", "Match a named tool's declared input and output contract.", ("Act",)),
    AuthoringRule("tool_parallelism_unknown", "Use a tool in PAR only when its supplied registry confirms parallel use.", ("Par",)),
    AuthoringRule("duplicate_act_input", "Bind each act input placeholder once.", ("Act",)),
    AuthoringRule("duplicate_act_output", "Declare each act output placeholder once.", ("Act",)),
    AuthoringRule("act_binding_overlap", "Do not use one act placeholder as both input and output.", ("Act",)),
    AuthoringRule("act_placeholder_mismatch", "Make act instruction placeholders equal its inputs and outputs.", ("Act",)),
    AuthoringRule("duplicate_emit_placeholder", "Bind each emitted placeholder once.", ("Emit",)),
    AuthoringRule("unbound_process_binding", "Read only a visible prior process-local binding.", ("Process",)),
    AuthoringRule("process_binding_redefined", "Do not redefine a visible immutable process binding.", ("Process",)),
    AuthoringRule("invalid_text_constant", "Give each TEXT constant one string value.", ("Constant",)),
    AuthoringRule("invalid_csv_constant", "Give each CSV constant one non-empty list of object rows.", ("Constant",)),
    AuthoringRule("csv_column_mismatch", "Use the same columns in every CSV row.", ("Constant",)),
    AuthoringRule("invalid_csv_cell", "Use only JSON scalar values in CSV cells.", ("Constant",)),
    AuthoringRule("missing_line_bound", "Give each lines constraint a minimum, maximum, or both.", ("Lines",)),
    AuthoringRule("invalid_line_bounds", "Keep a lines minimum at or below its maximum.", ("Lines",)),
    AuthoringRule("unresolved_where_example", "Do not give examples to a WHERE entry with placeholder-valued bounds.", ("Where",)),
    AuthoringRule("invalid_where_example", "Make every WHERE example satisfy its local constraints.", ("Where",)),
    AuthoringRule("duplicate_where_placeholder", "Define each schema placeholder once in WHERE.", ("Schema",)),
    AuthoringRule("placeholder_where_mismatch", "Make the template and WHERE placeholder sets equal.", ("Schema",)),
    AuthoringRule("unknown_constraint_placeholder", "Reference only another placeholder in the same schema.", ("Schema",)),
)

RULES = tuple(sorted(_RULES, key=lambda rule: rule.code))
RULES_BY_CODE = {rule.code: rule for rule in RULES}

SOURCE_GUIDANCE = (
    GuidanceRule("treat-context", "Treat the complete supplied host context as the source, regardless of modality."),
    GuidanceRule("map-instructions", "Map directives, policies, interpretation rules, and required behaviour to instructions."),
    GuidanceRule("map-constants", "Map stable values needed during use to constants."),
    GuidanceRule("map-schemas", "Map reusable information shapes and output contracts to schemas."),
    GuidanceRule("map-state", "Map values that can change while the knowledge runs to state."),
    GuidanceRule("map-triggers", "Map arrival reasons, state guards, and selected processes to triggers."),
    GuidanceRule("map-processes", "Map ordered ways to perform tasks to processes."),
    GuidanceRule("map-interfaces", "Map verifiable document-boundary crossings to interfaces."),
    GuidanceRule("leave-part", "Leave a part empty when the source provides no justified entry."),
    GuidanceRule("avoid-invention", "Do not invent state, triggers, processes, interfaces, or relative paths."),
    GuidanceRule("write-document", "Write exactly one valid OAK document containing one node."),
    GuidanceRule("emit-document", "Emit the final OAK document as the sole response."),
)

ENTRY_ID_GUIDANCE = (
    GuidanceRule("allow-brevity", "Do not require a minimum word count for an entry id."),
    GuidanceRule("form-process", "Use `<verb>-<object>[-<outcome-or-context>]` for process ids."),
    GuidanceRule("start-process", "Start each process id with an exact base-form action verb."),
    GuidanceRule("form-instruction", "Use `<verb>-<object>` for instruction ids."),
    GuidanceRule("name-structure", "Use noun phrases for constant, schema, state, and interface ids."),
    GuidanceRule("phrase-trigger", "Use circumstance phrases for trigger ids."),
)

NAMING_GUIDANCE = (
    GuidanceRule("name-result", "Name each reusable process for what it establishes, not how it works."),
    GuidanceRule("name-queryprocess", "Name each query process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<query-action>_<object>` and a non-mutating action (is|has|find|read) (e.g. `find-document` and `Find document`)."),
    GuidanceRule("name-commandprocess", "Name each command process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<command-action>_<object>` and expose the state change (create|write|publish|delete) (e.g. `publish-report` and `Publish report`)."),
    GuidanceRule("name-combinedprocess", "Name each combined process with matching `SlugId` and two-word `ProcessName` forms that place its mutating action first and use the semantic structure `<command-action>_<object>[_if_<condition>]` (e.g. `create-folder-if-missing` and `Create folder-if-missing`)."),
    GuidanceRule("name-verificationprocess", "Name each verification process with matching `SlugId` and `ProcessName` forms that use the semantic structure `(test|validate|prove)_<object>[_<condition>][_<outcome>]` (e.g. `validate-candidate` and `Validate candidate`)."),
    GuidanceRule("define-logprocess", "Define each required log event as a reusable process with the semantic structure `log_<object>_<event>` (e.g. `log-artifact-published` and `Log artifact-published`)."),
    GuidanceRule("perform-logging", "Perform interpreter-native logging with plain `ACT`."),
    GuidanceRule("select-logtool", "Use `ACT TOOL` only when one exact registered logging tool must perform the logging operation."),
    GuidanceRule("reuse-logging", "Reuse a logging process from other processes with `CALL`."),
    GuidanceRule("name-value", "Name each value with the semantic structure `<role>_<object>_<kind-or-unit>` using a `SlugId` for a constant or state entry and a `Placeholder` for a schema or process binding (e.g. `source-document-file` and `SOURCE_DOCUMENT_FILE`)."),
    GuidanceRule("name-collection", "Name each collection with the semantic structure `<contents>_<shape>` (e.g. `report-names` as a `SlugId` or `REPORT_NAMES` as a `Placeholder`)."),
    GuidanceRule("name-boolean", "Name each boolean as a positive condition or control (e.g. `is-ready` as a `SlugId` or `IS_READY` as a `Placeholder`)."),
    GuidanceRule("name-quantity", "Name each quantity with the semantic structure `[<context>_]<quantity>_<unit>` (e.g. `poll-interval-seconds` as a `SlugId` or `POLL_INTERVAL_SECONDS` as a `Placeholder`)."),
    GuidanceRule("name-identifier", "Name each identifier value with the semantic structure `<object>_id` (e.g. `document-id` as a `SlugId` or `DOCUMENT_ID` as a `Placeholder`)."),
    GuidanceRule("name-mapping", "Name each mapping with the semantic structure `<key>_to_<value>` (e.g. `filename-to-document-id` as a `SlugId` or `FILENAME_TO_DOCUMENT_ID` as a `Placeholder`)."),
    GuidanceRule("represent-lifetime", "Represent each variable-like value by its source and lifetime: `CONSTANT` for fixed values, `STATE` for mutable values, a process binding for local immutable values, and an `INTERFACE` binding for boundary values (e.g. `$constant.max-retries`, `$state.current-candidate`, or `$CANDIDATE`)."),
    GuidanceRule("reuse-domain", "Use the shortest unambiguous name that states purpose or result and reuses one exact domain noun across every part, including verification processes (e.g. schema `candidate`, state `current-candidate`, process `validate-candidate`, and interface `verified-candidate-output`; do not rename `candidate` as `option` or `proposal`)."),
    GuidanceRule("replace-generics", "Replace generic nouns and vague process verbs with exact domain terms that state purpose or action (e.g. replace (data|item|result|value|config|response|path) with (candidate|verification-step|verified-candidate|retry-limit|validation-rules|review-feedback|source-document-file), and replace (handle|process|manage|do) with (validate|publish|archive|verify))."),
)

DECOMPOSITION_GUIDANCE = (
    GuidanceRule("decompose-phases", "Decompose each multi-phase task into one process per phase."),
    GuidanceRule("contract-phase", "Give each phase process one input schema and one output schema."),
    GuidanceRule("name-contractschema", "Name each contract schema as the information shape it carries."),
    GuidanceRule("orchestrate-trigger", "Keep each trigger-selected process an orchestrator of calls and emits."),
    GuidanceRule("restrict-phaseemit", "Do not emit from a phase process."),
    GuidanceRule("restrict-state", "Keep pipeline values in call contracts; use state only for values that persist between arrivals."),
)

ACT_GUIDANCE = (
    GuidanceRule("treat-default", "Treat plain `ACT` as the default action form."),
    GuidanceRule("use-native", "Use plain `ACT` when the interpreter performs the instruction with its native capabilities."),
    GuidanceRule("interpret-missingtool", "No `ACT.tool` means interpreter-native work."),
    GuidanceRule("use-exacttool", "Use `ACT TOOL` only when one exact registered tool must perform the instruction."),
    GuidanceRule("omit-tool", "Omit `ACT TOOL` when the interpreter may choose how to perform the instruction."),
    GuidanceRule("copy-tool", "Copy each tool name from the supplied exact tool registry."),
    GuidanceRule("preserve-tool", "Preserve each tool name verbatim."),
    GuidanceRule("avoid-toolguess", "Do not invent, normalize, or infer a tool name."),
    GuidanceRule("use-call", "Use `CALL` to run another OAK process."),
    GuidanceRule("avoid-toolcall", "Do not use `ACT TOOL` to run an OAK process."),
    GuidanceRule("keep-implementation", "Keep tool implementations, handlers, transport, credentials, server configuration, and aliases outside the OAK document."),
    GuidanceRule("prefer-tool", "Prefer `ACT TOOL` when stable tool selection, contract validation, auditability, or controlled side effects matter."),
    GuidanceRule("fix-registry", "An exact tool name fixes which registry entry is selected."),
    GuidanceRule("allow-variance", "An exact tool name does not guarantee deterministic output."),
    GuidanceRule("require-determinism", "Require the selected tool itself to provide deterministic behaviour when deterministic output is required."),
    GuidanceRule("expose-native", "Expose plain `ACT` as `ACT(instruction, ...)` in direct Python authoring."),
    GuidanceRule("expose-tool", "Expose named `ACT TOOL` as `ACT.tool(name, instruction, ...)` in direct Python authoring."),
    GuidanceRule("return-act", "Make `ACT(...)` and `ACT.tool(...)` return the existing `Act` model."),
    GuidanceRule("keep-kind", "Keep `ACT(...)` and `ACT.tool(...)` as one `act` process step kind."),
    GuidanceRule("keep-syntax", "Keep the rendered OAK syntax unchanged."),
    GuidanceRule("omit-infer", "Do not expose `ACT.infer`."),
    GuidanceRule("omit-use", "Do not expose `ACT.use`."),
    GuidanceRule("avoid-helper", "Add no second helper for interpreter-native work."),
)

AUTHORING_GUIDANCE = (
    *SOURCE_GUIDANCE,
    *ENTRY_ID_GUIDANCE,
    *NAMING_GUIDANCE,
    *DECOMPOSITION_GUIDANCE,
    *ACT_GUIDANCE,
)


def rule_error(
    code: str,
    message: str,
    context: dict[str, object] | None = None,
) -> PydanticCustomError:
    """Return one registered Pydantic authoring error."""
    if code not in RULES_BY_CODE:
        raise RuntimeError(f"unregistered OAK rule {code}")
    return PydanticCustomError(code, message, context or {})
