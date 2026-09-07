<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
guidance: YAML<<
- Map outside events, receive sources, state guards, and selected work to triggers.
- Route each receive interface through one source-backed trigger into a process with
  the same resolved input schema.
- Declare each trigger once with named fields; omit unused fields and keep source
  payloads separate from event seeds.
>>

routing: "Source triggers share receive/process schemas and omit seeds. Guards read state, may compare literals/constants, never process bindings. CALL sequences internal work."
</constants>
