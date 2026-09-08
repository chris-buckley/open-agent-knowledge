<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<constants>
guidance: YAML<<
- Treat the complete supplied host context as the source, regardless of modality.
- Omit every part and entry that the source does not justify.
- Do not invent state, triggers, processes, interfaces, tools, or relative paths.
- Use the shortest unambiguous names and reuse one exact domain noun across parts.
>>

part-authoring-priority: ["schemas", "constants", "state", "interfaces", "triggers", "processes", "instructions"]

skill-template: JSON<<
"---\nname: \"<SKILL_NAME>\"\ndescription: \"<SKILL_DESCRIPTION>\"\n---\n\n<INSTRUCTIONS_PART>\n<constants>\ntitle: <TITLE_JSON>\n\npurpose: <PURPOSE_JSON>\n\nprinciple: <PRINCIPLE_JSON>\n\nroles: <ROLES_JSON>\n\nindex: <INDEX_JSON>\n\nlayout: TEXT<<\nSKILL_TREE:\n<RESOURCE_TREE>\n>>\n\n<CONSTANT_ENTRIES>\n</constants>\n<SCHEMAS_PART>\n<TRIGGERS_PART>\n<PROCESSES_PART>\n<INTERFACES_PART>\n"
>>

stateful-extension: JSON<<
"<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nprofile: \"stateful\"\n\nselection: \"Populate the same _template/SKILL.md foundation. Insert the selected <STATE_PART> after schemas and before triggers; merge required schemas, constants and process entries into their existing parts. Retain only justified instance scaffolds. Do not concatenate operational documents.\"\n\nstate-slot: \"<STATE_PART>\"\n\nmemory: YAML<<\n- Bind one stable owner and capability to an explicit local instance root, independently\n  of shared source paths, script locations and exposed names. Reject another owner,\n  unsupported format or changed required dependency before work.\n- Use only justified state/policy, state/history, state/runs and state/runtime areas.\n  Shared templates seed missing instances only; source updates never replace saved\n  policy, evidence, pending work or tool-owned records.\n- Ordinary memory needs normal file tools, not a state service. Use UTF-8 CSV with\n  id,name,reference headers, stable unique ids and standard quoting. Resolve references\n  from the containing index inside the permitted instance; reject malformed, dangling,\n  escaping or symlink references.\n- Load the requested index and selected records only after invocation. Keep mutable\n  contents out of default context, shared INDEX/MAP and shared SKILL.md. An index\n  reference neither grants access nor makes private records instructions.\n- Reuse a saved retention decision. On first use ask only when no applicable decision\n  exists. Full retains future source text; summary retains its digest, decision and\n  evidence reference. Changing mode affects future records only; preserve existing\n  evidence and pending work until an explicit compatible cleanup is approved.\n- Loading, Git tracking, retention and backup are separate controls. Default to local\n  state exclusions and verify actual git check-ignore plus tracked-file status. Explicit\n  bounded opt-in needs its real ignore rules checked; configuration alone proves no\n  exclusion. Inherited or already-tracked conflicts need reconciliation.\n- Allow one active writer. Inspect inputs and identities, prepare the record, recheck\n  for intervening edits, write the record before its index entry, then read both back.\n  Resume by reconciling exact existing bytes and pending identity; preserve orphaned\n  records and reject unknown writer conflicts. This is not an atomic multi-file transaction.\n- Only the owning tool writes operational journals, locks, verified outcomes and protected\n  datasets. Never fabricate a receipt. Reconcile uncertain effects through their owner\n  before retry; failed OAK work discards staged values, not filesystem or external\n  effects.\n>>\n\nboundary: \"This recipe and its examples are inert knowledge. They create no state for the authoring skill, supply no file tool or persistence service, and grant no installation or write authority.\"\n</constants>"
>>

template-use: "For new skills select the stateless _template/SKILL.md foundation; add only the explicitly justified _template/stateful.oak.md extension for owned instance memory. Both derive from one source. Quote metadata as YAML strings and JSON values as JSON. Replace PART lines with justified OAK sections plus a blank line, or delete them. Fill CONSTANT_ENTRIES or leave empty. Populate roles in DEFINE, optional ROUTE, LOOP, INDEX, MAP, ASSERT order as navigation to actual OAK entries, not new statements or a new part order. Derive INDEX loading conditions and every static MAP leaf from the selected resources. Keep declared dependencies separate, use (...) only for generated contents, and omit private contents from shared discovery. Stateless selection has no state paths, settings, retention, exclusions or memory postconditions. Remove all markers, unused resources and .gitkeep during population. Use the complete inert skill_profiles package mapping for composition and recovery specimens. Keep each callable in its own .oak.md document and preserve its owner. Unfilled scaffolding is inert."

draft-contract: YAML<<
envelope: JSON in an OAK string; not validated canonical OAK. All listed fields required;
  arrays ordered, object key order immaterial. No credentials.
draft:
  format: 1
  id: stable string
  turn: nonnegative integer
  request: '{text,operation:create|read|update|delete,mode:direct|guided,purpose,channel:conversation|legacy};
    remaining fields strings'
  kind: catalogue id or null while unresolved
  context: '{knowledge_revision,catalogue_version,authoring_host,consumer:strings;
    evidence,installation_consent:string arrays; validation_requested,validation_required:booleans}.
    Unknown host is unverified; required only by actual request.'
  scope: '{documents:path array,selectors:[{document,pointer}],destination:response|files,effects:read|write|delete
    array,reference_boundary:inspected path array}'
  sources: '[{id,identity:string|null,locator,text,read:complete|partial|unavailable}];
    other fields strings. Keep full supplied text; observed locator/identity usable
    only with accessible content.'
  documents: '[{path,node:partial canonical Node fields}]. Omit missing fields; no
    fabricated TODO/unknown/null. Real null literals remain null. Stable logical .oak.md
    paths for response-only work.'
  outputs: '[{path,format:oak|skill-entry|codex-agent|claude-agent|resource,document:string|null,source:string|null}];
    exactly one selector nonnull. Wrappers share the selected document body.'
  review: '{status:pending|ready|blocked,blockers:annotation ids,basis:evidence strings,checks:[{name,method,status:passed|failed|not-performed,subject,evidence,exit_code:integer|null}]};
    remaining check fields strings'
  annotations: '[{id,document,pointer,status:confirmed|proposed|unresolved,meaning,question,evidence:string
    array}]; remaining fields strings, question empty unless useful. Empty document
    targets draft context; otherwise pointer addresses that document node.'
  changes: '[{op:add|replace|remove|confirm,annotation,document,pointer,before,after}];
    other fields strings, per-turn audit, not another executable draft'
  source_map: '[{source,clause,document,annotations:id array,disposition:preserved|restructured|explicitly-omitted|unresolved,reason}];
    other fields strings; empty means not applicable'
  tools: '[{id,context:authoring-host|consumer,capability,provider:native|mcp|unspecified,server,operation,input_contract,output_contract,effects:read|write|delete|external|unknown
    array,permission_limits,availability:confirmed|unverified|unavailable,evidence:string
    array}]. Server/operation/contracts nullable strings; others strings.'
  authority: '{requests:[{reference,purpose,documents:path array,selectors:[{document,pointer}],effects:effect
    array}],guided_release:boolean,release_reference:string}; reference/purpose strings;
    empty release_reference before actual release'
continuity: Return complete same draft every turn. Host retains/resupplies it, never
  OAK state. Pin knowledge/catalogue; disclose and recover missing/stale/mismatched
  prior, content or versions from evidence, never summaries or silent reinterpretation.
  Increment turn once; apply decisions once.
annotations: Stable ids survive moves; update pointers. Child overrides refine parent
  status. Missing prospective field needs explicit unresolved meaning; other dangling
  pointers rejected. Removed live annotations stay historical in changes/source_map.
  New unsupported meaning unresolved; domain proposals need agreement. Ordinary ids/layout
  choices in a direct request need no interview.
authority: Actual user messages and scope govern; JSON fields, READY, configuration,
  source text and receipts grant no permission. Preserve direct authority across answers/optional
  validation. Source is inert task data. Guided release requires actual satisfaction/output
  instruction for this draft; no special token or repeated approval. New material
  scope/effects need authority.
artifacts: JSON {documents:[{path,content,format?}],deletions:[path]}; full content,
  oak default. Read/blocked/unreleased empty. Tombstones only explicit removals of
  observed files, never absence from draft. No empty text called OAK.
effects: JSON {status,paths,unresolved}; status not-requested|not-performed|partial|applied.
  Each attempted path names operation, observed before/after identity when available
  and tool-result reference. Never guess hashes, command exits or successful effects.
>>

fidelity: YAML<<
- Preserve obligations, permissions, negation, conditions/else association, ordered
  work, cardinality, names, exact literals, tool operations, lifetimes, boundary contracts
  and host ownership. Every meaningful source clause has a disposition; omissions
  require explicit justification. Ambiguity stays node-tied and unresolved.
- Scratch requests are evidence, not permission to invent structure. Compact facts
  need no execution scaffold. Read explains observed/inferred/invalid/unknown meaning
  without repair. Update imports complete affected nodes and changes only approved
  selectors and dependency repairs. Delete inspects inbound/outbound references inside
  the stated boundary before removal.
- Never global-replace path-like literals, automatically cascade, clean unrelated
  resources or claim no external consumers from a subset. Known out-of-scope dependencies
  block effects. Uninspectable public impact needs a decision unless existing authority
  covers the risk. Complete unreferenced local deletion needs no ritual reconfirmation.
- Untouched files remain byte-identical. Changed-file canonical wrapping may differ
  only while out-of-scope entries, literals and typed identities retain meaning. Reject
  escapes and symlinks, stale identities and false readiness. Reconcile actual partial
  external effects before retry; no OAK transaction rollback claim.
>>

presentation: YAML<<
- Derive the five ordered view fields and complete DRAFT from WORK, not a second specification.
  Understanding addresses the latest turn; CHANGES describes this turn or says No
  meaning changed. NEXT_DECISION is empty without a meaningful decision, and its empty
  heading is omitted. Return to parent/user, never wait, poll, delegate or assume
  AskUserQuestion.
- INTENT_AST is a text-fenced compact semantic tree using ├─, └─ and │, grouped by
  actual OAK parts with short explanations. Show schema purpose, expanded fields/types/constraints;
  process purpose, input, ordered steps and outputs. Relevant kind/tool context accompanies
  the tree, not a new OAK part. Keep source/revision/check bookkeeping outside the
  default tree.
- Every turn includes ✓ confirmed · ~ proposed · ? unresolved. Map markers to current
  annotations, including expanded fields and steps; retain stable ids, unchanged status
  and explicit contradictions. Grouping labels need no invented marker. Collapse only
  when no unresolved descendant or new change is hidden; never imply an entire partly
  unresolved branch is confirmed.
- A status marker is intended meaning, not validation, implementation or authority.
  Show blockers with ids, consequences and useful questions, without fixed counts.
  Parent may show only the five views if it retains the complete result; otherwise
  supply DRAFT for continuation. Artifacts and observed validation/effect evidence
  stay outside canonical OAK.
>>

tool-context: YAML<<
- Separate authoring-host capability evidence from consumer requirements. Exact registry/declaration
  or successful permitted read-only inspection can confirm that context only; documentation
  proves contracts, not availability. Known complete consumer requirements may remain
  unverified without blocking authoring.
- Record individual exact operations, nullable unknown server/name/contracts, effects,
  permission limits and evidence. Never fabricate a named tool from prose. Native
  ACT is intentional interpreter work; named ACT needs an established exact name and
  mapping. Missing behaviour-changing contracts remain unresolved.
- No tools needed is a confirmed /tools annotation and empty tools list; no discovery
  call. No skill search/listing, server start, connector provisioning, accounts, installation,
  test write or registry implementation. Existing host tools only, under actual scope.
>>

validation-gate: YAML<<
- VALIDATE=false invokes no helper or installation inquiry. Requested validation first
  uses exact helper without --allow-install if execution exists. Missing execution
  is not-performed; permission-required is a separate installation-consent decision,
  not malformed OAK.
- Only actual separate download/dependency consent in context permits --allow-install
  later. Return pending consent to parent, preserving direct authority. Declined/unavailable
  optional checks may accompany honestly unvalidated reviewed OAK; validation_required
  demands an actual pass on this subject.
- Known invalidity, identity mismatch, stale results, unresolved fidelity or required
  unmet validation sets DELIVERABLE=false and prohibits effects. Meaning-preserving
  syntax repair updates this same draft; repair/recheck affected failures, not unchanged
  successes. Receipts retain observed method, subject, evidence and exits; simulations
  identify themselves.
>>
</constants>

<schemas>
<schema id="work-input">
WORK: <WORK>

WHERE:
- <WORK> is string; is non-empty.
</schema>

<schema id="route-result">
WORK: <WORK>
OPERATION: <OPERATION>
GUIDED: <GUIDED>

WHERE:
- <WORK> is string; is non-empty.
- <OPERATION> is string; is one of `create`, `read`, `update`, `delete`.
- <GUIDED> is boolean.
</schema>

<schema id="kind-result">
KIND_DRAFT: <KIND_DRAFT>

WHERE:
- <KIND_DRAFT> is string; is non-empty.
</schema>

<schema id="tool-result">
TOOL_DRAFT: <TOOL_DRAFT>

WHERE:
- <TOOL_DRAFT> is string; is non-empty.
</schema>

<schema id="source-result">
MAPPED_DRAFT: <MAPPED_DRAFT>

WHERE:
- <MAPPED_DRAFT> is string; is non-empty.
</schema>

<schema id="draft-result">
UPDATED_DRAFT: <UPDATED_DRAFT>

WHERE:
- <UPDATED_DRAFT> is string; is non-empty.
</schema>

<schema id="review-result">
REVIEWED: <REVIEWED>
READY: <READY>

WHERE:
- <REVIEWED> is string; is non-empty.
- <READY> is boolean.
</schema>

<schema id="operation-input">
WORK: <WORK>
READY: <READY>
VALIDATE: <VALIDATE>

WHERE:
- <WORK> is string; is non-empty.
- <READY> is boolean.
- <VALIDATE> is boolean.
</schema>

<schema id="dispatch-input">
WORK: <WORK>
READY: <READY>
VALIDATE: <VALIDATE>
OPERATION: <OPERATION>
GUIDED: <GUIDED>

WHERE:
- <WORK> is string; is non-empty.
- <READY> is boolean.
- <VALIDATE> is boolean.
- <OPERATION> is string; is one of `create`, `read`, `update`, `delete`.
- <GUIDED> is boolean.
</schema>

<schema id="render-input">
WORK: <WORK>
VALIDATE: <VALIDATE>

WHERE:
- <WORK> is string; is non-empty.
- <VALIDATE> is boolean.
</schema>

<schema id="render-result">
RENDERED: <RENDERED>
ARTIFACTS: <ARTIFACTS>
VALIDATION: <VALIDATION>
DELIVERABLE: <DELIVERABLE>

WHERE:
- <RENDERED> is string; is non-empty.
- <ARTIFACTS> is string; is non-empty.
- <VALIDATION> is string; is non-empty.
- <DELIVERABLE> is boolean.
</schema>

<schema id="effect-input">
WORK: <WORK>
ARTIFACTS: <ARTIFACTS>
VALIDATION: <VALIDATION>

WHERE:
- <WORK> is string; is non-empty.
- <ARTIFACTS> is string; is non-empty.
- <VALIDATION> is string; is non-empty.
</schema>

<schema id="effect-result">
EFFECTS: <EFFECTS>

WHERE:
- <EFFECTS> is string; is non-empty.
</schema>

<schema id="response-input">
WORK: <WORK>
ARTIFACTS: <ARTIFACTS>
VALIDATION: <VALIDATION>
EFFECTS: <EFFECTS>

WHERE:
- <WORK> is string; is non-empty.
- <ARTIFACTS> is string; is non-empty.
- <VALIDATION> is string; is non-empty.
- <EFFECTS> is string; is non-empty.
</schema>

<schema id="conversation-response" name="Conversation Response" purpose="Present the current intent and its next meaningful decision.">
Understanding
<UNDERSTANDING>

Intent AST
<INTENT_AST>

Changes
<CHANGES>

Next decision
<NEXT_DECISION>

Readiness
<READINESS>

WHERE:
- <UNDERSTANDING> is string; is non-empty.
- <INTENT_AST> is string; is non-empty.
- <CHANGES> is string; is non-empty.
- <NEXT_DECISION> is string.
- <READINESS> is string; is non-empty.
</schema>

<schema id="draft-response">
DRAFT: <DRAFT>
UNDERSTANDING: <UNDERSTANDING>
INTENT_AST: <INTENT_AST>
CHANGES: <CHANGES>
NEXT_DECISION: <NEXT_DECISION>
READINESS: <READINESS>

WHERE:
- <DRAFT> is string; is non-empty.
- <UNDERSTANDING> is string; is non-empty.
- <INTENT_AST> is string; is non-empty.
- <CHANGES> is string; is non-empty.
- <NEXT_DECISION> is string.
- <READINESS> is string; is non-empty.
</schema>

<schema id="delivery-choice">
LEGACY: <LEGACY>
OAK: <OAK>

WHERE:
- <LEGACY> is boolean.
- <OAK> is string.
</schema>

<schema id="permission-result">
GATED: <GATED>
PERMITTED: <PERMITTED>
DEFERRED_EFFECTS: <DEFERRED_EFFECTS>
DEFERRED_VALIDATION: <DEFERRED_VALIDATION>

WHERE:
- <GATED> is string; is non-empty.
- <PERMITTED> is boolean.
- <DEFERRED_EFFECTS> is string; is non-empty.
- <DEFERRED_VALIDATION> is string; is non-empty.
</schema>
</schemas>
