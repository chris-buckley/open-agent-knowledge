<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Not: One child condition whose result is inverted.
</instructions>

<constants>
example-1: "NOT($state.status equals \"closed\")"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_condition_not = not_condition ;
>>
</constants>

<schemas>
<schema id="condition-not" name="Not" purpose="One child condition whose result is inverted.">
NOT(<CONDITION>)

WHERE:
- <CONDITION> is string; is non-empty; The child condition to invert..
</schema>
</schemas>
