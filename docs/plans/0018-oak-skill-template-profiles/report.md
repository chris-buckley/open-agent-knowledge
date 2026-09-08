# Plan 0018 implementation report

[Plan](plan.md)

The reusable skill-template capability is implemented. One stateless foundation now supports an explicitly selected stateful extension, with complete package descriptions and worked composition and memory examples. The authoring skill remains stateless and both authoring forms contain the same knowledge.

The plan is self-contained and sanitised. Private workspace paths, personal identifiers and unrelated project provenance are excluded. R01-R09, E01-E06, D01-D06 and all twenty implementation tasks remain represented. Original private material and recovery records were kept outside the repository.

## Published implementation

The planning-format milestone is `1e21b227faae9a4f5ead997047af718db84ffd8d`. The profile implementation is `9cd9e366a024c7ba953ec8a853bd49cebade5799`, on `docs/prepare-skill-template-profiles` through PR 26. Both commits were pushed and their exact remote tips confirmed.

The first milestone delivers the sanitised plan, metadata frontmatter, Intent before Situation, prospective adoption from Plan 0018, and preservation of older planning formats and checks. The second delivers the source-owned template, selected resources, worked packages, fixture host and acceptance checks. This report and the completed checklist are documentation of that verified implementation.

## Requirements and comparisons

| Comparison | Observed result |
| --- | --- |
| E01: shared foundation | One base in [skill_template.py](../../../build/skill_template.py), with the state slot selected explicitly. Both profiles populate through canonical Node assembly. The installed template and standalone literal match their source. |
| E02: stateless package | The classifier accepts explicit text and policy, returns the fixed expected category, rejects invalid inputs and outputs, and leaves source bytes and persistent storage unchanged. |
| E03: owned memory | Two synthetic owners remain isolated. Saved retention choices are reused. Compatible source updates and renamed exposure preserve the stable instance. Interrupted record/index publication recovers exact existing work without duplicate writes. |
| E04: INDEX and MAP | Independent expected file sets match the actual package maps, fixed local scaffolds and declared loading conditions. Roles retain the requested order while OAK parts remain canonical. Mutable records do not enter the shared discovery index. |
| E05: composition and boundaries | The reviewer calls the same separate classifier export. Missing, changed, escaping, wrong-kind and cyclic dependencies are rejected, as is foreign state access. Detached execution passes with repository imports and network access blocked. |
| E06: illustrations | The original larger illustrations remain labelled illustrative. D05 records the smaller complete selected packages and every actual leaf. |

The [profile checks](../../../build/checks/skill_profiles.py) cover manifests, resource selection, both groupings, declared graph roots, optional validation and detached execution. The [memory cases](../../../build/checks/skill_profile_cases.py) cover malformed CSV, duplicate IDs, dangling and escaping references, symbolic links, owner/version mismatches, writer conflicts, input drift, failed read-back, retention and protected records. The [normal-file adapter](../../../build/checks/skill_profile_memory.py) is repository-only fixture code.

The fixture demonstrates record-before-index publication, exact orphan reconciliation, read-back of an already-published pair, and preservation of a simulated tool-owned effect after interruption. A failed OAK transaction leaves caller state unchanged; it does not undo file or external effects.

## Delivered files and ownership

| Package | Shared files |
| --- | --- |
| classify-item | `SKILL.md`, `processes/classify-item.oak.md` |
| review-items | `SKILL.md`, `references/memory.oak.md` |

The stateful instance separately creates `.gitignore`, `state/configuration.json`, `state/policy/index.csv`, `state/policy/priority.json`, `state/history/index.csv` and `state/runs/index.csv`. Learned policy records, reviewed history records and run contents are generated locally. The example does not need raw or runtime directories. Shared updates do not supply or overwrite these mutable files.

The [scenario catalogue](../../../examples/catalog.py) owns registration and canonical siblings. Only the complete inert package mapping and sample data enter supplementary installed teaching. The four original core stages and their existing operational specimens remain intact; no nested example `SKILL.md` is installed.

The final product diagram in the plan covers the source and generated changes. The separate planning-format milestone also changes [docs ownership](../../AGENTS.md), the [SMEAC source](../../../examples/schemas/smeac_plan.py), its canonical sibling and planning checks. No original inspection file is included.

## Verification

The implementation candidate had content fingerprint `8831154a3a0c44e1b95801c174b08b96c9e0cfa8208c033ce21db8585084fbd4`. The complete candidate file manifest remained unchanged across both full checks and repeated generation. The fingerprint was computed from actual tracked and untracked candidate bytes before staging, not assigned by the model.

| Check | Observed result |
| --- | --- |
| `python -m compileall -q oak build examples` | Passed |
| `python -m examples.catalog` | Passed, canonical source-derived siblings |
| EBNF, definitions, agents and authoring generators | Passed |
| `python -m build.examples` | Passed |
| `python build/examples.py` | Passed |
| Repeat all affected generators | Identical candidate file manifest |
| Generated files against Git index | All 83 generated files matched, including native templates |
| Privacy and retained requirements | Passed full-plan review and focused scans |
| `git diff --check` and scoped AGENTS bounds | Passed; root remains 500 lines |

Local verification used Python 3.13.2 and the declared dependencies, including Pydantic 2.13.5, in an external environment without an editable repository installation. Repository acceptance includes cold generation, repair, detached closure, unsafe paths, consent handling and native authoring parity. The existing Verify OAK workflow repeats both full entry points and performs its approved detached bootstrap check on published revisions; the PR checks retain the current head result.

| Delivery | Observed size | Existing limit |
| --- | ---: | ---: |
| Authoring skill entry | 22,518 bytes, 457 lines | 24,000 bytes, 500 lines |
| Standalone authoring agent | 122,744 bytes | 128,000 bytes |

The skill version is `3.4.0`. OAK package code and dependency declarations are unchanged, so the optional validator retains revision `85ddd5393fd4349632f728f5a05cb67f9bc5dbf5`, source fingerprint `9bca0d69e12c26aac64d3e7218f4ccfc620e7a7196b569d324ff7ac8197053bc` and dependency-declaration fingerprint `2412c436c0ffaa05c604da2d58be4b72c443b37efcaa094380845fd0fe3a3702`.

## Task evidence

| Tasks | Evidence |
| --- | --- |
| P01.01-P01.04 | Confirmed branch and baseline, complete source inspection, resolved D01-D05, independent manifests and measured unchanged byte budgets. |
| P02.01-P02.04 | Build ownership, single template source, explicit extension routing, canonical assembly, inertness and skill/standalone parity checks. |
| P03.01-P03.04 | Registered complete examples, actual shared call, two-owner file fixtures, retention, recovery, input/writer conflict and protected-record cases. |
| P04.01-P04.04 | Complete regenerated deliveries, preserved immutable validator identity, cold repair, detached execution and final size checks. |
| P05.01-P05.04 | Both full verification commands, repeat-generation identity, privacy and diff review, this report and delivery through the existing PR. |

## Acceptance boundary

Acceptance covers the authored knowledge, generated artifacts and deterministic local fixtures. The optional validator reports parse and resolve checks, not memory integrity or successful effects. Actual host discovery, permissions, persistence, concurrent-writer enforcement and live external operations need their own evidence. No installation, live-instance change, provider configuration or merge is part of this delivery.

Verdict: the complete OAK product scope is implemented and locally verified. The final published PR revision must retain passing CI before the review handoff.
