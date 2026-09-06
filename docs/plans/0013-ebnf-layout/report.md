# OAK EBNF layout report

Status: Implemented and verified locally; independent review and remote delivery are pending.
Plan: [0013 EBNF layout](plan.md)
Branch: docs/plan-ebnf-layout
Destination: main
Merge authorisation: Not granted; leave main unchanged.

## Outcome

The generated reference now has the six accepted component-to-document sections, canonical part subsections, aligned binding groups, expanded trigger and statement alternatives, and nearby source-owned notes. Every baseline production occurrence remains present with identical ordered tokens and literal content. The four grammar deliveries come from one generator.

The implementation does not change any byte under oak, any surface descriptor, parser, model, executor, dependency declaration, example, validator helper or skill metadata. The pre-existing duplicate constant_target pair and opaque special sequences remain deliberately unchanged.

## Revisions and evidence

Planning baseline: `7e002d5e8a3632f9f48026c22a5ad0bbec68e77d`.
Product baseline: `bf0975dd7959320fd6727cee926370eca1808e07`.
Local checkout base: `cd648d224510a902acac46c85753ec6e97854195`.
Verified working-tree product fingerprint: `cd1dd883722f554c3dc6edf6314a84f219a6b45f7336e89725e411c203397688`.
The fingerprint includes source and delivered product bytes, excluding this plan's records and the temporary workbench. Remote commit and CI identities are recorded at delivery; this report does not claim a future CI result.

The initial DNS failure was bypassed with an Actions-generated Git bundle, not a manually reconstructed repository. The baseline artifact checksum was verified before cloning its real history. [Baseline run 34020468020](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/34020468020), job 101451979662, passed both complete entry points with the declared dependencies.

Observed records: [baseline](evidence/baseline.json), [baseline log](evidence/baseline-ci.log), [claim map](evidence/claims.json), [comparison](evidence/comparison.json), [verification](evidence/verification.json), [regeneration](evidence/regeneration.json), and [complexity](evidence/complexity.json).
Reproduce the comparison with `python docs/plans/0013-ebnf-layout/evidence/compare.py` from a checkout containing the baseline history.

## Required comparisons

| Criterion | Observed result |
| --- | --- |
| E01 | The six named sections and seven canonical subsections pass order checks for default, XML-only, Markdown-only and reversed groupings. All 141 source-qualified occurrences have recorded placement. |
| E02 | The five value and binding productions match the fixed alignment specimen and baseline token sequences. |
| E03 | Both trigger productions match the fixed multiline specimen. Required, optional, authored-order, canonical-order, event, guard and seed restrictions remain present. |
| E04 | The complete ordered statement alternative list matches the fixed specimen. Statement aliases and descriptions remain in Processes. |
| E05 | Descriptive bodies, escaped question marks, quoted terminals, multiline indentation and the six documented opaque width exceptions are preserved. All 45 surface projections are covered. |
| E06 | All 141 default and 124 single-grouping production occurrences match the frozen baseline. Removed or reordered alternatives, changed names or literals, reindented bodies, lost or added duplicates, missing or unassigned sources and misplaced surfaces are rejected. |
| E07 | The two grammar files are byte-identical; both embedded values match them. Replacing only the old grammar value reproduces both new embeddings exactly. All unrelated deliveries remain unchanged, budgets pass, and repeat generation changes no bytes. |

## Validator-pin refinement

The first candidate shortened commentary in oak/surface/syntax.py. The full suite correctly rejected it with `RuntimeError: validator source pin is stale`; [the failed run](evidence/failed-pin-check.json) is retained rather than hidden.

The delivered candidate restores the complete pinned package. Build metadata places original convention strings verbatim and does not invent another prose registry. Seven redundant claims are carried by their existing productions rather than repeated as comments. The claim map covers all 19 package conventions and six build-owned baseline claims. This is a documented refinement of the proposed commentary approach, not a validator-pin change or weakening of verification.

Validator revision: `dc71e5ec140e1b94351ceabab3a55b9ab8aa9dce`.
Validator source fingerprint: `4adedc8035e384d57c2ca7762faadd3b0e5f425f5ece1bf0a95e0be00f7c75f3`.

## Verification

Both `python -m build.examples` and `python build/examples.py` exited zero on the final local implementation. Together they exercise the existing checks plus the new EBNF check: 35 named verification groups, including parser, renderer, round-trip, model contracts, execution, JSON-LD, detached scenarios, skill-agent parity and freshness. Compilation, focused checks, plan and scoped-knowledge checks, independent baseline comparisons, repeated generation and `git diff --check` also pass.

Local Python is 3.13.5. The preinstalled pydantic-settings 2.14.1 is below the repository's declared minimum; this is disclosed, not silently treated as a conforming dependency installation. Baseline Actions passed with declared dependencies. The candidate must also pass declared-dependency Actions before final handoff.

No formatter, linter or static type-checker is configured by this repository; no such run is claimed. The recorded AST complexity method counts decisions, comprehensions and boolean operators, with nested functions measured separately. The grammar entry point changes from 8 to 1; source assembly is 9, layout assembly is 8, and the maximum new function count is 10. This is an explicit measurement, not a claim that a particular third-party complexity tool ran.

## Sizes

| Delivery | Baseline bytes | Candidate bytes | Limit |
| --- | ---: | ---: | ---: |
| Grammar file, each copy | 13,284 | 13,307 | Not separately capped |
| Standalone authoring agent | 63,974 | 63,997 | 64,000 |
| Skill entry | 8,022 | 8,022 | 10,000 |

The standalone has three bytes of remaining headroom. Its guard is unchanged and executable. No examples, literal bodies or unrelated guidance were removed to meet the budget, and no separately compact embedded grammar was introduced.

## Changed paths

Presentation sources: build/ebnf.py and build/_ebnf_layout.py.
Verification: build/checks/ebnf.py, build/checks/ebnf_fixtures.py and build/checks/__init__.py.
Durable operating knowledge: build/AGENTS.md.
Generated deliveries: outputs/oak.ebnf, skills/oak-authoring/references/oak.ebnf, skills/oak-authoring/references/00-structure.oak.md and outputs/oak-authoring.oak.md.
History: this plan, report and supporting evidence.
Temporary branch-only transport workflows and payloads are removed before final delivery; their original commits remain in history. The ordinary verification workflow is unchanged.

## Review and delivery

Implementing-agent review inspected the complete grammar, source boundaries, literal protection, note coverage, exact specimens, all grouping modes, final diff and budgets. The stale-pin finding was corrected and verification rerun. No unresolved in-scope finding remains from that review.

Independent review: Pending. No independent approval or Approved verdict is claimed yet.
Pull request: Pending publication of the verified tree.
The remaining review and delivery tasks stay unchecked until their evidence exists.
