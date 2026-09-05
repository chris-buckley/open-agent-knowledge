<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Schema: One reusable information shape with one Where per placeholder.
Define each schema placeholder once in WHERE.
Make the template and WHERE placeholder sets equal.
Reference only another placeholder in the same schema.
</instructions>

<constants>
example-1: "<schema id=\"outline\" name=\"Hierarchical Outline\" purpose=\"Generate a numbered outline.\">\n## <OUTLINE_TITLE>\n\n\nWHERE:\n- <OUTLINE_TITLE> is string.\n</schema>"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_schema = ? <schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">
<TEMPLATE>

WHERE:
<WHERE>
</schema> ? ;
>>
</constants>

<schemas>
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
</schemas>
