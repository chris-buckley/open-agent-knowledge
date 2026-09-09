<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
profile: "stateful"

selection: "Populate the same _template/SKILL.md foundation. Insert the selected <STATE_PART> after schemas and before triggers; merge required schemas, constants and process entries into their existing parts. Retain only justified instance scaffolds. Do not concatenate operational documents."

state-slot: "<STATE_PART>"

memory: YAML<<
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

boundary: "This recipe and its examples are inert knowledge. They create no state for the authoring skill, supply no file tool or persistence service, and grant no installation or write authority."
</constants>
