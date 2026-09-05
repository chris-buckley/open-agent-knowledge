~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Map outside events, receive sources, state guards, and selected work to triggers.
- Route each receive interface through one source-backed trigger into a process with
  the same resolved input schema.
>>

routing: "An event describes an outside occurrence. An optional source identifies one receiving interface; its schema must resolve identically to process input, with no seeds. A guard reads state only. Internal work uses CALL, never triggers."
~~~~
