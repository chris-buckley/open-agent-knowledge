# Self-contained examples: implementation report

Plan: [SMEAC plan](plan.md)
Status: Complete; delivered for review in PR #13. Not merged.
Branch: `plan/self-contained-examples`
Product baseline: `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a`
Source export: `c396b6e771efd7236b6a0f47edfef65ca731d545`
Tested product SHA256: `3476d694910ea0dc0f7fa855105ba5d102351f2aaafbf342f01317c42d167f4c`

## Outcome

Eight self-contained OAK scenario directories now replace the flat agent collection and supply one source-derived catalogue. The shared skill teaching core progresses through fixed facts, shaped information, a typed stateless pipeline and two-arrival persistent state. Collaborating operational documents remain separate. The OAK grammar, models, runtime semantics, dependencies and validator identity remain unchanged.

## Source and delivery map

| Original Python source | Scenario Python source |
| --- | --- |
| `examples/agents/compound_growth.py` | `examples/compound_growth/example.py` |
| `examples/agents/delegation.py` | `examples/delegation/example.py` |
| `examples/agents/task_reviewer.py` | `examples/delegation/task_reviewer.py` |
| `examples/agents/implementer.py` | `examples/implementer/example.py` |
| `examples/agents/interpreter_context.py` | `examples/interpreter_context/example.py` |
| `examples/agents/shape_writer.py` | `examples/shape_writer/example.py` |
| `examples/agents/successor.py` | `examples/successor/example.py` |
| `examples/agents/amendment_reviewer.py` | `examples/successor/amendment_reviewer.py` |
| `examples/agents/successor_verifier.py` | `examples/successor/successor_verifier.py` |

Every source above has the matching relocated `.oak.md` sibling listed in [baseline evidence](evidence/baseline.json). `examples/agents/bindings.py` moves to `examples/bindings.py`; scenario copies are generated, not independently maintained. The obsolete agents package marker is deleted.

The fixed-knowledge definition moves from the authoring generator to `examples/fixed_knowledge/example.py`. `examples/shape_gallery/example.py` exposes the existing unchanged shared shape library. Scenario-local `shape_gallery.oak.md` and `verification.oak.md` are generated from the library, whose twelve source definitions and snapshots stay at their original paths, including SMEAC. The repeat-marker Python file is a shared helper, not a thirteenth schema example.

`examples/catalog.py` generates the complete repository catalogue and eight OAK teaching documents under `skills/oak-authoring/references/examples`. The review guide holds that exact mapping as inert JSON knowledge, also embedded in the assembled agent. JSON is used because complete embedded OAK documents can contain their own `>>` constant delimiter; no escaping dialect or parser change is introduced. Python fixture hosts are intentionally outside the compact teaching-only package.

## Verification

| Check | Observed result |
| --- | --- |
| Baseline module and direct commands | Passed locally and GitHub Actions run 33961608238 with declared dependencies. |
| Compilation and all generation entry points | Exit 0. |
| `python -m build.examples` | Exit 0 locally and in implementation/PR CI, all 32 registered check groups. |
| `python build/examples.py` | Exit 0 locally and in implementation/PR CI. |
| Isolated OAK scenario closure | Eight complete bundles, both groupings. |
| Detached scripts | Seven commands, repository imports and network denied. |
| Shared teaching | Eight exact documents, four stages, scope rejection and execution parity pass. |
| Baseline semantics | Nine relocated Nodes equal after 21 explicit typed schema-target rebases. |
| Protected sources | 149 files byte-identical, including all oak implementation, shared schemas, pyproject and generated grammar. |
| Repeated generation | 124 product files have identical paths and SHA256 hashes. |
| Skill entry | 8299 bytes; 190 lines. Limits remain 10000 bytes and 500 lines. |
| Assembled agent | 63822 bytes. Limit remains 64000 bytes. |
| Declared-dependency implementation verification | Run 33963385094, job 101299087839: success, including exact product fingerprint, both full commands, repeat generation and approved validator bootstrap/cache reuse. |
| Review PR verification | Run 33963494307, job 101299389541: success at reviewed product commit d626fc424ebf046d0ea3b92a8e94fe0a3ed633f7. |

Machine-readable records: [baseline](evidence/baseline.json), [equivalence](evidence/equivalence.json), [freshness](evidence/freshness.json), [verification](evidence/verification.json).

The candidate fingerprint excludes planning records and temporary CI transport. It covers product sources and generated outputs, so adding the PR number does not imply that untested code was accepted.

## Per-task evidence

| Task | Evidence |
| --- | --- |
| P01.01 | `evidence/baseline.json` inventories all nine original agent documents and twelve schema snapshots; applicable scoped owners were read. |
| P01.02 | The baseline path map covers all nine sources and sibling documents; schema dependencies become local generated copies, and the shared binding helper moves to `examples/bindings.py`. |
| P01.03 | Both baseline commands passed locally and on GitHub run 33961608238 after declared-dependency installation. The exported source tree matched 32dc36770c68812e39a9a2ec3c4df811eca4219e. |
| P01.04 | Four-stage core reuses compound growth for persistent state. No new stateful node or grammar is needed. |
| P02.01 | Eight registered directories contain eleven scenario source/document pairs; three cooperating workers remain in their parent scenario. |
| P02.02 | Local shape-gallery and verification OAK documents and four binding-helper copies are generated from unchanged shared sources. All twelve schema library examples remain registered. |
| P02.03 | `evidence/equivalence.json` records nine equal canonical meanings after 21 typed schema-target rebases; payloads, templates and exact tool names compare equal. |
| P02.04 | `examples/catalog.py` is the one explicit registration for generation, teaching selection and normal verification; it calls existing build/run functions. |
| P02.05 | `examples/catalog.oak.md` records learning order, entry/dependency paths, lessons, omitted authored parts, host limitations and commands. Its core view is generated for teaching. |
| P03.01 | `examples/fixed_knowledge/example.py` owns the two former generator-defined facts and passes canonical checks without actions or state. |
| P03.02 | `examples/shape_gallery/example.py` uses the existing schema library and exact populated instances. `validate_shapes` retains presentation and cardinality assertions. |
| P03.03 | Shape-writer sample constants contain complete input/output bindings for all four phases; the portable `run.py` verifies exact emissions and populated layouts from local source-derived documents. |
| P03.04 | Growth asserts balances 815.04 then 6642.28 and reflection targets 6400 then 51200; reflection failure after staged growth raises act_failed, preserves caller state and permits a clean retry. |
| P03.05 | Only fixed knowledge and the schema-gallery scenario wrapper are new entries. Fixtures stay inline at their source and generate sample documents; no empty fixtures or new tool services were added. |
| P04.01 | Eight generated teaching documents cover all four stages, the catalogue, local shape dependencies and sample data. Python hosts remain in repository bundles. |
| P04.02 | The review action explicitly consumes TEACHING and the catalogue route. The three obsolete flat teaching files and generator-owned scenario definitions are removed. |
| P04.03 | The full teaching mapping is literal JSON knowledge, preserving document bytes including nested constant delimiters. It is never fused as active example processes or policy. |
| P04.04 | Skill version is 2.1.0. Validator revision and source/dependency fingerprints are unchanged; existing installation-consent and optional-validator checks pass. |
| P04.05 | Skill entry is 8299 bytes and 190 lines; assembled agent is 63822 bytes. Original limits are unchanged. |
| P05.01 | All 32 normal check groups pass. Catalogue-driven example checking retains every prior schema/scenario registration, both groupings, binding and presentation checks. |
| P05.02 | Eight actual scenario bundles resolve in bounded temporary directories. Seven declared scripts pass using copied unchanged OAK, installed dependencies, isolated imports and blocked network; the shape gallery has no detached Python claim. |
| P05.03 | Negative cases reject duplicate registration, missing stage four, missing dependencies, stale or missing snapshots, changed sample data, lexical escapes and supported symlink escapes. |
| P05.04 | Actual delivered core bundles resolve in isolated copies. Operational teaching documents are rejected as fusion inputs, embedded event arrivals produce no work, and skill/agent traces match across existing consent outcomes. |
| P05.05 | Nine baseline node meanings and 149 protected files are preserved. `evidence/freshness.json` records identical file sets and bytes across two full generations of 124 product files. |
| P06.01 | Examples, skills, build and output scoped owners are updated. Active path search finds only the preserved inert DIFF fixture; no historical navigation required relocation, and plan navigation checks pass. |
| P06.02 | Compilation, all generators and both required entry points passed; `evidence/verification.json` identifies the tested product independently of delivery metadata. |
| P06.03 | Full source diff and baseline Node comparisons were reviewed. No oak implementation, library schema, grammar output, dependency declaration, tool contract or validation-consent change is present. |
| P06.04 | This report maps every task to evidence and declares environment/fixture limitations. A second complete registered-check pass and product identity comparison preceded upload. |
| P06.05 | Implementation fa4ede02530264b905fb81f02923623a34aab3dc and cleanup d626fc424ebf046d0ea3b92a8e94fe0a3ed633f7 are committed. PR #13 targets main; all 67 actual changed filenames were inspected and the portability-check patch reviewed. PR CI passed. No temporary transfer files remain and no merge occurred. |

## Limitations and review notes

Fixture hosts prove their declared inputs, dataflow and expected outputs, not arbitrary model quality or live external effects. The detached implementer command validates structure; its real execution requires the named host tools. Repository evidence checks retain a simulated commit sink, labelled as such. The shape-gallery Python wrapper requires the repository library, while its delivered OAK is self-contained and needs no action host.

The local environment uses Pydantic 2.13.4 but pydantic-settings 2.14.1, below the unchanged >=2.15 declaration. Implementation run 33963385094 and PR run 33963494307 installed the declared dependencies and passed, resolving that local verification limitation. Some combined local commands exceeded the tool execution window; individual required commands were rerun and passed. No interrupted command is counted as a pass.

The literal `examples/agents/compound_growth.py: +12 -2` remains unchanged in the delegation input fixture. It is test data, not a file lookup or active reference. Historical plan path snapshots are preserved. No historical navigational link to a moved example was found.

Container DNS prevented normal clone/push. A temporary branch-only GitHub Actions workflow exported the actual committed repository; its archive SHA256 and Git tree were checked before editing. The temporary patch transport and workspace workflow were removed before PR creation. The cleaned remote tree exactly matched the locally reviewed tree 4723a026c4bd995f4a28aca4101fe4b12727a6df. Their creation and removal remain in branch history, not in the final PR diff. The normal verification workflow gains only example catalogue generation before its unchanged check sequence.

## Delivery

Implementation commit: `fa4ede02530264b905fb81f02923623a34aab3dc`.
Reviewed product commit: `d626fc424ebf046d0ea3b92a8e94fe0a3ed633f7`.
Review PR: [#13](https://github.com/chris-buckley/open-agent-knowledge/pull/13), open against `main`.
Implementation verification: [run 33963385094](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33963385094).
PR verification: [run 33963494307](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33963494307).
Final evidence commit: the exact metadata-only head and its check result are recorded in the PR delivery comment, avoiding a self-referential commit hash in this file. Product identity remains the fingerprint above.
Merge: Not performed and not authorized.
