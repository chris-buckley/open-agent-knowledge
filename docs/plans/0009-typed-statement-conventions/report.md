# Typed statement conventions: implementation report

Plan: [0009](plan.md)
Branch: `plan/typed-statement-conventions`
Status: Complete; delivered for review in PR #15.
Baseline: `82b6e66d7e50511a3212046812c6b0567cf9c3e4`, based on merged main `4fd86cee4b85bb946a9c8ce7eab2c405e5568144`.
Package pin: `2b542c613c5d1a7e64b597884fae4f444ac34916`.

## Outcome

One action sentence changes in `examples/shape_writer/example.py`. The process remains `process.decide-change`, using its existing input/output schemas, bindings, fixture, native handler, and surrounding pipeline.

Before:

```text
For <CRITERION>, weigh <CURRENT> against <PROPOSED> and produce <DECISION> and <RATIONALE>.
```

After:

```text
Assess <CURRENT> and <PROPOSED> against <CRITERION>; produce <DECISION> and <RATIONALE>.
```

CURRENT and PROPOSED remain the alternatives, CRITERION remains the standard, and DECISION and RATIONALE remain the results. The wording makes the relation explicit without adding an obligation, negation, authority, proof claim, or effect. This is a prose review, not evidence of improved model performance.

Two advisory rules in `oak/rules/guidance.py` describe action roles and distinguish validate, assess, and publish. The existing binding rule now states that role names alone are not types. `build/authoring_guides.py` assigns each rule one guide owner; `examples/AGENTS.md` points there rather than copying a vocabulary.

The same generated decision example and rule text reach the progressive skill and assembled agent. Repeated explanatory wording in the structure, schema, and process guides is shortened to retain the existing size limits. No teaching document, grammar material, schema, scope, or consent obligation is removed.

## Verification and evidential limits

[Baseline evidence](evidence/baseline.json) records the input revision, verified archive tree, protected file list, existing pilot structure, fixtures, sizes, and local dependency versions. [Verification evidence](evidence/verification.json) records exact comparisons, observed command results, and all 32 check groups.

| Check | Observed result |
| --- | --- |
| `python -m compileall -q oak build examples skills/oak-authoring/scripts` | Passed. |
| `python -m examples.catalog` | Passed; full source-owned bundles regenerated. |
| `python -m build.ebnf` and `python -m build.docs` | Passed; protected grammar and reference contracts unchanged. |
| `python -m build.authoring` | Passed; source-derived skill and agent refreshed. |
| `python -m build.examples` | Exit 0. |
| `python build/examples.py` | Exit 0. |
| All registered checks, individually observed | 32 passed. |
| Repeat all four generators | 92 owner-derived product files retain exact paths and bytes. |
| Protected files | All 150 retain exact bytes. |
| Pilot structure | Entire normalized node equals baseline after restoring only the selected instruction text. |
| Fixtures and populated layouts | Unchanged. |
| Skill/agent parity, detached bundles, scope rejection, consent checks | Passed through existing full verification. |
| Pinned download and isolated install/cache reuse | Passed in implementation run 33966380583 and PR run 33966523488. |

The added checks use the existing schemas and actual pipeline. Missing input roles and a numeric CURRENT fail schema binding. Missing or unexpected outputs fail with `act_output_mismatch`; empty DECISION and numeric RATIONALE fail with `invalid_act_output`, before any later fixture phase runs. Two alternative sentences parse and round-trip in both groupings and retain the declared fixture dataflow.

The contrary judgment `Accept blank titles.` with `No reason is needed.` remains structurally valid. Its populated result differs from the fixture, and the existing next-phase fixture handler rejects those unexpected inputs. That is an exact fixture comparison, not a general truth checker. There is no new English parser, nominal role datatype, effect system, function registry, or synonym ban.

The full suite retains the existing source-backed arrivals, local scope, closed bundles, inert operational teaching examples, and refusal of unsafe fusion. It does not certify arbitrary interpreter reasoning, real publication, or live external effects.

## Capability identity and size

Skill version: `2.2.0`.
Validator source revision: `2b542c613c5d1a7e64b597884fae4f444ac34916`.
Source SHA256: `e9c301a254ec8897698816091bac99cc117d8e0fa052192e728d356d19c27bd1`.
Dependency SHA256: `2412c436c0ffaa05c604da2d58be4b72c443b37efcaa094380845fd0fe3a3702`, unchanged.

The guidance edit changes the whole-package source fingerprint. The refreshed pin identifies a real committed package with the exact local tree `c48dedf0a567f3182337801a69a028cab9373930`; the validator algorithm is unchanged. Its Python syntax tree matches the baseline after excluding only version, source revision, and source fingerprint assignments.

The skill entry remains 8,299 bytes and 190 lines. The assembled agent is 63,943 bytes, below the unchanged 64,000-byte limit. The teaching collection remains the same four-stage set. Rules about non-closed shape selection, repeated placeholders, and avoiding forced lists remain in `preserve-schema-shape`, `respect-schema-cardinality`, and `choose-schema-shape`; only duplicate explanation was removed.

## Per-task evidence

| Task | Evidence |
| --- | --- |
| P01.01 | Root and routed owners, complete amended plan, pilot/fixture/schema sources, generators, relevant checks, and Pydantic skill reviewed. Pydantic model/strict-mode documentation checked for fresh validation of test variants. |
| P01.02 | `evidence/baseline.json`; baseline CI run 33965141124 and both local entry points passed. |
| P01.03 | Before/after role review above and the `pilot_change` evidence. |
| P02.01 | One-line Python instruction diff and normalized-node comparison. |
| P02.02 | This report and preserved plan E01-E04; no second maintained exemplar. |
| P02.03 | `build/checks/shapes.py::_decision_statement`, reached by `validate_shapes`. |
| P03.01 | Two added guidance entries and refined `bind-values`. |
| P03.02 | `distinguish-action-promises` explicitly separates claims and retains host authority and exact tool names. |
| P03.03 | `RULE_OWNERS`, source-owned generated references, and the single examples-owner pointer. |
| P03.04 | `_guidance_delivery` verifies every rule's source-to-guide-to-agent equality; `_decision_statement` accepts alternative prose in both groupings. |
| P04.01 | Committed package pin and matching complete source/dependency fingerprints; helper logic comparison. |
| P04.02 | Catalogue, grammar, reference, and authoring generators, then full freshness checks. |
| P04.03 | Sizes above; guidance compaction retains all obligations through their original owners. |
| P04.04 | Existing parity, detached closure, inert teaching, and operational fusion rejection checks pass. |
| P05.01 | Both full entry points exit 0; all 32 registered checks also pass individually. |
| P05.02 | New-pin bootstrap and cache reuse passed in GitHub runs 33966380583 and 33966523488 with declared dependencies. |
| P05.03 | Protected comparison, 92-product repeat-generation equality, and no obsolete sentence outside historical plan evidence. |
| P05.04 | Implementing-agent diff and meaning review; findings resolved below. |
| P05.05 | PR #15 opened; head d3c532fc5ea24a3c807fd8a7ced108c1a081047f passed run 33966523488. The final status commit changes only this plan, report, and verification record; its own CI is checked before handoff. |

## Review and operational notes

The first full check rejected noncanonical YAML wrapping in the new examples-owner pointer. Rendering that AGENTS document canonically fixed it. Grouped local verification commands encountered execution-tool timeouts; rerunning each entry point separately produced explicit exit 0 results. A one-off evidence script initially needed the repository on its Python import path; it was rerun successfully without changing repository code.

Local checks use preinstalled Pydantic 2.13.4 and pydantic-settings 2.14.1. The latter is below the repository's declared minimum 2.15, so local runs supplement, rather than replace, GitHub runs that install all declared dependencies. No dependency declaration was changed.

A temporary branch-only workflow exports the committed source because direct cloning fails DNS resolution. Its artifact matches GitHub's exact Git tree. All transfer files and the temporary workflow are absent from the cleaned PR tree; their creation and removal remain in branch history. The ordinary verification workflow is unchanged.

Product SHA256: `764f28c1ca9390f69a8eb62c3421e5e92b17a241f5db2232f10513eca90de503`. This hashes sorted tracked paths and bytes with NUL separators, excluding `docs/plans/` and temporary transfer/workspace paths, as described in verification evidence.

Review verdict: Approved for review delivery after all applicable checks passed. This is implementing-agent review, not an independent review. All 19 tasks have evidence. No merge is authorized.

## Delivery evidence

PR: [#15](https://github.com/chris-buckley/open-agent-knowledge/pull/15).
Implementation: `288ac782c5ee940a9fba209ca4e24cd953907175`, verified in [run 33966380583](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33966380583).
Cleaned candidate: `d3c532fc5ea24a3c807fd8a7ced108c1a081047f`, tree `d4614d380a43f4b0ef2e2e57d5bfc07b2dca1c4c`, exactly equal to the locally reviewed tree.
PR verification: [run 33966523488](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33966523488), job `101307509725`, all steps successful, including full checks, generation freshness, and pinned bootstrap/cache reuse.

During delivery main advanced to `21c2dc5b9366068875709e1cefab3a942f51836c`, adding only `.agents/rules/coding-standards.md`. This PR has no overlapping changes; GitHub reports it mergeable and its test merge passed verification. The unrelated document is not overwritten or removed.

The status-only closeout preserves the tested product fingerprint above. Its final-head verification is recorded in the PR conversation after the check finishes; no commit claims to contain its own future CI result.
