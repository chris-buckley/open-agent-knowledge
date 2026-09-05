# OAK architecture documentation migration report

```yaml
status: complete
verdict: Approved
repository: chris-buckley/open-agent-knowledge
branch: docs/architecture-manual
baseline_commit: 9a2c9598fbb64ef4de5b630910f015b2344728b6
plan: docs/plans/0002-architecture-documentation/plan.md
```

## Outcome

The single product requirements document is replaced by a routed architecture manual and one practical authoring guide.

`AGENTS.md` now requires the architecture overview before implementation files and routes each task to every matching document.

It is the only documentation index. No repository or docs README index is used.

Exact model fields, syntax, validation codes, parsing, rendering, resolution, and runtime behaviour remain owned by the package and generated reference.

## Documentation tree

```text
docs/
├── architecture/
│   ├── overview.md
│   ├── document.md
│   ├── graph.md
│   ├── validation.md
│   ├── execution.md
│   ├── representation.md
│   └── repository.md
├── guides/
│   └── authoring.md
└── plans/
    ├── 0000-plan.md
    ├── 0000-report.md
    ├── 0001-plan.md
    ├── 0001-report.md
    ├── 0002-plan.md
    └── 0002-report.md
```

## Authority

| Concern | Owner |
|---|---|
| Repository work rules and reading routes | `AGENTS.md` |
| Current explanatory architecture | `docs/architecture` |
| Practical authoring method | `docs/guides/authoring.md` |
| Exact executable contracts | `oak` |
| Generated grammar and reference | `outputs` |
| Change history | `docs/plans` |

`docs/PRD.md` is deleted.

Historical plans remain unchanged and can retain references to the authority that existed when they were written.

## Authoring prompt

The generated authoring prompt now contains:

- one compact ordered guidance registry;
- one architecture capsule;
- the generated XML grammar;
- one complete example that exercises all seven parts;
- one output schema;
- one write process;
- one emit interface.

The prompt no longer contains the complete validation rule catalog, one schema for every Python model, or the extra orchestrator example.

The prompt changed from 37,886 bytes to 15,719 bytes, a reduction of 22,167 bytes or about 58.5 percent.

The build enforces an 18,000 byte maximum.

## Verification

GitHub Actions run `33839432410` validated commit `86a797e9a7b2723c341296868d536d8429f04162` and committed the exact generated products as `b6498041cdf6e64ea7ab7576130d1484fbaa4121`.

The final branch passed:

- `python -m compileall -q oak build examples`;
- every committed Python example and sibling OAK snapshot check;
- `python build/authoring.py`;
- `python build/docs.py`;
- `python build/ebnf.py`;
- `python -m build.examples`;
- `python build/examples.py`;
- canonical parse and render of the authoring prompt;
- canonical parse and render of the authoring guide example;
- generated output content and path freshness;
- documentation path, AGENTS router, and local link freshness;
- absence of repository and docs README indexes;
- exact absence of current `docs/PRD.md`, `read-prd`, and the old product-requirements instruction outside historical plans;
- documentation checks for em dashes and asterisk emphasis;
- repeated generation without output changes;
- `git diff --check`.

The final diff was inspected for accidental changes, duplicate ownership, stale output, obsolete paths, and temporary support files.

GitHub Actions run `33840439650` validated the AGENTS-only router correction and the full build.

The temporary workspace workflow is removed.

## Verdict

No unresolved item remains.

Verdict: Approved
