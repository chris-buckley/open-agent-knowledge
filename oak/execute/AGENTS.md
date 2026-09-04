<instructions>
This document owns one execution cycle, arrivals, trigger selection, process frames, steps, tools, state, emissions, failures, and transaction behaviour.
Accept one root node or resolved graph, one arrival, one complete state mapping, an optional native action handler, and an exact tool registry.
Do not mutate the caller state mapping.
Require one arrival to contain exactly one event or one local receive interface with values.
Give an event arrival no values.
Require a receive arrival to supply one complete instance of its `RECEIVES` interface schema.
Validate supplied state and the arrival before trigger selection.
Match an event arrival to source-less triggers by exact event text.
Match a receive arrival to source-backed triggers by exact interface target.
Keep a source-backed trigger event as a semantic signpost, not as its machine match key.
Evaluate each matching guard after the event or source match with authored-order short-circuiting.
Run no process for zero trigger matches, one selected process for one match, and fail for multiple matches.
Resolve event-backed process input from its explicit seeds.
Use a validated receive instance as the complete source-backed process input.
Validate process input before creating its frame.
Keep local bindings immutable inside each process frame.
Promote validated action and call outputs as new bindings.
Give branches, loop iterations, and called processes child scopes that do not leak undeclared bindings.
Share staged state and emissions across called processes in one top-level transaction.
Execute process steps in authored order.
Use plain `ACT` for interpreter-native work through the supplied native handler.
Use `ACT TOOL` for one exact tool registry entry whose contract matches the authored action.
Validate every action input before invocation and every exact returned output before promotion.
Stage each valid local `SET` write and expose it to later transaction steps.
Run `CALL` synchronously in a fresh frame and promote only its declared validated outputs.
Do not use `CALL` to dispatch another agent.
Target each `EMIT` at one local `EMITS` interface.
Resolve an explicit emission from its bindings and an inferred emission from same-named visible bindings in schema order.
Validate each complete emitted instance before staging it.
Use strict JSON equality and order only two numbers or two strings.
Treat booleans as distinct from numbers.
Execute only the selected `IF` branch and stop on a failed `ASSERT` or executed `FAIL`.
Run `FOREACH` in list index order with one fresh child scope per item.
Test `WHILE` before each bounded iteration and fail when its condition remains true after the limit.
Resolve and validate every `PAR` child input before launching any child.
Give each parallel child one immutable binding snapshot and keep outputs hidden until the following `JOIN`.
Promote successful parallel outputs in authored child order and promote none when any child fails.
Commit staged state and emissions only after successful top-level completion.
Discard staged state and emissions after failure without claiming rollback for external tool effects.
Return the selected process target, committed state, and ordered emissions after success.
Use stable execution error codes and retain suppressed parallel child failures when available.
Permit a host to invoke a process through another controlled entry while the standard cycle enters work through triggers.
</instructions>