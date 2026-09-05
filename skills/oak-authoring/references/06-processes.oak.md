~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Map ordered local work to processes.
- Start each process id with an exact base-form action verb and name the result it
  establishes.
- Give reusable process phases input and output schemas when their values need contracts.
- Keep multi-phase entry processes as orchestrators that compose reusable processes
  with `CALL`.
- Use plain `ACT` when the interpreter performs the work with native capabilities.
- Use `ACT TOOL` only for one exact tool name copied from the supplied registry.
- Use `PAR` and `JOIN` only for independent exact tool actions.
- Model a delegated agent as its own typed OAK document and dispatch it through an
  exact host tool contract.
>>

scopes: TEXT<<
A process binding is immutable within its frame. CALL promotes declared outputs; child branches and iterations have local scope. IF does not promote branch-local outputs to its parent. EMIT inside the relevant branch or use declared process contracts instead of inventing persistent state. Use assertions, conditions, loops, and parallel steps only when the source justifies their semantics.
>>
~~~~
