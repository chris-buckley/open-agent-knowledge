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

fixed-example: TEXT<<
~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
service-name: "Task board"

title-limit: 120
~~~~
>>

stateless-example: TEXT<<
~~~~instructions
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Keep the proposed change limited to the supplied request.
~~~~

~~~~schemas
~~~schema;id="change-request"
<REQUEST>

WHERE:
- <REQUEST> is string; is non-empty.
~~~

~~~schema;id="guide-1-option-comparison";name="Option Comparison";purpose="Compare current and proposed behaviour for one criterion."
| Criterion | Current | Proposed |
| --- | --- | --- |
| <CRITERION> | <CURRENT> | <PROPOSED> |

WHERE:
- <CRITERION> is string; matches `^[^|\r\n]+$`.
- <CURRENT> is string; matches `^[^|\r\n]+$`.
- <PROPOSED> is string; matches `^[^|\r\n]+$`.
~~~

~~~schema;id="guide-1-decision-brief";name="Decision Brief";purpose="State one decision and explain its rationale."
## Decision
<DECISION>

### Rationale
<RATIONALE>

WHERE:
- <DECISION> is string; is non-empty.
- <RATIONALE> is string; is non-empty.
~~~

~~~schema;id="guide-1-work-outline";name="Work Outline";purpose="Nest one implementation step and its check beneath one goal."
1. <GOAL>
   1. <STEP>
      1. <CHECK>

WHERE:
- <GOAL> is string; is non-empty; is one line.
- <STEP> is string; is non-empty; is one line.
- <CHECK> is string; is non-empty; is one line.
~~~

~~~schema;id="guide-1-code-file";name="Code File";purpose="Present one Python file with its complete source."
### <FILE_PATH>

```python
<CODE>
```

WHERE:
- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\-]+$`.
- <CODE> is string; is non-empty.
~~~
~~~~

~~~~triggers
change-requested(
  event="A small code change needs explanation.",
  source=interface.request,
  process=process.prepare-change,
)
~~~~

~~~~processes
~~~process;id="compare-options";name="Compare options";input="schema.change-request";output="schema.guide-1-option-comparison"
ACT input="schema.change-request" output="schema.guide-1-option-comparison": Compare current and proposed behaviour for <REQUEST>; produce <CRITERION>, <CURRENT>, and <PROPOSED>. (
  REQUEST=$REQUEST,
) -> CRITERION, CURRENT, PROPOSED
~~~

~~~process;id="decide-change";name="Decide change";input="schema.guide-1-option-comparison";output="schema.guide-1-decision-brief"
ACT input="schema.guide-1-option-comparison" output="schema.guide-1-decision-brief": For <CRITERION>, weigh <CURRENT> against <PROPOSED> and produce <DECISION> and <RATIONALE>. (
  CRITERION=$CRITERION,
  CURRENT=$CURRENT,
  PROPOSED=$PROPOSED,
) -> DECISION, RATIONALE
~~~

~~~process;id="plan-change";name="Plan change";input="schema.guide-1-decision-brief";output="schema.guide-1-work-outline"
ACT input="schema.guide-1-decision-brief" output="schema.guide-1-work-outline": Plan <DECISION> under <RATIONALE>; produce one <GOAL>, implementation <STEP>, and nested <CHECK>. (
  DECISION=$DECISION,
  RATIONALE=$RATIONALE,
) -> GOAL, STEP, CHECK
~~~

~~~process;id="write-file";name="Write file";input="schema.guide-1-work-outline";output="schema.guide-1-code-file"
ACT input="schema.guide-1-work-outline" output="schema.guide-1-code-file": Implement <STEP> for <GOAL> and <CHECK>; produce <FILE_PATH> and complete Python <CODE>. (
  GOAL=$GOAL,
  STEP=$STEP,
  CHECK=$CHECK,
) -> FILE_PATH, CODE
~~~

~~~process;id="prepare-change";name="Prepare change";input="schema.change-request"
CALL process.compare-options (REQUEST=$REQUEST) -> CRITERION, CURRENT, PROPOSED
EMIT interface.comparison
CALL process.decide-change (
  CRITERION=$CRITERION,
  CURRENT=$CURRENT,
  PROPOSED=$PROPOSED,
) -> DECISION, RATIONALE
EMIT interface.decision
CALL process.plan-change (DECISION=$DECISION, RATIONALE=$RATIONALE) -> GOAL, STEP, CHECK
EMIT interface.outline
CALL process.write-file (GOAL=$GOAL, STEP=$STEP, CHECK=$CHECK) -> FILE_PATH, CODE
EMIT interface.file
~~~
~~~~

~~~~interfaces
request RECEIVES schema.change-request
comparison EMITS schema.guide-1-option-comparison
decision EMITS schema.guide-1-decision-brief
outline EMITS schema.guide-1-work-outline
file EMITS schema.guide-1-code-file
~~~~
>>

example-rationale: CSV<<
example,justified structure,omitted parts
01-fixed-knowledge,two fixed facts,"authored instructions, schemas, state, triggers, processes, interfaces"
02-shape-gallery,four reusable templates and populated fixed examples,"authored instructions, state, triggers, processes, interfaces"
03-stateless-writer,"typed comparison, decision, plan, and code pipeline with one residual scope policy",constants and state
>>
~~~~
