<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Emit: One schema instance emitted through one local output interface.
Bind each emitted placeholder once.
Bind every interface schema placeholder exactly once in an explicit EMIT.
Target only an EMITS interface from EMIT.
Use interfaces only in the active OAK document.
Make every inferred EMIT placeholder visible at its step.
Make every statically known emission satisfy its interface schema.
</instructions>

<constants>
example-1: "EMIT interface.result"

example-2: "EMIT interface.result (RESULT=$FINAL_RESULT)"

grammar: TEXT<<
surface_step_emit_inferred = ? EMIT <INTERFACE> ? ;
surface_step_emit_explicit = ? EMIT <INTERFACE> (<BINDINGS>) ? ;
>>
</constants>

<schemas>
<schema id="step-emit-inferred" name="Emit step-emit-inferred" purpose="One schema instance emitted through one local output interface.">
EMIT <INTERFACE>

WHERE:
- <INTERFACE> is string; is non-empty; The local output interface target..
</schema>

<schema id="step-emit-explicit" name="Emit step-emit-explicit" purpose="One schema instance emitted through one local output interface.">
EMIT <INTERFACE> (<BINDINGS>)

WHERE:
- <INTERFACE> is string; is non-empty; The local output interface target..
- <BINDINGS> is string; is non-empty; The optional explicit projection bindings in authored order..
</schema>
</schemas>
