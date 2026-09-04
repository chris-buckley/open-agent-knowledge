# Structured-first scoped OAK AGENTS migration report

```yaml
status: complete
verdict: Approved
repository: chris-buckley/open-agent-knowledge
branch: docs/scoped-oak-agents
baseline_commit: 9791ba43f881957325f18cd1685b2f485e4c9867
implementation_commit: 7369a368abb009c9c22547a7d84054d9347defeb
implementation_tree: 0c84790367ba3de08df0cda3043c379cf5d923fd
plan: docs/plans/0003-plan.md
```

## Outcome

Current architecture and repository operating knowledge now live in nine scoped canonical OAK `AGENTS.md` documents.

The root document owns product intent, repository-wide knowledge, task contracts, routing, and the repository work process. Each nested document owns one directory concern. Host AGENTS hierarchy supplies scope. It does not create implicit OAK imports.

The parallel `docs/architecture` manuals and `docs/guides/authoring.md` are removed.

## Structured-first decision

The first implementation used authored instructions as the only populated part. The user rejected that design and established the correct priority: instructions are the last part to add.

The completed graph applies this order:

```text
schemas
constants
state
interfaces
triggers
processes
instructions
```

All nine current documents contain zero authored instructions.

The visible `<instructions>` section in each render contains only generated interpretation lines selected by the OAK renderer from the structured features present in that document. Parsing removes those exact generated lines, so the canonical node has an empty authored instructions part.

The root document uses constants, schemas, triggers, processes, and interfaces. It omits state because no persistent AGENTS runtime value is justified. Nested documents use constants and processes for their owned knowledge. A future authored instruction is valid only when the same document includes one non-empty `constant.instruction-justification`.

## Scoped graph

| Path | Owned concern | Lines |
|---|---|---:|
| `AGENTS.md` | Product intent, global knowledge, task contracts, and routing | 139 |
| `oak/AGENTS.md` | Package and representation architecture | 54 |
| `oak/node/AGENTS.md` | Document, node, parts, values, schemas, and local validation | 59 |
| `oak/resolve/AGENTS.md` | Target paths and document graph resolution | 41 |
| `oak/execute/AGENTS.md` | Runtime execution and transactions | 54 |
| `build/AGENTS.md` | Generation, checks, freshness, and authoring prompt | 42 |
| `examples/AGENTS.md` | Practical authoring and executable examples | 39 |
| `outputs/AGENTS.md` | Generated-only output rules | 26 |
| `docs/AGENTS.md` | Plans and reports as history | 25 |

Every file is below the enforced 500-line maximum.

## Duplication control

`build/checks/agents.py` now:

- discovers the exact nine-file graph;
- requires canonical XML-grouped OAK parse and render equality;
- requires structured content in every document;
- requires one unique first `owned-concern` constant;
- requires at least one operating process;
- verifies the root router, task schemas, triggers, processes, and interfaces;
- verifies the structured part priority and the 500-line limit against root constants;
- rejects authored instructions without explicit justification;
- rejects duplicate normalized authored claims, including repeated structured list or row claims;
- rejects a child claim repeated from an ancestor;
- excludes generated interpretation lines from authored duplication checks;
- rejects current PRD, architecture-manual, guide, README-index, and obsolete-check paths.

Exact identifiers can repeat where they are references or table keys. Complete authored claims cannot repeat.

## Verification

Local verification passed:

```text
python -m compileall -q oak build examples
python build/authoring.py
python build/docs.py
python build/ebnf.py
python -m build.examples
python build/examples.py
git diff --check
```

Repeated generation changed no generated output or example snapshot.

GitHub Actions run `33870244092` independently checked the first structured implementation. It passed source compilation, every generator, both complete verification entry points, generated-product freshness, and `git diff --check`, then committed the verified structured graph as `b19791fb8fca3c386285445c467143ffb88fd65a`.

Run `33870083573` reached the final freshness command after all repository checks passed but compared the intentionally changed `examples/AGENTS.md` and `outputs/AGENTS.md` against their old forms. The harness was corrected to compare generated artifacts only.

The duplicate-claim check was then strengthened to retain repeated claims within one file and to check structured list and row claims. A manual blob transfer changed three Python token sequences. Run `33871413691` exposed that transport error during compilation. No product or design check failed. The repair workflow required the corrected checker to equal the locally verified Git blob `6388643a04b8307785763109c167eae04f558eda` before it could continue.

Final GitHub Actions run `33871631284` passed source compilation, every generator, both complete verification entry points, generated-product freshness, and `git diff --check`. It committed the exact verified result as `7369a368abb009c9c22547a7d84054d9347defeb` with tree `0c84790367ba3de08df0cda3043c379cf5d923fd`.

Temporary support existed only on `automation/structured-agents-revision` and `automation/structured-agents-final-verification`. Cleanup runs `33870548651` and `33871764395` deleted those branches. No temporary workflow or payload is present in the pull request tree.

The final remote implementation tree `0c84790367ba3de08df0cda3043c379cf5d923fd` equals the locally verified implementation tree.

## Verdict

No unresolved item remains.

Verdict: Approved
