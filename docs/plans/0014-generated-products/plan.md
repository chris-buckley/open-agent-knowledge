# Consolidate generated OAK products

Prepared: 2026-09-06T21:54:55+10:00
Classification: PUBLIC

Plan status: Ready for implementation.
Implementation status: Not started.
Authorisation: The user requested this plan on a new branch. Implementation, pull request creation, and merging are not authorised by this planning request.
Repository: `chris-buckley/open-agent-knowledge`
Baseline: `main` at `2a3ba6c27b6110de4ace334e51d2f195a7ded522`.
Branch: `docs/plan-generated-products`
Plan: `docs/plans/0014-generated-products/plan.md`
Format: `examples/schemas/smeac_plan.oak.md`, governed by `docs/AGENTS.md`.

## 1. Situation

### Operating Environment
OAK delivers a generated grammar, per-construct language reference, a standalone authoring agent, and a modular authoring skill. This change makes those products easy to inspect together while keeping every maintained source outside their generated delivery tree.

### Current State
At the pinned baseline, `outputs/` holds `oak.ebnf`, `docs/`, and `oak-authoring.oak.md`, while the skill is under `skills/oak-authoring/`. Most skill material is generated, but `skills/oak-authoring/scripts/validate.py` is maintained source that `build/authoring.py` reads for helper text and validator identity. Both `outputs/AGENTS.md` and `skills/AGENTS.md` contain maintained repository guidance, so neither directory can simply be treated as wholly reproducible output.

### Challenges
- Mixed ownership: Moving the skill alone would conceal maintained validator source inside a directory called generated.
- Bootstrap dependence: The authoring generator currently reads the delivered helper, and its artifact mapping does not include generating that helper.
- Path coupling: Generators, reference content, checks, ownership routing, and other live consumers can retain obsolete locations after a filesystem move.
- Tight size budget: The baseline standalone agent is 63,995 bytes against the existing 64,000-byte limit. Required path changes must not silently discard knowledge or relax the limit.
- Historical evidence: Old locations in completed records and literal specimens must not be rewritten as though the new layout existed at the time.

### Supporting Factors
- Higher intent: Present one authoring capability in two usable forms, alongside its generated language reference, without adding another source of truth.
- Adjacent efforts: Preserve the existing default render, skill organisation, flat Python authoring, self-contained examples, and EBNF presentation. This plan does not reopen their designs.
- Supporting resources: Existing generators, source-owned rules and surfaces, detached example checks, skill-agent parity checks, and freshness checks support a bounded migration.

### Assumptions
- The agreed product names remain `oak-authoring.oak.md`, `oak-authoring/`, and `SKILL.md`.
- Generated products remain Git-tracked for inspection and distribution.
- Existing sources outside the delivery directories can generate the products after the validator helper is separated; verify this rather than assuming no other bootstrap dependency exists.
- No external consumer requiring compatibility at `outputs/` or top-level `skills/` has been named. Do not invent compatibility aliases or forwarding copies.

### Constraints and Limitations
- Constraint: This commit contains the plan only. Leave every execution checkbox open and do not change current ownership rules until implementation is authorised.
- Constraint: The final product root has only the agreed grammar, reference directory, standalone agent, and skill directory. Do not add `agents/`, `prompts/`, `skills/`, or repository README indexes beneath it.
- Constraint: Keep `.agents/skills/`, the top-level `docs/` planning area, legacy APS material, and the example source/sibling layout in place. This is not a relocation of every generated file in the repository.
- Constraint: Preserve language meaning, syntax, schema identities, process order, fusion scope, literal teaching payloads, and validator security and consent contracts.
- Constraint: Keep maintained repository guidance and helper source outside `generated/`. No hand-authored `AGENTS.md` belongs in the delivered product tree.
- Limitation: The planning baseline was inspected through GitHub. A local checkout attempt failed because the environment could not resolve `github.com`; repository build checks were not run during planning. Implementation verification remains required before any completion claim.

### Baseline Evidence
Paths in this subsection identify the inspected source at the pinned baseline, not future locations. `AGENTS.md`, `docs/AGENTS.md`, `examples/AGENTS.md`, `build/AGENTS.md`, `outputs/AGENTS.md`, and `skills/AGENTS.md` establish routing, plan format, and ownership. `build/authoring.py`, `build/docs.py`, and `skills/oak-authoring/scripts/validate.py` establish generation, the embedded grammar path, and validator source ownership. The GitHub listing for `outputs/` establishes the standalone agent size. `build/checks/plans.py` supplies the plan structure rules reviewed for this record.

## 2. Mission

The implementer consolidates OAK's generated products on the work branch after explicit implementation approval, preserving their content and behaviour while making source ownership and clean regeneration unambiguous.

Task: Complete the layout migration, verification, and delivery report in one implementation pass after approval and before requesting review.
Purpose: Let a reader find the grammar, browsable language reference, single-file authoring agent, and modular skill together without mistaking generated deliveries for maintained sources.
End state: All four products are generated under `generated/`, the old delivery roots are removed, and a clean rebuild recreates every delivered file without reading previous generated copies.

### State Comparisons

#### E01: Product layout
Authority: required
Current state:
The baseline delivery roots and their relevant children are:
```text
outputs/
├── AGENTS.md
├── oak.ebnf
├── docs/
└── oak-authoring.oak.md
skills/
├── AGENTS.md
└── oak-authoring/
    ├── SKILL.md
    ├── references/
    ├── guides/
    ├── assets/
    ├── scripts/validate.py
    └── _template/
```
Desired state:
The generated product root is:
```text
generated/
├── oak.ebnf
├── reference/
├── oak-authoring.oak.md
└── oak-authoring/
    ├── SKILL.md
    ├── references/
    │   ├── oak.ebnf
    │   └── ...
    ├── guides/
    ├── assets/
    │   └── examples/
    ├── scripts/
    │   └── validate.py
    └── _template/
```
Acceptance: Match all named paths exactly. The ellipsis abbreviates existing generated reference files, not a new file or permission to omit them. Compare complete source-derived file manifests, not only these abbreviated trees. Top-level `outputs/` and `skills/` are absent; `.agents/skills/`, repository `docs/`, and example siblings retain their existing roles. Do not add a duplicate product wrapper or forwarding tree.

#### E02: Source and guidance ownership
Authority: required
Current state:
```text
skills/oak-authoring/scripts/validate.py  -> maintained helper and validator identity
skills/AGENTS.md                        -> maintained capability guidance
outputs/AGENTS.md                       -> maintained generated-output guidance
build/authoring.py                      -> reads helper from delivery directory
```
Desired state:
```text
build/authoring_validator.py            -> sole maintained helper and identity source
build/AGENTS.md                         -> build and generated-product ownership
build/authoring.py                      -> reads source and generates delivery
generated/oak-authoring/scripts/validate.py -> generated standalone helper
```
Acceptance: Move the helper's source and identity to `build/authoring_validator.py` and generate `generated/oak-authoring/scripts/validate.py` from it. The delivered helper bytes match that source and remain usable without importing repository build modules. Consolidate the nonduplicated output and capability responsibilities into source-owned `build/AGENTS.md`, within the 500-line limit, and update root routing and product-location rules. Preserve the existing host-scoping and fusion boundaries. No maintained input or repository guidance remains under `generated/` or the removed roots.

#### E03: Reference identity and purpose
Authority: required
Current state:
`outputs/docs/act.md` is one generated construct reference. Its generated content includes:
```text
syntax-reference: "outputs/oak.ebnf"
```
Desired state:
The same page is delivered as `generated/reference/act.md`, with:
```text
syntax-reference: "generated/oak.ebnf"
```
Acceptance: Move the complete generated reference from `outputs/docs/` to `generated/reference/`, keeping existing page filenames and content responsibilities. Derive it from the same models, rules, and surfaces through `build/docs.py`; change its source-owned location references rather than patching generated bytes. The root reference remains independently browsable, not a runtime dependency of the portable skill or standalone agent. Preserve the skill's internal `references/` directory and its own grammar copy.

#### E04: Clean and repeatable generation
Authority: required
Current state:
`build/authoring.py` reads `skills/oak-authoring/scripts/validate.py` before generating the skill and standalone agent. Deleting that delivery directory removes a required maintained input, so the complete product cannot be regenerated from the remaining source tree alone.
Desired state:
In a disposable working snapshot, deleting all of `generated/` leaves every required maintained input available. An explicit rebuild sequence creates the grammar, reference, standalone agent, complete skill, optional helper, examples, template, and deliberate empty-directory markers. A second rebuild produces the same path set and bytes.
Acceptance: Demonstrate cold generation in a fresh interpreter process with both old delivery roots absent and no cached generated imports. Compare complete relative-path and content-hash manifests after cold and repeated generation. Remove or corrupt a generated helper and another product, regenerate, and prove restoration from source; prove stale owned outputs are rejected or pruned. Read no previous generated files as maintained source. Intermediate products emitted earlier in the same rebuild may be consumed for assembly. Confine destructive checks to disposable snapshots and generator-owned paths.

#### E05: Portable behaviour and content preservation
Authority: required
Current state:
The existing skill and standalone agent share generated OAK knowledge. The optional helper has immutable validator identity checks, separate installation consent, bounded loading, and distinct valid, invalid, and not-performed outcomes; the skill template and teaching examples are inert knowledge.
Desired state:
Both relocated authoring forms preserve those contracts. Copying only `generated/oak-authoring/` provides the modular skill; copying only `generated/oak-authoring.oak.md` provides the assembled OAK authoring knowledge without a dependency on sibling `reference/` or repository build sources.
Acceptance: Preserve relative document closure, metadata identity consistency, scope-safe fusion and refusal cases, literal teaching/template payloads, both OAK grouping checks, and skill-agent execution parity. Keep no-install authoring, explicit installation consent, validator fingerprints, safe extraction, and result/exit semantics. The root and skill grammar files remain byte-identical and their embedded values equal. Keep the 10,000-byte skill-entry and 64,000-byte agent limits. Byte differences must be explained by exact location references or necessary verified delivery metadata; this plan does not authorise policy rewriting, knowledge deletion, syntax changes, or a new language version.

## 3. Execution

Intent: Consolidate the visible products without creating a new authoring system. Separate maintained source before moving delivery paths, preserve each product's purpose, and prove that the new layout is reproducible and portable.
Concept of operations: First confirm source ownership and path consumers against the implementation baseline. Then separate the validator source, migrate generators and ownership guidance, and replace the old delivery roots. Add checks that fail on incomplete relocation or dependence on generated copies, verify the full repository, and record the delivered evidence. These phases are ordering within one complete change, not deferred scope.

### Phase 1: Confirm the implementation baseline
Objective: Establish an exact migration inventory before editing source.
- [ ] Key task: P01.01 Obtain explicit implementation approval, read the root and all applicable scoped AGENTS documents and Python standards, and record the starting branch tip.
- [ ] Key task: P01.02 Inventory every tracked file under `outputs/` and top-level `skills/`, classify maintained inputs versus generated deliveries, and map each file to its source owner and final destination.
- [ ] Key task: P01.03 Search active code, checks, workflow configuration, guidance, examples, templates, and commands for complete paths and split path constructions involving the old roots; classify historical snapshots and literal examples separately.
- [ ] Key task: P01.04 Capture baseline file manifests, helper identity and bytes, product sizes, generated content, and verification outcomes; do not treat an existing failure as caused by this migration without evidence.
Success criteria: The inventory covers E01 through E05, records exact source owners and consumers, and distinguishes accepted changes from preserved material; store supporting evidence in this plan's `evidence/` directory when implementation begins.
Transition trigger: Approval is recorded and the baseline inventory is complete, with no unresolved source ownership.

### Phase 2: Separate maintained sources
Objective: Make generation independent of pre-existing delivered files.
- [ ] Key task: P02.01 Move the maintained helper to `build/authoring_validator.py`; make the authoring generator read its content and identity there and include the delivered helper in its generated artifact mapping.
- [ ] Key task: P02.02 Keep the helper self-contained and test its delivery-location discovery rather than deriving runtime paths from its new maintained-source location.
- [ ] Key task: P02.03 Consolidate output and capability ownership into `build/AGENTS.md`, remove duplicate claims, and update root routing and the distinction between `.agents` assistance and generated products.
- [ ] Key task: P02.04 Audit generator imports and reads for any other dependency on previous generated output; preserve existing immutable validator pins when package and dependency fingerprints are unchanged.
Success criteria: E02 is satisfied by one maintained helper owner and no authored guidance in delivery paths; E04 has no unresolved bootstrap dependency; E05 retains validator identity and discovery semantics. Record inspected dependencies and helper-copy evidence.
Transition trigger: All maintained inputs are outside the generated product tree and generation can begin without either old delivery root.

### Phase 3: Migrate the products and consumers
Objective: Produce the agreed layout from the existing source owners.
- [ ] Key task: P03.01 Retarget `build/ebnf.py` to `generated/oak.ebnf`, `build/docs.py` to `generated/reference/`, and `build/authoring.py` to the sibling agent and skill destinations.
- [ ] Key task: P03.02 Update source-owned path references, including the reference's `syntax-reference` value, guide text where necessary, checks, active commands, workflow configuration, and scoped guidance; do not perform a blind replacement of ordinary words such as outputs or skills.
- [ ] Key task: P03.03 Generate the complete skill, preserving internal references, guides, assets, teaching catalogue, optional script, template, and deliberate `.gitkeep` files; keep portable grammar copies rather than replacing them with repository symlinks.
- [ ] Key task: P03.04 Remove the tracked old delivery roots and obsolete path assumptions without compatibility wrappers, then verify that unrelated development skills, legacy material, example siblings, and planning records are not relocated.
Success criteria: E01 and E03 match their exact destinations and source-derived manifests; E02 remains source-owned and E05 content changes are narrowly accounted for. Record the old-to-new path map and any allowed byte changes.
Transition trigger: All migrated products exist in the new tree and no active consumer still requires a removed location.

### Phase 4: Enforce regeneration and portability
Objective: Make incomplete migration and generated-source dependence fail verification.
- [ ] Key task: P04.01 Update existing output, authoring, optional-validator, architecture, AGENTS, EBNF, and example checks for the new ownership and expected file sets; keep them registered in the full verification entry point.
- [ ] Key task: P04.02 Add cold-generation and second-generation checks from a disposable source snapshot with `generated/`, `outputs/`, and top-level `skills/` absent, then compare complete generated manifests and bytes.
- [ ] Key task: P04.03 Exercise rejection or repair of missing and edited generated helpers, missing product files, stale generated reference pages, and obsolete-root dependencies; ensure cleanup never deletes maintained sources or follows escaping paths.
- [ ] Key task: P04.04 Run detached skill and standalone-agent checks without sibling root reference files, repository build imports, network access, or undeclared supporting files; retain operational-fusion refusal and literal-preservation tests.
- [ ] Key task: P04.05 Verify helper source/delivery equality, no-install and consent outcomes, exact validator identity, grammar-copy and embedded-value equality, and unchanged product byte limits.
Success criteria: E01 through E05 have executable checks covering successful migration and meaningful rejected corruptions; cold rebuild and detached evidence demonstrate the guarantees rather than inferring them from file existence.
Transition trigger: The updated checks pass against generated products and fail against their deliberately corrupted counterparts.

### Phase 5: Verify the complete candidate
Objective: Establish repository-wide correctness and a reviewable final diff.
- [ ] Key task: P05.01 Use an external Python environment satisfying `pyproject.toml`, with no editable repository install; use a clean snapshot including pending changes when ignored local checkouts interfere with ownership scans.
- [ ] Key task: P05.02 Compile affected Python, run the existing EBNF, reference, authoring, and example generators through their owning entry points, then run `python -m build.examples` and `python build/examples.py`.
- [ ] Key task: P05.03 Repeat generation, compare complete manifests and Git diffs, inspect every allowed content change, and verify the new root contains only the agreed generated products.
- [ ] Key task: P05.04 Search for obsolete paths and sources again, distinguish live references from preserved historical text, verify any repaired navigational links, and review scope, portability, size, and security requirements independently of the generation code.
Success criteria: E01 through E05 are verified on the final candidate with recorded commands, environment, exit codes, manifests, size measurements, and diff review; repeated generation leaves no diff and required checks pass without weakening their contracts.
Transition trigger: Final-candidate evidence is complete and all review findings are resolved; otherwise keep the failed tasks open.

### Phase 6: Record and deliver the implementation
Objective: Deliver the completed change without overstating verification or altering history.
- [ ] Key task: P06.01 Add `report.md` with the baseline and delivered revision, source/destination map, observations for E01 through E05, check evidence, limitations, changed paths, and final review verdict.
- [ ] Key task: P06.02 Tick each task only after its success criteria are met, commit implementation and evidence with compliant subjects, preserve every original commit, and verify the remote branch contains the reviewed candidate.
- [ ] Key task: P06.03 After user-authorised delivery, create the pull request into `main` with the final layout and verification summary; do not merge without a separate explicit merge request.
Success criteria: The report and pull request identify the verified E01 through E05 result, every applicable execution checkbox is supported by evidence, and repository history is preserved.
Transition trigger: The completed implementation is available for review; merging remains a separate user decision.

### Coordinating Instructions
- Timeline: Complete only plan creation now. Start the ordered implementation after explicit approval, and finish all accepted scope before requesting review; no background work or time estimate is implied.
- Boundaries: Preserve OAK semantics and public model APIs. Move product locations, their source ownership where necessary, active references, and checks together; do not add another framework, registry, prompt family, or documentation index.
- Operating guidelines: Keep the accepted names and flat layout. A generated file is a delivery, not source authority. Use current scoped contracts and existing dependencies; read required Python-topic and specialist material before implementation involving them.
- Risk mitigation: Preserve historical path snapshots and literal examples. Repair active navigation with appropriate current or revision-pinned destinations, not wholesale history rewriting. Do not increase byte limits, relax validator identity, or enable downloads merely to make checks pass.

### Contingencies
- If `main` advances before implementation, then merge it into the work branch as needed, preserve commit identities and this allocated plan directory, and record any baseline differences before continuing.
- If another maintained input is found inside a delivery directory, then give it a source owner outside `generated/` in the same migration and extend the generation and corruption checks before removing its old path.
- If a changed location string affects the byte budget, then account for the exact generated differences and preserve the limit and knowledge; escalate a genuinely incompatible requirement rather than silently deleting content or widening the limit.
- If validator package or dependency inputs change, then follow the existing immutable revision and fingerprint policy, record the necessity, and never accept a new identity on a version string alone.
- If an external consumer requires an old path, then obtain an explicit compatibility decision; do not create aliases speculatively.
- If verification is unavailable or fails, then record the exact limitation or failure, leave affected tasks open, and do not report implementation complete.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Pinned repository baseline | One commit | GitHub commit `2a3ba6c27b6110de4ace334e51d2f195a7ded522` | AVAILABLE |
| Work branch | One branch | `docs/plan-generated-products` | AVAILABLE |
| Source contracts and plan schema | Applicable documents | Root and scoped AGENTS documents plus SMEAC schema | AVAILABLE |
| Existing generators and checks | Existing build entry points | Repository `build/` and `examples/` | AVAILABLE |
| Implementation approval | One explicit user instruction | Repository owner | PENDING |
| Isolated checkout and Python environment | One disposable verification setup | Implementation execution environment | PENDING |
| Verification evidence | One final-candidate evidence set | This plan's `evidence/` and `report.md`, created during implementation | PENDING |

Supply: Use the repository's declared dependencies and existing generators. No live model service, extra dependency, or automatic optional-validator installation is required by this layout change.
Transportation: Deliver the grammar, reference, standalone agent, and skill through their new Git-tracked paths. Preserve relative skill paths so copying the skill directory does not require copying its repository parents.
Sustainment: Keep generator ownership and source routing in source-owned guidance, enforce freshness and file-set checks, and retain the plan directory as the record of this accepted change.
Rollback: Make corrective or revert commits if implementation fails. Do not amend, squash, rebase, force-push, or remove original commits; perform deletion-based regeneration checks only in disposable snapshots.

## 5. Command and Signal

1. The repository owner approves implementation, any material change to the accepted architecture, and any eventual merge.
2. The implementing assistant or developer follows this plan on the work branch, records evidence, and does not self-authorise missing gates.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| User conversation | Chat | Approval, material findings, blockers, and delivery | At decisions and meaningful progress |
| Plan and supporting evidence | Git-tracked Markdown and evidence files | Preserve task state and final-candidate observations | As evidence is established |
| Pull request | GitHub | Review the completed implementation | After authorised implementation and verification |

Reporting: The planning response identifies the branch, committed plan, and not-started implementation status. It does not claim repository checks ran. The implementation report links every required comparison to observed verification and separates successful checks, failures, and checks not performed.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Commit this plan on a new branch | User's planning request | Repository owner |
| Begin implementation | Explicit subsequent user approval | Repository owner |
| Change agreed layout, semantics, limits, or compatibility scope | Repository owner | Stop the affected work and present the conflict |
| Mark tasks complete | Implementer with recorded passing evidence | Reviewer or repository owner |
| Open the delivery pull request | User-authorised implementation and delivery | Repository owner |
| Merge or delete branch references | Separate user request and root history rules | Repository owner |

### Acknowledgement
The user requested this plan for the discussed layout on 2026-09-06. The plan is ready for review and execution after approval; no implementation, completion verdict, pull request, or merge approval is inferred from its creation.
