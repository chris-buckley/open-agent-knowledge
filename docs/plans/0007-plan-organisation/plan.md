# Plan organisation and default SMEAC authoring

Prepared: 2026-09-05T14:58:48+10:00
Classification: PUBLIC

## 1. Situation

### Operating Environment
OAK stores persistent implementation plans and completion reports under docs/plans. The root router selects scoped AGENTS documents, and the build runs the repository verification checks.

### Current State
The baseline is main at f2343dacc62764379c105801ce90218f33989228. Seven plan/report pairs use flat numeric filenames. SMEAC is documented for new plans, but the build does not check the structure of populated plans.

### Challenges
- Navigation: numeric filenames hide the topic and separate related records in a flat listing.
- History: six plans predate SMEAC and must retain their recorded content and formats.
- Enforcement: new saved plans need an explicit creation route and structural verification.

### Supporting Factors
- Higher intent: make plans easy to find and consistently structured for people and agents.
- Adjacent efforts: the compact SMEAC checkbox phase layout is already available.
- Supporting resources: the existing schema, scoped guidance, Git history, Python environment, and complete build checks.

### Assumptions
- Each existing numeric identifier remains stable during the move.
- The existing report records remain historical evidence after relocation.
- Conversational planning does not require a saved plan directory.

### Constraints and Limitations
- Constraint: implement the approved directory design and push directly to main after verification.
- Constraint: preserve historical claims and recorded path snapshots; repair navigational references.
- Constraint: create no README index, duplicate SMEAC template, or empty evidence directory.
- Limitation: structural checks can verify layout and task identifiers, not the quality or truth of a plan's claims.

## 2. Mission

Organise the repository's plans into stable named directories and enforce SMEAC for new saved plans so people and agents can find, author, and verify them consistently.

Task: migrate all seven plan/report pairs, route plan creation, and add repository checks for the approved structure.
Purpose: improve navigation and make the default plan format dependable.
End state: every pair shares a named directory; current and future SMEAC plans pass structural checks; the six earlier formats remain intact; the verified change is ready for the authorised direct push to main.

## 3. Execution

Intent: keep storage rules in docs/AGENTS.md, phase presentation in the existing SMEAC schema, and verification in build. Use one numeric identity and topic per directory.
Concept of operations: record the policy, relocate the existing records, implement focused structural checks, and verify the full publishing candidate before committing and pushing it.

### Phase 1: Organise the records
Objective: put each plan and report in one stable named directory without rewriting history.
- [x] Key task: P01.01 Record the approved storage rules and root planning route in their owning AGENTS documents.
- [x] Key task: P01.02 Move the seven existing pairs into directories named from their identifiers and topics.
- [x] Key task: P01.03 Repair navigational references and compare the moved records with the baseline.
Success criteria: all fourteen records are present at their intended destinations and differ only where navigation requires an updated reference; the diff and comparisons provide evidence.
Transition trigger: the migrated records and governing policy are ready for structural verification.

### Phase 2: Enforce the default
Objective: verify named plan directories and populated SMEAC plans through the complete build.
- [x] Key task: P02.01 Check unique numeric directory identities, required plan files, optional reports, and evidence placement.
- [x] Key task: P02.02 Derive required section order and phase labels from the existing SMEAC schema and check compact checkbox tasks with unique stable identifiers.
- [x] Key task: P02.03 Preserve the six explicitly named historical format exceptions and exercise accepted and rejected plan structures.
Success criteria: focused checks accept the migrated records and reject malformed layouts, missing sections, and invalid task structure with actionable errors.
Transition trigger: plan verification is registered in the repository's normal check sequence.

### Phase 3: Verify the publishing candidate
Objective: produce a reviewed change and completion evidence for the authorised push.
- [x] Key task: P03.01 Compile the affected sources, regenerate products, and pass both complete verification entry points in a clean checkout.
- [x] Key task: P03.02 Confirm repeated generation is byte-identical and search for obsolete live plan references.
- [x] Key task: P03.03 Review the final diff and record the outcome, migration mapping, and observed verification in report.md.
Success criteria: the complete checks and generation comparison pass, historical preservation is verified, and the report describes observed results without inventing a future commit hash.
Transition trigger: the reviewed candidate is ready for the user's authorised direct commit and push to main.

### Coordinating Instructions
- Timeline: complete the migration, checks, verification, and publication in this task.
- Boundaries: plan storage, scoped planning guidance, build verification, and affected navigation.
- Operating guidelines: preserve unrelated local and ignored material; use a clean temporary checkout when local material affects repository discovery.
- Risk mitigation: compare moved records to the baseline and test failure cases for the new structural checks.

### Contingencies
- If the remote main branch advances, integrate the new tip and revalidate any affected candidate before pushing.
- If a structural check conflicts with a preserved historical record, apply the explicit historical format policy instead of rewriting the record.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Historical records | 14 files | Existing docs/plans records | AVAILABLE |
| SMEAC schema | One canonical schema | examples/schemas/smeac_plan.oak.md | AVAILABLE |
| Python runtime | One existing environment | Repository .venv | AVAILABLE |

Supply: use existing dependencies and repository check infrastructure.
Transportation: relocate tracked records within docs/plans and publish through the existing origin remote.
Sustainment: keep the plan rules and verification in their current scoped owners.
Rollback: use Git history to reverse the migration and its governing changes if required.

## 5. Command and Signal

1. The user owns the accepted layout and publication authority.
2. The implementation assistant executes the approved change and reports verification results.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Task conversation | Codex messages | Report material progress and the final commit | During work and at completion |
| Plan and report | Markdown files in this directory | Record intended work and observed results | As evidence becomes available |

Reporting: provide the direct main commit and plan-directory link after the push, with the verification outcome.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Directory layout and SMEAC default | User approval in this conversation | User for material scope changes |
| Direct push to main | Explicit user request in this conversation | User if an external policy blocks the push |

### Acknowledgement
The user approved the proposed structure and explicitly requested implementation and a direct push to main. The assistant acknowledges that scope and authority.
