<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

ConstantValue: One value read from a local or relative constant entry.
</instructions>

<constants>
example-1: "$constant.policy"

grammar: TEXT<<
surface_value_constant = ? $<CONSTANT> ? ;
>>
</constants>

<schemas>
<schema id="value-constant" name="ConstantValue" purpose="One value read from a local or relative constant entry.">
$<CONSTANT>

WHERE:
- <CONSTANT> is string; is non-empty; The local or relative constant target to read..
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
