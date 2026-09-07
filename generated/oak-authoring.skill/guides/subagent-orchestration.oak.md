<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
guidance: YAML<<
- Use plain `ACT` when the interpreter performs the work with native capabilities.
- Use `ACT TOOL` only for one exact tool name copied from the supplied registry.
- Use `PAR` and `JOIN` only for independent exact tool actions.
- Model a delegated agent as its own typed OAK document and dispatch it through an
  exact host tool contract.
>>

orchestration: YAML<<
- The coordinator owns splitting, dispatch, integration and final claims. Give each
  leaf a bounded independent task and mapped request/result schemas, not coordinator
  authority.
- Give workers one pinned revision, full applicable governing text, scope and evidence
  requirements. Restore truncation, preserve document scopes and report blocked work.
- CALL composes processes synchronously, not agents. ACT.tool constructs a tool action,
  not a capability or permission.
- PAR outputs stay isolated until immediate JOIN promotes them in authored order.
  Before synthesis reject blocked, failed, malformed or wrong-revision results; reconcile
  conflicts and retain gaps.
- Hosts own concurrency limits, deadlines, cancellation, cleanup and tool/sandbox
  enforcement. Fixture overlap proves no live subagent behavior.
>>
</constants>
