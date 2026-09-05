<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Par: One deterministic group of exact named-tool acts.
Follow a final PAR with JOIN.
Put no step between PAR and JOIN.
Give every PAR child a distinct output binding.
Put only exact named-tool acts inside PAR.
Use a tool in PAR only when its supplied registry confirms parallel use.
</instructions>

<constants>
example-1: "PAR:\n  ACT TOOL \"tool-a\": Produce <A>. () -> A\n  ACT TOOL \"tool-b\": Produce <B>. () -> B"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_step_par = ? PAR:
  <STEPS> ? ;
>>
</constants>

<schemas>
<schema id="step-par" name="Par" purpose="One deterministic group of exact named-tool acts.">
PAR:
  <STEPS>

WHERE:
- <STEPS> is string; is non-empty; The exact named-tool acts launched in authored order..
</schema>
</schemas>
