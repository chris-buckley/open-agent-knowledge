~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Map complete document-boundary crossings to one-way interfaces.
- Emit one complete schema instance and use inferred `EMIT` only when same-named visible
  bindings satisfy it.
>>

boundaries: "Reuse boundary schemas; never redefine their shapes inside interfaces or treat instances as mutable storage."
~~~~
