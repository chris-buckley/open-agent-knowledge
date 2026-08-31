<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and THEN omit $.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.

Treat the complete supplied host context as the source, regardless of modality.
Map directives, policies, interpretation rules, and required behaviour to instructions.
Map stable values needed during use to constants.
Map reusable information shapes and output contracts to schemas.
Map values that can change while the knowledge runs to state.
Map arrival reasons, state guards, and selected processes to triggers.
Map ordered ways to perform tasks to processes.
Map verifiable document-boundary crossings to interfaces.
Leave a part empty when the source provides no justified entry.
Do not invent state, triggers, processes, interfaces, or relative paths.
Write exactly one valid OAK document containing one node.
Emit the final OAK document as the sole response.
Do not require a minimum word count for an entry id.
Use `<verb>-<object>[-<outcome-or-context>]` for process ids.
Start each process id with an exact base-form action verb.
Use `<verb>-<object>` for instruction ids.
Use noun phrases for constant, schema, state, and interface ids.
Use circumstance phrases for trigger ids.
Name each reusable process for what it establishes, not how it works.
Name each query process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<query-action>_<object>` and a non-mutating action (is|has|find|read) (e.g. `find-document` and `Find document`).
Name each command process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<command-action>_<object>` and expose the state change (create|write|publish|delete) (e.g. `publish-report` and `Publish report`).
Name each combined process with matching `SlugId` and two-word `ProcessName` forms that place its mutating action first and use the semantic structure `<command-action>_<object>[_if_<condition>]` (e.g. `create-folder-if-missing` and `Create folder-if-missing`).
Name each verification process with matching `SlugId` and `ProcessName` forms that use the semantic structure `(test|validate|prove)_<object>[_<condition>][_<outcome>]` (e.g. `validate-candidate` and `Validate candidate`).
Define each required log event as a reusable process with the semantic structure `log_<object>_<event>` (e.g. `log-artifact-published` and `Log artifact-published`).
Perform interpreter-native logging with plain `ACT`.
Use `ACT TOOL` only when one exact registered logging tool must perform the logging operation.
Reuse a logging process from other processes with `CALL`.
Name each value with the semantic structure `<role>_<object>_<kind-or-unit>` using a `SlugId` for a constant or state entry and a `Placeholder` for a schema or process binding (e.g. `source-document-file` and `SOURCE_DOCUMENT_FILE`).
Name each collection with the semantic structure `<contents>_<shape>` (e.g. `report-names` as a `SlugId` or `REPORT_NAMES` as a `Placeholder`).
Name each boolean as a positive condition or control (e.g. `is-ready` as a `SlugId` or `IS_READY` as a `Placeholder`).
Name each quantity with the semantic structure `[<context>_]<quantity>_<unit>` (e.g. `poll-interval-seconds` as a `SlugId` or `POLL_INTERVAL_SECONDS` as a `Placeholder`).
Name each identifier value with the semantic structure `<object>_id` (e.g. `document-id` as a `SlugId` or `DOCUMENT_ID` as a `Placeholder`).
Name each mapping with the semantic structure `<key>_to_<value>` (e.g. `filename-to-document-id` as a `SlugId` or `FILENAME_TO_DOCUMENT_ID` as a `Placeholder`).
Represent each variable-like value by its source and lifetime: `CONSTANT` for fixed values, `STATE` for mutable values, a process binding for local immutable values, and an `INTERFACE` binding for boundary values (e.g. `$constant.max-retries`, `$state.current-candidate`, or `$CANDIDATE`).
Use the shortest unambiguous name that states purpose or result and reuses one exact domain noun across every part, including verification processes (e.g. schema `candidate`, state `current-candidate`, process `validate-candidate`, and interface `verified-candidate-output`; do not rename `candidate` as `option` or `proposal`).
Replace generic nouns and vague process verbs with exact domain terms that state purpose or action (e.g. replace (data|item|result|value|config|response|path) with (candidate|verification-step|verified-candidate|retry-limit|validation-rules|review-feedback|source-document-file), and replace (handle|process|manage|do) with (validate|publish|archive|verify)).
Decompose each multi-phase task into one process per phase.
Give each phase process one input schema and one output schema.
Name each contract schema as the information shape it carries.
Keep each multi-phase trigger-selected process an orchestrator of calls and emits.
Do not emit from a phase process.
Keep pipeline values in call contracts; use state only for values that persist between arrivals.
Treat plain `ACT` as the default action form.
Use plain `ACT` when the interpreter performs the instruction with its native capabilities.
No `ACT.tool` means interpreter-native work.
Use `ACT TOOL` only when one exact registered tool must perform the instruction.
Omit `ACT TOOL` when the interpreter may choose how to perform the instruction.
Copy each tool name from the supplied exact tool registry.
Preserve each tool name verbatim.
Do not invent, normalize, or infer a tool name.
Use `CALL` to run another OAK process.
Do not use `ACT TOOL` to run an OAK process.
Keep tool implementations, handlers, transport, credentials, server configuration, and aliases outside the OAK document.
Prefer `ACT TOOL` when stable tool selection, contract validation, auditability, or controlled side effects matter.
An exact tool name fixes which registry entry is selected.
An exact tool name does not guarantee deterministic output.
Require the selected tool itself to provide deterministic behaviour when deterministic output is required.
Expose plain `ACT` as `ACT(instruction, ...)` in direct Python authoring.
Expose named `ACT TOOL` as `ACT.tool(name, instruction, ...)` in direct Python authoring.
Make `ACT(...)` and `ACT.tool(...)` return the existing `Act` model.
Keep `ACT(...)` and `ACT.tool(...)` as one `act` process step kind.
Keep the rendered OAK syntax unchanged.
Do not expose `ACT.infer`.
Do not expose `ACT.use`.
Add no second helper for interpreter-native work.
Model each subagent as one worker OAK document with one in interface and one out interface.
Treat the worker in interface schema as the request contract and the worker out interface schema as the result contract.
Type each dispatch process with relative targets to the worker request and result schemas as its input and output schemas.
Dispatch each worker inside its dispatch process with one exact tool name from the supplied registry.
Prefer one registered portable `agent.<worker>` contract when the host permits registration.
Use the native runner name verbatim when the host does not permit registration.
Give each agent tool contract the worker request placeholders as inputs and the worker result placeholders as outputs.
Keep agent invocation, model selection, and transport in the host registry, outside the OAK document.
Treat the supplied registry as the worker allowlist.
Run parallel workers as `PAR` children, one exact agent tool act per worker.
Keep delegation depth at one: each worker returns its result to the coordinator and dispatches no workers.
Do not dispatch a worker with `CALL`.
`CALL` composes processes inside one interpreter and one transaction.
Treat each dispatch as separate-interpreter host work, not as running an OAK process with `ACT TOOL`.
Treat committed worker effects as external tool effects that the coordinator transaction cannot roll back.
Do not use one act placeholder as both input and output.
Make act instruction placeholders equal its inputs and outputs.
Remove or repair an assertion that is statically false.
Match each call's inputs and outputs to the called process schemas.
Give each ALL or ANY condition at least two children.
Keep the resolved process call graph acyclic.
Use the same columns in every CSV row.
Remove a process branch that cannot run.
Bind each act input placeholder once.
Declare each act output placeholder once.
Bind each emitted placeholder once.
Use each entry id once in one OAK document.
Define each schema placeholder once in WHERE.
Bind every interface schema placeholder exactly once when emitting.
Make every reachable relative document available through the explicit loader.
Make every resolved fragment target exist in its document.
Read and emit interfaces only in the active OAK document.
Supply the referencing document path before resolving a relative target.
Read and write state only in the active OAK document.
Use a new loop binding that does not shadow a visible binding.
Give FOREACH a value that resolves to a JSON list.
Read only in or inout interfaces and emit only out or inout interfaces.
Use only JSON scalar values in CSV cells.
Give each CSV constant one non-empty list of object rows.
Use a relative POSIX document path ending in .oak.md without a scheme, query, or extra fragment.
Keep a lines minimum at or below its maximum.
Make every statically known emission satisfy its interface schema.
Give each TEXT constant one string value.
Do not read an interface or local binding in a trigger guard.
Make every WHERE example satisfy its local constraints.
Put JOIN immediately after one PAR.
Give each lines constraint a minimum, maximum, or both.
Target an entry that exists in the current OAK document.
Order only two numbers or two strings without coercion.
Make equal trigger WHEN values provably disjoint.
Follow a final PAR with JOIN.
Put no step between PAR and JOIN.
Give every PAR child a distinct output binding.
Put only exact named-tool acts inside PAR.
Make the template and WHERE placeholder sets equal.
Do not redefine a visible immutable process binding.
Keep the local process call graph acyclic.
Make every process output schema placeholder visible after successful completion.
Remove an assertion that is statically true.
Match a named tool's declared input and output contract.
Use a tool in PAR only when its supplied registry confirms parallel use.
Give every non-true trigger guard at least one state read.
Select only a process without an input schema from a trigger.
Read only a visible prior process-local binding.
Reference only another placeholder in the same schema.
Read a placeholder present in the interface schema.
Name a tool exposed by the supplied exact tool registry.
Remove a process step after a path that always fails.
Do not give examples to a WHERE entry with placeholder-valued bounds.
Target the part required by the typed reference field.
</instructions>

<constants>
oak-ebnf: TEXT<<
oak_document = xml_document | markdown_document ;
xml_document = xml_instructions_part, blank_line, xml_constants_part, blank_line, xml_schemas_part, blank_line, xml_state_part, blank_line, xml_triggers_part, blank_line, xml_processes_part, blank_line, xml_interfaces_part ;
xml_instructions_part = "<instructions>", lf, text_body, "</instructions>" ;
xml_constants_part = "<constants>", lf, text_body, "</constants>" ;
xml_schemas_part = "<schemas>", lf, text_body, "</schemas>" ;
xml_state_part = "<state>", lf, text_body, "</state>" ;
xml_triggers_part = "<triggers>", lf, text_body, "</triggers>" ;
xml_processes_part = "<processes>", lf, text_body, "</processes>" ;
xml_interfaces_part = "<interfaces>", lf, text_body, "</interfaces>" ;
markdown_document = markdown_instructions_part, blank_line, markdown_constants_part, blank_line, markdown_schemas_part, blank_line, markdown_state_part, blank_line, markdown_triggers_part, blank_line, markdown_processes_part, blank_line, markdown_interfaces_part ;
markdown_instructions_part = "~~~~instructions", lf, text_body, "~~~~" ;
markdown_constants_part = "~~~~constants", lf, text_body, "~~~~" ;
markdown_schemas_part = "~~~~schemas", lf, text_body, "~~~~" ;
markdown_state_part = "~~~~state", lf, text_body, "~~~~" ;
markdown_triggers_part = "~~~~triggers", lf, text_body, "~~~~" ;
markdown_processes_part = "~~~~processes", lf, text_body, "~~~~" ;
markdown_interfaces_part = "~~~~interfaces", lf, text_body, "~~~~" ;
xml_body_entry = "<", entry_tag, attributes, ">", lf, text_body, "</", entry_tag, ">" ;
markdown_body_entry = "~~~", entry_tag, markdown_attributes, lf, text_body, "~~~" ;
entry_tag = "schema" | "trigger" | "process" | "interface" ;
constant = inline_constant | text_constant | json_constant | csv_constant | yaml_constant ;
inline_constant = slug_id, ": ", json_value ;
text_constant = slug_id, ": TEXT<<", lf, text_body, ">>" ;
json_constant = slug_id, ": JSON<<", lf, json_value, lf, ">>" ;
csv_constant = slug_id, ": CSV<<", lf, csv_body, lf, ">>" ;
yaml_constant = slug_id, ": YAML<<", lf, yaml_body, lf, ">>" ;
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
dotted_path = ( "constant" | "schema" | "state" | "process" | "interface" ), ".", slug_id, [ ".", placeholder ] ;
value_reference = "$", ( placeholder | constant_target | state_target | interface_value_path ) ;
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
surface_constant_inline = ? <ID>: <VALUE> ? ;
surface_constant_text = ? <ID>: TEXT<<
<VALUE>
>> ? ;
surface_constant_json = ? <ID>: JSON<<
<VALUE>
>> ? ;
surface_constant_csv = ? <ID>: CSV<<
<VALUE>
>> ? ;
surface_constant_yaml = ? <ID>: YAML<<
<VALUE>
>> ? ;
surface_schema = ? <schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">
<TEMPLATE>

WHERE:
<WHERE>
</schema> ? ;
surface_state = ? <ID>: <VALUE> ? ;
surface_value_literal = ? <VALUE> ? ;
surface_value_constant = ? $<CONSTANT> ? ;
surface_value_state = ? $<STATE> ? ;
surface_value_interface = ? $<INTERFACE>.<PLACEHOLDER> ? ;
surface_value_binding = ? $<BINDING> ? ;
surface_value_binding_line = ? <PLACEHOLDER>=<VALUE> ? ;
surface_condition_compare = ? <LEFT> <OPERATOR> <RIGHT> ? ;
surface_condition_all = ? ALL:
  <CONDITIONS> ? ;
surface_condition_any = ? ANY:
  <CONDITIONS> ? ;
surface_condition_not = ? NOT:
  <CONDITION> ? ;
surface_act_native = ? ACT <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_act_tool = ? ACT TOOL "<TOOL>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_step_set = ? SET <STATE> = <VALUE> ? ;
surface_step_emit = ? EMIT <INTERFACE> (<BINDINGS>) ? ;
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
surface_trigger = ? <trigger id="<ID>">
GIVEN: <GIVEN>
WHEN: <WHEN>
THEN: <THEN>
</trigger> ? ;
surface_interface = ? <interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">
<DESCRIPTION>
</interface> ? ;
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
Use the supplied schema.
</instructions>

<constants>
</constants>

<schemas>
</schemas>

<state>
</state>

<triggers>
</triggers>

<processes>
</processes>

<interfaces>
</interfaces>
>>

orchestrator-example: TEXT<<
<process id="implement-task" name="Implement task">
CALL process.plan-task (TASK_BRIEF=$interface.task-request-input.TASK_BRIEF, CONTEXT=$interface.task-request-input.CONTEXT) -> PLAN
CALL process.implement-plan (PLAN=$PLAN) -> CHANGESET
CALL process.test-changeset (CHANGESET=$CHANGESET) -> TESTS
CALL process.review-changeset (PLAN=$PLAN, CHANGESET=$CHANGESET) -> FINDINGS
EMIT interface.implementation-report-output (CHANGESET=$CHANGESET, TESTS=$TESTS, FINDINGS=$FINDINGS)
</process>
>>
</constants>

<schemas>
<schema id="constraint-type" name="Type" purpose="The bound value has one datatype from the vocabulary catalog.">
is <OF>

WHERE:
- <OF> is string; is non-empty; The datatype name..
</schema>

<schema id="constraint-one-of" name="OneOf" purpose="The bound value is one of the listed values.">
is one of <VALUES>

WHERE:
- <VALUES> is string; is non-empty; The allowed values..
</schema>

<schema id="constraint-regex" name="Regex" purpose="The bound value matches one anchored portable rust-regex pattern.">
matches `<PATTERN>`

WHERE:
- <PATTERN> is string; is non-empty; The whole-value portable pattern..
</schema>

<schema id="constraint-non-empty" name="NonEmpty" purpose="The bound value has at least one character or item.">
is non-empty

WHERE:
</schema>

<schema id="constraint-max-chars" name="MaxChars" purpose="The bound value has at most n characters.">
is at most <N> characters

WHERE:
- <N> is string; is non-empty; The character limit..
</schema>

<schema id="constraint-lines" name="Lines" purpose="The bound value has one positive line-count bound.">
has <MIN> to <MAX> lines

WHERE:
- <MIN> is string; The fewest lines..
- <MAX> is string; The most lines..
</schema>

<schema id="constraint-list-of" name="ListOf" purpose="The bound value is items of one datatype joined by one separator.">
is a list of <ITEM> joined by `<SEPARATOR>`

WHERE:
- <ITEM> is string; is non-empty; The datatype of every item..
- <SEPARATOR> is string; is non-empty; The text between items..
</schema>

<schema id="constraint-at-least" name="AtLeast" purpose="The bound value is at least a number or another placeholder value.">
is at least <VALUE>

WHERE:
- <VALUE> is string; is non-empty; A number or a placeholder of the same schema..
</schema>

<schema id="constraint-at-most" name="AtMost" purpose="The bound value is at most a number or another placeholder value.">
is at most <VALUE>

WHERE:
- <VALUE> is string; is non-empty; A number or a placeholder of the same schema..
</schema>

<schema id="where" name="Where" purpose="One placeholder, its constraints, examples, and description.">
- <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>.

WHERE:
- <PLACEHOLDER> is string; is non-empty; The bare placeholder name..
- <CONSTRAINTS> is string; is non-empty; The constraints every bound value must satisfy..
- <EXAMPLES> is string; Values that satisfy every locally resolvable constraint..
- <DESCRIPTION> is string; What the placeholder holds, in one line..
</schema>

<schema id="instruction" name="Instruction" purpose="One rule the interpreter must follow.">
<BODY>

WHERE:
- <BODY> is string; is non-empty; One directive or declarative rule..
</schema>

<schema id="constant-inline" name="Constant constant-inline" purpose="One value that stays the same during use.">
<ID>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-text" name="Constant constant-text" purpose="One value that stays the same during use.">
<ID>: TEXT<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-json" name="Constant constant-json" purpose="One value that stays the same during use.">
<ID>: JSON<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-csv" name="Constant constant-csv" purpose="One value that stays the same during use.">
<ID>: CSV<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-yaml" name="Constant constant-yaml" purpose="One value that stays the same during use.">
<ID>: YAML<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="schema" name="Schema" purpose="One reusable information shape with one Where per placeholder.">
<schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">
<TEMPLATE>

WHERE:
<WHERE>
</schema>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; The display name..
- <PURPOSE> is string; What the information shape is for..
- <TEMPLATE> is string; is non-empty; The literal shape with variable parts written as <PLACEHOLDER>..
- <WHERE> is string; One Where per distinct template placeholder, in authored order..
</schema>

<schema id="state" name="State" purpose="One JSON value that can change while the interpreter runs.">
<ID>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The JSON value that can change..
</schema>

<schema id="value-literal" name="LiteralValue" purpose="One authored JSON value.">
<VALUE>

WHERE:
- <VALUE> is string; is non-empty; The authored JSON value..
</schema>

<schema id="value-constant" name="ConstantValue" purpose="One value read from a local or relative constant entry.">
$<CONSTANT>

WHERE:
- <CONSTANT> is string; is non-empty; The local or relative constant target to read..
</schema>

<schema id="value-state" name="StateValue" purpose="One value read from local state.">
$<STATE>

WHERE:
- <STATE> is string; is non-empty; The local state target to read..
</schema>

<schema id="value-interface" name="InterfaceValue" purpose="One placeholder value read from one active local input interface.">
$<INTERFACE>.<PLACEHOLDER>

WHERE:
- <INTERFACE> is string; is non-empty; The active local input interface target to read..
- <PLACEHOLDER> is string; is non-empty; The interface schema placeholder to read..
</schema>

<schema id="value-binding" name="BindingValue" purpose="One value read from a visible process-local binding.">
$<BINDING>

WHERE:
- <BINDING> is string; is non-empty; The visible process-local binding to read..
</schema>

<schema id="value-binding-line" name="ValueBinding" purpose="One placeholder bound to one process value.">
<PLACEHOLDER>=<VALUE>

WHERE:
- <PLACEHOLDER> is string; is non-empty; The placeholder receiving the process value..
- <VALUE> is string; is non-empty; The process value bound to the placeholder..
</schema>

<schema id="condition-compare" name="Compare" purpose="One strict structural or ordered comparison.">
<LEFT> <OPERATOR> <RIGHT>

WHERE:
- <LEFT> is string; is non-empty; The value on the left of the comparison..
- <OPERATOR> is string; is non-empty; The strict comparison operator..
- <RIGHT> is string; is non-empty; The value on the right of the comparison..
</schema>

<schema id="condition-all" name="All" purpose="Every child condition must be true in authored order.">
ALL:
  <CONDITIONS>

WHERE:
- <CONDITIONS> is string; is non-empty; The child conditions in authored order..
</schema>

<schema id="condition-any" name="Any" purpose="At least one child condition must be true in authored order.">
ANY:
  <CONDITIONS>

WHERE:
- <CONDITIONS> is string; is non-empty; The child conditions in authored order..
</schema>

<schema id="condition-not" name="Not" purpose="One child condition whose result is inverted.">
NOT:
  <CONDITION>

WHERE:
- <CONDITION> is string; is non-empty; The child condition to invert..
</schema>

<schema id="act-native" name="Act act-native" purpose="One interpreter-native or exact named-tool action.">
ACT <INSTRUCTION> (<INPUTS>) -> <OUTPUTS>

WHERE:
- <INSTRUCTION> is string; is non-empty; The action the interpreter or exact tool performs..
- <INPUTS> is string; The action input bindings in authored order..
- <OUTPUTS> is string; The immutable local bindings the action must produce..
</schema>

<schema id="act-tool" name="Act act-tool" purpose="One interpreter-native or exact named-tool action.">
ACT TOOL "<TOOL>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS>

WHERE:
- <TOOL> is string; is non-empty; The exact host tool name, or null for interpreter-native work..
- <INSTRUCTION> is string; is non-empty; The action the interpreter or exact tool performs..
- <INPUTS> is string; The action input bindings in authored order..
- <OUTPUTS> is string; The immutable local bindings the action must produce..
</schema>

<schema id="step-set" name="Set" purpose="One local state write.">
SET <STATE> = <VALUE>

WHERE:
- <STATE> is string; is non-empty; The local state target to write..
- <VALUE> is string; is non-empty; The process value written to state..
</schema>

<schema id="step-emit" name="Emit" purpose="One schema instance emitted through one local output interface.">
EMIT <INTERFACE> (<BINDINGS>)

WHERE:
- <INTERFACE> is string; is non-empty; The local output interface target..
- <BINDINGS> is string; is non-empty; One value binding for each interface schema placeholder..
</schema>

<schema id="step-if" name="If" purpose="One recursive condition with a then branch and optional else branch.">
IF <CONDITION>:
THEN:
  <THEN>
ELSE:
  <OTHERWISE>

WHERE:
- <CONDITION> is string; is non-empty; The recursive condition that selects the branch..
- <THEN> is string; is non-empty; The steps run when the condition is true..
- <OTHERWISE> is string; The steps run when the condition is false..
</schema>

<schema id="step-call" name="Call" purpose="One synchronous process invocation with schema-bound inputs and outputs.">
CALL <PROCESS> (<INPUTS>) -> <OUTPUTS>

WHERE:
- <PROCESS> is string; is non-empty; The local or relative process target to invoke..
- <INPUTS> is string; The called process input bindings in authored order..
- <OUTPUTS> is string; The called process outputs promoted to this process..
</schema>

<schema id="step-fail" name="Fail" purpose="One explicit process failure.">
FAIL <MESSAGE>

WHERE:
- <MESSAGE> is string; is non-empty; The failure message..
</schema>

<schema id="step-assert" name="Assert" purpose="One required condition that aborts the transaction when false.">
ASSERT <CONDITION>
MESSAGE <MESSAGE>

WHERE:
- <CONDITION> is string; is non-empty; The required recursive condition..
- <MESSAGE> is string; The optional assertion failure message..
</schema>

<schema id="step-foreach" name="Foreach" purpose="One deterministic sequential iteration over a JSON list.">
FOREACH <BINDING> IN <VALUE>:
  <STEPS>

WHERE:
- <BINDING> is string; is non-empty; The immutable loop binding..
- <VALUE> is string; is non-empty; The process value that must resolve to a JSON list..
- <STEPS> is string; is non-empty; The sequential iteration steps..
</schema>

<schema id="step-while" name="While" purpose="One bounded pre-test loop over a recursive condition.">
WHILE <CONDITION> LIMIT <LIMIT>:
  <STEPS>

WHERE:
- <CONDITION> is string; is non-empty; The recursive condition tested before every iteration..
- <LIMIT> is string; is non-empty; The hard maximum number of iterations..
- <STEPS> is string; is non-empty; The steps run in one fresh child binding scope per iteration..
</schema>

<schema id="step-par" name="Par" purpose="One deterministic group of exact named-tool acts.">
PAR:
  <STEPS>

WHERE:
- <STEPS> is string; is non-empty; The exact named-tool acts launched in authored order..
</schema>

<schema id="step-join" name="Join" purpose="The barrier immediately after one parallel group.">
JOIN

WHERE:
</schema>

<schema id="process" name="Process" purpose="One named ordered way to do a task.">
<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<STEPS>
</process>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; is non-empty; The two-word process display name..
- <INPUT> is string; The optional schema that defines initial local bindings..
- <OUTPUT> is string; The optional schema that defines successful local outputs..
- <STEPS> is string; is non-empty; The typed process steps in authored order..
</schema>

<schema id="trigger" name="Trigger" purpose="One GIVEN, WHEN, and THEN signpost to a process.">
<trigger id="<ID>">
GIVEN: <GIVEN>
WHEN: <WHEN>
THEN: <THEN>
</trigger>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <GIVEN> is string; True or the recursive state guard checked after WHEN..
- <WHEN> is string; is non-empty; Why the interpreter enters the knowledge..
- <THEN> is string; is non-empty; The local or relative process target selected by the trigger..
</schema>

<schema id="interface" name="Interface" purpose="One crossing of information at the active document boundary.">
<interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">
<DESCRIPTION>
</interface>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <DIRECTION> is string; is non-empty; The direction across the document boundary..
- <SCHEMA_ID> is string; is non-empty; The local or relative schema target that defines the shape..
- <DESCRIPTION> is string; What the document boundary crossing means..
</schema>

<schema id="node" name="Node" purpose="One complete idless set of the seven OAK parts.">
<instructions>
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
</interfaces>

WHERE:
- <INSTRUCTIONS> is string; The node instructions in authored order..
- <CONSTANTS> is string; The node constants in authored order..
- <SCHEMAS> is string; The node schemas in authored order..
- <STATE> is string; The node state values in authored order..
- <TRIGGERS> is string; The node triggers in authored order..
- <PROCESSES> is string; The node processes in authored order..
- <INTERFACES> is string; The node interfaces in authored order..
</schema>

<schema id="oak-document" name="OAK Document" purpose="Carry the one valid OAK document written from the supplied source.">
<OAK>

WHERE:
- <OAK> is string; is non-empty; the complete valid OAK document.
</schema>
</schemas>

<state>
</state>

<triggers>
<trigger id="source-supplied">
GIVEN: true
WHEN: "Any source material is supplied with this prompt."
THEN: process.write-oak
</trigger>
</triggers>

<processes>
<process id="write-oak" name="Write OAK">
ACT Derive <DRAFT> from the complete supplied source. () -> DRAFT
ACT Validate <DRAFT> against every supplied OAK contract and produce <OAK>. (DRAFT=$DRAFT) -> OAK
EMIT interface.oak-document-output (OAK=$OAK)
</process>
</processes>

<interfaces>
<interface id="oak-document-output" direction="out" schema="schema.oak-document">
The sole OAK document returned to the caller.
</interface>
</interfaces>
