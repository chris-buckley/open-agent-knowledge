<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Act: One interpreter-native or exact named-tool action.
Do not use one act placeholder as both input and output.
Make act instruction placeholders equal its inputs and outputs.
Match act inputs and outputs to its input and output schema placeholders.
Bind each act input placeholder once.
Declare each act output placeholder once.
Do not start an act instruction with an act schema attribute.
Match a named tool's declared placeholder sets and schema targets.
Name a tool exposed by the supplied exact tool registry.
</instructions>

<constants>
example-1: "ACT Turn <REQUEST> into <RESULT>. (REQUEST=\"Example request.\") -> RESULT"

example-2: "ACT TOOL \"mcp__docs__search\" input=\"schema.query\" output=\"schema.result\": Find <QUERY> and return <RESULT>. (\n  QUERY=\"OAK\",\n) -> RESULT"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_act_native = ? ACT input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_act_tool = ? ACT TOOL "<TOOL>" input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
>>
</constants>

<schemas>
<schema id="act-native" name="Act act-native" purpose="One interpreter-native or exact named-tool action.">
ACT input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS>

WHERE:
- <INPUT> is string; The optional schema that validates the resolved input values before invocation..
- <OUTPUT> is string; The optional schema that validates the produced outputs before promotion..
- <INSTRUCTION> is string; is non-empty; The action the interpreter or exact tool performs..
- <INPUTS> is string; The action input bindings in authored order..
- <OUTPUTS> is string; The immutable local bindings the action must produce..
</schema>

<schema id="act-tool" name="Act act-tool" purpose="One interpreter-native or exact named-tool action.">
ACT TOOL "<TOOL>" input="<INPUT>" output="<OUTPUT>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS>

WHERE:
- <TOOL> is string; is non-empty; The exact host tool name, or null for interpreter-native work..
- <INPUT> is string; The optional schema that validates the resolved input values before invocation..
- <OUTPUT> is string; The optional schema that validates the produced outputs before promotion..
- <INSTRUCTION> is string; is non-empty; The action the interpreter or exact tool performs..
- <INPUTS> is string; The action input bindings in authored order..
- <OUTPUTS> is string; The immutable local bindings the action must produce..
</schema>
</schemas>
