# Native OAK interpreter context and revision-linked evidence: completion report

## Outcome

Implemented the accepted change without a new authored format, language token, canonical part, or dependency. The current architecture remains in the scoped AGENTS documents and implementation, not this historical report.

## Implementation

`oak/context.py` derives detached canonical OAK documents. `build_interpreter_context` preserves all source documents, their policy scope, the current transaction state, and original schema identities. It adds one native action invocation whose inputs are literal values. Generated filenames avoid collisions. The host interprets that invocation under the original source instructions; it does not run the other supplied processes.

`task_context` defaults to the complete graph. An explicit process selects its whole owning document and transitive document dependencies; exact additional document paths can be retained for host-known prose dependencies. It never merges identities, prunes individual entries, scans directories, or replaces the execution graph.

`execute(..., interpreter=...)` supplies the OAK context for native actions. The existing `act` callback remains supported for programmatic consumers, with ambiguous dual handlers rejected. Named-tool dispatch, output validation, binding promotion, loops, and transaction behavior remain unchanged.

The implementer now follows plan, implement, review, apply findings, snapshot, verify, and commit. Shared verification identifies subject, SHA-256 snapshot revision, versioned check, observed result, and evidence location. Commit is gated on subject, revision, required check, and success. The effect-producing host must reject drift before acting; a post-effect assertion also detects a host that reports a different committed revision without claiming external rollback.

## Verification

Local compilation and both `python -m build.examples` and `python build/examples.py` passed. The new context and evidence checks run in that same existing check collection. `git diff --check` passed. All reference outputs were regenerated and remained unchanged; affected example snapshots were regenerated. A second generation left the checked products byte-identical.

Context checks cover cross-document calls, nested loop frames, scoped instructions, same-named schemas in different documents, current typed state, invalid input before invocation, invalid output before promotion, mutation isolation, deterministic generation, document-reference cycles, filename collisions, dependency closure, and explicit retention.

Evidence checks execute fixed before/after source fixtures, record actual check results, and reject wrong subjects, stale revisions, wrong checks, failed results, malformed booleans, empty or unrecorded evidence, and pre-commit drift. Blocked work emits escalation without snapshotting or committing. The simulated commit sink is explicitly labelled; these checks do not claim a production Git commit or live model call.

GitHub verification: compilation, both repository entry points, and repeated-generation freshness passed in [run 33927416096](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33927416096).

## Changed areas

Context API and public exports; native action dispatch and process frame identity; scoped package, execution, and example knowledge; the implementer and its render; the shared verification schema and render; the interpreter-context example and render; registered context/evidence checks and export guards; this plan and report.

## Limits

This is a conservative document-level context selector, not a semantic proof of which prose can be dropped. Host tools must establish evidence truth and perform safe external effects. The adapters demonstrate the same OAK task through deterministic host paths, not equivalence between live models. Temporary branch-verification and transport files are removed from the final implementation tree.
