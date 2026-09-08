<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<constants>
workflow: YAML<<
- Bind one stable owner and capability to an explicit local instance root, independently
  of shared source paths, script locations and exposed names. Reject another owner,
  unsupported format or changed required dependency before work.
- Use only justified state/policy, state/history, state/runs and state/runtime areas.
  Shared templates seed missing instances only; source updates never replace saved
  policy, evidence, pending work or tool-owned records.
- Ordinary memory needs normal file tools, not a state service. Use UTF-8 CSV with
  id,name,reference headers, stable unique ids and standard quoting. Resolve references
  from the containing index inside the permitted instance; reject malformed, dangling,
  escaping or symlink references.
- Load the requested index and selected records only after invocation. Keep mutable
  contents out of default context, shared INDEX/MAP and shared SKILL.md. An index
  reference neither grants access nor makes private records instructions.
- Reuse a saved retention decision. On first use ask only when no applicable decision
  exists. Full retains future source text; summary retains its digest, decision and
  evidence reference. Changing mode affects future records only; preserve existing
  evidence and pending work until an explicit compatible cleanup is approved.
- Loading, Git tracking, retention and backup are separate controls. Default to local
  state exclusions and verify actual git check-ignore plus tracked-file status. Explicit
  bounded opt-in needs its real ignore rules checked; configuration alone proves no
  exclusion. Inherited or already-tracked conflicts need reconciliation.
- Allow one active writer. Inspect inputs and identities, prepare the record, recheck
  for intervening edits, write the record before its index entry, then read both back.
  Resume by reconciling exact existing bytes and pending identity; preserve orphaned
  records and reject unknown writer conflicts. This is not an atomic multi-file transaction.
- Only the owning tool writes operational journals, locks, verified outcomes and protected
  datasets. Never fabricate a receipt. Reconcile uncertain effects through their owner
  before retry; failed OAK work discards staged values, not filesystem or external
  effects.
>>

record-contract: "History records are JSON with version=1, owner, capability, id, writer=agent, category, instance-relative policy reference, policy_sha256, source_sha256 and mode. Full also retains source text. A policy record has version=1, owner, capability, id, writer=agent and term. State/runs records contain pending OAK checkpoints; records marked writer=tool are protected. These are example contracts, not OAK datatypes."

recovery: "Keep the pending checkpoint after failure. Compare the prepared source/index identities before writing. An exact orphan record may receive its missing index entry. An exact already-published pair needs read-back only. A differing record, index row, policy or writer must stop without a success result. Persist successfully returned OAK state before acknowledging progress."
</constants>

<schemas>
<schema id="configuration" purpose="Identify one instance and its saved decision for future records.">
{"version": <VERSION>, "owner": "<OWNER>", "capability": "<CAPABILITY>", "retention": "<MODE>"}

WHERE:
- <VERSION> is integer; is one of `1`.
- <OWNER> is string; is non-empty.
- <CAPABILITY> is string; is non-empty.
- <MODE> is string; is one of `full`, `summary`.
</schema>

<schema id="index-row" purpose="Name one authoritative record using containing-index-relative resolution.">
id,name,reference
<ID>,<NAME>,<REFERENCE>

WHERE:
- <ID> is string; is non-empty.
- <NAME> is string; is non-empty.
- <REFERENCE> is string; is non-empty.
</schema>

<schema id="policy" purpose="Validate one agent-owned synthetic policy record before applying it.">
{"version": <VERSION>, "owner": "<OWNER>", "capability": "<CAPABILITY>", "id": "<ID>", "writer": "<WRITER>", "term": "<TERM>"}

WHERE:
- <VERSION> is integer; is one of `1`.
- <OWNER> is string; is non-empty.
- <CAPABILITY> is string; is non-empty.
- <ID> is string; is non-empty.
- <TERM> is string; is non-empty.
- <WRITER> is string; is one of `agent`.
</schema>
</schemas>