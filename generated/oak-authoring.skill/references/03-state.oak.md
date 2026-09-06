<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
guidance: YAML<<
- Map values that persist and can change across arrivals to state.
- Use constants for fixed values, state for values across arrivals, process bindings
  for local values, and interfaces for boundary instances.
- Keep pipeline values in process bindings and use state only for values that must
  survive an arrival.
>>

value-lifetimes: CSV<<
value,scope
constant,fixed during document use
state,persistent across arrivals
process binding,immutable in one frame or child scope
interface instance,one complete boundary occurrence
>>
</constants>
