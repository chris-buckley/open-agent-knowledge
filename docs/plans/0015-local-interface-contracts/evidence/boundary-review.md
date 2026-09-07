# Boundary completeness review

Scope: direct review of the root candidate, with its implementations inspected separately. This is a semantic review by the implementing interpreter, not an independent reviewer or proof supplied by nonempty descriptions. The exact reviewed product bytes are identified in `product-manifest.json` and `verification.json`.

## Root-only boundary review

Every schema named below is defined in the root schemas part. The state and entry processes needed to understand the lifecycle also remain there. Initial checkpoint fields permit emptiness where incoming requests or successful receipts do not.

| Interface | Local payload and meaning | Conditions, route, and effect visible in the root | External responsibility |
| --- | --- | --- | --- |
| task-request | repository-task: unique host task id, requested work, paths, constraints | task-started selects start-task; inactive task required; reject immediate id reuse; retain request, clear earlier receipts, advance to prepare, emit progress | Host guarantees globally unique ids and serializes requests; root does not keep a ledger of every earlier id. |
| task-resume | resume-request: task id and expected resumable phase | task-resumed selects resume-task; reject wrong task/phase; preparation awaits decision; later phases require matching approval and workspace; advance exactly one supplied phase, then emit progress or result | Host restores the pinned graph and successful state, loads scoped knowledge, supplies tools, and reconciles partial effects. |
| task-approval | approval-decision: task id, exact proposal identity, boolean user decision | task-decided selects decide-task; require awaiting-approval and matching identities; true checks workspace and authorizes implement; false clears approval and cancels; emit progress | Host authenticates the real user decision and derives proposal/workspace identities. A typed boolean is not authentication. |
| task-cancel | task-handle identifies an active task | task-cancelled selects cancel-task; reject wrong or inactive task; clear approval, set cancelled, emit progress; do not undo external effects | Host delivers the decision and handles external-effect reconciliation. |
| status-request | the same task-handle, used as a query rather than cancellation | status-requested selects show-task; require retained id; emit progress without phase change or new approval | Host delivers the response. Initial idle state has no nonempty retained task id to query. |
| progress | task-progress: retained task id, phase, proposal identity and text | publish-progress explicitly fills all four slots; returned with successful checkpoint transitions or a status query; not completion evidence | Executor commits staged state/emissions on success; host durably saves and delivers them. |
| task-result | repository-result: task id, outcome, observed evidence, complete changed paths | produce-repository-result requires verified working revision and nonempty evidence, composes the response, rechecks revision, sets complete, emits all fields | Native verification/revision observation and delivery remain host duties. Evidence strings do not prove their own truth. |
| name-request | change-description: type, scope, imperative summary, breaking flag, migration meaning | name-requested selects local name-change; explicit typed CALL maps all five fields; no authority to create branches, commits, or merges | The separate naming owner performs naming and the breaking-migration check under its private process contract. |
| name-result | change-name: nonempty single-line branch and subject, optional body | local process output and EMIT validate the public shape after private outputs return | External naming work can fail; host delivers only a successful returned emission. |
| branch-update | branch-targets: remote, work/source branch, integration/destination branch | branch-update-requested selects update-branch; require inactive lifecycle; explicit CALL delegates the authorized update from destination | Git owner preserves history by merging; host authenticates targets and performs the effect. |
| merge-request | same branch-targets, explicitly requesting a merge commit | merge-requested selects merge-change; require inactive lifecycle; typed CALL maps exact targets | Git owner/host must preserve history and perform only the authorized merge. |
| merge-receipt | same branch-targets, a confirmed completed merge rather than another merge request | branch-merged selects clean-merged-branch; require inactivity; delegate ancestry-checked cleanup | Host confirms the merge; Git owner checks source ancestry and unchanged tip before deleting branch references. |

## Responsibility and dependency review

Schemas define payloads and constraints, constants retain fixed routes and limits, state retains twelve checkpoint values, interfaces distinguish crossings, triggers select nine arrival routes, and local processes retain every lifecycle decision. Cross-arrival trust and persistence assumptions remain instructions. No rule bag, schema alias, new completeness flag, process kind, or implicit import was added.

The 75-line context module owns only stateless knowledge preparation and its private two-field input contract. It reads root router/priority constants through explicit references and performs the original five preparation actions in the original order. It has no authored policy, state, interfaces, or arrivals; its rendered interpretation instructions are derived OAK context. Its references back to the root create an allowed document cycle, not a process-call cycle. The host's virtual `repository/AGENTS.oak.md` identity remains explicit.

The change module retains private naming/Git contracts and procedures. Its input and output schema identities intentionally differ from the root's public ones. Source-backed arrivals use one exact local identity; CALL maps public/private values and local output validation is not replaced by structural equivalence. The retired schema-only task module has no remaining current consumer.

The root is boundary-complete, not a claim of dependency-free execution. Its complete execution graph has three documents. Specialist paths in context constants and scoped AGENTS router paths are host-loaded prose dependencies, not automatic graph imports. General OAK still permits a supplied graph to share external interface schemas and permits schema-only libraries or omitted unjustified parts.

## Required comparisons

| Comparison | Observed result | Evidence |
| --- | --- | --- |
| E01 | PASS: all twelve interfaces use local shapes; approval fields, types and refusal preserved; meanings distinguish identical payloads used differently | Root, root-contract structural check, schema preservation in size gate, review table above |
| E02 | PASS: all twelve initial state values and slot constraints preserved locally; exact phase vocabulary, resets, invalid phase, serialized restore tested | Size gate and lifecycle checks |
| E03 | PASS: original happy path, stale/duplicate requests, approval, cancellation, revision drift, failed verification, pre/post-effect failures and Git inactivity checks pass | Both complete verification entry points; safeguard mutation checks |
| E04 | PASS: four authoring rules distinguish boundary/closure/host claims; shared relative-schema receive/emit execution succeeds; missing/wrong target and identity mismatch fail | Positive graph fixture, context checks, unchanged core APIs, generated guide ownership |
| E05 | PASS: naive insertion is 569 lines; full candidate is 500 canonical lines; actual 501-line validator rejection exercised; both grouping round-trips and one-native-action constraint pass | size-gate.json, verification.json, lifecycle and AGENTS checks |
| E06 | PASS: explicit root naming adapter preserves private owner; invalid mapped input fails before host, private-valid bad output fails public validation | Lifecycle adapter tests and detached local_contracts example |

## Additional review findings resolved

The assembled agent had only five bytes of baseline capacity. New guidance was fitted by shortening repeated explanatory wording and helper comments/docstrings, not by increasing the 64,000-byte cap. The final agent is 63,981 bytes and the skill entry 7,999 bytes. An AST comparison confirms helper execution logic is unchanged after excluding its version, immutable source revision, source digest, and non-executable docstrings/comments. Consent gating, no-install behavior, isolated dependency setup, exact source identity, safe extraction, cache reuse, and truthful not-performed outcomes remain covered by the existing tests.

The first full-suite calls hit the environment's per-call wall limit. Running the commands with persistent logs in this same task produced observed exit zero for both complete entry points. No product timeout or verification requirement was relaxed.

Verdict: no blocking defect found in this direct review. Limits are deliberately tight: the root has no remaining line capacity and the assembled agent has 19 bytes. Future changes must continue to satisfy the existing checks rather than silently grow the limits.
