<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Treat the complete supplied host context as the source, regardless of modality.
Map directives, policies, interpretation rules, and required behaviour to instructions.
Map stable values needed during use to constants.
Map reusable information shapes and contracts to schemas.
Map values that persist and can change across arrivals to state.
Map outside events, receive sources, state guards, and selected work to triggers.
Map ordered local work to processes.
Map complete document-boundary crossings to one-way interfaces.
Omit every part and entry that the source does not justify.
Do not invent state, triggers, processes, interfaces, tools, or relative paths.
Write one idless node using only the seven parts in canonical order.
Use constants for fixed values, state for values across arrivals, process bindings for local values, and interfaces for boundary instances.
Use the shortest unambiguous names and reuse one exact domain noun across parts.
Start each process id with an exact base-form action verb and name the result it establishes.
Give reusable process phases input and output schemas when their values need contracts.
Keep multi-phase entry processes as orchestrators that compose reusable processes with `CALL`.
Keep pipeline values in process bindings and use state only for values that must survive an arrival.
Route each receive interface through one source-backed trigger into a process with the same resolved input schema.
Use plain `ACT` when the interpreter performs the work with native capabilities.
Use `ACT TOOL` only for one exact tool name copied from the supplied registry.
Keep tool implementations, handlers, transport, credentials, model selection, and server configuration in the host.
Use `PAR` and `JOIN` only for independent exact tool actions.
Model a delegated agent as its own typed OAK document and dispatch it through an exact host tool contract.
Bind constants, state, processes, actions, and interfaces to schemas where values must validate.
Emit one complete schema instance and use inferred `EMIT` only when same-named visible bindings satisfy it.
Check the draft against the supplied grammar, example, and every stated OAK contract.
Produce exactly one valid OAK document.
Emit the final OAK document as the sole response.
</instructions>

<constants>
architecture-capsule: TEXT<<
One UTF-8 OAK document contains one idless node.
The node has only instructions, constants, schemas, state, triggers, processes, and interfaces.
Schemas define reusable information shapes independently of boundaries and processes.
Constants are fixed, state persists across arrivals, process bindings are local, and interfaces carry complete boundary instances.
Target paths connect documents into a graph; local state and interface operations stay in the active document.
Triggers route outside occurrences; CALL composes internal process work.
OAK text is the default authored render; JSON-LD is the interchange render.
The host owns tools, credentials, transport, model selection, external side effects, persistence, and deployment.
>>

oak-ebnf: TEXT<<
oak_document = xml_document ;
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
xml_body_entry = "<", entry_tag, attributes, ">", lf, text_body, "</", entry_tag, ">" ;
entry_tag = "schema" | "process" ;
trigger_fact = "trigger.", slug_id, ".", trigger_field, " := ", trigger_value ;
trigger_field = "event" | "source" | "guard" | "process" | ( "seed.", placeholder ) ;
trigger_value = ? one field-typed value; a composite guard continues on indented condition lines ? ;
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
surface_value_binding_line = ? <PLACEHOLDER>=<VALUE> ? ;
surface_condition_compare = ? <LEFT> <OPERATOR> <RIGHT> ? ;
surface_condition_all = ? ALL:
  <CONDITIONS> ? ;
surface_condition_any = ? ANY:
  <CONDITIONS> ? ;
surface_condition_not = ? NOT:
  <CONDITION> ? ;
surface_act_native = ? ACT input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_act_tool = ? ACT TOOL "<TOOL>" input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_step_set = ? SET <STATE> = <VALUE> ? ;
surface_step_emit_inferred = ? EMIT <INTERFACE> ? ;
surface_step_emit_explicit = ? EMIT <INTERFACE> (<BINDINGS>) ? ;
surface_step_if = ? IF <CONDITION>:
THEN:
  <THEN>
ELSE:
  <OTHERWISE> ? ;
surface_step_call = ? CALL <PROCESS> (<INPUTS>) -> <OUTPUTS> ? ;
surface_step_fail = ? FAIL <MESSAGE> ? ;
surface_step_assert = ? ASSERT <CONDITION>
MESSAGE <MESSAGE> ? ;
surface_step_foreach = ? FOREACH <BINDING> IN <VALUE>:
  <STEPS> ? ;
surface_step_while = ? WHILE <CONDITION> LIMIT <LIMIT>:
  <STEPS> ? ;
surface_step_par = ? PAR:
  <STEPS> ? ;
surface_step_join = ? JOIN ? ;
surface_process = ? <process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<STEPS>
</process> ? ;
surface_trigger = ? trigger.<ID>.event := <EVENT>
trigger.<ID>.source := <SOURCE>
trigger.<ID>.guard := <GUARD>
trigger.<ID>.process := <PROCESS>
trigger.<ID>.seed.<SEED> ? ;
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

canonical-oak: TEXT<<
<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Classify each support request by urgency.
</instructions>

<constants>
urgent-terms: ["outage", "security"]
</constants>

<schemas>
<schema id="support-request" name="Support Request" purpose="Carry one support request into classification.">
Message: <MESSAGE>

WHERE:
- <MESSAGE> is string; is non-empty; the support request text.
</schema>

<schema id="support-result" name="Support Result" purpose="Carry one classified support request.">
Priority: <PRIORITY>
Summary: <SUMMARY>

WHERE:
- <PRIORITY> is string; is one of `urgent`, `normal`; the assigned urgency.
- <SUMMARY> is string; is non-empty; the concise request summary.
</schema>

<schema id="workflow-state" name="Workflow State" purpose="Constrain the persistent classification state.">
Status: <STATUS>

WHERE:
- <STATUS> is string; is one of `idle`, `running`; the current workflow status.
</schema>
</schemas>

<state>
review-status AS schema.workflow-state.STATUS: "idle"
</state>

<triggers>
trigger.support-requested.event := "A support request is supplied."
trigger.support-requested.source := interface.request
trigger.support-requested.guard := $state.review-status equals "idle"
trigger.support-requested.process := process.classify-request
</triggers>

<processes>
<process id="classify-request" name="Classify request" input="schema.support-request" output="schema.support-result">
SET state.review-status = "running"
ACT output="schema.support-result": Classify <MESSAGE> using <URGENT_TERMS>, then produce <PRIORITY> and <SUMMARY>. (MESSAGE=$MESSAGE, URGENT_TERMS=$constant.urgent-terms) -> PRIORITY, SUMMARY
EMIT interface.result
SET state.review-status = "idle"
</process>
</processes>

<interfaces>
request RECEIVES schema.support-request
result EMITS schema.support-result
</interfaces>
>>
</constants>

<schemas>
<schema id="oak-document" name="OAK Document" purpose="Carry the one valid OAK document written from the supplied source.">
<OAK>

WHERE:
- <OAK> is string; is non-empty; the complete valid OAK document.
</schema>
</schemas>

<triggers>
trigger.source-supplied.event := "Any source material is supplied with this prompt."
trigger.source-supplied.process := process.write-oak
</triggers>

<processes>
<process id="write-oak" name="Write OAK" output="schema.oak-document">
ACT Derive <DRAFT> from the complete supplied source. () -> DRAFT
ACT Validate <DRAFT> against the supplied architecture, grammar, example, and OAK contracts, then produce <OAK>. (DRAFT=$DRAFT) -> OAK
EMIT interface.oak-document-output
</process>
</processes>

<interfaces>
oak-document-output EMITS schema.oak-document: "The sole OAK document returned to the caller."
</interfaces>
