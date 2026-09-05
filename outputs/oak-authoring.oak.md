~~~~instructions
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
~~~~

~~~~constants
guide-1-guidance: YAML<<
- Treat the complete supplied host context as the source, regardless of modality.
- Omit every part and entry that the source does not justify.
- Do not invent state, triggers, processes, interfaces, tools, or relative paths.
- Write one idless node using only the seven parts in canonical order.
- Use the shortest unambiguous names and reuse one exact domain noun across parts.
- Keep tool implementations, handlers, transport, credentials, model selection, and
  server configuration in the host.
>>

guide-1-part-authoring-priority: ["schemas", "constants", "state", "interfaces", "triggers", "processes", "instructions"]

guide-1-part-order: ["instructions", "constants", "schemas", "state", "triggers", "processes", "interfaces"]

guide-1-part-responsibilities: CSV<<
part,owns,lifetime,excludes
instructions,irreducible interpreter policy,whole document use,"facts, reusable shapes, mutable values, routing, ordered work, and boundary payloads"
constants,fixed JSON knowledge,whole document use,mutable values
schemas,reusable information shapes,definition,boundary flow and process routing
state,persistent mutable JSON values,across arrivals,invocation-local results
triggers,outside occurrence routing,one arrival decision,internal sequencing
processes,ordered local work,one invocation,outside transport
interfaces,complete boundary schema instances,one receive or emission,information shape definitions
>>

guide-1-host-boundary: CSV<<
owner,responsibility
OAK,"knowledge, internal contracts, canonical models, authored representations, explicit graph resolution, and execution semantics"
host,"model selection, credentials, transport, tool implementations, scheduling, persistence mechanism, delivery, and external side effects"
>>

guide-1-reading: TEXT<<
Load needed guides in authoring order, not render order. The entry routes work; supporting files supply fixed knowledge and reusable shapes. Omit empty parts. Select complete scenarios via references/examples/catalog.oak.md. The assembled agent has identical knowledge with local targets. Authoring and interpretation of either form need no Python, package, network, or validator.
>>

guide-2-guidance: YAML<<
- Map reusable information shapes and contracts to schemas.
- 'Choose schema templates by information relationships: tables for comparison, outlines
  for hierarchy, sections for explanation, and fenced blocks for code; use lists only
  for list-shaped information.'
- Preserve requested layouts; the demonstrated shapes are examples, not a closed catalogue
  or a reason to force every schema into labelled fields.
- Keep templates and WHERE constraints in schema definitions; populated outputs fill
  its slots rather than copying the schema definition.
- A binding supplies one value per placeholder; repeated names reuse that value, and
  an ellipsis alone does not create independently typed rows or sections.
- Bind constants, state, processes, actions, and interfaces to schemas where values
  must validate; role names alone are not types.
>>

guide-2-populated-shapes: TEXT<<
Option Comparison
| Criterion | Current | Proposed |
| --- | --- | --- |
| Blank title | Accepted | Rejected |

Decision Brief
## Decision
Reject blank titles.

### Rationale
A title must identify the task.

Work Outline
1. Require meaningful titles.
   1. Check the stripped title.
      1. Test empty, whitespace, and valid titles.

Code File
### title.py

```python
def valid_title(title: str) -> bool:
    return bool(title.strip())
```
>>

guide-2-shape-notes: TEXT<<
populated-shapes shows filled instances of these four reusable schemas without WHERE or schema wrappers. The one-row table is fixed-cardinality. Extend templates explicitly when justified; apply the schema guidance above.
>>

guide-3-guidance: YAML<<
- Map stable values needed during use to constants.
>>

guide-3-forms: CSV<<
form,use
JSON,"short fixed scalars, arrays, or objects"
TEXT,verbatim fixed text
CSV,tabular fixed knowledge
YAML,readable structured fixed knowledge
>>

guide-4-guidance: YAML<<
- Map values that persist and can change across arrivals to state.
- Use constants for fixed values, state for values across arrivals, process bindings
  for local values, and interfaces for boundary instances.
- Keep pipeline values in process bindings and use state only for values that must
  survive an arrival.
>>

guide-4-value-lifetimes: CSV<<
value,scope
constant,fixed during document use
state,persistent across arrivals
process binding,immutable in one frame or child scope
interface instance,one complete boundary occurrence
>>

guide-4-omission: "A draft or pipeline intermediate is not state. Omit state unless a later arrival must observe a changed value."

guide-5-guidance: YAML<<
- Map complete document-boundary crossings to one-way interfaces.
- Emit one complete schema instance and use inferred `EMIT` only when same-named visible
  bindings satisfy it.
>>

guide-5-boundaries: "Reuse an existing schema at a boundary; do not redefine its shape inside the interface. Interface instances are not ambient mutable storage."

guide-6-guidance: YAML<<
- Map outside events, receive sources, state guards, and selected work to triggers.
- Route each receive interface through one source-backed trigger into a process with
  the same resolved input schema.
- Declare each trigger once with named fields; omit unused fields and keep source
  payloads separate from event seeds.
>>

guide-6-routing: "An event describes an outside occurrence. An optional source identifies one receiving interface; its schema must resolve identically to process input, with no seeds. A guard requires a state read and may compare literals or fixed constants; it cannot read process bindings. Internal work uses CALL, never triggers."

guide-7-guidance: YAML<<
- Map ordered local work to processes.
- Start each process id with an exact base-form action verb and name the result it
  establishes.
- Give reusable process phases input and output schemas when their values need contracts.
- Name an action's participants, their relationship or criterion, and required results
  or effects. Omit unjustified roles; prefer natural domain wording over a mandatory
  sentence template.
- Prefer validate for a named contract check, assess for judgment against a criterion,
  and publish for a host-authorized external effect; these words add no capability.
  Schema validity proves neither sound judgment nor performed work; EMIT does not
  prove delivery. Native ACT can have effects; preserve exact tool names.
- Keep multi-phase entry processes as orchestrators that compose reusable processes
  with `CALL`.
- Use plain `ACT` when the interpreter performs the work with native capabilities.
- Use `ACT TOOL` only for one exact tool name copied from the supplied registry.
- Use `PAR` and `JOIN` only for independent exact tool actions.
- Model a delegated agent as its own typed OAK document and dispatch it through an
  exact host tool contract.
- Use the same explicit recursive condition structure for branches, loop conditions,
  assertions, and guards; preserve child order and bounded-loop failures.
- Use delimiter continuation for long expressions and indentation for ordered action
  suites; follow the shared grammar instead of inventing another layout dialect.
>>

guide-7-scopes: TEXT<<
Bindings are immutable per frame. CALL promotes declared outputs; branches and iterations have local scope. IF never promotes child outputs. EMIT in the branch or use process contracts, not invented state. Assertions, conditions, loops, and parallel steps need source-justified semantics.
>>

guide-8-guidance: YAML<<
- Author instructions last; include only meaning that schemas, constants, state, interfaces,
  triggers, and processes cannot express.
>>

guide-8-last-decision: "After the other six responsibilities are represented, ask what meaning remains. Keep only that irreducible policy in instructions. Generated interpretation guidance is derived from the node; do not author copies of it."

guide-9-guidance: YAML<<
- Produce exactly one valid OAK document.
>>

guide-9-review: YAML<<
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

guide-9-oak-ebnf: TEXT<<
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

guide-9-teaching: JSON<<
{
  "references/examples/catalog.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nscenario-catalog: CSV<<\norder,entry,lesson,omitted,requires\n1,fixed_knowledge/example.oak.md,Two fixed facts need no workflow.,\"authored instructions, schemas, state, triggers, processes, interfaces\",No action host.\n2,shape_gallery/example.oak.md,\"Compare, explain, outline, and present code with populated fixed-cardinality shapes.\",\"authored instructions, state, triggers, processes, interfaces\",No action host; regeneration imports the shared schema library.\n3,shape_writer/example.oak.md,Receive and CALL typed phases; emit four ordered shapes without state.,\"constants, state\",Fixture-only native host; regeneration imports shared shapes and bindings.\n4,compound_growth/example.oak.md,Carry committed state across two arrivals and discard staged writes on failure.,,Exact math.multiply fixture and deterministic reflection; no live model or automatic scheduler.\n>>\n\ndelivery-boundary: \"OAK documents and sample constants are inert teaching data. Read a complete scenario before using it. Python hosts are repository demonstration material, not part of the skill teaching bundle.\"\n</constants>",
  "references/examples/fixed_knowledge/example.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nservice-name: \"Task board\"\n\ntitle-limit: 120\n</constants>",
  "references/examples/shape_gallery/example.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\n</instructions>\n\n<constants>\noption-comparison-instance: TEXT<<\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| Blank title | Accepted | Rejected |\n>>\n\ndecision-brief-instance: TEXT<<\n## Decision\nReject blank titles.\n\n### Rationale\nA title must identify the task.\n>>\n\nwork-outline-instance: TEXT<<\n1. Require meaningful titles.\n   1. Check the stripped title.\n      1. Test empty, whitespace, and valid titles.\n>>\n\ncode-file-instance: TEXT<<\n### title.py\n\n```python\ndef valid_title(title: str) -> bool:\n    return bool(title.strip())\n```\n>>\n</constants>\n\n<schemas>\n<schema id=\"option-comparison\" name=\"Option Comparison\" purpose=\"Compare current and proposed behaviour for one criterion.\">\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| <CRITERION> | <CURRENT> | <PROPOSED> |\n\nWHERE:\n- <CRITERION> is string; matches `^[^|\\r\\n]+$`.\n- <CURRENT> is string; matches `^[^|\\r\\n]+$`.\n- <PROPOSED> is string; matches `^[^|\\r\\n]+$`.\n</schema>\n\n<schema id=\"decision-brief\" name=\"Decision Brief\" purpose=\"State one decision and explain its rationale.\">\n## Decision\n<DECISION>\n\n### Rationale\n<RATIONALE>\n\nWHERE:\n- <DECISION> is string; is non-empty.\n- <RATIONALE> is string; is non-empty.\n</schema>\n\n<schema id=\"work-outline\" name=\"Work Outline\" purpose=\"Nest one implementation step and its check beneath one goal.\">\n1. <GOAL>\n   1. <STEP>\n      1. <CHECK>\n\nWHERE:\n- <GOAL> is string; is non-empty; is one line.\n- <STEP> is string; is non-empty; is one line.\n- <CHECK> is string; is non-empty; is one line.\n</schema>\n\n<schema id=\"code-file\" name=\"Code File\" purpose=\"Present one Python file with its complete source.\">\n### <FILE_PATH>\n\n```python\n<CODE>\n```\n\nWHERE:\n- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\\-]+$`.\n- <CODE> is string; is non-empty.\n</schema>\n</schemas>",
  "references/examples/shape_writer/example.oak.md": "<instructions>\n$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.\nProcess input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.\nACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.\nRECEIVES accepts one complete instance of its schema.\nA source-backed trigger supplies the received instance as the selected process input.\nEMITS publishes one complete instance of its schema.\nEMIT without bindings fills the target schema from same-named visible process bindings.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\nEach trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.\nEach process is the exact ordered way to do one task; follow its typed steps from top to bottom.\n\nKeep the proposed change limited to the supplied request.\n</instructions>\n\n<schemas>\n<schema id=\"change-request\">\n<REQUEST>\n\nWHERE:\n- <REQUEST> is string; is non-empty.\n</schema>\n</schemas>\n\n<triggers>\nchange-requested(\n  event=\"A small code change needs explanation.\",\n  source=interface.request,\n  process=process.prepare-change,\n)\n</triggers>\n\n<processes>\n<process id=\"compare-options\" name=\"Compare options\" input=\"schema.change-request\" output=\"shape_gallery.oak.md#schema.option-comparison\">\nACT input=\"schema.change-request\" output=\"shape_gallery.oak.md#schema.option-comparison\": Compare current and proposed behaviour for <REQUEST>; produce <CRITERION>, <CURRENT>, and <PROPOSED>. (\n  REQUEST=$REQUEST,\n) -> CRITERION, CURRENT, PROPOSED\n</process>\n\n<process id=\"decide-change\" name=\"Decide change\" input=\"shape_gallery.oak.md#schema.option-comparison\" output=\"shape_gallery.oak.md#schema.decision-brief\">\nACT input=\"shape_gallery.oak.md#schema.option-comparison\" output=\"shape_gallery.oak.md#schema.decision-brief\": Assess <CURRENT> and <PROPOSED> against <CRITERION>; produce <DECISION> and <RATIONALE>. (\n  CRITERION=$CRITERION,\n  CURRENT=$CURRENT,\n  PROPOSED=$PROPOSED,\n) -> DECISION, RATIONALE\n</process>\n\n<process id=\"plan-change\" name=\"Plan change\" input=\"shape_gallery.oak.md#schema.decision-brief\" output=\"shape_gallery.oak.md#schema.work-outline\">\nACT input=\"shape_gallery.oak.md#schema.decision-brief\" output=\"shape_gallery.oak.md#schema.work-outline\": Plan <DECISION> under <RATIONALE>; produce one <GOAL>, implementation <STEP>, and nested <CHECK>. (\n  DECISION=$DECISION,\n  RATIONALE=$RATIONALE,\n) -> GOAL, STEP, CHECK\n</process>\n\n<process id=\"write-file\" name=\"Write file\" input=\"shape_gallery.oak.md#schema.work-outline\" output=\"shape_gallery.oak.md#schema.code-file\">\nACT input=\"shape_gallery.oak.md#schema.work-outline\" output=\"shape_gallery.oak.md#schema.code-file\": Implement <STEP> for <GOAL> and <CHECK>; produce <FILE_PATH> and complete Python <CODE>. (\n  GOAL=$GOAL,\n  STEP=$STEP,\n  CHECK=$CHECK,\n) -> FILE_PATH, CODE\n</process>\n\n<process id=\"prepare-change\" name=\"Prepare change\" input=\"schema.change-request\">\nCALL process.compare-options (REQUEST=$REQUEST) -> CRITERION, CURRENT, PROPOSED\nEMIT interface.comparison\nCALL process.decide-change (\n  CRITERION=$CRITERION,\n  CURRENT=$CURRENT,\n  PROPOSED=$PROPOSED,\n) -> DECISION, RATIONALE\nEMIT interface.decision\nCALL process.plan-change (DECISION=$DECISION, RATIONALE=$RATIONALE) -> GOAL, STEP, CHECK\nEMIT interface.outline\nCALL process.write-file (GOAL=$GOAL, STEP=$STEP, CHECK=$CHECK) -> FILE_PATH, CODE\nEMIT interface.file\n</process>\n</processes>\n\n<interfaces>\nrequest RECEIVES schema.change-request\ncomparison EMITS shape_gallery.oak.md#schema.option-comparison\ndecision EMITS shape_gallery.oak.md#schema.decision-brief\noutline EMITS shape_gallery.oak.md#schema.work-outline\nfile EMITS shape_gallery.oak.md#schema.code-file\n</interfaces>",
  "references/examples/shape_writer/shape_gallery.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\n</instructions>\n\n<constants>\noption-comparison-instance: TEXT<<\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| Blank title | Accepted | Rejected |\n>>\n\ndecision-brief-instance: TEXT<<\n## Decision\nReject blank titles.\n\n### Rationale\nA title must identify the task.\n>>\n\nwork-outline-instance: TEXT<<\n1. Require meaningful titles.\n   1. Check the stripped title.\n      1. Test empty, whitespace, and valid titles.\n>>\n\ncode-file-instance: TEXT<<\n### title.py\n\n```python\ndef valid_title(title: str) -> bool:\n    return bool(title.strip())\n```\n>>\n</constants>\n\n<schemas>\n<schema id=\"option-comparison\" name=\"Option Comparison\" purpose=\"Compare current and proposed behaviour for one criterion.\">\n| Criterion | Current | Proposed |\n| --- | --- | --- |\n| <CRITERION> | <CURRENT> | <PROPOSED> |\n\nWHERE:\n- <CRITERION> is string; matches `^[^|\\r\\n]+$`.\n- <CURRENT> is string; matches `^[^|\\r\\n]+$`.\n- <PROPOSED> is string; matches `^[^|\\r\\n]+$`.\n</schema>\n\n<schema id=\"decision-brief\" name=\"Decision Brief\" purpose=\"State one decision and explain its rationale.\">\n## Decision\n<DECISION>\n\n### Rationale\n<RATIONALE>\n\nWHERE:\n- <DECISION> is string; is non-empty.\n- <RATIONALE> is string; is non-empty.\n</schema>\n\n<schema id=\"work-outline\" name=\"Work Outline\" purpose=\"Nest one implementation step and its check beneath one goal.\">\n1. <GOAL>\n   1. <STEP>\n      1. <CHECK>\n\nWHERE:\n- <GOAL> is string; is non-empty; is one line.\n- <STEP> is string; is non-empty; is one line.\n- <CHECK> is string; is non-empty; is one line.\n</schema>\n\n<schema id=\"code-file\" name=\"Code File\" purpose=\"Present one Python file with its complete source.\">\n### <FILE_PATH>\n\n```python\n<CODE>\n```\n\nWHERE:\n- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\\-]+$`.\n- <CODE> is string; is non-empty.\n</schema>\n</schemas>",
  "references/examples/shape_writer/sample.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nrequest: {\"REQUEST\": \"Reject blank task titles with one Python predicate.\"}\n\nsteps: [{\"schema\": \"shape_gallery.oak.md#schema.option-comparison\", \"interface\": \"interface.comparison\", \"input\": {\"REQUEST\": \"Reject blank task titles with one Python predicate.\"}, \"output\": {\"CRITERION\": \"Blank title\", \"CURRENT\": \"Accepted\", \"PROPOSED\": \"Rejected\"}}, {\"schema\": \"shape_gallery.oak.md#schema.decision-brief\", \"interface\": \"interface.decision\", \"input\": {\"CRITERION\": \"Blank title\", \"CURRENT\": \"Accepted\", \"PROPOSED\": \"Rejected\"}, \"output\": {\"DECISION\": \"Reject blank titles.\", \"RATIONALE\": \"A title must identify the task.\"}}, {\"schema\": \"shape_gallery.oak.md#schema.work-outline\", \"interface\": \"interface.outline\", \"input\": {\"DECISION\": \"Reject blank titles.\", \"RATIONALE\": \"A title must identify the task.\"}, \"output\": {\"GOAL\": \"Require meaningful titles.\", \"STEP\": \"Check the stripped title.\", \"CHECK\": \"Test empty, whitespace, and valid titles.\"}}, {\"schema\": \"shape_gallery.oak.md#schema.code-file\", \"interface\": \"interface.file\", \"input\": {\"GOAL\": \"Require meaningful titles.\", \"STEP\": \"Check the stripped title.\", \"CHECK\": \"Test empty, whitespace, and valid titles.\"}, \"output\": {\"FILE_PATH\": \"title.py\", \"CODE\": \"def valid_title(title: str) -> bool:\\n    return bool(title.strip())\"}}]\n\nhost: \"A deterministic adapter supports only this fixture, not arbitrary requests or live inference.\"\n</constants>",
  "references/examples/compound_growth/example.oak.md": "<instructions>\n$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.\nConditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.\nProcess input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.\nACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.\nEvent-backed trigger seeds fill the selected process input schema; each seeded value validates before the process runs.\nEMITS publishes one complete instance of its schema.\nText after `: ` states boundary meaning absent from the interface schema.\nAS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.\nConstants hold values that do not change while the knowledge runs.\nEach schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.\nState holds values that persist and can change while processes run.\nEach trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.\nEach process is the exact ordered way to do one task; follow its typed steps from top to bottom.\n\nRun this machine continuously: after each cycle commits, apply the same arrival again.\n</instructions>\n\n<constants>\ngrowth-rate AS schema.scaling.FACTOR: 1.05\n\nreflection-step AS schema.scaling.FACTOR: 8\n</constants>\n\n<schemas>\n<schema id=\"scaling\" name=\"Scaling\" purpose=\"Carry one balance and the factor to scale it by.\">\nBalance: <BALANCE>\nFactor: <FACTOR>\n\nWHERE:\n- <BALANCE> is number; is at least 0; the non-negative balance to scale.\n- <FACTOR> is number; is at least 1; the multiplication factor.\n</schema>\n\n<schema id=\"scaled-balance\" name=\"Scaled Balance\" purpose=\"Carry the balance after one multiplication.\">\n<SCALED_BALANCE>\n\nWHERE:\n- <SCALED_BALANCE> is number; the balance after one multiplication.\n</schema>\n\n<schema id=\"growth-target\" name=\"Growth Target\" purpose=\"Carry the balance one growth cycle must reach.\">\nTarget: <TARGET>\n\nWHERE:\n- <TARGET> is number; is at least 0; the balance the cycle must reach.\n</schema>\n\n<schema id=\"reflection\" name=\"Reflection\" purpose=\"Carry one growth reflection for the chat.\">\nBalance: <BALANCE>\nReflection: <REFLECTION>\n\nWHERE:\n- <BALANCE> is number; the balance at the end of the cycle.\n- <REFLECTION> is string; is non-empty; the reflection on this growth cycle.\n</schema>\n</schemas>\n\n<state>\ncurrent-balance AS schema.scaling.BALANCE: 100\nreflection-target AS schema.scaling.BALANCE: 800\n</state>\n\n<triggers>\ngrowth-requested(\n  event=\"Continue growing the balance.\",\n  process=process.grow-balance,\n  seed=(TARGET=$state.reflection-target),\n)\n</triggers>\n\n<processes>\n<process id=\"scale-balance\" name=\"Scale balance\" input=\"schema.scaling\" output=\"schema.scaled-balance\">\nACT TOOL \"math.multiply\" input=\"schema.scaling\" output=\"schema.scaled-balance\": Multiply <BALANCE> by <FACTOR> and round to 2 decimals to produce <SCALED_BALANCE>. (\n  BALANCE=$BALANCE,\n  FACTOR=$FACTOR,\n) -> SCALED_BALANCE\n</process>\n\n<process id=\"grow-balance\" name=\"Grow balance\" input=\"schema.growth-target\">\nWHILE $state.current-balance is less than $TARGET LIMIT 60:\n  CALL process.scale-balance (\n    BALANCE=$state.current-balance,\n    FACTOR=$constant.growth-rate,\n  ) -> SCALED_BALANCE\n  SET state.current-balance = $SCALED_BALANCE\nACT Reflect on <BALANCE> reaching <TARGET> and produce <REFLECTION>. (\n  BALANCE=$state.current-balance,\n  TARGET=$TARGET,\n) -> REFLECTION\nCALL process.scale-balance (\n  BALANCE=$state.reflection-target,\n  FACTOR=$constant.reflection-step,\n) -> SCALED_BALANCE\nSET state.reflection-target = $SCALED_BALANCE\nEMIT interface.reflection-output (BALANCE=$state.current-balance, REFLECTION=$REFLECTION)\n</process>\n</processes>\n\n<interfaces>\nreflection-output EMITS schema.reflection: \"The reflection written to the chat before the next cycle starts.\"\n</interfaces>",
  "references/examples/compound_growth/sample.oak.md": "<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\narrival: {\"event\": \"Continue growing the balance.\", \"count\": 2}\n\ninitial-state: {\"state.current-balance\": 100, \"state.reflection-target\": 800}\n\nexpected-states: [{\"state.current-balance\": 815.04, \"state.reflection-target\": 6400}, {\"state.current-balance\": 6642.28, \"state.reflection-target\": 51200}]\n\nexpected-emissions: [{\"BALANCE\": 815.04, \"REFLECTION\": \"Balance 815.04 passed target 800.\"}, {\"BALANCE\": 6642.28, \"REFLECTION\": \"Balance 6642.28 passed target 6400.\"}]\n\nfailure: \"A reflection failure after staged growth leaves caller state unchanged and returns no committed result. Host calls are not rolled back.\"\n\nhost: \"Exact math.multiply arithmetic and deterministic reflection; two fixture arrivals, not an automatic infinite scheduler.\"\n</constants>"
}
>>

guide-10-guidance: YAML<<
- Review the draft against the grammar, populated examples, and OAK contracts; run
  programmatic validation only when requested and report whether it actually ran.
- Return the final OAK document and, when validation is requested, an honest validation
  result outside the authored document.
>>

guide-10-identity: {"version": "2.2.0", "validator-revision": "2b542c613c5d1a7e64b597884fae4f444ac34916"}

guide-10-validation-policy: YAML<<
- Run programmatic validation only when the user requests it. Authoring and interpretation
  need no installation.
- The script uses Python 3.11 or newer. Reuse a matching installed validator, an explicit
  --source and optional --python, or its retained cache. The source fingerprint must
  match, not just the package name or version.
- Use scripts/validate.py from the skill. In the standalone agent, materialize validator-script
  exactly as a local validate.py only when validation is requested.
- 'First run: python validate.py document.oak.md. Use --root for a larger explicitly
  allowed document graph. In the skill directory the script path is scripts/validate.py.'
- When the result says permission-required, ask permission to download the identified
  OAK revision and install its declared dependencies in an isolated cached environment.
  Requesting validation is not installation consent.
- Only after explicit approval, repeat the command with --allow-install. No published
  OAK package is needed. Keep the matching installation for future requests.
- 'When installation is declined, continue authoring and say: Programmatic validation
  was not performed (installation declined). Do not run the installer.'
- When Python, network, dependencies, or execution are unavailable, continue authoring
  and state the actual reason validation was not performed.
- Exit 0 means parse and resolution checks passed, 1 means invalid, and 2 means not
  performed. Report the actual checks, revision, and errors; never imply execution
  or semantic correctness was proved.
- Keep validation status outside the authored OAK document. Repair reported authoring
  errors and recheck only under the same user permission. Do not silently switch validator
  revisions.
>>

guide-10-validator-script: TEXT<<
"""Optional, consent-gated OAK validation. The authoring skill needs no Python.

Run: python scripts/validate.py document.oak.md [--root document-directory]
Exit 0: valid; 1: invalid; 2: not performed (including permission required).
Only --allow-install permits downloads and an isolated dependency installation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from urllib.request import urlopen
import venv
from zipfile import BadZipFile, ZipFile

SKILL_VERSION = "2.2.0"
REPOSITORY = "chris-buckley/open-agent-knowledge"
REVISION = "2b542c613c5d1a7e64b597884fae4f444ac34916"
SOURCE_SHA256 = "e9c301a254ec8897698816091bac99cc117d8e0fa052192e728d356d19c27bd1"
PROJECT_SHA256 = "2412c436c0ffaa05c604da2d58be4b72c443b37efcaa094380845fd0fe3a3702"
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024


def package_digest(package: Path) -> str:
    """Identify all validator Python sources, not the project's placeholder version."""
    digest = hashlib.sha256()
    files = sorted(package.rglob("*.py"))
    if not files or not (package / "__init__.py").is_file():
        raise ValueError("OAK package sources are missing")
    for path in files:
        digest.update(path.relative_to(package).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def activate(source: Path | None) -> None:
    """Verify matching code before importing it in the selected interpreter."""
    if source is not None:
        package = source.resolve() / "oak"
    else:
        spec = importlib.util.find_spec("oak")
        if spec is None or spec.origin is None:
            raise ValueError("no OAK installation in this interpreter")
        package = Path(spec.origin).parent
    if package_digest(package) != SOURCE_SHA256:
        raise ValueError("OAK source fingerprint does not match this skill")
    if source is not None:
        sys.path.insert(0, str(source.resolve()))
    import oak  # Imports and dependency checks happen only after identity verification.

    if Path(oak.__file__).resolve().parent != package.resolve():
        raise ValueError("a different OAK installation was imported")


def report(status: str, **details: object) -> None:
    print(json.dumps({"status": status, "revision": REVISION, **details}, ensure_ascii=False))


def cache_directory() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "oak" / "validators"


def environment_python(directory: Path) -> Path:
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def command(python: Path, source: Path | None, *arguments: str) -> list[str]:
    values = [str(python), "-I", str(Path(__file__).resolve()), *arguments]
    if source is not None:
        values.extend(("--source", str(source.resolve())))
    return values


def matches(python: Path, source: Path | None) -> bool:
    try:
        result = subprocess.run(
            command(python, source, "--probe"), capture_output=True, text=True,
            timeout=30, check=False,
        )
        return result.returncode == 0 and json.loads(result.stdout).get("status") == "matching"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def installation_path(cache: Path) -> Path:
    return cache / f"{REVISION}-py{sys.version_info.major}.{sys.version_info.minor}"


def discover(args: argparse.Namespace, destination: Path) -> tuple[Path, Path | None] | None:
    """Check only explicit, adjacent, current-interpreter, and exact-cache locations."""
    python = Path(args.python or sys.executable)
    candidates: list[tuple[Path, Path | None]] = []
    if args.source is not None:
        candidates.append((python, args.source))
    else:
        script = Path(__file__).resolve()
        if len(script.parents) >= 4:
            adjacent = script.parents[3]
            if (adjacent / "oak" / "__init__.py").is_file():
                candidates.append((python, adjacent))
        candidates.append((python, None))
    candidates.append((environment_python(destination / "environment"), destination / "source"))
    for candidate in candidates:
        if matches(*candidate):
            return candidate
    return None


def extract_archive(archive: Path, destination: Path) -> None:
    """Extract pinned source without traversal, symlinks, or zip-bomb expansion."""
    prefix = f"open-agent-knowledge-{REVISION}"
    with ZipFile(archive) as bundle:
        if sum(item.file_size for item in bundle.infolist()) > MAX_ARCHIVE_BYTES:
            raise ValueError("OAK source archive exceeds the extraction limit")
        for item in bundle.infolist():
            path = PurePosixPath(item.filename)
            if (not path.parts or path.parts[0] != prefix or path.is_absolute()
                    or ".." in path.parts or "\\" in item.filename
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError("unsafe or unexpected OAK source archive entry")
            relative = Path(*path.parts[1:])
            # Only the validator and its dependency declaration are needed at runtime.
            if not relative.parts or relative.parts[0] not in {"oak", "pyproject.toml"}:
                continue
            target = destination / relative
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(item) as incoming, target.open("wb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
    if package_digest(destination / "oak") != SOURCE_SHA256:
        raise ValueError("downloaded OAK sources do not match the pinned revision")
    if hashlib.sha256((destination / "pyproject.toml").read_bytes()).hexdigest() != PROJECT_SHA256:
        raise ValueError("downloaded dependency declaration does not match the pin")


def install(cache: Path) -> tuple[Path, Path]:
    """Install only after caller consent; keep a ready environment for later calls."""
    destination = installation_path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    lock = destination.with_name(destination.name + ".lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError(f"another installation owns {lock}; validation was not performed") from None
    created = False
    try:
        python = environment_python(destination / "environment")
        source = destination / "source"
        if matches(python, source):
            return python, source
        if destination.exists():
            # Never delete an unrecognized user directory or silently repair a broken cache.
            raise RuntimeError(f"inspect and remove the incomplete cache before retrying: {destination}")
        destination.mkdir()
        created = True
        with tempfile.TemporaryDirectory(prefix="oak-download-", dir=cache) as temporary:
            archive = Path(temporary) / "source.zip"
            url = f"https://codeload.github.com/{REPOSITORY}/zip/{REVISION}"
            with urlopen(url, timeout=60) as incoming, archive.open("wb") as outgoing:
                total = 0
                while chunk := incoming.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_ARCHIVE_BYTES:
                        raise ValueError("OAK download exceeds the archive limit")
                    outgoing.write(chunk)
            extract_archive(archive, source)
        project = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        dependencies = project["dependencies"]
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            raise ValueError("invalid pinned dependency list")
        venv.EnvBuilder(with_pip=True).create(destination / "environment")
        subprocess.run(
            [str(python), "-I", "-m", "pip", "--isolated", "install",
             "--disable-pip-version-check", *dependencies],
            check=True, stdout=sys.stderr, stderr=sys.stderr, timeout=600,
        )
        if not matches(python, source):
            raise RuntimeError("installed validator failed its identity or dependency check")
        (destination / "installation.json").write_text(
            json.dumps({"revision": REVISION, "source_sha256": SOURCE_SHA256,
                        "project_sha256": PROJECT_SHA256}, indent=2) + "\n", encoding="utf-8",
        )
        return python, source
    except BaseException:
        if created:
            shutil.rmtree(destination, ignore_errors=True)
        raise
    finally:
        lock.rmdir()


def oak_body(text: str, path: Path) -> str:
    """The standard skill entry may wrap its OAK body in YAML frontmatter."""
    if path.name == "SKILL.md" and text.startswith("---\n"):
        _metadata, separator, body = text[4:].partition("\n---\n")
        if not separator:
            raise ValueError("SKILL.md frontmatter is not closed")
        return body.lstrip("\n")
    return text


def validate(paths: list[Path], boundary: Path | None) -> int:
    """Parse and resolve data only. Never execute an authored process or tool."""
    from oak import parse, resolve

    results = []
    for path in paths:
        path = path.resolve()
        root = boundary.resolve() if boundary is not None else path.parent
        try:
            if not path.is_relative_to(root):
                raise ValueError("document is outside the explicit document root")

            def load(name: str) -> str | None:
                target = Path(name).resolve()
                if not target.is_relative_to(root):
                    raise ValueError("document reference escapes the document root")
                return target.read_text(encoding="utf-8") if target.is_file() else None

            node = parse(oak_body(path.read_text(encoding="utf-8"), path))
            # SKILL.md has a virtual OAK identity in the same directory, not an import.
            identity = path if path.name.endswith(".oak.md") else path.with_name(path.stem + ".oak.md")
            graph = resolve(node, source=identity.as_posix(), load=load, root=root.as_posix())
            results.append({"path": str(path), "status": "valid", "documents": len(graph.documents)})
        except Exception as error:
            results.append({"path": str(path), "status": "invalid", "error": str(error)})
    valid = all(item["status"] == "valid" for item in results)
    report("valid" if valid else "invalid", checks=["parse", "resolve"], results=results)
    return 0 if valid else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents", type=Path, nargs="*")
    parser.add_argument("--root", type=Path, help="allowed root for explicit document references")
    parser.add_argument("--source", type=Path, help="existing matching OAK repository root")
    parser.add_argument("--python", type=Path, help="interpreter for an existing validator installation")
    parser.add_argument("--cache-dir", type=Path, default=cache_directory())
    parser.add_argument("--allow-install", action="store_true", help="user approved the download and isolated installation")
    parser.add_argument("--probe", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.probe or args.worker:
            activate(args.source)
            if args.probe:
                report("matching")
                return 0
            if not args.documents:
                raise ValueError("no document was supplied")
            return validate(args.documents, args.root)
        if not args.documents:
            parser.error("supply at least one OAK document or SKILL.md")
        destination = installation_path(args.cache_dir.resolve())
        selected = discover(args, destination)
        if selected is None:
            if not args.allow_install:
                report("not-performed", reason="permission-required", detail=(
                    "Programmatic validation was not performed. Ask permission to download "
                    "the pinned OAK revision and install dependencies in an isolated cached "
                    "environment. Continue authoring if permission is declined."))
                return 2
            selected = install(args.cache_dir.resolve())
        arguments = ["--worker"]
        if args.root is not None:
            arguments.extend(("--root", str(args.root.resolve())))
        arguments.extend(str(path.resolve()) for path in args.documents)
        return subprocess.run(command(*selected, *arguments), check=False).returncode
    except (OSError, ValueError, RuntimeError, BadZipFile, subprocess.SubprocessError) as error:
        report("not-performed", reason="validator-unavailable", detail=str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
>>
~~~~

~~~~schemas
~~~schema;id="authoring-request"
SOURCE: <SOURCE>
VALIDATE: <VALIDATE>

WHERE:
- <SOURCE> is string; is non-empty.
- <VALIDATE> is boolean.
~~~

~~~schema;id="oak-candidate"
CANDIDATE: <CANDIDATE>

WHERE:
- <CANDIDATE> is string; is non-empty.
~~~

~~~schema;id="authoring-result"
OAK: <OAK>
VALIDATION: <VALIDATION>

WHERE:
- <OAK> is string; is non-empty.
- <VALIDATION> is string; is non-empty.
~~~

~~~schema;id="validator-check"
INSTALL_REQUIRED: <INSTALL_REQUIRED>
REPORT: <REPORT>

WHERE:
- <INSTALL_REQUIRED> is boolean.
- <REPORT> is string; is non-empty.
~~~

~~~schema;id="installation-consent"
APPROVED: <APPROVED>

WHERE:
- <APPROVED> is boolean.
~~~

~~~schema;id="validation-context"
CANDIDATE: <CANDIDATE>
REPORT: <REPORT>
ALLOW_INSTALL: <ALLOW_INSTALL>

WHERE:
- <CANDIDATE> is string; is non-empty.
- <REPORT> is string; is non-empty.
- <ALLOW_INSTALL> is boolean.
~~~

~~~schema;id="guide-2-option-comparison";name="Option Comparison";purpose="Compare current and proposed behaviour for one criterion."
| Criterion | Current | Proposed |
| --- | --- | --- |
| <CRITERION> | <CURRENT> | <PROPOSED> |

WHERE:
- <CRITERION> is string; matches `^[^|\r\n]+$`.
- <CURRENT> is string; matches `^[^|\r\n]+$`.
- <PROPOSED> is string; matches `^[^|\r\n]+$`.
~~~

~~~schema;id="guide-2-decision-brief";name="Decision Brief";purpose="State one decision and explain its rationale."
## Decision
<DECISION>

### Rationale
<RATIONALE>

WHERE:
- <DECISION> is string; is non-empty.
- <RATIONALE> is string; is non-empty.
~~~

~~~schema;id="guide-2-work-outline";name="Work Outline";purpose="Nest one implementation step and its check beneath one goal."
1. <GOAL>
   1. <STEP>
      1. <CHECK>

WHERE:
- <GOAL> is string; is non-empty; is one line.
- <STEP> is string; is non-empty; is one line.
- <CHECK> is string; is non-empty; is one line.
~~~

~~~schema;id="guide-2-code-file";name="Code File";purpose="Present one Python file with its complete source."
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
authoring-requested(
  event="OAK authoring is requested for supplied source material.",
  process=process.capture-request,
)
request-received(
  event="A complete OAK authoring request is received.",
  source=interface.authoring-input,
  process=process.author-document,
)
~~~~

~~~~processes
~~~process;id="capture-request";name="Capture request"
ACT output="schema.authoring-request": Capture the complete supplied source as <SOURCE> and set <VALIDATE> true only when programmatic validation was requested; otherwise false. () -> SOURCE, VALIDATE
CALL process.author-document (SOURCE=$SOURCE, VALIDATE=$VALIDATE)
~~~

~~~process;id="author-document";name="Author document";input="schema.authoring-request"
ACT Use <STRUCTURE> and the complete supplied <SOURCE> to establish <SCOPE>; consult the rest of that structure guide only as needed. (
  STRUCTURE=$constant.guide-1-guidance,
  SOURCE=$SOURCE,
) -> SCOPE
ACT Apply <GUIDANCE> to <SCOPE> and <SOURCE> to decide schemas; omit unjustified entries and produce <DESIGN_1>. Use the supplied schema definitions and their <POPULATED> instances to preserve the requested information shape. (
  GUIDANCE=$constant.guide-2-guidance,
  SCOPE=$SCOPE,
  SOURCE=$SOURCE,
  POPULATED=$constant.guide-2-populated-shapes,
) -> DESIGN_1
ACT Apply <GUIDANCE> to <DESIGN_1> and <SOURCE> to decide constants; omit unjustified entries and produce <DESIGN_2>. (
  GUIDANCE=$constant.guide-3-guidance,
  DESIGN_1=$DESIGN_1,
  SOURCE=$SOURCE,
) -> DESIGN_2
ACT Apply <GUIDANCE> to <DESIGN_2> and <SOURCE> to decide state; omit unjustified entries and produce <DESIGN_3>. (
  GUIDANCE=$constant.guide-4-guidance,
  DESIGN_2=$DESIGN_2,
  SOURCE=$SOURCE,
) -> DESIGN_3
ACT Apply <GUIDANCE> to <DESIGN_3> and <SOURCE> to decide interfaces; omit unjustified entries and produce <DESIGN_4>. (
  GUIDANCE=$constant.guide-5-guidance,
  DESIGN_3=$DESIGN_3,
  SOURCE=$SOURCE,
) -> DESIGN_4
ACT Apply <GUIDANCE> to <DESIGN_4> and <SOURCE> to decide triggers; omit unjustified entries and produce <DESIGN_5>. (
  GUIDANCE=$constant.guide-6-guidance,
  DESIGN_4=$DESIGN_4,
  SOURCE=$SOURCE,
) -> DESIGN_5
ACT Apply <GUIDANCE> to <DESIGN_5> and <SOURCE> to decide processes; omit unjustified entries and produce <DESIGN_6>. (
  GUIDANCE=$constant.guide-7-guidance,
  DESIGN_5=$DESIGN_5,
  SOURCE=$SOURCE,
) -> DESIGN_6
ACT Apply <GUIDANCE> to <DESIGN_6> and <SOURCE> to decide instructions; omit unjustified entries and produce <DESIGN_7>. (
  GUIDANCE=$constant.guide-8-guidance,
  DESIGN_6=$DESIGN_6,
  SOURCE=$SOURCE,
) -> DESIGN_7
ACT Review <DESIGN_7> against <REVIEW>, <GRAMMAR>, and the complete scenarios in <TEACHING>. Produce <CANDIDATE> as one OAK node in canonical section order, without claiming a programmatic check. (
  DESIGN_7=$DESIGN_7,
  REVIEW=$constant.guide-9-review,
  GRAMMAR=$constant.guide-9-oak-ebnf,
  TEACHING=$constant.guide-9-teaching,
) -> CANDIDATE
IF $VALIDATE equals true:
  CALL process.validate-and-deliver (CANDIDATE=$CANDIDATE)
ELSE:
  EMIT interface.authored-document (
    OAK=$CANDIDATE,
    VALIDATION="Programmatic validation was not performed (not requested).",
  )
~~~

~~~process;id="validate-and-deliver";name="Check validator";input="schema.oak-candidate"
ACT output="schema.validator-check": Apply <POLICY> to check <CANDIDATE> with the exact <HELPER> without --allow-install. Reuse matching code when available. Return the actual <REPORT> and set <INSTALL_REQUIRED> true only for permission-required, not for invalid OAK or an unavailable execution tool. (
  POLICY=$constant.guide-10-validation-policy,
  HELPER=$constant.guide-10-validator-script,
  CANDIDATE=$CANDIDATE,
) -> INSTALL_REQUIRED, REPORT
IF $INSTALL_REQUIRED equals true:
  ACT output="schema.installation-consent": Ask the user for permission to download the OAK revision in <IDENTITY> and install its dependencies in an isolated retained environment. Set <APPROVED> true only after explicit approval; a validation request alone is not approval. (
    IDENTITY=$constant.guide-10-identity,
  ) -> APPROVED
  IF $APPROVED equals true:
    CALL process.finalize-validation (CANDIDATE=$CANDIDATE, REPORT=$REPORT, ALLOW_INSTALL=true)
  ELSE:
    EMIT interface.authored-document (
      OAK=$CANDIDATE,
      VALIDATION="Programmatic validation was not performed (installation declined).",
    )
ELSE:
  CALL process.finalize-validation (CANDIDATE=$CANDIDATE, REPORT=$REPORT, ALLOW_INSTALL=false)
~~~

~~~process;id="finalize-validation";name="Report validation";input="schema.validation-context"
ACT output="schema.authoring-result": Use <REPORT> for <CANDIDATE> under <POLICY>. With <ALLOW_INSTALL> true, run the exact <HELPER> with --allow-install; otherwise never download or install. Repair reported authoring errors when possible and recheck changed documents under the same permission. Do not rerun an unchanged successful check. Produce <OAK> and truthful <VALIDATION>, including errors or why a check could not run. (
  REPORT=$REPORT,
  CANDIDATE=$CANDIDATE,
  ALLOW_INSTALL=$ALLOW_INSTALL,
  POLICY=$constant.guide-10-validation-policy,
  HELPER=$constant.guide-10-validator-script,
) -> OAK, VALIDATION
EMIT interface.authored-document
~~~
~~~~

~~~~interfaces
authoring-input RECEIVES schema.authoring-request
authored-document EMITS schema.authoring-result
~~~~
