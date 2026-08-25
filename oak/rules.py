"""Stable authoring rules shared by validation and generated outputs."""

from dataclasses import dataclass

from pydantic_core import PydanticCustomError


@dataclass(frozen=True, slots=True)
class AuthoringRule:
    """One stable validator instruction."""

    code: str
    instruction: str
    models: tuple[str, ...] = ()


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
    AuthoringRule("dead_process_branch", "Remove a process branch that cannot run.", ("If",)),
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


def rule_error(
    code: str,
    message: str,
    context: dict[str, object] | None = None,
) -> PydanticCustomError:
    """Return one registered Pydantic authoring error."""
    if code not in RULES_BY_CODE:
        raise RuntimeError(f"unregistered OAK rule {code}")
    return PydanticCustomError(code, message, context or {})
