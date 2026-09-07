# Local interface contracts completion report

Status: Implementation and local verification complete; final publication pending.
Verdict: PASS for the implemented product and direct semantic review. PR handoff remains a separate observed step.

## Verified subject

Product content fingerprint: `9f3991dd7e78e6884a906f6c5eb6cea65ed2e0ba7ed7d792dcd920bfd26e73b3` (SHA-256).

The complete path-to-content mapping and algorithm are in [product-manifest.json](evidence/product-manifest.json). It covers maintained source, scoped knowledge, checks, examples, and generated products; historical/task records and temporary transport files are explicitly excluded to avoid self-referential evidence. The eventual immutable implementation commit is recorded during publication, without changing the verified product bytes.

Validator source revision: `85ddd5393fd4349632f728f5a05cb67f9bc5dbf5`. The matching package digest is `9bca0d69e12c26aac64d3e7218f4ccfc620e7a7196b569d324ff7ac8197053bc`; the authoring capability is version 3.1.0.

The original checkout revision `1cbdb29db39a7769df89fa15759634e20cfe27a6` and subsequently observed remote tip `c42c526df6baeab916ec2d389e8ac990b6edcf16` have identical tree `142fa5f707ff3c12c536ba00532101e3aab89fa3`. The identity drift was checked before publication; our writes append to the current remote history without amend, rebase, squash, or force push. The reviewed snapshot and plan references are preserved as historical evidence.

## Outcome

The root now defines all sixteen of its contracts locally: nine distinct public interface shapes plus its checkpoint and task-specific proposal, revision, change, verification, and outcome shapes. All twelve interfaces have descriptions; all twelve state bindings are local. Nine arrival routes and the existing phase sequence are preserved. Root-specific structural checks are separate from the general OAK models and resolver, so valid shared external schemas remain supported.

The former schema-only task module was removed after migrating its current consumers. Stateless knowledge preparation moves to `.agents/rules/context.oak.md`, with an explicit two-field private input and references to the root-owned router/priority. The separate change module keeps private naming/Git procedures. Root decisions, state, host trust requirements, approvals, revision checks, and result emission remain local.

The new `examples/local_contracts` scenario demonstrates public TEXT/TITLE contracts adapting to private RAW_TEXT/CLEAN_TEXT work. It accepts a valid trimmed title and rejects empty or multiline worker results at the public boundary. It runs with a deterministic trimming host, not a claimed live model or external publication. The four-stage teaching core and existing shared-schema examples remain intact.

## Size, closure, and semantics

| Measure | Observed | Unchanged limit |
| --- | --- | --- |
| Root canonical lines | 500 | 500 |
| Root schemas / interfaces / state / arrivals | 16 / 12 / 12 / 9 | Existing public protocol preserved |
| Root local processes | 18 | At most one native ACT per process |
| Context module canonical lines | 75 | No root contract externalized |
| Authoring skill entry | 7,999 bytes | 10,000 bytes |
| Assembled authoring agent | 63,981 bytes | 64,000 bytes |

The complete candidate was measured before product edits: naive insertion was 569 lines. Compact semantic templates and separately owned stateless preparation, not deleted safeguards or a relaxed limit, produced the 500-line candidate. See [size-gate.json](evidence/size-gate.json).

Exact execution closure:
```text
repository/.agents/rules/context.oak.md
repository/.agents/rules/repository-change.oak.md
repository/AGENTS.oak.md
```

This is a boundary-complete root, not dependency-free execution. Prose specialist/scoped-AGENTS routes still require host loading; schema references do not authenticate users or implement persistence, delivery, or tools. The [boundary review](evidence/boundary-review.md) records every root interface and E01 through E06 with these distinctions.

## Verification evidence

Both complete entry points ran against the same product bytes using Python 3.13.5 and repository dependencies outside the checkout, without an editable install.

| Command | Observed result |
| --- | --- |
| `python -m build.examples` | Exit 0; 42.374 seconds |
| `python build/examples.py` | Exit 0; 42.514 seconds |
| Compilation and all four source generators | Exit 0 |
| Repeat generation | Identical complete generated path and byte mapping |
| Helper execution AST comparison | Unchanged except version/source pin/digest and non-executable descriptions |
| Git whitespace check | Passed |

The complete entry points cover all 36 registered checks, including lifecycle serialization and replay, approval/refusal/cancellation, drift and external-effect failures, malformed receipts and emissions, source/schema identity, public/private adapter input/output rejection, shared external schemas, missing/wrong dependencies, detached examples, consent/caches, cold regeneration, output repair, symlink refusal, graph closure, both groupings, fusion parity, and architectural invariants. New mutation tests detect removed approval/revision gates and silent guard filtering; an exactly 501-line canonical document is rejected by the actual AGENTS line check.

Full command timestamps, versions, sizes, and exact check names are in [verification.json](evidence/verification.json). Earlier tool-call timeouts are recorded as incomplete attempts, not passed tests; the two commands above returned actual exit zero. Live network bootstrap and remote CI results will be recorded during the PR handoff rather than inferred from local fixtures.

## Required comparisons

| Comparison | Result |
| --- | --- |
| E01 local public schemas and approval meaning | PASS |
| E02 local checkpoint and value lifetimes | PASS |
| E03 resumable protocol and failure preservation | PASS |
| E04 honest document/graph/host claims and shared schemas | PASS |
| E05 full canonical root within 500 lines | PASS |
| E06 explicit public/private adaptation | PASS |

Detailed acceptance mapping appears in the boundary review and executable checks; nonempty prose is never presented as semantic proof.

## Changed paths

The following list describes this implementation relative to the planning checkout; the temporary checkout/transfer workflow is removed before handoff. Completed older plan records are unchanged.
```text
.agents/rules/context.oak.md
.agents/rules/repository-task.oak.md
AGENTS.md
build/AGENTS.md
build/authoring_guides.py
build/authoring_validator.py
build/checks/agents.py
build/checks/authoring.py
build/checks/coding_standards.py
build/checks/repository_contracts.py
build/checks/repository_lifecycle.py
docs/plans/0015-local-interface-contracts/evidence/boundary-review.md
docs/plans/0015-local-interface-contracts/evidence/product-manifest.json
docs/plans/0015-local-interface-contracts/evidence/size-gate.json
docs/plans/0015-local-interface-contracts/evidence/verification.json
docs/plans/0015-local-interface-contracts/plan.md
examples/AGENTS.md
examples/catalog.oak.md
examples/catalog.py
examples/local_contracts/example.oak.md
examples/local_contracts/example.py
examples/local_contracts/sample.oak.md
examples/local_contracts/worker.oak.md
examples/local_contracts/worker.py
generated/oak-authoring.oak.md
generated/oak-authoring.skill/SKILL.md
generated/oak-authoring.skill/guides/authoring.oak.md
generated/oak-authoring.skill/guides/review.oak.md
generated/oak-authoring.skill/guides/validation.oak.md
generated/oak-authoring.skill/references/00-structure.oak.md
generated/oak-authoring.skill/references/01-schemas.oak.md
generated/oak-authoring.skill/references/04-interfaces.oak.md
generated/oak-authoring.skill/references/05-triggers.oak.md
generated/oak-authoring.skill/references/06-processes.oak.md
generated/oak-authoring.skill/references/07-instructions.oak.md
generated/oak-authoring.skill/scripts/validate.py
oak/AGENTS.md
oak/node/AGENTS.md
oak/resolve/AGENTS.md
oak/rules/guidance.py
docs/plans/0015-local-interface-contracts/report.md
```

## Limits and handoff

No new runtime syntax, schema alias, completeness flag, universal locality restriction, dependency, or tool capability was added. General descriptions remain optional where meaning is unambiguous. The optional validator pin is immutable and source-checked; consent, no-install authoring, isolated installation, extraction protection, and cache behavior are preserved.

All reported lifecycle effects are deterministic test-host observations. They do not prove production user authentication, durable host storage, delivery, successful real Git operations, or exactly-once external effects. Review was performed directly by the implementing interpreter, without subagents or a claimed independent approval.

The root has zero spare lines and the agent nineteen spare bytes. Both unchanged caps remain enforced. No merge or branch deletion is performed. Final commit, PR, and remote checks are recorded after publication.
