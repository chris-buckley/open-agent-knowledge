# Python conventions migration report

Status: Complete; local verification and pull-request CI passed.
Branch: improve/python-code-conventions
Baseline: 21c2dc5b9366068875709e1cefab3a942f51836c
Plan: [plan](plan.md)
Pull request: https://github.com/chris-buckley/open-agent-knowledge/pull/16
Verified candidate: 7a1f1bf9cc5c3cdba453b63a3b322d728e21950e

## Corrected interpretation

The user's canonical source was .agents/rules/coding-standards.md, not the four OAK example-authoring rules. The actual style is compact, fully typed, flat, data-oriented Python with explicit boundaries, deterministic behaviour, semantic vocabulary, and restrained abstraction. It is standard-library-first rather than universally Pydantic-first.

Preserved preferences include the 120-character fallback width, short horizontal signatures, private-name prefixes, rare terse STE comments, meaningful type annotations, supported public compatibility, narrowly justified dependencies, guard clauses, and tests of observable behaviour. Repository conventions and supported APIs continue to take precedence over the general defaults.

## Reassessment of the earlier suggestions

| Earlier suggestion | Corrected treatment |
| --- | --- |
| Name meaningful units instead of every multiline expression | Already supported by sections 3.5, 3.6, and 14.1; relax the mechanical OAK example rule only. |
| Declare repeated identity once | Already covered by sections 3.3 and 14.2; retain the OAK-specific local-target derivation refinement. |
| Permit small binding helpers | Already consistent with section 3.5; clarify OAK authoring without adding a builder. |
| Type callbacks and separate construction, checking, and writing | Already required by sections 3.1, 6.4, 7.1, and 14.1. |
| Expand short signatures vertically | Withdraw the mechanical expansion; preserve section 13.1 and the configured formatter's precedence. |
| Expand every constructor or binding | Withdraw any mechanical reading; preserve one coherent idea per line and meaningful grouping. |
| Prefer keywords for ambiguous neighbouring arguments | Already covered by sections 5.2 and 14.7; preserve existing public signatures. |
| Remove an otherwise meaningless one-element list alias | Apply within OAK composition; do not ban meaningful named collections. |
| Keep exact template whitespace | Add a focused refinement and literal-equivalence example. |
| Capture shared dependency inputs once per operation | Add a focused refinement; exclude global caching and APIs that promise live reads. |
| Identify separately failed contracts | Refine existing actionable-error rules and retain sensitive-data exclusions. |
| Share fixture setup, not the implementation-derived oracle | Add an explicit independent-expectations refinement. |
| Infer obvious locals without weakening meaningful typing | Clarify section 3.1; keep stored state, callbacks, public boundaries, domain identifiers, and otherwise unknown collection types explicit. |
| Replace the Pydantic skill or the compound-growth program | Withdraw the mistaken target interpretation; neither is the source being modularised. |

## Delivered structure

The current source is .agents/rules/coding-standards.oak.md and eight topic documents under .agents/rules/python: naming, layout, types, design, effects, dependencies, documentation, and verification.

Each document is canonical OAK. Rule records live in constants. Teaching snippets are labelled literal constants with a structured example index. Schemas define the change-comparison and complexity-report shapes. The entry process uses explicit cross-document references, so OAK resolution verifies the complete bounded document graph. Generated interpretation text is not authored policy.

The old Markdown monolith is removed rather than retained as a competing source. The .oak.md entry extension is required by OAK's document resolver. Root AGENTS routes Python work to the new entry. Examples AGENTS owns only OAK-specific authoring choices, and build AGENTS owns verification. The Pydantic specialist skill and runtime semantics are unchanged.

## Preservation evidence

The original 1,393-line source contains 18 numbered top-level sections, represented by 63 non-empty rule groups. Migration preserves 380 text items, 68 literal blocks, one table, and all 42 review questions. Five explicit refinements and four additional before-and-after pairs are separate from the original records.

[source mapping](evidence/migration.json) records the baseline commit, source blob, source SHA-256, section destinations, original record digests, and literal digests. Every original record and literal was compared with the parsed destination OAK. Markdown inline markers and unchecked-box markers were removed from prose; literal code retained its content apart from the fence-boundary trailing newline described in the evidence. Source headers and precedence remain explicit entry knowledge. No source requirement was intentionally weakened or deleted.

The mapping is historical evidence, not a second live rule owner. Future changes belong in the OAK documents and their routing. Original section identifiers remain stable catalogue identities; new refinements are separately named.

## Verification

[initial checks](evidence/verification.json) records the first successful local pass. [Final checks](evidence/closeout.json) records the reconciled candidate, latest local command results, corrected decision count, and observed GitHub CI. Document hashes and migration coverage remain unchanged.

The following completed successfully: compilation; python -m build.examples; python build/examples.py; example, grammar, reference, and authoring regeneration; repeat authoring generation; generated-artifact diff; and git diff --check. Generated example and skill deliveries and runtime outputs remained unchanged.

The registered coding-standard check validates both groupings, complete bounded resolution, one concern and section owner, example references and section ownership, and populated teaching shapes. Twelve rejection cases cover missing or extra documents, noncanonical bytes, escaping paths, missing external entries, missing or duplicate sections, malformed rules, empty snippets, wrong example ownership, numeric section coercion, and symbolic links. The literal-whitespace pair is checked against an independent expected string.

The new checker has annotated callable boundaries, no lines beyond 120 characters, and a maximum observed custom AST decision count of ten. The recorded counting method includes comprehensions and boolean operators; this is not a Radon result. No existing runtime function was refactored, so no runtime before/after complexity claim is made.

Earlier synchronous execution attempts timed out and were not counted as passes. Bounded subprocess execution subsequently completed the exact commands above. Ruff, mypy, Pyright, and Radon were not installed or added and were not claimed as run. The 68 preserved snippets are illustrative and may require missing context or a newer Python baseline; they were not all executed. A valid report schema is not evidence that an example ran.

## Review and scope

Main advanced to e7da4c557c1443eb5d99867c42ea0d795ace148d during the work. The branch incorporates those changes, retains the typed-statement naming rule, and moves this plan from the concurrently occupied 0009 number to 0010. Root routing now points to the OAK entry rather than the removed Markdown path.

All task-created snapshot, application, and transport files are removed from the final tree. The pre-existing statement-closeout workflow from main is unchanged. An intermediate CI run rejected an extra trailing newline introduced while merging examples/AGENTS.md. The canonical bytes were restored, the local full suite passed again, and GitHub Verify OAK run 33968786024 passed on candidate 7a1f1bf, including approved detached bootstrap and cache reuse.

The final closeout changes only this plan and its evidence. No general formatter, new dependency, blanket API migration, alternate OAK authoring language, or repository-wide cosmetic rewrite is included. Final review verdict: ready for user review. No independent human approval is claimed. This task does not merge the pull request or modify main.
