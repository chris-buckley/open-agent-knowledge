~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Treat the complete supplied host context as the source, regardless of modality.
- Omit every part and entry that the source does not justify.
- Do not invent state, triggers, processes, interfaces, tools, or relative paths.
- Write one idless node using only the seven parts in canonical order.
- Use the shortest unambiguous names and reuse one exact domain noun across parts.
- Keep tool implementations, handlers, transport, credentials, model selection, and
  server configuration in the host.
>>

part-authoring-priority: ["schemas", "constants", "state", "interfaces", "triggers", "processes", "instructions"]

part-order: ["instructions", "constants", "schemas", "state", "triggers", "processes", "interfaces"]

part-responsibilities: CSV<<
part,owns,lifetime,excludes
instructions,irreducible interpreter policy,whole document use,"facts, reusable shapes, mutable values, routing, ordered work, and boundary payloads"
constants,fixed JSON knowledge,whole document use,mutable values
schemas,reusable information shapes,definition,boundary flow and process routing
state,persistent mutable JSON values,across arrivals,invocation-local results
triggers,outside occurrence routing,one arrival decision,internal sequencing
processes,ordered local work,one invocation,outside transport
interfaces,complete boundary schema instances,one receive or emission,information shape definitions
>>

host-boundary: CSV<<
owner,responsibility
OAK,"knowledge, internal contracts, canonical models, authored representations, explicit graph resolution, and execution semantics"
host,"model selection, credentials, transport, tool implementations, scheduling, persistence mechanism, delivery, and external side effects"
>>

reading: TEXT<<
Load needed guides in authoring order, not render order. The entry routes work; supporting files supply fixed knowledge and reusable shapes. Omit empty parts. Select complete scenarios via references/examples/catalog.oak.md. The assembled agent has identical knowledge with local targets. Authoring and interpretation of either form need no Python, package, network, or validator.
>>
~~~~
