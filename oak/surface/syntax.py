"""Shared authored-expression tokens and canonical layout policy."""

CONDITION_GROUPS = ("ALL", "ANY", "NOT")
TRIGGER_FIELDS = ("event", "source", "guard", "process", "seed")
REQUIRED_TRIGGER_FIELDS = frozenset(("event", "process"))
INDENT_WIDTH = 2
CANONICAL_WIDTH = 100

EXPRESSION_CONVENTIONS = (
    "One condition grammar serves IF, WHILE, ASSERT, and trigger guards.",
    "ALL and ANY require at least two conditions; NOT requires exactly one.",
    "Condition operators preserve the authored tree and left-to-right short-circuit order.",
    "IF and WHILE headers end with a colon; their non-empty action suites indent two spaces.",
    "ELSE aligns with its IF and immediately follows its suite, allowing blank lines.",
    "WHILE requires LIMIT and one positive decimal integer literal; exhaustion while true fails.",
    "ASSERT has a condition and optional indented MESSAGE metadata, not an action suite.",
    "Balanced parentheses continue one logical statement across physical lines without action scopes.",
    "OAK lists accept a trailing comma; JSON values retain their separate JSON grammar.",
    "Trigger fields are named, unique, and may be authored in any order; event and process are required.",
    "Canonical trigger field order is event, source, guard, process, seed; absent optionals are omitted.",
    "Do not author guard=true or an empty seed; a source-backed trigger has no seed field.",
    "A seed is an ordered named-binding list using the same value grammar as process inputs.",
    "Strings, JSON literals, and typed targets are consumed as whole tokens before separators or operators.",
    "Structural tabs, positional fields, truthiness, general calls, comments, infix aliases, and chained comparisons are invalid.",
    "Canonical expression width is 100 Unicode code points, including indentation, prefixes, and suffixes.",
    "Flat lists have no trailing comma; expanded lists put one item per line with a trailing comma and two-space indentation.",
    "Closing delimiters align with their owning line; nested lists apply the same width rule recursively.",
    "Indivisible values and prose may exceed the soft width; formatting never rewrites their contents.",
)

# These productions describe token structure. The shared reader owns tokenization;
# complete JSON values are atomic here, and logical newlines ignore open delimiters.
EXPRESSION_GRAMMAR = (
    'condition = comparison | all_condition | any_condition | not_condition ;',
    'comparison = process_value, comparison_operator, process_value ;',
    'all_condition = "ALL", "(", condition, ",", condition, { ",", condition }, [ "," ], ")" ;',
    'any_condition = "ANY", "(", condition, ",", condition, { ",", condition }, [ "," ], ")" ;',
    'not_condition = "NOT", "(", condition, [ "," ], ")" ;',
    'process_value = json_value | "$", value_target ;',
    'value_target = constant_target | local_state_target | placeholder ;',
    'constant_target = [ relative_document_path, "#" ], "constant.", slug_id ;',
    'process_target = [ relative_document_path, "#" ], "process.", slug_id ;',
    'local_state_target = "state.", slug_id ;',
    'local_interface_target = "interface.", slug_id ;',
    'value_binding = placeholder, "=", process_value ;',
    'binding_list = "(", [ value_binding, { ",", value_binding }, [ "," ] ], ")" ;',
    'output_bindings = "->", placeholder, { ",", placeholder } ;',
    'trigger_declaration = slug_id, "(", trigger_field, { ",", trigger_field }, [ "," ], ")", logical_nl ;',
    'trigger_field = "event", "=", json_string | "source", "=", local_interface_target | "guard", "=", condition | "process", "=", process_target | "seed", "=", binding_list ;',
    'if_statement = "IF", condition, ":", suite, [ "ELSE", ":", suite ] ;',
    'while_statement = "WHILE", condition, "LIMIT", positive_integer, ":", suite ;',
    'assert_statement = "ASSERT", condition, logical_nl, [ indent, "MESSAGE", json_string, logical_nl, dedent ] ;',
    'call_statement = "CALL", process_target, binding_list, [ output_bindings ], logical_nl ;',
    'emit_statement = "EMIT", local_interface_target, [ binding_list ], logical_nl ;',
    'set_statement = "SET", local_state_target, "=", process_value, logical_nl ;',
    'fail_statement = "FAIL", json_string, logical_nl ;',
    'suite = logical_nl, indent, process_step, { process_step }, dedent ;',
    'process_step = if_statement | while_statement | assert_statement | call_statement | emit_statement | set_statement | fail_statement | surface_act_native | surface_act_tool | surface_step_foreach | surface_step_par | surface_step_join ;',
    'positive_integer = ? an ASCII decimal integer literal with value greater than zero ? ;',
    'json_string = ? one double-quoted JSON string, with JSON escapes ? ;',
    'logical_nl = ? physical LF outside balanced delimiters; blank lines are ignored inside process suites ? ;',
    'indent = ? exactly two additional spaces for a suite or MESSAGE metadata; tabs are invalid ? ;',
    'dedent = ? return to the immediately enclosing suite indentation ? ;',
)

EXPRESSION_SURFACES = {
    "condition-compare": "comparison",
    "condition-all": "all_condition",
    "condition-any": "any_condition",
    "condition-not": "not_condition",
    "value-binding-line": "value_binding",
    "step-if": "if_statement",
    "step-while": "while_statement",
    "step-assert": "assert_statement",
    "step-call": "call_statement",
    "step-emit-inferred": '"EMIT", local_interface_target, logical_nl',
    "step-emit-explicit": '"EMIT", local_interface_target, binding_list, logical_nl',
    "step-set": "set_statement",
    "step-fail": "fail_statement",
    "trigger": "trigger_declaration",
}
