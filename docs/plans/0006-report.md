# Compact OAK Authored Syntax: Completion Report

Prepared: 2026-09-05
Classification: PUBLIC
Plan: [0006-plan.md](0006-plan.md)
Branch: `feat/compact-oak-syntax`
Implementation verdict: Approved, following a separate self-review pass.
Delivery status: complete; all 101 plan tasks are evidenced and PR #12 is open for review.

## Outcome

The accepted D01-D18 surface revision is implemented. Conditions use recursive `ALL(...)`, `ANY(...)`, and `NOT(...)` expressions. `IF condition:` has a direct indented suite and aligned `ELSE:`. Bounded `WHILE` and `ASSERT` share the condition parser. Triggers are named declarations with typed targets, explicit fields, optional guards, and shared seed bindings. Long lists use the fixed 100-code-point canonical layout.

This is a breaking authored-syntax change, not a semantic-model redesign. The old live trigger fact ledger and `THEN` wrappers are rejected. There is no compatibility mode, host-language evaluation, infix alias, truthiness rule, implicit seed, or new version field in OAK documents. The authoring capability is version 2.0.0. The package's pre-existing 0.0.0 version remains unchanged.

All current AGENTS documents, affected example renders, generated references, the portable skill, and the assembled agent use the new surface. The SMEAC convention for future numbered plans is retained in `docs/AGENTS.md`. Historical plans and legacy APS material were not rewritten.

## Verification subjects and publication

| Subject | Revision or evidence |
| --- | --- |
| Planning baseline on main | `a451cb5fcddf9383d4f01135a7316c3f06dcc97a` |
| Committed plan acknowledged by continuation | `565d284a4130e371fe07da3e9a8dbfd5dc66785b` |
| User execution authorisation | 2026-09-05T13:03:09+10:00, in the task conversation |
| Executed baseline | `cad4f084729b22fd360ada9a332cc66793b286ed`; product sources equal the planning baseline, with a temporary export workflow added |
| Published immutable validator package | `dac756b5424f7b1e19fc6f87ffc0400e90319b96` |
| Verified implementation and capability candidate | `8ef93c13d1a9dc0f181bc0b4200e878f44b541dc` |
| Baseline runner | [33940880581](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33940880581), successful |
| Publication and complete verification runner | [33943082560](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33943082560), successful |

Direct GitHub networking in the container failed on DNS. A temporary branch-only workflow exported a credential-free Git bundle and declared dependency wheels. The bundle was imported into an isolated local checkout, so the local checks below executed actual repository code rather than reconstructed excerpts. A later branch-only workflow verified the before and after hashes of all 26 transferred Python sources, regenerated products through their owners, published the package, and repinned the capability in a subsequent commit. All temporary workflow and transport files were removed from the delivered tree. There is no permanent CI change.

Both the GitHub runner and the local Python 3.13 environment ran the complete baseline and candidate verification. The published candidate was imported from the runner's Git bundle, checked against the reviewed local package fingerprint, and verified again locally. Main was unchanged during delivery preparation, and the branch was ahead of main with no missing upstream commit.

## Observed checks

The following commands exited 0 against the published candidate. The two repository entry points also passed against the baseline before implementation.

```text
python -m compileall -q oak build examples skills/oak-authoring/scripts
python -m build.ebnf
python -m build.docs
python -m build.authoring
python -m build.examples
python build/examples.py
python -m build.ebnf
python -m build.docs
python -m build.authoring
git diff --exit-code
git diff --check
```

The module and direct verification entry points include the ten new compact-syntax check functions, the existing checks, generation freshness, scoped AGENTS ownership, example resolution, authoring fusion, and optional-validator outcomes. The successful full commands are recorded in runner 33943082560 and were repeated locally on the imported candidate. Repeated generation left no tracked changes. The published checkout was clean.

Actual baseline comparisons were byte-identical for the normalized 21 example Nodes, 38 model-example families, Node JSON Schema, public exports, and example JSON-LD. Eighteen existing execution traces and forty additional compact-syntax runtime traces were also identical between old and new packages. These observations cover returned state, ordered emissions, errors, untouched caller state, and native action inputs and outputs. They are evidence for the exercised behaviours, not a claim of exhaustive proof for arbitrary programs.

The cross-version runtime comparison executes the same programmatically constructed canonical Nodes with both executors. The old parser is not asked to accept the new syntax. Separate new-parser checks prove that each reviewed text specimen constructs its expected Node, resolves its targets, and round-trips under both groupings and both supported styles.

| Comparison capture | SHA-256, identical baseline and candidate bytes |
| --- | --- |
| Public export list | `877562ef9b1845a301e4abb4b27d83c63613326d10c345a9d9c20a2aa54447e9` |
| Node JSON Schema | `ccf652f190d00632bc8026e832ae9c870df6953dcb73af2b0a03665b820351f2` |
| 38 model-example families | `e792728cc3e3f1d545d1c1a0f3415e4ae2acc5be5ae93d1c698fe304d0de8be7` |
| 21 normalized example Nodes | `fab78d4e789b70ec3945702a77ea13ca7b793a912124dd656eb6694262cdc91e` |
| Example JSON-LD | `74156d79b1a57d404586c8f8219aef5a9f3525da6908d1150b0564ddfdc00535` |
| 18 existing execution traces | `353987c71caa1fabb401cf9ca8e584d6e169689b76ecbaeae6af0358e2b11569` |
| 40 compact-syntax execution traces | `d82c785188d16ae31a8b1c985b0e316a1550b88ae912da630bd2b484ae4fe61e` |

## Capability identity and scope

| Field | Verified value |
| --- | --- |
| Skill version | `2.0.0` |
| Validator revision | `dac756b5424f7b1e19fc6f87ffc0400e90319b96` |
| Source fingerprint | `06b44c4d4f2cb29e986952d734fcee984bdea5c055152071758790595b7eeafe` |
| Dependency declaration fingerprint | `2412c436c0ffaa05c604da2d58be4b72c443b37efcaa094380845fd0fe3a3702` |
| Skill entry size | 8,234 bytes; limit 10,000 |
| Standalone agent size | 51,952 bytes; limit 64,000 |

The package candidate was pushed before its revision was written into the validator. A subsequent metadata/product commit publishes the matching identity. The package and dependency declaration have no diff between that pinned revision and the verified candidate. Existing validator checks exercised actual valid/invalid subprocess outcomes, not-performed results, no-consent refusal, fingerprint mismatches, cache reuse, and controlled mocked installation/error cases without silently installing a runtime validator. The real detached bootstrap also passed in the existing PR workflow, run 33943314174: no-consent refusal, approved pinned download, isolated dependency installation, standalone parsing/resolution, and retained cache reuse without another permission flag.

Fusion still has one operational entry document and supporting constants/schemas only. Source instructions are not transplanted across policy scopes. Typed targets are resolved and rewritten, while literal values, embedded teaching documents, templates, scripts, and tool names retain their meaning. Both capability forms come from the same generated knowledge sources; they are not independently authored prompts.

## Changed owners

| Concern | Committed source and product paths |
| --- | --- |
| Shared syntax contract | `oak/surface/syntax.py`, `oak/surface/processes.py`, `oak/surface/entries.py` |
| Quote-aware recursive parsing | `oak/parse/expressions.py`, `conditions.py`, `values.py`, `steps.py`, `triggers.py`, `fragments.py` in `oak/parse/` |
| Canonical expression and declaration rendering | `expressions.py`, `processes.py`, `triggers.py`, `arrangement.py` in `oak/render/oak/` |
| Generated interpreter descriptions and authoring rules | `oak/node/interpretation.py`, `oak/rules/guidance.py` |
| Grammar and reference generation | `build/ebnf.py`, `build/surfaces.py`, `build/docs.py`, `outputs/oak.ebnf`, `outputs/docs/` |
| Conformance checks and registration | `build/checks/compact_fixtures.py`, `compact_syntax.py`, `compact_runtime.py`, `build/checks/__init__.py`; affected expectations in `execution.py`, `interfaces.py`, `rendering.py` |
| Shared authoring capability | `build/authoring_guides.py`, `skills/oak-authoring/`, `outputs/oak-authoring.oak.md` |
| Governance and practical examples | All ten repository AGENTS documents and affected sibling renders in `examples/agents/` |
| Plan and evidence | `docs/plans/0006-plan.md`, this report |

The existing Python example models already express the required canonical meaning and did not require semantic source edits. Their owning writers regenerated every sibling render. No executor, resolver, condition model, semantic validation, target vocabulary, or dependency implementation was changed. The guard clarification in `oak/node/AGENTS.md` documents the existing allowance for fixed constants rather than tightening validation.

## Task-to-evidence audit

Ranges below cover every task ID in the named range inclusively. The final delivery row is closed with the confirmed PR and observed final verification evidence. No task is removed or labelled not applicable.

| Task IDs | Evidence and result |
| --- | --- |
| P01.01-P01.04 | Preparation evidence in the committed SMEAC plan and the durable `docs/AGENTS.md` format convention; preserved historical records. |
| P01.05 | User continuation timestamp above; the remote planning tip matched the acknowledged plan before execution. |
| P02.01-P02.07 | Isolated bundle checkout, baseline runner 33940880581, local baseline module/direct commands, root and scoped owner reads, routed specialist reads, old-syntax inventory, and the captured model/API/interchange/runtime comparisons above. |
| P03.01-P03.07 | D01-D18 represented by the shared syntax constants, conventions, grammar productions and surface descriptors; capability 2.0.0 and unchanged package placeholder version. |
| P04.01-P04.08 | `ExpressionReader`, shared condition/binding entry points, complete-fragment checks, and `validate_compact_lexing`; malformed values retain physical line and field diagnostics. |
| P05.01-P05.09 | `oak/parse/steps.py`, `validate_compact_control`, S01-S07/S12, and the runtime checks; direct suites, aligned ELSE, required bounds, assertion metadata, unchanged canonical step fields. |
| P06.01-P06.10 | `oak/parse/triggers.py`, shared field order and required-field definitions, `validate_compact_triggers`, `validate_compact_routing`, existing interface/resolution checks, and S08-S11. |
| P07.01-P07.09 | `ListText`, shared expression rendering, trigger separator, `validate_compact_layout`, generated snapshots, all specimen grouping/style checks, and byte-stable repeated generation. |
| P08.01-P08.08 | Source/product ownership table above; generated EBNF and reference; unchanged semantic export/schema/interchange captures; all AGENTS ownership and canonical checks; classified obsolete-syntax search. |
| P09.01-P09.14 | S01-S12 and C01-C12 mapping below; ten registered conformance functions; 80 deterministic nested condition trees; 24 trigger field-order permutations; positive and negative contract cases; existing example writers and runner. |
| P10.01-P10.09 | Shared guide ownership and rule routing, generated skill/agent parity checks, observed byte sizes, two-commit immutable pin sequence, actual source/dependency equality, existing authoring and optional-validator checks. Explicit detached bootstrap passed in PR run 33943314174. |
| P11.01-P11.06 | Compilation, generators, both complete entry points, repeated clean regeneration, seven byte-identical comparison captures, current-syntax search, and observed 58 runtime traces. |
| P11.07-P11.09 | Separate self-review described below, resolved integration findings, repeated candidate checks, and this task/specimen/conformance evidence audit. |
| P12.01-P12.06 | This report, complete published candidate, and the confirmed PR/final-state evidence recorded in the delivery section. PR effects and handoff are not claimed before they occur. |

## Specimen and conformance mapping

Every S01-S12 specimen is defined in `build/checks/compact_fixtures.py` and exercised by `validate_compact_specimens` in `build/checks/compact_syntax.py`. Each exact text specimen parses into the expected contracted Node and resolves, then passes XML/Markdown and authored/controlled-style canonical round trips.

| Specimens | Meaning and additional checks |
| --- | --- |
| S01-S04 | Simple comparison, alternative branch, ALL, nested NOT; `validate_compact_control`, `validate_compact_short_circuit` |
| S05-S06 | ANY/deeper nesting and inner/outer ELSE association; `validate_compact_control`, `validate_compact_short_circuit` |
| S07 | Simple and compound bounded WHILE; `validate_compact_control`, `validate_compact_loop_bounds` |
| S08-S09 | Complete source forwarding and state guard; `validate_compact_triggers`, `validate_compact_routing` |
| S10 | Source-less event with state seed; `validate_compact_triggers`, loop and relative-target checks |
| S11 | Quoted punctuation, nested JSON and operator-like strings; `validate_compact_lexing`, `validate_compact_triggers`, `validate_compact_routing` |
| S12 | Shared assertion condition and MESSAGE metadata; `validate_compact_control` and existing execution checks |

| Conformance rows | Observed check owners |
| --- | --- |
| C01 | `validate_compact_specimens`: all twelve specimens, expected Nodes, resolution, two groupings and two styles |
| C02 | `validate_compact_lexing`: strings, escaped quotes/backslashes, operators, commas, nested JSON, target-like literals and ACT tool/prose preservation |
| C03 | `validate_compact_lexing`, `validate_compact_control`, `validate_compact_triggers`: malformed syntax, arity, unsupported forms and physical diagnostics |
| C04 | `validate_compact_control`: nested ELSE association, blank lines, two-space suites, structural tabs, assertion metadata and 80 generated condition trees |
| C05 | `validate_compact_short_circuit`, `validate_compact_loop_bounds`: strict equality, error order, zero/early/exact-limit/exhausted loops, state/emission behaviour |
| C06 | `validate_compact_triggers`, `validate_compact_routing` and existing interface checks: 24 field permutations, input coverage, source/guard/seed rules, exact matching, overlap and ambiguity |
| C07 | `validate_compact_frames`, `validate_compact_relative_targets` and existing execution/resolution checks: frames, promotion, tools, failures, local emissions and supported relative calls |
| C08 | `validate_compact_layout`, specimen variants and repeated generation: 99/100/101 code points, indentation/suffix width, atomic values, recursive expansion and idempotence |
| C09 | Existing agents, outputs, surfaces, rendering, parsing, human-example and authoring checks, plus all owning generators |
| C10 | Existing authoring and optional-validator checks, immutable revision/fingerprint checks, product byte limits, and successful explicit PR-CI bootstrap in run 33943314174 |
| C11 | Both complete candidate commands, clean regeneration, separate self-review and the inclusive task-ID audit |
| C12 | Confirmed branch and PR effects, report/plan publication, final head and final-state checks in the delivery evidence |

## Fresh self-review

A separate self-review pass inspected the final source diff, delimiter parsing, direct-suite association, declaration fields, formatting decisions, formal grammar, scope preservation, generated outputs, validator identity, and the task evidence. This is not an independent human or second-agent approval. Verdict: Approved for the accepted syntax migration, with no unresolved material finding in that scope.

Resolved findings and dispositions:

- The old comparison parser could select an operator phrase inside a quoted operand. The new reader consumes complete JSON operands before the comparison operator. Both left and right quoted operands are covered.
- Fragment parsing could return the first parsed item without proving complete consumption. Condition, step and trigger fragment paths now reject surplus items or trailing text; rejection checks cover these cases.
- An existing compound-WHILE rendering expectation still named the removed block header. It now asserts the shared compact condition and retained bound. An invalid-interface fixture's tool colon was corrected so that it exercises the intended interface rejection, not an unrelated malformed ACT header.
- Full verification initially rejected the stale optional-validator fingerprint, as required. Publishing the immutable package and regenerating the subsequent identity/product commit resolved those failures. The complete commands were rerun successfully rather than suppressing the checks.
- Old-surface search matches remaining in current code are explicitly labelled rejection fixtures, valid literal/prose content, diagnostics, or semantic field names such as `then`. Completed historical plans and legacy snapshots remain evidence, not current syntax authority.

S11 deliberately tests that an object-valued seed survives parsing unchanged. Its illustrative fixture uses the existing `NonEmpty` constraint, whose runtime binding semantics accept text/lists rather than objects. The runtime check preserves the resulting `invalid_process_input` rejection and separately proves successful forwarding of a permitted list-valued payload. Syntax validity is not presented as evidence of schema-valid runtime input, and this change does not broaden schema semantics.

Relative-process checks use supported declared-output promotion followed by an emission in the caller's local document. They do not claim to repair the pre-existing mismatch between externally qualified emission addresses and the runtime emission model's local-target restriction. No unrelated runtime redesign was included.

## Delivery evidence

The implementation and generated products are committed and pushed at `8ef93c13d1a9dc0f181bc0b4200e878f44b541dc`. The package identity is pinned separately as recorded above. This report commit is evidence-only and is not the validator pin.

PR: [#12](https://github.com/chris-buckley/open-agent-knowledge/pull/12), open and non-draft, from `feat/compact-oak-syntax` to `main`.
Final checklist: all 101 stable task IDs are checked. The handoff response discharges P12.06 as specified by the plan; no merge is part of delivery.
PR verification: [run 33943314174](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33943314174) passed the complete product/freshness checks and the actual detached validator bootstrap and cache reuse.

Final evidence closure verifies the PR and prior CI through GitHub before changing the checklist, then runs compilation, generators, both complete entry points, explicit bootstrap, identity checks and clean regeneration against the completed documents. It commits and pushes only after those checks pass, verifies the PR head again, and exports the exact commit plus command logs. The temporary closure workflow removes itself before the final checks and commit. The closure commit is evidence-only relative to the verified product candidate; no package, generated product, dependency or permanent CI file changes during closure.

The closure runner is [run 33943632760](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33943632760). Its artifact records the exact verification subject and final source bundle. Later evidence-only or identical-tree CI-trigger commits do not alter the pinned package. The final remote head is reported through the PR and the user handoff rather than inventing a self-referential hash inside this report.

No merge, branch deletion, release, or force-push was performed.
