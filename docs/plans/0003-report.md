# Scoped OAK AGENTS migration report

```yaml
status: complete
verdict: Approved
repository: chris-buckley/open-agent-knowledge
branch: docs/scoped-oak-agents
baseline_commit: 9791ba43f881957325f18cd1685b2f485e4c9867
plan: docs/plans/0003-plan.md
```

## Outcome

Current architecture and repository operating knowledge now live in one scoped graph of canonical OAK `AGENTS.md` documents.

The root document owns global rules and routing. Each nested document owns one directory concern. The hierarchy is host scoping and does not imply OAK imports.

The parallel `docs/architecture` manuals and `docs/guides/authoring.md` are removed.

## Scoped graph

| Path | Owned concern | Lines |
|---|---|---:|
| `AGENTS.md` | Product intent, global work rules, and routing | 64 |
| `oak/AGENTS.md` | Package and representation architecture | 41 |
| `oak/node/AGENTS.md` | Document, node, parts, values, schemas, and local validation | 36 |
| `oak/resolve/AGENTS.md` | Target paths and document graph resolution | 23 |
| `oak/execute/AGENTS.md` | Runtime execution and transactions | 44 |
| `build/AGENTS.md` | Generation, checks, freshness, and authoring prompt | 24 |
| `examples/AGENTS.md` | Practical authoring and executable examples | 25 |
| `outputs/AGENTS.md` | Generated-only output rules | 10 |
| `docs/AGENTS.md` | Plans and reports as history | 11 |

Every document uses only the OAK instructions part. Every document parses and renders back to identical canonical XML-grouped OAK. No document approaches the 500-line maximum.

## Ownership and duplication

Each nested document starts with one sole-ownership instruction.

The root names every nested document exactly once through visible tree router lines. Parent documents route to child owners instead of restating child architecture.

The build normalizes authored instruction bodies and rejects duplicates across the complete graph. It separately rejects a child instruction repeated from an ancestor. Generated interpretation instructions are not included in this authored-content comparison.

A manual semantic overlap review found no competing architecture owner. The only close pair is the global 500-line requirement and the build check that enforces it. That is an intentional rule and enforcement relationship, not duplicate ownership.

## Removed ownership

The migration removes:

- `docs/architecture/overview.md`;
- `docs/architecture/document.md`;
- `docs/architecture/graph.md`;
- `docs/architecture/validation.md`;
- `docs/architecture/execution.md`;
- `docs/architecture/representation.md`;
- `docs/architecture/repository.md`;
- `docs/guides/authoring.md`;
- `build/checks/documentation.py`.

Completed plans retain historical references that were correct when those plans were written.

## Verification

The completed source tree passed:

- `python -m compileall -q oak build examples`;
- `python build/authoring.py`;
- `python build/docs.py`;
- `python build/ebnf.py`;
- `python -m build.examples`;
- `python build/examples.py`;
- repeated generation with no changed outputs;
- canonical parse and render equality for all nine scoped documents;
- exact AGENTS path discovery and root router coverage;
- the 500-line limit;
- sole-ownership first instructions;
- normalized duplicate and ancestor-repeat rejection;
- absence of current architecture manuals, guides, the removed PRD, README indexes, and the obsolete documentation checker;
- generated output path freshness with `outputs/AGENTS.md` excluded from generated artifacts;
- `git diff --check`;
- final diff and obsolete-path inspection.

GitHub Actions run `33847808289` independently repeated compilation, all product generators, both complete verification entry points, and the clean generated-worktree check. Every stage passed.

The isolated validation branch and all temporary workflow files were removed before the pull request branch was finalised.

## Verdict

No unresolved item remains.

Verdict: Approved
