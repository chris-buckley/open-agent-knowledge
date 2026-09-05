# Modular Python conventions in OAK

Prepared: 2026-09-05T12:31:36Z
Classification: PUBLIC

## 1. Situation

### Operating Environment
OAK stores repository knowledge in scoped OAK documents. This change belongs to improve/python-code-conventions and concerns the user's general Python standard, not the Pydantic reference.

### Current State
Main at 21c2dc5b9366068875709e1cefab3a942f51836c adds .agents/rules/coding-standards.md, a 1,393-line standard with 18 numbered sections. Earlier suggestions relied on four OAK-specific example-authoring rules and mischaracterised the general standard.

### Challenges
- Preservation: Retain every requirement, exception, checklist item, and teaching example.
- Scope: General defaults must not override established OAK contracts or introduce a repository-wide cosmetic refactor.
- Verification: A read-only branch workflow supplied a pinned archive; its reconstructed Git tree matches the baseline exactly.

### Supporting Factors
- Higher intent: Make the actual preferences portable and inspectable without a parallel prose owner.
- Adjacent efforts: Preserve scoped AGENTS ownership, the example catalogue, and complete verification.
- Supporting resources: Canonical OAK models, parser, renderer, resolver, source archive, and GitHub CI.

### Assumptions
- The user authorises implementation and modularisation; no merge is authorised.
- The newly tracked standard supersedes the earlier inference about general Python style.

### Constraints and Limitations
- Constraint: Preserve precedence, supported public behaviour, the 120-character fallback width, horizontal signatures, private-name conventions, and rare terse comments.
- Constraint: Maintain the standards directly as pure OAK, not a Python knowledge generator or duplicated monolith.
- Constraint: Keep the Pydantic skill and unrelated runtime architecture unchanged.
- Limitation: Structural checks do not prove subjective style compliance or execution of illustrative snippets.

## 2. Mission

The assistant replaces the monolithic Python standard with modular OAK knowledge and verifies the completed branch during this task.

Task: Reassess the accepted suggestions, migrate the complete knowledge, connect routing and verification, and open a pull request.
Purpose: Preserve compact, fully typed, data-oriented Python while clarifying ownership and review.
End state: One OAK entry routes to focused modules; coverage evidence accounts for the original; the verified branch is ready for review.

## 3. Execution

Intent: Preserve meaning before improving presentation. Add only refinements that survive comparison with the full standard.
Concept of operations: Inventory the source, migrate concern-specific knowledge, and verify coverage, rendering, routing, and repository behaviour. Keep history separate from current policy.

### Phase 1: Establish the corrected baseline
Objective: Replace the earlier inferred standard with the complete tracked source.
- [x] Key task: P01.01 Read the root and applicable scoped instructions plus the complete coding standard.
- [x] Key task: P01.02 Fast-forward the branch to the tracked-standard commit and verify the archive tree.
- [x] Key task: P01.03 Inventory all source sections, examples, tables, and checklist items; reassess earlier suggestions.
Success criteria: The baseline and complete coverage are recorded without conflating OAK authoring with general Python preferences.
Transition trigger: The inventory and corrected interpretation are ready.

### Phase 2: Migrate the knowledge and integrations
Objective: Deliver one concern per OAK module with explicit routing and no parallel prose owner.
- [x] Key task: P02.01 Replace coding-standards.md with a pure OAK entry and focused topic documents.
- [x] Key task: P02.02 Preserve all original requirements and examples; record source-to-destination coverage.
- [x] Key task: P02.03 Add exact-whitespace, operation-snapshot, diagnostic, typing, and independent-expectation refinements.
- [x] Key task: P02.04 Route Python work from root AGENTS and reconcile OAK-specific authoring rules.
- [x] Key task: P02.05 Add canonical, graph, routing, coverage, and rejection checks to the existing entry point.
Success criteria: OAK is the maintained source; general and OAK-specific rules remain distinct; runtime behaviour is unchanged.
Transition trigger: The complete candidate is ready for verification.

### Phase 3: Verify and deliver
Objective: Demonstrate preservation and report only observed checks.
- [x] Key task: P03.01 Validate every OAK document, both groupings, dependency closure, teaching shapes, and rejected cases.
- [x] Key task: P03.02 Run compilation, both complete commands, regeneration, and repeated freshness checks.
- [ ] Key task: P03.03 Inspect the diff and source coverage; remove the temporary workflow and obsolete policy.
- [ ] Key task: P03.04 Commit the candidate, open a pull request, inspect CI, and record the result and limitations.
Success criteria: Each applicable check has observed evidence; the branch is reviewable without merging main.
Transition trigger: The completion report and pull request are delivered.

### Coordinating Instructions
- Timeline: Complete the accepted change in this task.
- Boundaries: .agents/rules, routing owners, verification, and this plan's records.
- Operating guidelines: Reuse existing dependencies and OAK forms; label excerpts honestly.
- Risk mitigation: Compare source units and code literals with the pinned original, and reject missing, duplicated, or escaping references.

### Contingencies
- If a proposal conflicts with the full standard then preserve the standard and record the withdrawn proposal.
- If a verification command cannot run then record the limitation instead of claiming it passed.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Canonical standard | 1 | Main commit 21c2dc5 | AVAILABLE |
| Verified baseline archive | 1 | GitHub Actions artifact | AVAILABLE |
| OAK runtime and checks | 1 | Verified source | AVAILABLE |
| Pull-request CI | 1 | Existing workflow | AVAILABLE |

Supply: Use installed repository dependencies; add no new checker or formatter package.
Transportation: Commit through the GitHub connector to the conventions branch.
Sustainment: Edit owning OAK modules and verify through the existing check registry.
Rollback: Revert task commits. The original remains available at the pinned Git revision.

## 5. Command and Signal

1. User: owns preferences, scope changes, and merge approval.
2. Assistant: implements the accepted migration and reports evidence.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Conversation | Chat | Corrections and completion | Material milestones |
| Review | Pull request | Diff and CI | Final candidate |

Reporting: Record coverage, retained and withdrawn suggestions, observed checks, and limitations in report.md and evidence.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Preserve actual preferences | User instruction | User |
| Implement the migration | Assistant | User on genuine conflict |
| Merge main | User | User |

### Acknowledgement
The user authorised the work and identified the source. The assistant has read it and accepts the preservation and verification gates.
