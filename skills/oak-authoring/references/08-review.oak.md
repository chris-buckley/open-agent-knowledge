~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Produce exactly one valid OAK document.
>>

review: YAML<<
- Check one idless node, unique entry ids, canonical section order, and omission of
  unjustified parts.
- Check exact local and relative targets, complete schema bindings, data lifetimes,
  and native versus named tool work.
- Read populated output, not only the schema definition. Check actual layout, code
  fences, and cardinality.
- The grammar describes syntax. Human review is not a claim of programmatic validation.
- The examples are fixed teaching data, not additional agents or outside entry points
  to execute.
>>

oak-ebnf: TEXT<<
oak_document = xml_document | markdown_document ;
(* an empty part is omitted from the render *)
xml_document = [ xml_parts_from_instructions ] ;
xml_parts_from_instructions = xml_instructions_part, [ blank_line, xml_parts_from_constants ] | xml_parts_from_constants ;
xml_parts_from_constants = xml_constants_part, [ blank_line, xml_parts_from_schemas ] | xml_parts_from_schemas ;
xml_parts_from_schemas = xml_schemas_part, [ blank_line, xml_parts_from_state ] | xml_parts_from_state ;
xml_parts_from_state = xml_state_part, [ blank_line, xml_parts_from_triggers ] | xml_parts_from_triggers ;
xml_parts_from_triggers = xml_triggers_part, [ blank_line, xml_parts_from_processes ] | xml_parts_from_processes ;
xml_parts_from_processes = xml_processes_part, [ blank_line, xml_parts_from_interfaces ] | xml_parts_from_interfaces ;
xml_parts_from_interfaces = xml_interfaces_part ;
xml_instructions_part = "<instructions>", lf, text_body, "</instructions>" ;
xml_constants_part = "<constants>", lf, text_body, "</constants>" ;
xml_schemas_part = "<schemas>", lf, text_body, "</schemas>" ;
xml_state_part = "<state>", lf, text_body, "</state>" ;
xml_triggers_part = "<triggers>", lf, text_body, "</triggers>" ;
xml_processes_part = "<processes>", lf, text_body, "</processes>" ;
xml_interfaces_part = "<interfaces>", lf, text_body, "</interfaces>" ;
markdown_document = [ markdown_parts_from_instructions ] ;
markdown_parts_from_instructions = markdown_instructions_part, [ blank_line, markdown_parts_from_constants ] | markdown_parts_from_constants ;
markdown_parts_from_constants = markdown_constants_part, [ blank_line, markdown_parts_from_schemas ] | markdown_parts_from_schemas ;
markdown_parts_from_schemas = markdown_schemas_part, [ blank_line, markdown_parts_from_state ] | markdown_parts_from_state ;
markdown_parts_from_state = markdown_state_part, [ blank_line, markdown_parts_from_triggers ] | markdown_parts_from_triggers ;
markdown_parts_from_triggers = markdown_triggers_part, [ blank_line, markdown_parts_from_processes ] | markdown_parts_from_processes ;
markdown_parts_from_processes = markdown_processes_part, [ blank_line, markdown_parts_from_interfaces ] | markdown_parts_from_interfaces ;
markdown_parts_from_interfaces = markdown_interfaces_part ;
markdown_instructions_part = "~~~~instructions", lf, text_body, "~~~~" ;
markdown_constants_part = "~~~~constants", lf, text_body, "~~~~" ;
markdown_schemas_part = "~~~~schemas", lf, text_body, "~~~~" ;
markdown_state_part = "~~~~state", lf, text_body, "~~~~" ;
markdown_triggers_part = "~~~~triggers", lf, text_body, "~~~~" ;
markdown_processes_part = "~~~~processes", lf, text_body, "~~~~" ;
markdown_interfaces_part = "~~~~interfaces", lf, text_body, "~~~~" ;
xml_body_entry = "<", entry_tag, attributes, ">", lf, text_body, "</", entry_tag, ">" ;
markdown_body_entry = "~~~", entry_tag, markdown_attributes, lf, text_body, "~~~" ;
entry_tag = "schema" | "process" ;
condition = comparison | all_condition | any_condition | not_condition ;
comparison = process_value, comparison_operator, process_value ;
all_condition = "ALL", "(", condition, ",", condition, { ",", condition }, [ "," ], ")" ;
any_condition = "ANY", "(", condition, ",", condition, { ",", condition }, [ "," ], ")" ;
not_condition = "NOT", "(", condition, [ "," ], ")" ;
process_value = json_value | "$", value_target ;
value_target = constant_target | local_state_target | placeholder ;
constant_target = [ relative_document_path, "#" ], "constant.", slug_id ;
process_target = [ relative_document_path, "#" ], "process.", slug_id ;
local_state_target = "state.", slug_id ;
local_interface_target = "interface.", slug_id ;
value_binding = placeholder, "=", process_value ;
binding_list = "(", [ value_binding, { ",", value_binding }, [ "," ] ], ")" ;
output_bindings = "->", placeholder, { ",", placeholder } ;
trigger_declaration = slug_id, "(", trigger_field, { ",", trigger_field }, [ "," ], ")", logical_nl ;
trigger_field = "event", "=", json_string | "source", "=", local_interface_target | "guard", "=", condition | "process", "=", process_target | "seed", "=", binding_list ;
if_statement = "IF", condition, ":", suite, [ "ELSE", ":", suite ] ;
while_statement = "WHILE", condition, "LIMIT", positive_integer, ":", suite ;
assert_statement = "ASSERT", condition, logical_nl, [ indent, "MESSAGE", json_string, logical_nl, dedent ] ;
call_statement = "CALL", process_target, binding_list, [ output_bindings ], logical_nl ;
emit_statement = "EMIT", local_interface_target, [ binding_list ], logical_nl ;
set_statement = "SET", local_state_target, "=", process_value, logical_nl ;
fail_statement = "FAIL", json_string, logical_nl ;
suite = logical_nl, indent, process_step, { process_step }, dedent ;
process_step = if_statement | while_statement | assert_statement | call_statement | emit_statement | set_statement | fail_statement | surface_act_native | surface_act_tool | surface_step_foreach | surface_step_par | surface_step_join ;
positive_integer = ? an ASCII decimal integer literal with value greater than zero ? ;
json_string = ? one double-quoted JSON string, with JSON escapes ? ;
logical_nl = ? physical LF outside balanced delimiters; blank lines are ignored inside process suites ? ;
indent = ? exactly two additional spaces for a suite or MESSAGE metadata; tabs are invalid ? ;
dedent = ? return to the immediately enclosing suite indentation ? ;
comparison_operator = "equals" | "does not equal" | "is less than" | "is at most" | "is greater than" | "is at least" ;
(* Expression productions describe tokens, not a host-language expression evaluator.
Spaces separate words; punctuation is recognized only outside strings at its delimiter depth.
The $ token is adjacent to its value target. JSON owns its internal whitespace and delimiters.
One condition grammar serves IF, WHILE, ASSERT, and trigger guards.
ALL and ANY require at least two conditions; NOT requires exactly one.
Condition operators preserve the authored tree and left-to-right short-circuit order.
IF and WHILE headers end with a colon; their non-empty action suites indent two spaces.
ELSE aligns with its IF and immediately follows its suite, allowing blank lines.
WHILE requires LIMIT and one positive decimal integer literal; exhaustion while true fails.
ASSERT has a condition and optional indented MESSAGE metadata, not an action suite.
Balanced parentheses continue one logical statement across physical lines without action scopes.
OAK lists accept a trailing comma; JSON values retain their separate JSON grammar.
Trigger fields are named, unique, and may be authored in any order; event and process are required.
Canonical trigger field order is event, source, guard, process, seed; absent optionals are omitted.
Do not author guard=true or an empty seed; a source-backed trigger has no seed field.
A seed is an ordered named-binding list using the same value grammar as process inputs.
Strings, JSON literals, and typed targets are consumed as whole tokens before separators or operators.
Structural tabs, positional fields, truthiness, general calls, comments, infix aliases, and chained comparisons are invalid.
Canonical expression width is 100 Unicode code points, including indentation, prefixes, and suffixes.
Flat lists have no trailing comma; expanded lists put one item per line with a trailing comma and two-space indentation.
Closing delimiters align with their owning line; nested lists apply the same width rule recursively.
Indivisible values and prose may exceed the soft width; formatting never rewrites their contents.
Empty explicit EMIT bindings, empty seeds, and source-backed seeds are invalid.
Trigger events are non-blank single-line strings after decoding; guards must read state.
*)
constant = inline_constant | text_constant | json_constant | csv_constant | yaml_constant ;
inline_constant = slug_id, [ as_clause ], ": ", json_value ;
text_constant = slug_id, [ as_clause ], ": TEXT<<", lf, text_body, ">>" ;
json_constant = slug_id, [ as_clause ], ": JSON<<", lf, json_value, lf, ">>" ;
csv_constant = slug_id, [ as_clause ], ": CSV<<", lf, csv_body, lf, ">>" ;
yaml_constant = slug_id, [ as_clause ], ": YAML<<", lf, yaml_body, lf, ">>" ;
state_entry = slug_id, [ as_clause ], ": ", json_value ;
as_clause = " AS ", schema_placeholder_path ;
schema_placeholder_path = [ relative_document_path, "#" ], "schema", ".", slug_id, ".", placeholder ;
json_value = ? one JSON value ? ;
csv_body = ? one CSV header and one or more data rows ? ;
yaml_body = ? one YAML value ? ;
attributes = ? zero or more XML-like string attributes ? ;
markdown_attributes = ? zero or more semicolon JSON-string attributes ? ;
text_body = { text_line, lf } ;
text_line = ? any character except CR or LF ? ;
blank_line = lf, lf ;
lf = ? U+000A LINE FEED ? ;

slug_id = ? [a-z] ?, { ? [a-z0-9] ? }, { "-", ? [a-z0-9] ?, { ? [a-z0-9] ? } } ;
non_blank_line = { ? [^\r\n] ? }, ? [^\s] ?, { ? [^\r\n] ? } ;
process_name = ? [A-Z] ?, { ? [A-Za-z0-9] ? }, { "-", ? [A-Za-z0-9] ?, { ? [A-Za-z0-9] ? } }, " ", ? [A-Za-z0-9] ?, { ? [A-Za-z0-9] ? }, { "-", ? [A-Za-z0-9] ?, { ? [A-Za-z0-9] ? } } ;
placeholder = ? [A-Z] ?, { ? [A-Z0-9] ? }, { "_", ? [A-Z0-9] ?, { ? [A-Z0-9] ? } } ;
dotted_path = ( "constant" | "schema" | "state" | "process" | "interface" ), ".", slug_id ;
value_reference = "$", ( placeholder | constant_target | state_target ) ;
constant_target = [ relative_document_path, "#" ], "constant", ".", slug_id ;
state_target = "state", ".", slug_id ;
entry_part = "instruction" | "constant" | "schema" | "state" | "trigger" | "process" | "interface" ;
entry_path = entry_part, ".", slug_id ;
relative_document_path = ? one relative POSIX path of letters, digits, ".", "_", "-", and "/" ending in .oak.md ? ;
target_path = entry_path | relative_document_path, "#", entry_path ;
regex_pattern = "^", { ( "." | "[", [ "^" ], ( ? [^\r\n\\\[\]\-&~] ?, "-", ? [^\r\n\\\[\]\-&~] ? | ( "\\", ? [\\.^$|?*+(){}\[\]/-] ? | "\\", ? [nrt] ? ) | ? [^\r\n\\\[\]\-&~] ? ), { ( ? [^\r\n\\\[\]\-&~] ?, "-", ? [^\r\n\\\[\]\-&~] ? | ( "\\", ? [\\.^$|?*+(){}\[\]/-] ? | "\\", ? [nrt] ? ) | ? [^\r\n\\\[\]\-&~] ? ) }, "]" | "\\", ? [\\.^$|?*+(){}\[\]/-] ? | "\\", ? [nrt] ? | ? [^\r\n\\.^$*+?{}\[\]()|] ? ), [ ( "*" | "+" | "?" | "{", ? [0-9] ?, { ? [0-9] ? }, "}" | "{", ? [0-9] ?, { ? [0-9] ? }, ",}" | "{", ? [0-9] ?, { ? [0-9] ? }, ",", ? [0-9] ?, { ? [0-9] ? }, "}" ) ] }, "$" ;

surface_constraint_type = ? is <OF> ? ;
surface_constraint_one_of = ? is one of <VALUES> ? ;
surface_constraint_regex = ? matches `<PATTERN>` ? ;
surface_constraint_non_empty = ? is non-empty ? ;
surface_constraint_max_chars = ? is at most <N> characters ? ;
surface_constraint_lines = ? has <MIN> to <MAX> lines ? ;
surface_constraint_list_of = ? is a list of <ITEM> joined by `<SEPARATOR>` ? ;
surface_constraint_at_least = ? is at least <VALUE> ? ;
surface_constraint_at_most = ? is at most <VALUE> ? ;
surface_where = ? - <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>. ? ;
surface_instruction = ? <BODY> ? ;
surface_constant_inline = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE> ? ;
surface_constant_text = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: TEXT<<
<VALUE>
>> ? ;
surface_constant_json = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: JSON<<
<VALUE>
>> ? ;
surface_constant_csv = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: CSV<<
<VALUE>
>> ? ;
surface_constant_yaml = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: YAML<<
<VALUE>
>> ? ;
surface_schema = ? <schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">
<TEMPLATE>

WHERE:
<WHERE>
</schema> ? ;
surface_state = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE> ? ;
surface_value_literal = ? <VALUE> ? ;
surface_value_constant = ? $<CONSTANT> ? ;
surface_value_state = ? $<STATE> ? ;
surface_value_binding = ? $<BINDING> ? ;
surface_value_binding_line = value_binding ;
surface_condition_compare = comparison ;
surface_condition_all = all_condition ;
surface_condition_any = any_condition ;
surface_condition_not = not_condition ;
surface_act_native = ? ACT input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_act_tool = ? ACT TOOL "<TOOL>" input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_step_set = set_statement ;
surface_step_emit_inferred = "EMIT", local_interface_target, logical_nl ;
surface_step_emit_explicit = "EMIT", local_interface_target, binding_list, logical_nl ;
surface_step_if = if_statement ;
surface_step_call = call_statement ;
surface_step_fail = fail_statement ;
surface_step_assert = assert_statement ;
surface_step_foreach = ? FOREACH <BINDING> IN <VALUE>:
  <STEPS> ? ;
surface_step_while = while_statement ;
surface_step_par = ? PAR:
  <STEPS> ? ;
surface_step_join = ? JOIN ? ;
surface_process = ? <process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<STEPS>
</process> ? ;
surface_trigger = trigger_declaration ;
surface_interface_receives = ? <ID> RECEIVES <SCHEMA_ID>: <DESCRIPTION> ? ;
surface_interface_emits = ? <ID> EMITS <SCHEMA_ID>: <DESCRIPTION> ? ;
surface_node = ? <instructions>
<INSTRUCTIONS>
</instructions>

<constants>
<CONSTANTS>
</constants>

<schemas>
<SCHEMAS>
</schemas>

<state>
<STATE>
</state>

<triggers>
<TRIGGERS>
</triggers>

<processes>
<PROCESSES>
</processes>

<interfaces>
<INTERFACES>
</interfaces> ? ;
>>

teaching: JSON<<
{
  "references/examples/catalog.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nscenario-catalog: CSV<<\norder,entry,lesson,omitted,requires\n1,fixed_knowledge/example.oak.md,Two fixed facts need no workflow.,\"authored instructions, schemas, state, triggers, processes, interfaces\",No action host.\n2,shape_gallery/example.oak.md,\"Compare, explain, outline, and present code with populated fixed-cardinality shapes.\",\"authored instructions, state, triggers, processes, interfaces\",No action host; regeneration imports the shared schema library.\n3,shape_writer/example.oak.md,Receive and CALL typed phases; emit four ordered shapes without state.,\"constants, state\",Fixture-only native host; regeneration imports shared shapes and bindings.\n4,compound_growth/example.oak.md,Carry committed state across two arrivals and discard staged writes on failure.,,Exact math.multiply fixture and deterministic reflection; no live model or automatic scheduler.\n>>\n\ndelivery-boundary: \"OAK documents and sample constants are inert teaching data. Read a complete scenario before using it. Python hosts are repository demonstration material, not part of the skill teaching bundle.\"\n</constants>",
  "references/examples/fixed_knowledge/example.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nservice-name: \"Task board\"\n\ntitle-limit: 120\n</constants>",
  "references/examples/shape_gallery/example.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\n</instructions>\n\n<constants>\noption-comparison-instance: TEXT<<\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| Blank title | Accepted | Rejected |\n>>\n\ndecision-brief-instance: TEXT<<\n## Decision\nReject blank titles.\n\n### Rationale\nA title must identify the task.\n>>\n\nwork-outline-instance: TEXT<<\n1. Require meaningful titles.\n   1. Check the stripped title.\n      1. Test empty, whitespace, and valid titles.\n>>\n\ncode-file-instance: TEXT<<\n### title.py\n\n```python\ndef valid_title(title: str) -> bool:\n    return bool(title.strip())\n```\n>>\n</constants>\n\n<schemas>\n<schema id=\"option-comparison\" name=\"Option Comparison\" purpose=\"Compare current and proposed behaviour for one criterion.\">\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| <CRITERION> | <CURRENT> | <PROPOSED> |\n\nWHERE:\n- <CRITERION> is string; matches `^[^|\\r\\n]+$`.\n- <CURRENT> is string; matches `^[^|\\r\\n]+$`.\n- <PROPOSED> is string; matches `^[^|\\r\\n]+$`.\n</schema>\n\n<schema id=\"decision-brief\" name=\"Decision Brief\" purpose=\"State one decision and explain its rationale.\">\n## Decision\n<DECISION>\n\n### Rationale\n<RATIONALE>\n\nWHERE:\n- <DECISION> is string; is non-empty.\n- <RATIONALE> is string; is non-empty.\n</schema>\n\n<schema id=\"work-outline\" name=\"Work Outline\" purpose=\"Nest one implementation step and its check beneath one goal.\">\n1. <GOAL>\n   1. <STEP>\n      1. <CHECK>\n\nWHERE:\n- <GOAL> is string; is non-empty; is one line.\n- <STEP> is string; is non-empty; is one line.\n- <CHECK> is string; is non-empty; is one line.\n</schema>\n\n<schema id=\"code-file\" name=\"Code File\" purpose=\"Present one Python file with its complete source.\">\n### <FILE_PATH>\n\n```python\n<CODE>\n```\n\nWHERE:\n- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\\-]+$`.\n- <CODE> is string; is non-empty.\n</schema>\n</schemas>",
  "references/examples/shape_writer/example.oak.md": "<instructions>\n$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.\nProcess input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.\nACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.\nRECEIVES accepts one complete instance of its schema.\nA source-backed trigger supplies the received instance as the selected process input.\nEMITS publishes one complete instance of its schema.\nEMIT without bindings fills the target schema from same-named visible process bindings.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\nEach trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.\nEach process is the exact ordered way to do one task; follow its typed steps from top to bottom.\n\nKeep the proposed change limited to the supplied request.\n</instructions>\n\n<schemas>\n<schema id=\"change-request\">\n<REQUEST>\n\nWHERE:\n- <REQUEST> is string; is non-empty.\n</schema>\n</schemas>\n\n<triggers>\nchange-requested(\n  event=\"A small code change needs explanation.\",\n  source=interface.request,\n  process=process.prepare-change,\n)\n</triggers>\n\n<processes>\n<process id=\"compare-options\" name=\"Compare options\" input=\"schema.change-request\" output=\"shape_gallery.oak.md#schema.option-comparison\">\nACT input=\"schema.change-request\" output=\"shape_gallery.oak.md#schema.option-comparison\": Compare current and proposed behaviour for <REQUEST>; produce <CRITERION>, <CURRENT>, and <PROPOSED>. (\n  REQUEST=$REQUEST,\n) -> CRITERION, CURRENT, PROPOSED\n</process>\n\n<process id=\"decide-change\" name=\"Decide change\" input=\"shape_gallery.oak.md#schema.option-comparison\" output=\"shape_gallery.oak.md#schema.decision-brief\">\nACT input=\"shape_gallery.oak.md#schema.option-comparison\" output=\"shape_gallery.oak.md#schema.decision-brief\": For <CRITERION>, weigh <CURRENT> against <PROPOSED> and produce <DECISION> and <RATIONALE>. (\n  CRITERION=$CRITERION,\n  CURRENT=$CURRENT,\n  PROPOSED=$PROPOSED,\n) -> DECISION, RATIONALE\n</process>\n\n<process id=\"plan-change\" name=\"Plan change\" input=\"shape_gallery.oak.md#schema.decision-brief\" output=\"shape_gallery.oak.md#schema.work-outline\">\nACT input=\"shape_gallery.oak.md#schema.decision-brief\" output=\"shape_gallery.oak.md#schema.work-outline\": Plan <DECISION> under <RATIONALE>; produce one <GOAL>, implementation <STEP>, and nested <CHECK>. (\n  DECISION=$DECISION,\n  RATIONALE=$RATIONALE,\n) -> GOAL, STEP, CHECK\n</process>\n\n<process id=\"write-file\" name=\"Write file\" input=\"shape_gallery.oak.md#schema.work-outline\" output=\"shape_gallery.oak.md#schema.code-file\">\nACT input=\"shape_gallery.oak.md#schema.work-outline\" output=\"shape_gallery.oak.md#schema.code-file\": Implement <STEP> for <GOAL> and <CHECK>; produce <FILE_PATH> and complete Python <CODE>. (\n  GOAL=$GOAL,\n  STEP=$STEP,\n  CHECK=$CHECK,\n) -> FILE_PATH, CODE\n</process>\n\n<process id=\"prepare-change\" name=\"Prepare change\" input=\"schema.change-request\">\nCALL process.compare-options (REQUEST=$REQUEST) -> CRITERION, CURRENT, PROPOSED\nEMIT interface.comparison\nCALL process.decide-change (\n  CRITERION=$CRITERION,\n  CURRENT=$CURRENT,\n  PROPOSED=$PROPOSED,\n) -> DECISION, RATIONALE\nEMIT interface.decision\nCALL process.plan-change (DECISION=$DECISION, RATIONALE=$RATIONALE) -> GOAL, STEP, CHECK\nEMIT interface.outline\nCALL process.write-file (GOAL=$GOAL, STEP=$STEP, CHECK=$CHECK) -> FILE_PATH, CODE\nEMIT interface.file\n</process>\n</processes>\n\n<interfaces>\nrequest RECEIVES schema.change-request\ncomparison EMITS shape_gallery.oak.md#schema.option-comparison\ndecision EMITS shape_gallery.oak.md#schema.decision-brief\noutline EMITS shape_gallery.oak.md#schema.work-outline\nfile EMITS shape_gallery.oak.md#schema.code-file\n</interfaces>",
  "references/examples/shape_writer/shape_gallery.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\n</instructions>\n\n<constants>\noption-comparison-instance: TEXT<<\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| Blank title | Accepted | Rejected |\n>>\n\ndecision-brief-instance: TEXT<<\n## Decision\nReject blank titles.\n\n### Rationale\nA title must identify the task.\n>>\n\nwork-outline-instance: TEXT<<\n1. Require meaningful titles.\n   1. Check the stripped title.\n      1. Test empty, whitespace, and valid titles.\n>>\n\ncode-file-instance: TEXT<<\n### title.py\n\n```python\ndef valid_title(title: str) -> bool:\n    return bool(title.strip())\n```\n>>\n</constants>\n\n<schemas>\n<schema id=\"option-comparison\" name=\"Option Comparison\" purpose=\"Compare current and proposed behaviour for one criterion.\">\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| <CRITERION> | <CURRENT> | <PROPOSED> |\n\nWHERE:\n- <CRITERION> is string; matches `^[^|\\r\\n]+$`.\n- <CURRENT> is string; matches `^[^|\\r\\n]+$`.\n- <PROPOSED> is string; matches `^[^|\\r\\n]+$`.\n</schema>\n\n<schema id=\"decision-brief\" name=\"Decision Brief\" purpose=\"State one decision and explain its rationale.\">\n## Decision\n<DECISION>\n\n### Rationale\n<RATIONALE>\n\nWHERE:\n- <DECISION> is string; is non-empty.\n- <RATIONALE> is string; is non-empty.\n</schema>\n\n<schema id=\"work-outline\" name=\"Work Outline\" purpose=\"Nest one implementation step and its check beneath one goal.\">\n1. <GOAL>\n   1. <STEP>\n      1. <CHECK>\n\nWHERE:\n- <GOAL> is string; is non-empty; is one line.\n- <STEP> is string; is non-empty; is one line.\n- <CHECK> is string; is non-empty; is one line.\n</schema>\n\n<schema id=\"code-file\" name=\"Code File\" purpose=\"Present one Python file with its complete source.\">\n### <FILE_PATH>\n\n```python\n<CODE>\n```\n\nWHERE:\n- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\\-]+$`.\n- <CODE> is string; is non-empty.\n</schema>\n</schemas>",
  "references/examples/shape_writer/sample.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nrequest: {\"REQUEST\": \"Reject blank task titles with one Python predicate.\"}\n\nsteps: [{\"schema\": \"shape_gallery.oak.md#schema.option-comparison\", \"interface\": \"interface.comparison\", \"input\": {\"REQUEST\": \"Reject blank task titles with one Python predicate.\"}, \"output\": {\"CRITERION\": \"Blank title\", \"CURRENT\": \"Accepted\", \"PROPOSED\": \"Rejected\"}}, {\"schema\": \"shape_gallery.oak.md#schema.decision-brief\", \"interface\": \"interface.decision\", \"input\": {\"CRITERION\": \"Blank title\", \"CURRENT\": \"Accepted\", \"PROPOSED\": \"Rejected\"}, \"output\": {\"DECISION\": \"Reject blank titles.\", \"RATIONALE\": \"A title must identify the task.\"}}, {\"schema\": \"shape_gallery.oak.md#schema.work-outline\", \"interface\": \"interface.outline\", \"input\": {\"DECISION\": \"Reject blank titles.\", \"RATIONALE\": \"A title must identify the task.\"}, \"output\": {\"GOAL\": \"Require meaningful titles.\", \"STEP\": \"Check the stripped title.\", \"CHECK\": \"Test empty, whitespace, and valid titles.\"}}, {\"schema\": \"shape_gallery.oak.md#schema.code-file\", \"interface\": \"interface.file\", \"input\": {\"GOAL\": \"Require meaningful titles.\", \"STEP\": \"Check the stripped title.\", \"CHECK\": \"Test empty, whitespace, and valid titles.\"}, \"output\": {\"FILE_PATH\": \"title.py\", \"CODE\": \"def valid_title(title: str) -> bool:\\n    return bool(title.strip())\"}}]\n\nhost: \"A deterministic adapter supports only this fixture, not arbitrary requests or live inference.\"\n</constants>",
  "references/examples/compound_growth/example.oak.md": "<instructions>\n$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.\nConditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.\nProcess input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.\nACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.\nEvent-backed trigger seeds fill the selected process input schema; each seeded value validates before the process runs.\nEMITS publishes one complete instance of its schema.\nText after `: ` states boundary meaning absent from the interface schema.\nAS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.\nConstants hold values that do not change while the knowledge runs.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\nState holds values that persist and can change while processes run.\nEach trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.\nEach process is the exact ordered way to do one task; follow its typed steps from top to bottom.\n\nRun this machine continuously: after each cycle commits, apply the same arrival again.\n</instructions>\n\n<constants>\ngrowth-rate AS schema.scaling.FACTOR: 1.05\n\nreflection-step AS schema.scaling.FACTOR: 8\n</constants>\n\n<schemas>\n<schema id=\"scaling\" name=\"Scaling\" purpose=\"Carry one balance and the factor to scale it by.\">\nBalance: <BALANCE>\nFactor: <FACTOR>\n\nWHERE:\n- <BALANCE> is number; is at least 0; the non-negative balance to scale.\n- <FACTOR> is number; is at least 1; the multiplication factor.\n</schema>\n\n<schema id=\"scaled-balance\" name=\"Scaled Balance\" purpose=\"Carry the balance after one multiplication.\">\n<SCALED_BALANCE>\n\nWHERE:\n- <SCALED_BALANCE> is number; the balance after one multiplication.\n</schema>\n\n<schema id=\"growth-target\" name=\"Growth Target\" purpose=\"Carry the balance one growth cycle must reach.\">\nTarget: <TARGET>\n\nWHERE:\n- <TARGET> is number; is at least 0; the balance the cycle must reach.\n</schema>\n\n<schema id=\"reflection\" name=\"Reflection\" purpose=\"Carry one growth reflection for the chat.\">\nBalance: <BALANCE>\nReflection: <REFLECTION>\n\nWHERE:\n- <BALANCE> is number; the balance at the end of the cycle.\n- <REFLECTION> is string; is non-empty; the reflection on this growth cycle.\n</schema>\n</schemas>\n\n<state>\ncurrent-balance AS schema.scaling.BALANCE: 100\nreflection-target AS schema.scaling.BALANCE: 800\n</state>\n\n<triggers>\ngrowth-requested(\n  event=\"Continue growing the balance.\",\n  process=process.grow-balance,\n  seed=(TARGET=$state.reflection-target),\n)\n</triggers>\n\n<processes>\n<process id=\"scale-balance\" name=\"Scale balance\" input=\"schema.scaling\" output=\"schema.scaled-balance\">\nACT TOOL \"math.multiply\" input=\"schema.scaling\" output=\"schema.scaled-balance\": Multiply <BALANCE> by <FACTOR> and round to 2 decimals to produce <SCALED_BALANCE>. (\n  BALANCE=$BALANCE,\n  FACTOR=$FACTOR,\n) -> SCALED_BALANCE\n</process>\n\n<process id=\"grow-balance\" name=\"Grow balance\" input=\"schema.growth-target\">\nWHILE $state.current-balance is less than $TARGET LIMIT 60:\n  CALL process.scale-balance (\n    BALANCE=$state.current-balance,\n    FACTOR=$constant.growth-rate,\n  ) -> SCALED_BALANCE\n  SET state.current-balance = $SCALED_BALANCE\nACT Reflect on <BALANCE> reaching <TARGET> and produce <REFLECTION>. (\n  BALANCE=$state.current-balance,\n  TARGET=$TARGET,\n) -> REFLECTION\nCALL process.scale-balance (\n  BALANCE=$state.reflection-target,\n  FACTOR=$constant.reflection-step,\n) -> SCALED_BALANCE\nSET state.reflection-target = $SCALED_BALANCE\nEMIT interface.reflection-output (BALANCE=$state.current-balance, REFLECTION=$REFLECTION)\n</process>\n</processes>\n\n<interfaces>\nreflection-output EMITS schema.reflection: \"The reflection written to the chat before the next cycle starts.\"\n</interfaces>",
  "references/examples/compound_growth/sample.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\narrival: {\"event\": \"Continue growing the balance.\", \"count\": 2}\n\ninitial-state: {\"state.current-balance\": 100, \"state.reflection-target\": 800}\n\nexpected-states: [{\"state.current-balance\": 815.04, \"state.reflection-target\": 6400}, {\"state.current-balance\": 6642.28, \"state.reflection-target\": 51200}]\n\nexpected-emissions: [{\"BALANCE\": 815.04, \"REFLECTION\": \"Balance 815.04 passed target 800.\"}, {\"BALANCE\": 6642.28, \"REFLECTION\": \"Balance 6642.28 passed target 6400.\"}]\n\nfailure: \"A reflection failure after staged growth leaves caller state unchanged and returns no committed result. Host calls are not rolled back.\"\n\nhost: \"Exact math.multiply arithmetic and deterministic reflection; two fixture arrivals, not an automatic infinite scheduler.\"\n</constants>"
}
>>
~~~~
