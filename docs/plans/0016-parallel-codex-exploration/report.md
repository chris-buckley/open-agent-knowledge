# Plan 0016 implementation and verification handoff

Status: Implementation complete with one controller review correction. Corrected-tree verification, Git publication and PR completion await the controller. No merge is authorized.
Plan: [Deliver OAK exploration agents as native Codex artifacts](plan.md).
Base: `88340b4bde9d58295e881884a80a0a99c247e13a` on `docs/plan-parallel-codex-exploration`.
Governing revision: `9956e6998869fcfbd84067eec0d6303273a54174`.
Candidate: Uncommitted complete source overlay, preserving the original history.
Recovery task: `82d0f13f-f86a-46bb-9f24-74f5d94bd5dd`.
Evidence: [artifact-verification.json](evidence/artifact-verification.json). Full source manifests, command receipts, logs and the controller review are included in the delivery archive.

## Result

The delivered agent is `generated/oak.agents/parallel_exploration/codex/.codex/agents/oak-explorer.toml`. It contains the exact canonical explorer document in `developer_instructions`, useful native metadata and the documented read-only, no-approval, disabled-web and leaf-agent defaults. It needs no external instruction file, launcher, tool registry or OAK installation for its instruction content. Manual placement is explained by the shared adaptor; this change performs no installation.

The complete five-file bundle also contains `coordinator.oak.md`, `explorer.oak.md`, `sample.oak.md` and `adaptors/codex/adaptor.oak.md`. Worker and coordinator remain separate operational scopes. The portable coordinator uses two exact `ACT.tool` actions in `Par`, immediate `Join`, post-join synthesis and a typed emission. Its repository fixtures invoke the actual worker OAK, demonstrate synchronized overlap, and reject blocked, failed, malformed or wrong-revision results before successful synthesis. The exact tool names belong to those fixtures, not to native Codex.

Both authoring forms contain the same orchestration and Codex knowledge with explicit action bindings. Native parent instructions ask for independent explorer instances and evidence reconciliation; they do not claim native prompting mechanically executes the OAK Python executor. Native tool availability, inherited permissions, installation, model behavior and live concurrency remain unverified and outside this artifact-only scope.

## Recovery and integration correction

The externally preserved final checkpoint 02 matched its 4,029,557-byte length and SHA-256 `884494e3345ab2eba9aabf4c200562072c5041d2b4cb85396e5af43225368d44`. A fresh clone of its bundled exact branch plus the complete overlay reproduced all 615 files and fingerprint `1b6f2771f56b4bfdcf00f21ce916fd0c3318dfad5049346baec36a55e292343f`. The controller review archive and all ten files in its internal manifest also matched. No superseded 613-file tree, loose recovery file or hybrid baseline was reused. Original governing files remain pinned inputs; changed scoped AGENTS files are task outputs. D01.01's already committed plan amendment was not repeated.

The controller's first full check failed because `build/checks/shapes.py` still imported `populated_examples` after D03 removed duplicate prompt fields. This was a real integration defect. The corrected check reads the complete literal shape-gallery teaching document from the assembled authoring knowledge and compares its four full schemas and populated instances with the independently authored `SHAPES` and `EXPECTED_INSTANCES`. Existing binding, literal-substitution, table, outline, Python-file, execution and rejection checks remain active. No compatibility shim or removed check conceals the failure.

The earlier D03 review is preserved as milestone history, not proof of a full repository pass. Its missing integration coverage is superseded by the observed full-check results below. Intermediate failed checks during this continuation remain in the external receipts: canonical WHERE descriptions initially contained invalid extra semicolons, and one negative fixture initially expected the wrong earlier rejection diagnostic. Both were corrected at their actual owner and rerun; no language rule or rejection was weakened.

## SMEAC Directory Changes

The actual `examples/schemas/smeac_plan.py` template and canonical sibling now contain Directory Changes after End state and before State Comparisons. All five string fields have nonempty constraints and descriptions: baseline, current tree, planned tree, ownership and verification. The fixed legend includes addition, modification, move with source path, removal, unchanged context and conditional checking.

`build/checks/plans.py` derives headings, fields, order and legend from that template. It reuses the existing field extraction and fenced-Markdown machinery rather than adding a tree or diff language. Independent populated fixtures in `build/checks/plan_fixtures.py` exercise additions, moves, visible removals, no-file-change and unknown-baseline cases. Rejections cover missing, duplicate, empty, unfilled, reordered and unclosed content, misplaced subsections, missing move sources, mixed no-change text and ellipses hiding leaves. Both OAK groupings and complete bound schema instances are checked.

The docs-owned policy applies from plan 0016 and to explicitly reopened older plans. Existing records are not rewritten. A reopened historical-format record receives the new directory subsection check without an unrelated format migration; its existing navigation and storage checks remain active. The current plan's annotated tree now names every changed leaf, including the shape consumer and specimen owner. The final changes manifest supplies exact paths and hashes, while the diagram remains the human-readable ownership view, not proof that a check ran.

## Content and size preservation

| Contract | Observed result |
| --- | --- |
| Standalone authoring agent | 63,844 bytes, limit 64,000 |
| Skill entry | 8,373 bytes, limit 10,000 |
| Literal teaching | All eight original documents byte-identical, including four complete shape schemas and populated instances |
| Package authoring rules | All 41 retained verbatim with one guide owner each |
| Grammar and template | Original bytes preserved |
| Optional validator | Skill version 3.2.0 only; implementation, immutable runtime revision, fingerprints and consent logic retained |
| Agent bundle | Exactly five source-derived text/TOML files; no runtime scripts |
| Protected boundaries | Root AGENTS, OAK core, dependency declarations, existing workflows, APS and older plan records unchanged |

D03 removed duplicate shape/lifetime copies, not the original teaching corpus. The schema action consumes the entire retained teaching mapping. Build-only `gN-` prefixes shorten generated support namespaces while preserving descriptive suffixes, identities, typed rewriting and collision checks. Detailed D03 meaning comparisons remain in [d03-preservation.json](evidence/d03-preservation.json); this continuation independently compared the current artifacts with the immutable baseline again.

## Executed verification

The controller restored the final 618-file delivery and verified its supplied checksum and complete manifest. Both full entry points passed in Python 3.11.9 with pydantic 2.13.4, pydantic-settings 2.15.0, pydantic-extra-types 2.11.1 and PyYAML 6.0.3; the source remained unchanged.

The controller then found one additional E17 gap: an unfilled `<PLAN_TITLE>` inside a directory fence was accepted because the checker searched only `DIRECTORY_` placeholders there. The checker now recognizes every placeholder from the actual SMEAC schema as well as unknown `DIRECTORY_` placeholders. Independent current/planned-view regression cases and the owning docs policy cover the correction. Targeted plan and scoped-knowledge checks passed; the corrected full-tree verification is recorded separately before publication. No other implementation behavior was changed by the controller.

All commands below returned exit code 0 with unchanged source manifests. These are real cloud executions, not inferred passes or controller results for the final candidate.

| Check | Command or scope | Seconds |
| --- | --- | ---: |
| Reconciled generation | Compilation, catalogue, grammar, definitions, native bundle and authoring generation, plan checks, repeated generation | 2.042 |
| Complete module entry point | `python -m build.examples` | 52.157 |
| Complete direct entry point | `python build/examples.py` | 52.653 |
| Content and boundary audit | Independent immutable-baseline comparisons, exact native bytes, protected paths, sizes and inventories | 2.107 |

Both complete entry points execute all 37 registered checks, including shapes, agent artifacts/parallel failures, authoring content and execution parity, the optional validator, prospective plans, scoped knowledge and lifecycle, detached examples, cold generation/repair, freshness and architecture. The full candidate checks above cover fingerprint `935212ab13b7b374fd3b730a084c93882890c9fb76aaf2e5b8a4e9411886e255`. Final plan/report/evidence edits change only Plan 0016 records; final post-report checks and their exact whole-tree manifests are supplied externally in the delivery archive. This report does not assert an exit code from a future run.

The implementation fingerprint, excluding only this plan/report/evidence directory to avoid self-reference, is `d41096a8eeca907d2fff1e557a35e3a3af217e6a93d7496211f7033298ea805b`. The archive contains the complete final file manifest including these records, plus an explicit deletion list. No product file or generated output is omitted from the implementation comparison.

Cloud environment: Python 3.13.5, pydantic 2.13.4, pydantic-settings 2.14.1, pydantic-extra-types 2.11.1 and PyYAML 6.0.3. The settings package is below the declared minimum of 2.15. No package was installed or requirement lowered. The controller's documented environment satisfies that minimum and must verify this final candidate there before completing D05.02. The old controller failure is not reused as a result for this corrected candidate.

## Separate final technical review

Review was performed directly by the implementing assistant after implementation, against the original agent/parallelism intent, artifact-only amendment, plan, acceptance comparisons and actual files. The Codex controller separately reviewed the delivered source and corrected the fenced-placeholder gap described above. No subagent or external reviewer is claimed.

The review confirmed separate OAK scopes, one native worker source, explicit exact-tool/native usage distinctions, complete shared guidance routing, retained knowledge and validator safeguards, schema-owned prospective checks, source-owned generation and absence of extra host machinery. It corrected the stale shape consumer and the incomplete path diagram. Shared field/fence helpers reduce duplicated checker mechanics without removing an existing validation class. No actionable implementation defect remains from this review; declared-dependency and publication evidence remain outstanding.

A local AST decision-count report records the touched checker refactoring, not a claimed external linter result. `validate_plan_directory` decreased from 18 to 9 and `_comparison_authority` from 10 to 2 after extraction of meaningful boundary checks. New directory helpers are at most 10 by the documented method. The existing `validate_shapes` verification coordinator decreased from 27 to 23, with `_prompt_gallery` at 8. This is a scoped maintenance assessment, not a universal complexity certification or a reason to skip behavioral checks.

## Acceptance and task state

| Comparison | Evidence and disposition |
| --- | --- |
| E13 | Exact native metadata, TOML decoding, full local worker closure and rejection checks pass |
| E14 | Named flat actions, immediate JOIN, real synchronized fixture overlap and failure isolation pass |
| E15 | Eight literal documents, 41 rules, template, grammar, validator and shared routing preserved within limits |
| E16 | Five-file closure, source-derived manifests, cold generation/repair and unsafe-path rejections pass |
| E17 | Actual five-field SMEAC schema, both groupings, independent positive/negative and prospective/reopened checks pass |
| E18 | Exact sample request and evidence/coverage/gaps/blocked semantics retained; no live evidence fabricated |
| E19 | Owning policy updated; root/core/dependencies/workflows/APS/historical records unchanged |
| E20 | Implementation/review/evidence prepared; final declared-dependency verification and actual PR publication remain pending |

D01-D04, D05.01, D05.03, D05.04 and D06.01 are evidenced: 19 of 22 tasks. D05.02 remains open only for the controller's declared-dependency verification of the final candidate; its local commands have passed. D06.02 and D06.03 remain open until actual committed remote bytes and the non-draft PR URL/check results are reported. Withdrawn host tasks were never marked passed.

## Controller handoff

Restore the delivered original base bundle and complete overlay, verifying its full manifest before execution. Run the two full repository entry points and generation freshness in the declared environment, then review and commit the complete change without amending, rebasing, squashing or force-pushing original history. Verify remote path/byte identities and create the non-draft PR targeting main. Supply the actual URL and check receipts before closing publication tasks. Record subsequent status corrections as new commits and recheck them. No merge, native installation, desktop operation or live Codex check is requested.
