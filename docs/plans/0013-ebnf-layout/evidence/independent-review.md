# Independent audit of the EBNF layout candidate

Reviewed candidate: `d44ba3046eee63e384e8ba2ae7224c640c47f752`
Reviewed tree: `aae26bb59ff404c0ea471685577d8abb2d2c4bd5`
Product baseline: `bf0975dd7959320fd6727cee926370eca1808e07`
Planning baseline: `7e002d5e8a3632f9f48026c22a5ad0bbec68e77d`

## Scope inspected

Files and evidence reviewed:
- `build/ebnf.py`
- `build/_ebnf_layout.py`
- `build/checks/ebnf.py`
- `build/checks/ebnf_fixtures.py`
- `build/checks/__init__.py`
- `build/AGENTS.md`
- `outputs/oak.ebnf`
- `skills/oak-authoring/references/oak.ebnf`
- `skills/oak-authoring/references/00-structure.oak.md`
- `outputs/oak-authoring.oak.md`
- `docs/plans/0013-ebnf-layout/plan.md`
- `docs/plans/0013-ebnf-layout/report.md`
- `docs/plans/0013-ebnf-layout/evidence/*.json`
- `docs/plans/0013-ebnf-layout/evidence/*.py`
- `docs/plans/0013-ebnf-layout/evidence/baseline-ci.log`

Criteria audited:
1. Every grammar source occurrence and all 45 surfaces remain accounted for, including both existing `constant_target` definitions and ordered alternatives.
2. Formatter and independent lexer preserve quoted strings, escaped-question-mark bodies, regular-expression fragments, and multiline special-sequence bytes.
3. E01-E07 specimens, source ownership, grouping and reverse-grouping selection, commentary claims, and the presentation-only boundary are satisfied.
4. Existing semantic, detached scenario, skill-agent, validator-pin, and unrelated generated-knowledge checks were not weakened.
5. Four deliveries agree, non-grammar embedding bytes remain unchanged, and the 10,000-byte skill-entry and 64,000-byte standalone budgets remain intact.
6. The new source and tests are scoped and reproducible.

## Commands run

The following commands were run in an isolated dependency environment matching the repository's declared requirements:

- `python -m compileall build oak` -> exit 0
- `. /tmp/oak-venv/bin/activate && python -m build.examples` -> exit 0
- `. /tmp/oak-venv/bin/activate && python build/examples.py` -> exit 0
- `. /tmp/oak-venv/bin/activate && python docs/plans/0013-ebnf-layout/evidence/compare.py` -> exit 0

Actual output from the compare script:

- `source_occurrences`: 141
- `surface_occurrences`: 45
- `source_content_preserved`: true
- `non_grammar_embedding_bytes_preserved`: true
- `unrelated_paths_unchanged`: true
- `validator_revision`: `dc71e5ec140e1b94351ceabab3a55b9ab8aa9dce`
- `validator_source_sha256`: `4adedc8035e384d57c2ca7762faadd3b0e5f425f5ece1bf0a95e0be00f7c75f3`

## Concrete findings

- None. I did not find an unresolved in-scope issue in the reviewed candidate.
- The source-qualified inventory remains stable: the baseline duplicate `constant_target` definitions remain present as two distinct occurrences rather than being merged, rewritten, or dropped.
- The independent lexer in `build/checks/ebnf.py` rejects any mutation that changes the ordered production content, alternate ordering, duplicate multiplicity, quoted literals, escaped question marks, or special-sequence bodies.
- The formatter in `build/_ebnf_layout.py` only reflows outer grammar boundaries and deliberately preserves quoted terminals and opaque special sequences. That is the essential guardrail for the literal bytes called out by the P05.04 review criteria.
- The candidate keeps the six section order and canonical part order while preserving the original grammar semantics and all four generated deliveries.
- The standalone authoring agent remains within budget with 3 bytes of margin remaining, and the skill entry remains under the 10,000-byte limit.

## Limitations

- This is a preservation and formatting review, not a proof of the full OAK grammar outside the repository's own checks and preserved baseline comparisons.
- The repository's detached example runtime rejects imports from a venv located under the repository root, so the verification was performed in an external virtual environment outside the worktree for the `-I` detached checks.
- The review is intentionally pinned to the exact implementation tree and does not infer approval from a workflow success flag or a PR status alone.

## Verdict

Approved.

The reviewed candidate satisfies the audit criteria for this review with no unresolved in-scope finding. It remains a layout-only change and does not change OAK semantics, package bytes, validator identity, or unrelated generated knowledge.
