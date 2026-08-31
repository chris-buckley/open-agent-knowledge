<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Act: One interpreter-native or exact named-tool action.
Do not use one act placeholder as both input and output.
Make act instruction placeholders equal its inputs and outputs.
Bind each act input placeholder once.
Declare each act output placeholder once.
Match a named tool's declared input and output contract.
Name a tool exposed by the supplied exact tool registry.
</instructions>

<constants>
example-1: "ACT Turn <REQUEST> into <RESULT>. (REQUEST=$interface.request.REQUEST) -> RESULT"

example-2: "ACT TOOL \"mcp__docs__search\": Find <QUERY> and return <RESULT>. (QUERY=\"OAK\") -> RESULT"

grammar: TEXT<<
surface_act_native = ? ACT <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
surface_act_tool = ? ACT TOOL "<TOOL>": <INSTRUCTION> (<INPUTS>) -> <OUTPUTS> ? ;
>>
</constants>

<schemas>
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
</schemas>

<state>
</state>

<triggers>
</triggers>

<processes>
</processes>

<interfaces>
</interfaces>
