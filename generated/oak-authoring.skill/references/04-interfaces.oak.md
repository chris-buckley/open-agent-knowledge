<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
guidance: YAML<<
- Map complete document-boundary crossings to one-way interfaces.
- Emit one complete schema instance and use inferred `EMIT` only when same-named visible
  bindings satisfy it.
- Prefer local interface schemas for independently understandable documents; define
  them in schemas, not interfaces. Deliberately graph-composed documents may share
  external schemas.
- Use schema purpose and WHERE descriptions for field meaning, interface descriptions
  for boundary purpose and authority, and triggers/processes for routing, conditions,
  effects, and failures. Omit redundant prose; its presence does not prove completeness.
>>

boundaries: "Interface instances are not mutable storage."
</constants>
