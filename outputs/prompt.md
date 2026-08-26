~~~~instructions
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
~~~~

~~~~constants
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
relative_document_path = ? one relative POSIX path ending in .oak.md ? ;
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
surface_value_binding_line = ? <PLACEHOLDER> = <VALUE> ? ;
surface_condition_compare = ? <LEFT> <OPERATOR> <RIGHT> ? ;
surface_condition_all = ? ALL:
  <CONDITIONS> ? ;
surface_condition_any = ? ANY:
  <CONDITIONS> ? ;
surface_condition_not = ? NOT:
  <CONDITION> ? ;
surface_act_native = ? ACT <INSTRUCTION>
  INPUTS:
    <INPUTS>
  OUTPUTS: <OUTPUTS> ? ;
surface_act_tool = ? ACT TOOL "<TOOL>": <INSTRUCTION>
  INPUTS:
    <INPUTS>
  OUTPUTS: <OUTPUTS> ? ;
surface_step_set = ? SET <STATE> = <VALUE> ? ;
surface_step_emit = ? EMIT <INTERFACE>:
  <BINDINGS> ? ;
surface_step_if = ? IF <CONDITION>:
THEN:
  <THEN>
ELSE:
  <OTHERWISE> ? ;
surface_step_call = ? CALL <PROCESS>:
  INPUTS:
    <INPUTS>
  OUTPUTS: <OUTPUTS> ? ;
surface_step_fail = ? FAIL <MESSAGE> ? ;
surface_step_assert = ? ASSERT <CONDITION>
MESSAGE <MESSAGE> ? ;
surface_step_foreach = ? FOREACH <BINDING> IN <VALUE>:
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
~~~~

~~~~schemas
~~~schema;id="constraint-type";name="Type";purpose="The bound value has one datatype from the vocabulary catalog."
is <OF>

WHERE:
- <OF> is string; is non-empty; The datatype name..
~~~

~~~schema;id="constraint-one-of";name="OneOf";purpose="The bound value is one of the listed values."
is one of <VALUES>

WHERE:
- <VALUES> is string; is non-empty; The allowed values..
~~~

~~~schema;id="constraint-regex";name="Regex";purpose="The bound value matches one anchored portable rust-regex pattern."
matches `<PATTERN>`

WHERE:
- <PATTERN> is string; is non-empty; The whole-value portable pattern..
~~~

~~~schema;id="constraint-non-empty";name="NonEmpty";purpose="The bound value has at least one character or item."
is non-empty

WHERE:
~~~

~~~schema;id="constraint-max-chars";name="MaxChars";purpose="The bound value has at most n characters."
is at most <N> characters

WHERE:
- <N> is string; is non-empty; The character limit..
~~~

~~~schema;id="constraint-lines";name="Lines";purpose="The bound value has one positive line-count bound."
has <MIN> to <MAX> lines

WHERE:
- <MIN> is string; is non-empty; The fewest lines..
- <MAX> is string; is non-empty; The most lines..
~~~

~~~schema;id="constraint-list-of";name="ListOf";purpose="The bound value is items of one datatype joined by one separator."
is a list of <ITEM> joined by `<SEPARATOR>`

WHERE:
- <ITEM> is string; is non-empty; The datatype of every item..
- <SEPARATOR> is string; is non-empty; The text between items..
~~~

~~~schema;id="constraint-at-least";name="AtLeast";purpose="The bound value is at least a number or another placeholder value."
is at least <VALUE>

WHERE:
- <VALUE> is string; is non-empty; A number or a placeholder of the same schema..
~~~

~~~schema;id="constraint-at-most";name="AtMost";purpose="The bound value is at most a number or another placeholder value."
is at most <VALUE>

WHERE:
- <VALUE> is string; is non-empty; A number or a placeholder of the same schema..
~~~

~~~schema;id="where";name="Where";purpose="One placeholder, its constraints, examples, and description."
- <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>.

WHERE:
- <PLACEHOLDER> is string; is non-empty; The bare placeholder name..
- <CONSTRAINTS> is string; is non-empty; The constraints every bound value must satisfy..
- <EXAMPLES> is string; is non-empty; Values that satisfy every locally resolvable constraint..
- <DESCRIPTION> is string; is non-empty; What the placeholder holds, in one line..
~~~

~~~schema;id="instruction";name="Instruction";purpose="One rule the interpreter must follow."
<BODY>

WHERE:
- <BODY> is string; is non-empty; One directive or declarative rule..
~~~

~~~schema;id="constant-inline";name="Constant constant-inline";purpose="One value that stays the same during use."
<ID>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-text";name="Constant constant-text";purpose="One value that stays the same during use."
<ID>: TEXT<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-json";name="Constant constant-json";purpose="One value that stays the same during use."
<ID>: JSON<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-csv";name="Constant constant-csv";purpose="One value that stays the same during use."
<ID>: CSV<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-yaml";name="Constant constant-yaml";purpose="One value that stays the same during use."
<ID>: YAML<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="schema";name="Schema";purpose="One reusable information shape with one Where per placeholder."
<schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">
<TEMPLATE>

WHERE:
<WHERE>
</schema>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; is non-empty; The display name..
- <PURPOSE> is string; is non-empty; What the information shape is for..
- <TEMPLATE> is string; is non-empty; The literal shape with variable parts written as <PLACEHOLDER>..
- <WHERE> is string; is non-empty; One Where per distinct template placeholder, in authored order..
~~~

~~~schema;id="state";name="State";purpose="One JSON value that can change while the interpreter runs."
<ID>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The JSON value that can change..
~~~

~~~schema;id="value-literal";name="LiteralValue";purpose="One authored JSON value."
<VALUE>

WHERE:
- <VALUE> is string; is non-empty; The authored JSON value..
~~~

~~~schema;id="value-constant";name="ConstantValue";purpose="One value read from a local or relative constant entry."
$<CONSTANT>

WHERE:
- <CONSTANT> is string; is non-empty; The local or relative constant target to read..
~~~

~~~schema;id="value-state";name="StateValue";purpose="One value read from local state."
$<STATE>

WHERE:
- <STATE> is string; is non-empty; The local state target to read..
~~~

~~~schema;id="value-interface";name="InterfaceValue";purpose="One placeholder value read from one active local input interface."
$<INTERFACE>.<PLACEHOLDER>

WHERE:
- <INTERFACE> is string; is non-empty; The active local input interface target to read..
- <PLACEHOLDER> is string; is non-empty; The interface schema placeholder to read..
~~~

~~~schema;id="value-binding";name="BindingValue";purpose="One value read from a visible process-local binding."
$<BINDING>

WHERE:
- <BINDING> is string; is non-empty; The visible process-local binding to read..
~~~

~~~schema;id="value-binding-line";name="ValueBinding";purpose="One placeholder bound to one process value."
<PLACEHOLDER> = <VALUE>

WHERE:
- <PLACEHOLDER> is string; is non-empty; The placeholder receiving the process value..
- <VALUE> is string; is non-empty; The process value bound to the placeholder..
~~~

~~~schema;id="condition-compare";name="Compare";purpose="One strict structural or ordered comparison."
<LEFT> <OPERATOR> <RIGHT>

WHERE:
- <LEFT> is string; is non-empty; The value on the left of the comparison..
- <OPERATOR> is string; is non-empty; The strict comparison operator..
- <RIGHT> is string; is non-empty; The value on the right of the comparison..
~~~

~~~schema;id="condition-all";name="All";purpose="Every child condition must be true in authored order."
ALL:
  <CONDITIONS>

WHERE:
- <CONDITIONS> is string; is non-empty; The child conditions in authored order..
~~~

~~~schema;id="condition-any";name="Any";purpose="At least one child condition must be true in authored order."
ANY:
  <CONDITIONS>

WHERE:
- <CONDITIONS> is string; is non-empty; The child conditions in authored order..
~~~

~~~schema;id="condition-not";name="Not";purpose="One child condition whose result is inverted."
NOT:
  <CONDITION>

WHERE:
- <CONDITION> is string; is non-empty; The child condition to invert..
~~~

~~~schema;id="act-native";name="Act act-native";purpose="One interpreter-native or exact named-tool action."
ACT <INSTRUCTION>
  INPUTS:
    <INPUTS>
  OUTPUTS: <OUTPUTS>

WHERE:
- <INSTRUCTION> is string; is non-empty; The action the interpreter or exact tool performs..
- <INPUTS> is string; is non-empty; The action input bindings in authored order..
- <OUTPUTS> is string; is non-empty; The immutable local bindings the action must produce..
~~~

~~~schema;id="act-tool";name="Act act-tool";purpose="One interpreter-native or exact named-tool action."
ACT TOOL "<TOOL>": <INSTRUCTION>
  INPUTS:
    <INPUTS>
  OUTPUTS: <OUTPUTS>

WHERE:
- <TOOL> is string; is non-empty; The exact host tool name, or null for interpreter-native work..
- <INSTRUCTION> is string; is non-empty; The action the interpreter or exact tool performs..
- <INPUTS> is string; is non-empty; The action input bindings in authored order..
- <OUTPUTS> is string; is non-empty; The immutable local bindings the action must produce..
~~~

~~~schema;id="step-set";name="Set";purpose="One local state write."
SET <STATE> = <VALUE>

WHERE:
- <STATE> is string; is non-empty; The local state target to write..
- <VALUE> is string; is non-empty; The process value written to state..
~~~

~~~schema;id="step-emit";name="Emit";purpose="One schema instance emitted through one local output interface."
EMIT <INTERFACE>:
  <BINDINGS>

WHERE:
- <INTERFACE> is string; is non-empty; The local output interface target..
- <BINDINGS> is string; is non-empty; One value binding for each interface schema placeholder..
~~~

~~~schema;id="step-if";name="If";purpose="One recursive condition with a then branch and optional else branch."
IF <CONDITION>:
THEN:
  <THEN>
ELSE:
  <OTHERWISE>

WHERE:
- <CONDITION> is string; is non-empty; The recursive condition that selects the branch..
- <THEN> is string; is non-empty; The steps run when the condition is true..
- <OTHERWISE> is string; is non-empty; The steps run when the condition is false..
~~~

~~~schema;id="step-call";name="Call";purpose="One synchronous process invocation with schema-bound inputs and outputs."
CALL <PROCESS>:
  INPUTS:
    <INPUTS>
  OUTPUTS: <OUTPUTS>

WHERE:
- <PROCESS> is string; is non-empty; The local or relative process target to invoke..
- <INPUTS> is string; is non-empty; The called process input bindings in authored order..
- <OUTPUTS> is string; is non-empty; The called process outputs promoted to this process..
~~~

~~~schema;id="step-fail";name="Fail";purpose="One explicit process failure."
FAIL <MESSAGE>

WHERE:
- <MESSAGE> is string; is non-empty; The failure message..
~~~

~~~schema;id="step-assert";name="Assert";purpose="One required condition that aborts the transaction when false."
ASSERT <CONDITION>
MESSAGE <MESSAGE>

WHERE:
- <CONDITION> is string; is non-empty; The required recursive condition..
- <MESSAGE> is string; is non-empty; The optional assertion failure message..
~~~

~~~schema;id="step-foreach";name="Foreach";purpose="One deterministic sequential iteration over a JSON list."
FOREACH <BINDING> IN <VALUE>:
  <STEPS>

WHERE:
- <BINDING> is string; is non-empty; The immutable loop binding..
- <VALUE> is string; is non-empty; The process value that must resolve to a JSON list..
- <STEPS> is string; is non-empty; The sequential iteration steps..
~~~

~~~schema;id="step-par";name="Par";purpose="One deterministic group of exact named-tool acts."
PAR:
  <STEPS>

WHERE:
- <STEPS> is string; is non-empty; The exact named-tool acts launched in authored order..
~~~

~~~schema;id="step-join";name="Join";purpose="The barrier immediately after one parallel group."
JOIN

WHERE:
~~~

~~~schema;id="process";name="Process";purpose="One named ordered way to do a task."
<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<STEPS>
</process>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; is non-empty; The two-word process display name..
- <INPUT> is string; is non-empty; The optional schema that defines initial local bindings..
- <OUTPUT> is string; is non-empty; The optional schema that defines successful local outputs..
- <STEPS> is string; is non-empty; The typed process steps in authored order..
~~~

~~~schema;id="trigger";name="Trigger";purpose="One GIVEN, WHEN, and THEN signpost to a process."
<trigger id="<ID>">
GIVEN: <GIVEN>
WHEN: <WHEN>
THEN: <THEN>
</trigger>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <GIVEN> is string; is non-empty; True or the recursive state guard checked after WHEN..
- <WHEN> is string; is non-empty; Why the interpreter enters the knowledge..
- <THEN> is string; is non-empty; The local or relative process target selected by the trigger..
~~~

~~~schema;id="interface";name="Interface";purpose="One crossing of information at the active document boundary."
<interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">
<DESCRIPTION>
</interface>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <DIRECTION> is string; is non-empty; The direction across the document boundary..
- <SCHEMA_ID> is string; is non-empty; The local or relative schema target that defines the shape..
- <DESCRIPTION> is string; is non-empty; What the document boundary crossing means..
~~~

~~~schema;id="node";name="Node";purpose="One complete idless set of the seven OAK parts."
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
- <INSTRUCTIONS> is string; is non-empty; The node instructions in authored order..
- <CONSTANTS> is string; is non-empty; The node constants in authored order..
- <SCHEMAS> is string; is non-empty; The node schemas in authored order..
- <STATE> is string; is non-empty; The node state values in authored order..
- <TRIGGERS> is string; is non-empty; The node triggers in authored order..
- <PROCESSES> is string; is non-empty; The node processes in authored order..
- <INTERFACES> is string; is non-empty; The node interfaces in authored order..
~~~

~~~schema;id="oak-result";name="OAK Result";purpose="Carry the one valid OAK document written from the supplied source."
<OAK>

WHERE:
- <OAK> is string; is non-empty; the complete valid OAK document.
~~~
~~~~

~~~~state
~~~~

~~~~triggers
~~~trigger;id="write-oak-trigger"
GIVEN: true
WHEN: "Any source material is supplied with this prompt."
THEN: process.write-oak
~~~
~~~~

~~~~processes
~~~process;id="write-oak";name="Write OAK"
ACT Derive <DRAFT> from the complete supplied source.
  OUTPUTS: DRAFT
ACT Validate <DRAFT> against every supplied OAK contract and produce <OAK>.
  INPUTS:
    DRAFT = $DRAFT
  OUTPUTS: OAK
EMIT interface.result:
  OAK = $OAK
~~~
~~~~

~~~~interfaces
~~~interface;id="result";direction="out";schema="schema.oak-result"
The sole OAK document returned to the caller.
~~~
~~~~
