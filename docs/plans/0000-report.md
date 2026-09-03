# OAK Refactor Completion Report

## Verdict

Approved

## Baseline

- Repository: chris-buckley/open-agent-knowledge
- Starting branch: main
- Starting commit: 408acd101e2123ea88d861c77340551841143cf6
- Final branch: refactor/organize-oak
- Final commit: ae9cdc4a9778c1b2bfbde5993691798722f31888 is the last code commit; the docs commits after it add the AGENTS.md rules, the PRD tree lines, and this report

## Completed phases

- [x] Phase 0: Safe baseline
- [x] Phase 1: Baseline behaviour capture
- [x] Phase 2: PRD approval
- [x] Phase 3: Shared foundations
- [x] Phase 4: Process models
- [x] Phase 5: Schema models
- [x] Phase 6: Node validation
- [x] Phase 7: Parsing
- [x] Phase 8: Resolution
- [x] Phase 9: Execution
- [x] Phase 10: Rules and surfaces
- [x] Phase 11: Rendering
- [x] Phase 12: Build verification
- [x] Phase 13: Examples and cleanup
- [x] Phase 14: Public API
- [x] Phase 15: Documentation
- [x] Phase 16: Obsolete implementation removal
- [x] Phase 17: Final verification
- [x] Phase 18: Commit and delivery

## Structural result

### Deleted monolithic files

- oak/parse.py
- oak/resolve.py
- oak/execute.py
- oak/rules.py
- oak/surface.py
- oak/node/graph.py
- oak/node/parts/processes.py
- oak/node/parts/schemas.py
- oak/render/oak/syntax.py
- oak/render/json_ld.py

### Added packages

- oak/node/parts/processes: operators, targets, values, conditions, steps, model
- oak/node/parts/schemas: constraints, binding, model
- oak/node/validation: values, conditions, flow, processes, triggers, tools, contracts, node
- oak/node/parts: entry (the identified base every part extends), part (the closed part union)
- oak/node/index.py, oak/node/structure.py, oak/node/interpretation.py
- oak/parse: errors, cursor, document, grouping, data, schemas, values, conditions, steps, processes, triggers, interfaces, fragments
- oak/resolve: errors, paths, graph, references, contracts, resolver
- oak/execute: models, context, values, actions, steps, executor
- oak/rules: model, validation, guidance
- oak/surface: model, constraints, processes, entries, registry
- oak/render: selection (the render function and RenderName, out of the initializer)
- oak/render/oak: data, processes, triggers (arrangement, groupings, instructions, styles kept)
- oak/render/json_ld: context, identifiers, values, entries, document
- build/checks: fixtures, text, metadata, surfaces, parsing, validation, resolution, execution, rendering, human_examples, outputs, architecture
- examples/agents/bindings.py (the local and interface binding helpers four agent examples shared) and examples/schemas/repeat_marker.py (the one repeat-marker instruction seven schema examples shared)

### Final size exceptions

- oak/node/parts/processes/steps.py, 25.7 KB: the closed set of eleven step models with their model-local checks and the shared step traversal; the plan forbids splitting one class per file merely to reduce size.
- build/checks/execution.py, 21.0 KB, and build/checks/architecture.py, 22.1 KB: verification corpora, not algorithmic production modules; the plan permits declarative check and registry modules to exceed ordinary size.

## Behaviour preservation

- [x] OAK snapshots match (58 files, every examples/**/*.oak.md and outputs/**, SHA-256 identical to the baseline)
- [x] Generated outputs match (outputs/oak.ebnf, outputs/authoring.md, outputs/docs/**, byte-identical; freshness gates pass)
- [x] Root API matches (sorted oak.__all__, 108 names, identical; now an explicit tuple)
- [x] Module imports match (every non-underscore symbol the baseline imported from oak, oak.parse, oak.resolve, oak.execute, oak.node.parts.processes, oak.node.parts.schemas, oak.render.json_ld still imports; the four cross-entry validators moved to oak.node.validation as planned; the eleven underscore-prefixed parser functions the build imported are replaced by oak.parse.fragments.parse_fragment as planned)
- [x] Model JSON Schemas match (43 models, identical)
- [x] Parse diagnostics match (the 46-failure snapshot captured from build/examples.py is identical: codes, paths, lines, messages, order)
- [x] Validation diagnostics match (same snapshot)
- [x] Resolution diagnostics match (same snapshot)
- [x] Execution diagnostics match (same snapshot, including suppressed parallel failures)
- [x] JSON-LD matches (renders exercised by the build; reviewers compared 48 baseline objects structurally and serialized)
- [x] Example execution matches (all 17 example scripts exit 0 and reproduce their committed renders)
- [x] Negative cases match (a probe run against a 408acd1 worktree and this tree produced identical records: dead branches, local and cross-document call cycles, missing source paths, documents, and entries, wrong target types, root escape, malformed trigger facts, indentation, and separators, plus both-grouping round trips and model dumps of all 21 example nodes)
- [x] Clean checkout builds (a fresh clone of the branch runs build/examples.py and every example with no output drift)

## Architectural checks

- [x] Parser imports no renderer
- [x] Renderer imports no parser
- [x] Node validation is separated by concern
- [x] Resolution owns cross-document checks
- [x] Execution uses context and frame objects
- [x] Comparison semantics have one implementation
- [x] Build imports no private parser functions
- [x] Public exports are explicit
- [x] Internal modules import the owning leaf module, never a package barrel
- [x] Package initializers hold a docstring, imports, and __all__ only
- [x] No compatibility shim remains
- [x] No obsolete path remains

## Commands run

```text
./.venv/Scripts/python.exe -m compileall -q oak build examples   exit 0
./.venv/Scripts/python.exe build/examples.py                     exit 0 (build.checks.CHECKS in order, validate_architecture last)
./.venv/Scripts/python.exe examples/agents/*.py examples/schemas/*.py   17 scripts, all exit 0
git status --short                                               empty after the build
git diff --check main..HEAD                                      clean
```

## Output comparison

```text
snapshots.sha256      58 files identical to the 408acd1 baseline
public-api.json       identical (108 names)
model-schemas.json    identical (43 models)
imports.json          every public-module symbol present
diagnostics.json      identical (46 failures)
probes                annotation metadata, SchemaBindingError signature, ResolvedGraph.registries equality, and every package __all__ bound
PRD Tree section      identical to the repository
negative probes       identical to a 408acd1 worktree (21 dumps, 42 round trips, 32 cases)
clean clone           build and 17 examples pass, git status empty
```

## Diff review

* Files added: 90 (89 before this report)
* Files modified: 42
* Files deleted: 10
* Unrelated changes: none

## Deviations from the plan

* The shared operator mapping is OPERATOR_PHRASES (ordered phrase, operator pairs) rather than the plan's example name OPERATOR_BY_TEXT; the parser needs the authored order, and no alias was added.
* No narrow part-name type was added; the repeated literals did not justify it.
* oak/node/validation/contracts.py exists in addition to the plan's seven validation modules: it owns the emit-contract and cycle algorithms shared by local validation and resolution (a reviewer finding).
* build/checks/architecture.py exists in addition to the plan's eleven check modules: the architecture guard has its own owner (a reviewer finding).
* Cross-entry contract checks lived briefly in oak/node/parts/processes/contracts.py between Phase 4 and Phase 6, then moved to oak/node/validation.
* The explicit root __all__ keeps the seven submodule names (authoring, base, defaults, node, rules, surface, vocabulary) that the computed baseline __all__ exposed; removing them needs the user's explicit approval, which was not requested.
* Two intermediate commits briefly dropped `from __future__ import annotations` in moved modules; the following commit restored it, and later fixes were folded into their block commits before the push.
* Phase 2's tick commit was pushed by GPT-5 Pro through the GitHub connector; every other commit was applied, gated, and pushed from the workstation.
* Entry moved from oak/base.py to oak/node/parts/entry.py: oak.base imported oak.vocabulary for SlugId while the vocabulary datatypes imported oak.base, and the baseline hid that cycle behind a lazy __getattr__ in oak/vocabulary/__init__.py. The vocabulary package now binds every export eagerly from its leaf modules. The import path oak.base.Entry no longer exists: Entry was never a root export, the plan's import-path snapshot does not cover oak.base, and no repository file outside oak imported it. Keeping Entry in oak/base.py would need a mid-module import to dodge the cycle, a stopgap the repository rules reject.
* Part moved to oak/node/parts/part.py and render() with RenderName moved to oak/render/selection.py, so every package initializer holds a docstring, imports, and __all__ only; the architecture guard now enforces that. render.__module__ reads oak.render.selection, as every function the plan moved into a leaf module reads its leaf; the function body and its dispatch are unchanged.
* Every internal module imports the owning leaf module; the guard rejects any name imported through a package barrel (only the root oak/__init__.py composes from packages).
* The explicit root __all__ follows the domain-grouped import order rather than the baseline's globals order; the plan defines the public API snapshot as sorted(oak.__all__) (plan lines 927 and 2208), and the sorted names are identical.
* The section 10 style pass (plan lines 803 to 844, 250, 251, 249, 1868) was applied after the user asked for it: every closed-union walker (executor steps and values, OAK and JSON-LD renderers, node validation, resolver references, static conditions) dispatches by model type through a match with one function per type; the step and trigger parsers are split per keyword and per fact; guard atoms and range bounds are named records; read-only parameters take Sequence, Mapping, and AbstractSet; vague locals and private helper names carry their domain noun; three build helpers moved to their one consumer; the agent examples share one binding-helper module and the schema examples share one repeat-marker instruction, every multi-line entry is a named module value, and reused literals are constants. The two PRD tree lines for the helper modules landed in 3961d80 after the user approved them.
* The JSON-LD type tables (step, constraint, value, condition) stay keyed by the model discriminators, as at the baseline, so a subclass cannot rename a node; they are dict constants like OPERATOR_TEXT in oak/node/parts/processes/operators.py, and plan line 827 concerns mutation ownership, not constant tables.
* The last fix-range reviewer measured behaviour against the mid-style commit 89eba8e rather than the baseline and flagged the restored discriminator tables, the restored error context, and the un-exported JSON_ADAPTER and TypedTarget; each of those matches 408acd1, which is the contract.
* build/checks/architecture.py enumerates source files with rglob. That is verification coverage of the whole tree, the same enumeration the plan's own bash checks perform with find; the plan's exclusion of automatic discovery concerns product registries and module loading, and nothing is imported or registered by the scan.
* AGENTS.md gained two rules in 4c57016 at the user's request: a Tree section line that mirrors a file already in the repository is written without asking, and a routine question is presumed, acted on, and reported.

## Remaining concerns

* 15 plan boxes stay open: line 252 (a shared typed lookup protocol between local and resolved validation, which the audit showed is not needed: the two lookups return different contracts), the two ruled deviations at lines 753 (OPERATOR_PHRASES) and 1072 (no part-name type), and the 12 stop conditions at lines 2272 to 2283, none of which occurred. Every behaviour-contract, section 10 style, phase exit, Phase 18, definition-of-done, and recovery box is ticked with evidence.
* The branch holds 91 commits including this report and the tree line that lists it. The user chose a merge commit over a squash, so the plan's single commit title is the pull request title.
