# Reorganise the OAK authoring skill

Prepared: 2026-09-06T02:46:56Z
Classification: INTERNAL
Readiness: Execution authorised by the user on 2026-09-06.
Execution: In progress.

## 1. Situation

### Operating Environment
The repository generates a portable authoring skill and a standalone authoring agent from shared OAK knowledge. This plan records the directory layout and generic skill template agreed with the user.

### Current State
The product at `skills/oak-authoring` has one entry, numbered references containing both language knowledge and practical guidance, teaching scenarios beneath `references/examples`, and an optional validator. It has no template directory. The baseline is commit `68aab91e7b4c807b91865642c3e9b2fec60956a0`; the working branch also contains the verified SMEAC and repository naming updates prepared before this plan.

### Challenges
- Generated paths: Guide bindings, the example catalogue, cleanup logic, and exact file-set checks currently assume the old locations.
- Operational scope: Template placeholders and example processes must remain inert when the authoring agent is assembled.
- Literal formatting: The approved tree notation must preserve its arrow, colon, and indentation exactly.
- Size budget: The standalone agent currently uses 63,943 of 64,000 bytes. Its new template knowledge requires recovering space from redundant representation while preserving the required content and behaviour. The skill entry uses 8,299 of 10,000 bytes.

### Supporting Factors
- Higher intent: Make the skill easy to navigate and provide a reusable OAK skill skeleton.
- Adjacent efforts: SMEAC now supports paired current and desired states; repository rules define shared change types and preserve commit history.
- Supporting resources: Existing generators, scenario sources, fusion checks, optional validator, and the local Python 3.11 environment.

### Assumptions
- The accepted layout comparisons below define the product outcome.
- The existing OAK language and runtime can represent the required knowledge; this change does not require a new syntax or runtime capability.
- The template provides placeholders for a future skill's purpose and content. It does not ship a completed domain skill.

### Constraints and Limitations
- Constraint: Change source owners and regenerate their outputs in one complete delivery.
- Constraint: Keep the authoring entry as the only operational scope of the assembled authoring capability. Supporting fusion documents contain constants and schemas only.
- Constraint: Preserve the complete teaching scenarios, shared skill and agent knowledge, validator consent rules, and verified runtime identity.
- Constraint: Use the root naming and commit-history rules for any subsequent repository actions.
- Constraint: Keep repository-development support separate from the distributable skill. Do not add directory README indexes or platform-specific packaging.
- Limitation: The live checkout's ignored `personal-examples/fabric-cli-source/AGENTS.md` trips the repository-owned AGENTS inventory check. Use an isolated copy of tracked files plus this task's new files for complete verification, and confirm it matches the deliverable.

## 2. Mission

Implement the agreed OAK skill layout and generic template in this repository once the user authorises execution, so the skill presents its knowledge clearly and supplies a reusable starting point.

Task: Reorganise the generated skill, add its generic template, update all consumers and checks, and verify both delivered forms.
Purpose: Preserve the user's intended structure and exact layout notation in a reviewable, reusable skill package.
End state: The delivered file tree matches E01, the generic scaffold meets E02, and its layout block matches E03. Generated files, the standalone agent, and verification agree with their source owners.

### State Comparisons

#### E01: Complete skill directory layout
Authority: required
Current state:
The existing delivered files are:

```text
oak-authoring/
  SKILL.md
  references/
    00-structure.oak.md
    01-schemas.oak.md
    02-constants.oak.md
    03-state.oak.md
    04-interfaces.oak.md
    05-triggers.oak.md
    06-processes.oak.md
    07-instructions.oak.md
    08-review.oak.md
    09-validation.oak.md
    10-oak.ebnf
    examples/
      catalog.oak.md
      fixed_knowledge/
        example.oak.md
      shape_gallery/
        example.oak.md
      shape_writer/
        example.oak.md
        sample.oak.md
        shape_gallery.oak.md
      compound_growth/
        example.oak.md
        sample.oak.md
  scripts/
    validate.py
```

Desired state:

```text
oak-authoring/
  SKILL.md
  references/
    00-structure.oak.md
    01-schemas.oak.md
    02-constants.oak.md
    03-state.oak.md
    04-interfaces.oak.md
    05-triggers.oak.md
    06-processes.oak.md
    07-instructions.oak.md
    oak.ebnf
  guides/
    authoring.oak.md
    review.oak.md
    validation.oak.md
  assets/
    examples/
      catalog.oak.md
      fixed_knowledge/
        example.oak.md
      shape_gallery/
        example.oak.md
      shape_writer/
        example.oak.md
        sample.oak.md
        shape_gallery.oak.md
      compound_growth/
        example.oak.md
        sample.oak.md
  _template/
    SKILL.md
    references/
    assets/
      constants/
      schemas/
    guides/
    processes/
    scripts/
  scripts/
    validate.py
```

Acceptance: Match these paths and directory relationships. Retain intended empty template directories with `.gitkeep` files, omitted from the displayed tree. Exclude runtime caches from the product inventory. Remove the old review, validation, grammar, and teaching delivery paths rather than leaving aliases. Verify exact generated file sets and complete scenario document closure.

#### E02: Generic OAK skill skeleton
Authority: required
Current state:
No `_template` directory or generic OAK skill entry is delivered. The current `SKILL.md` implements OAK authoring itself.

Desired state:
`_template/SKILL.md` supplies skill metadata placeholders, a short purpose or overview, and OAK structure to fill in for a future skill. Its supporting directory skeleton is the one shown in E01. The template contains no completed task implementation, fixed domain, or inherited identity from the authoring skill. Its use explains how to fill placeholders and omit parts or resources the eventual task does not need.

Acceptance: Inspect the template as a reusable scaffold. Supply only the required metadata and useful placeholder structure. Keep its supporting folders empty except for `.gitkeep`. Verify that a temporary populated fixture can be parsed and resolved after removing its skill metadata, without shipping that fixture as a completed example skill. Treat the unfilled template as inert material rather than an executable authoring document.

#### E03: Compact layout notation
Authority: required
Current state:
The OAK package has no generic template layout block. The legacy template used as the design reference lists references separately and describes the layout using a heading and bullet points; it is a reference for organisation, not OAK source authority.

Desired state:

```text
SKILL_TREE:
  SKILL.md→Skill entry point
  references/→Supporting knowledge
  assets/
    constants/→Reusable fixed values
    schemas/→Reusable information shapes
  processes/→OAK workflows
  guides/→Practical guidance
  scripts/→Executable helpers
```

Acceptance: Preserve this block in the generic template. Require the uppercase label and colon, the literal U+2192 arrow with no surrounding whitespace, two spaces per indentation level, and the supplied descriptions. Use no bullets or separate References index. The `references/` directory still appears once in the tree. Carry the exact block as literal OAK text knowledge so a completed skill entry remains OAK beneath its metadata; treat its paths as displayed knowledge rather than implicit imports.

## 3. Execution

Intent: Deliver the accepted layout without inventing a completed domain skill or changing OAK's execution boundaries. Keep each fact in its source owner and preserve the exact examples that define completion.
Concept of operations: Update the owning contracts and generated knowledge organisation, add the generic template, then regenerate and verify the complete delivery. These phases are checkpoints within one change, not deferred product releases.

### Phase 1: Reorganise the generated knowledge
Objective: Establish the source mapping and delivery locations required by the new layout.
- [ ] Key task: P01.01 Update `skills/AGENTS.md` with the accepted directory ownership, generic scaffold requirement, and purposeful empty template directories.
- [ ] Key task: P01.02 Update `build/authoring_guides.py` and `build/authoring.py` so references own language knowledge and `guides` owns practical authoring, review, and validation guidance, with one owner per claim.
- [ ] Key task: P01.03 Update `examples/catalog.py` and every current consumer for the teaching delivery beneath `assets/examples`; preserve complete scenario content and local dependencies.
Success criteria: Source mappings account for E01, every changed document reference resolves, and the shared rule inventory has no missing or duplicated claims.
Transition trigger: The new generated document graph and exact delivery inventory are ready for the template addition.

### Phase 2: Deliver the generic template
Objective: Generate the reusable skeleton and its compact layout description.
- [ ] Key task: P02.01 Author the template from the existing build owners, including its metadata placeholders, OAK body scaffold, and intentional `.gitkeep` entries.
- [ ] Key task: P02.02 Recover space from redundant wording or representation, then include the template's exact inert knowledge in the guides shared by the skill and standalone agent; keep template and teaching operational documents outside the fusion input graph.
- [ ] Key task: P02.03 Route template use from the authoring entry, preserve conditional validation, and update the skill product version consistently while retaining the validator identity unless its runtime actually changes.
Success criteria: The template meets E02 and E03, its files occupy the E01 locations, and both delivered forms carry identical template knowledge without acquiring extra operational scope.
Transition trigger: The complete candidate can be generated from its source owners.

### Phase 3: Verify and close the change
Objective: Prove the delivered package matches the accepted comparisons and repository contracts.
- [ ] Key task: P03.01 Extend `build/checks/authoring.py` to validate the complete new file set, deliberate scaffold placeholders, exact tree notation, template population, and skill-agent knowledge parity.
- [ ] Key task: P03.02 Update generation cleanup for all owned delivery locations; remove stale outputs and current references to replaced paths, preserving historical plan records.
- [ ] Key task: P03.03 Regenerate all affected products, compile the changed Python, and run both complete verification entry points using the existing Python 3.11 environment.
- [ ] Key task: P03.04 Confirm repeated generation changes no files, inspect the final diff, and write `report.md` with observed results for each required comparison.
Success criteria: E01, E02, and E03 pass their stated checks. Complete verification, detached examples, fusion scope, validator consent and identity, output size limits, and freshness pass. The tested copy matches the delivered working files.
Transition trigger: All tasks pass and the completion report records the verified outcome.

### Coordinating Instructions
- Timeline: Begin implementation after the user's execution instruction; complete all phases in the same delivery.
- Boundaries: This plan covers the portable authoring package, its shared agent, source owners, checks, and governing skill knowledge. The template's `processes/` folder is inert scaffolding and does not introduce another operational scope into the authoring capability.
- Operating guidelines: Follow the root naming and history contracts. Keep exact examples stable while the work is in progress; record any user-approved changes explicitly.
- Risk mitigation: Use exact path and byte comparisons, bounded document closure, literal preservation checks, and a temporary populated template fixture.

### Contingencies
- If a template representation fails parsing after population, revise the template's OAK representation while retaining the accepted literal block and folder structure.
- If the candidate exceeds a product size limit, remove duplicated material while preserving the applicable contracts. If the required content still cannot fit, present the measured constraint for a user decision before changing a limit.
- If a required source or contract changes during work, refresh the affected baseline and validate the complete candidate before accepting it.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Knowledge and delivery generators | Existing owners | `build/authoring_guides.py`, `build/authoring.py`, `build/fusion.py` | AVAILABLE |
| Teaching catalogue and scenarios | Existing shared core | `examples/catalog.py` and its registered sources | AVAILABLE |
| Verification and regeneration | Existing commands | `build/AGENTS.md` | AVAILABLE |
| Python environment | Python 3.11.9 | `.venv/Scripts/python.exe` | AVAILABLE |

Supply: Use existing dependencies and source owners. No package installation is needed to prepare or implement this layout.
Transportation: Generate the skill files and standalone output from the same declared knowledge. Keep the plan and its eventual report in this numbered directory.
Sustainment: Re-run relevant checks as changes occur and the complete required verification before delivery. Preserve the original user comparisons in this plan.
Rollback: Restore generated files through their owners. If a change has been committed, correct or revert it with an additional commit while preserving the original history.

## 5. Command and Signal

1. User: Owns the accepted product intent and the instruction to begin implementation.
2. Repository assistant: Implements and verifies within the accepted scope, reporting conflicts or missing evidence.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Working discussion | Task conversation | Decisions, material findings, and progress | During active work |
| Persistent record | This plan and the eventual report | Task state and verification evidence | On meaningful progress and completion |

Reporting: Keep execution checkboxes accurate. The completion report records the outcome, tests, E01 through E03 results, changed paths, and final verdict; desired specimens alone do not count as observed evidence.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Start product implementation | User | Keep the validated plan ready until instructed |
| Routine implementation within the accepted examples | Repository assistant | Report a conflict with the accepted outcome |
| Change the accepted layout or formatting | User | Present the concrete proposed change before applying it |

### Acknowledgement
The user's accepted directory, scaffold, and formatting decisions are recorded above. The user instructed execution and PR delivery on 2026-09-06. The executing assistant has read this plan and the applicable owning AGENTS documents.
