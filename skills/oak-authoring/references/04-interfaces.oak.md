~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Map complete document-boundary crossings to one-way interfaces.
- Emit one complete schema instance and use inferred `EMIT` only when same-named visible
  bindings satisfy it.
>>

boundaries: "Reuse an existing schema at a boundary; do not redefine its shape inside the interface. Interface instances are not ambient mutable storage."
~~~~
