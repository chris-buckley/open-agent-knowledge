# OAK authoring agent completion report

Date: 2026-09-08
Plan: [0017](plan.md)
Status: Complete. PR #25 is open for review; the implementation passed Verify OAK. Final record updates receive the same required checks.

## Outcome

The authoring skill now supports direct Create, Read, Update and Delete and optional guided intent development through one stateless workflow. It retains one partial draft, clause mappings and confirmed/proposed/unresolved annotations, and returns the complete draft with a compact explained intent tree on each turn. The user or parent retains continuation data and actual authority.

The 35-file skill includes the six-kind catalogue and separate Codex and Claude native definitions. Both native files contain the exact standalone body. The four existing explorer scenario/native files, eight teaching documents, all reference documents, grammar, generic scaffold and orchestration knowledge retain their original bytes. Only the capability version changes in the optional validator; its immutable source and dependency identities remain unchanged.

The user authorised the standalone budget revision and separately approved 24,000 bytes for the skill entry. The reviewed standalone ceiling is 128,000 bytes; the entry's existing 500-line bound remains. These are repository budgets, not claimed provider limits.

## Measurements

| Artifact | Actual | Limit |
| --- | ---: | ---: |
| Skill entry, metadata included | 22,256 bytes | 24,000 bytes |
| Skill entry | 456 lines | 500 lines |
| Complete shared standalone body | 95,579 bytes | 128,000 bytes |
| Codex native definition | 95,746 bytes | Body is exactly the shared standalone |
| Claude native definition | 95,754 bytes | Body is exactly the shared standalone |

Standalone SHA-256: `71b1cb0abef42080e10e9814c5a3733ea90fc2dcc9d8f9c057b44ee81c27ddc9`.
Code and product fingerprint: `485ca88a8e3b61352ab8fda41dc3382cca366dc8f369e5560bd6d0f94feeb530`. The full per-product byte manifest, all 16 shared input measurements and the fingerprint methods are in [verification.json](evidence/verification.json). This accounts for complete content, including protected literals, native metadata and generated interpretation guidance.

## Verification

The complete module and direct entry points passed all 38 registered checks in an external Python 3.11.9 environment with the declared dependencies. All five generators were repeated; the complete file, directory and byte inventory was identical. The exact checked workspace fingerprint was `a86b885fc36888af5194fafbf7eca4f0b7365e8cab19ec702b3b06c5b3c756fd` before this completion-record update. The publication process reruns required checks after record changes; the PR's check status is authoritative for its final Git head.

Independent review against published input commit `6df8e13c936376ada0967385888ca61ec09a867b` passed 190 preservation assertions. The package and dependency bytes were unchanged, all expected skill/native files were present, and both native bodies had standalone closure with no sibling instruction dependency.

| Command | Exit |
| --- | ---: |
| `python -m compileall -q oak build examples` | 0 |
| `python -m examples.catalog` | 0 |
| `python -m build.ebnf` | 0 |
| `python -m build.definitions` | 0 |
| `python -m build.agents` | 0 |
| `python -m build.authoring` | 0 |
| `python -m build.examples` | 0 |
| `python build/examples.py` | 0 |
| `python -m examples.catalog` | 0 |
| `python -m build.ebnf` | 0 |
| `python -m build.definitions` | 0 |
| `python -m build.agents` | 0 |
| `python -m build.authoring` | 0 |

| Required comparison | Observed evidence |
| --- | --- |
| E02 | Complete two-turn draft instances; missing value remains absent; annotation pointers, statuses, legend, expanded markers, continuity and forged-authority rejections; same result on four forms. |
| E03 | Direct CRUD and twelve kind cases bypass guided elicitation; natural and typed legacy entrances agree; multi-file legacy input returns an empty-manifest conversation result. |
| E04 | Read changes zero temporary-file bytes; scoped update preserves the other constant and unrelated binary; explicit reference resolution rejects a dangling consumer; tombstones and path, symlink, stale-source and partial-effect rejections. |
| E05 | The supplied JOB specimen executes both condition branches with exactly one outcome and read-before-review order. Independent mutations reject lost else, reordered work, changed literal, added state, invented named tool and erased no-write/host boundary. |
| E06 | Six catalogue records and version are exact constants; twelve named scratch/transformation outcomes run across modular, standalone and both native bodies. Changed knowledge/catalogue versions require recovery rather than silent reinterpretation. |
| E07 | Host and consumer tool records retain exact separate names, contracts and registry evidence; documentation cannot confirm availability; unknown operation remains null and no-tool input remains empty. |
| E08 | Both native formats decode to the exact standalone body, with independent metadata expectations and Unicode, quote, control-character and newline cases. Four explorer scenario/native files remain byte-identical. |
| E09 | Requested, unrequested, available, missing-execution, pending/declined/granted installation, failed, stale, required-unperformed and repaired validation decisions exercise gates. Existing real optional-helper identity, source/dependency, bootstrap and consent checks remain active. |
| E10 | Exact 35-file skill and 15-document supporting graph; one operational entry; canonical closure, cold repair, detached copies, symlink/fusion/literal rejections and complete teaching/template/helper/grammar preservation. |
| E11 | Pinned source archive and recovered edits were reconciled without replay. Independent preservation review and complete current verification have concrete manifests; publication remains a separate observed operation. |

E01 remains an illustrative presentation specimen. The E02 status/tree checks exercise the required continuity and display rules without claiming one fixed prose style or question count.

## Phase evidence

| Tasks | Evidence |
| --- | --- |
| P01.01-P01.05 | Published approved design and original input fingerprints. |
| P02.01-P02.04 | Four local public schemas, complete internal contracts, full content measurements, partial-draft and malformed-data fixtures. |
| P03.01-P03.05 | Maintained catalogue/platform owners, bounded loaders, exact profiles, source routing and unchanged explorer serialization. |
| P04.01-P04.05 | Ordered preparation, independent CRUD, guided release, fidelity/consent/effect gates, same-draft terminal emissions and four-form execution fixtures. |
| P05.01-P05.05 | 35-file skill, complete standalone/native bodies, version-only helper change, preserved explorer files and repeated generation. |
| P06.01-P06.05 | Both full entry points, all negative cases, cold/detached checks, exact manifests and final scope review. |
| P07.01-P07.03 | Independent intent/preservation review and this measured report. |
| P07.04 | [PR #25](https://github.com/chris-buckley/open-agent-knowledge/pull/25) is open and non-draft; implementation `20cc3c6` passed [Verify OAK](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/34190963898). The PR check record covers its final documentation head. |

## Review findings resolved

The recovered catalogue was moved to its approved build-owned assets/constants path. Repeated terminal code now shares a stateless finish-response process. The composition helper returns exactly its six new bindings; the caller retains artifact and validation/effect evidence and passes all nine fields to the complete publication boundary. This respects CALL's complete output promotion without changing OAK or rebinding existing inputs.

The repair matrix now selects explicit paths for the new native definitions and catalogue, avoiding a branch that previously repeated the explorer mutation.

The publication step compared all 631 Git index blobs with the verified workspace, including the Claude native file beneath the repository's ignored .claude directory pattern. This check is retained in build ownership knowledge.

The final review added independent draft/status/fidelity/CRUD/tool-context oracles and the missing validation cases. Each oracle is labelled as an offline specimen check. It complements actual OAK execution and format checks; it is not a second product runtime or evidence of natural-language model performance.

## Changed paths

The implementation changes relative to the published handoff are below. This report and its verification evidence are additional completion records; the plan's final directory tree includes them.

- `.agents/adaptors/codex/adaptor.oak.md`
- `.agents/rules/context.oak.md`
- `build/AGENTS.md`
- `build/agents.py`
- `build/authoring.py`
- `build/authoring_agent.py`
- `build/authoring_guides.py`
- `build/authoring_platforms.py`
- `build/authoring_resources/assets/constants/artifact-kinds.oak.md`
- `build/authoring_resources/platforms/claude/adaptor.oak.md`
- `build/authoring_resources/platforms/codex/adaptor.oak.md`
- `build/authoring_validator.py`
- `build/checks/__init__.py`
- `build/checks/agent_deliveries.py`
- `build/checks/authoring.py`
- `build/checks/authoring_agent.py`
- `build/checks/authoring_intent.py`
- `build/checks/ebnf.py`
- `build/checks/outputs.py`
- `docs/plans/0017-oak-authoring-agent/plan.md`
- `generated/oak-authoring.oak.md`
- `generated/oak-authoring.skill/SKILL.md`
- `generated/oak-authoring.skill/assets/constants/artifact-kinds.oak.md`
- `generated/oak-authoring.skill/guides/authoring.oak.md`
- `generated/oak-authoring.skill/guides/validation.oak.md`
- `generated/oak-authoring.skill/platforms/claude/adaptor.oak.md`
- `generated/oak-authoring.skill/platforms/claude/templates/.claude/agents/oak-authoring.md`
- `generated/oak-authoring.skill/platforms/codex/adaptor.oak.md`
- `generated/oak-authoring.skill/platforms/codex/templates/.codex/agents/oak-authoring.toml`
- `generated/oak-authoring.skill/scripts/validate.py`
- `generated/oak.agents/adaptors/codex/adaptor.oak.md`

## Limits and publication

No live Codex or Claude client loading, model-performance test, installation or permission-enforcement certification was performed. Native metadata requests defaults; the actual host retains tools, permissions, transport and persistence. No new workflow, runtime service, MCP registry or account configuration was introduced. The original Pro run finished without being stopped; its checkpoints and visible edits were recovered, then completed and verified locally.

The user authorised commits, pushes and one reviewable PR into main. Merge is not authorised. [PR #25](https://github.com/chris-buckley/open-agent-knowledge/pull/25) was published from `feat/oak-authoring-agent` into `main` at implementation commit `20cc3c66cbec94cbc6ec9e7bb3499a1659e95367`. [Verify OAK run 34190963898](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/34190963898) completed successfully, including its detached bootstrap/cache-reuse step. The PR remains unmerged. The final-head check in the PR is authoritative for this later record update.
