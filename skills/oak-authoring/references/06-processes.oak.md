~~~~instructions
Constants hold values that do not change while the knowledge runs.
~~~~

~~~~constants
guidance: YAML<<
- Map ordered local work to processes.
- Start each process id with an exact base-form action verb and name the result it
  establishes.
- Give reusable process phases input and output schemas when their values need contracts.
- Name an action's participants, their relationship or criterion, and required results
  or effects. Omit unjustified roles; prefer natural domain wording over a mandatory
  sentence template.
- Prefer validate for a named contract check, assess for judgment against a criterion,
  and publish for a host-authorized external effect; these words add no capability.
  Schema validity proves neither sound judgment nor performed work; EMIT does not
  prove delivery. Native ACT can have effects; preserve exact tool names.
- Keep multi-phase entry processes as orchestrators that compose reusable processes
  with `CALL`.
- Use plain `ACT` when the interpreter performs the work with native capabilities.
- Use `ACT TOOL` only for one exact tool name copied from the supplied registry.
- Use `PAR` and `JOIN` only for independent exact tool actions.
- Model a delegated agent as its own typed OAK document and dispatch it through an
  exact host tool contract.
- Use the same explicit recursive condition structure for branches, loop conditions,
  assertions, and guards; preserve child order and bounded-loop failures.
- Use delimiter continuation for long expressions and indentation for ordered action
  suites; follow the shared grammar instead of inventing another layout dialect.
>>

scopes: TEXT<<
Bindings are immutable per frame. CALL promotes declared outputs; branches and iterations have local scope. IF never promotes child outputs. EMIT in the branch or use process contracts, not invented state. Assertions, conditions, loops, and parallel steps need source-justified semantics.
>>
~~~~
