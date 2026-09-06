~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Map outside events, receive sources, state guards, and selected work to triggers.
- Route each receive interface through one source-backed trigger into a process with
  the same resolved input schema.
- Declare each trigger once with named fields; omit unused fields and keep source
  payloads separate from event seeds.
>>

routing: "Sources identify receive interfaces with the same resolved schema as process input and no seeds. Guards require state reads, may compare literals or constants, and never read process bindings. Internal work uses CALL, not triggers."
~~~~
