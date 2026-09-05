# Modular Python conventions in OAK

Prepared: 2026-09-05T12:31:36Z
Classification: PUBLIC

## 1. Situation

### Operating Environment
OAK stores repository knowledge in scoped OAK documents. This change belongs to the existing improve/python-code-conventions branch and concerns the user's general Python standard, not the Pydantic reference.

### Current State
Main at 21c2dc5b9366068875709e1cefab3a942f51836c adds .agents/rules/coding-standards.md, a 1,393-line standard covering 18 numbered sections. Earlier conversational suggestions relied on four OAK-specific example-authoring rules and therefore mischaracterised the general standard.

### Challenges
- Preservation: Splitting the source must retain every requirement, exception, checklist item, and teaching example.
- Scope: General defaults must not override established OAK contracts or introduce a repository-wide cosmetic refactor.
- Verification: Local GitHub networking is unavailable; a read-only branch workflow supplied a pinned baseline archive whose Git tree matches main.

### Supporting Factors
- Higher intent: Make the user's actual preferences portable, inspectable, and enforceable without duplicating policy.
- Adjacent efforts: Existing scoped AGENTS ownership, example catalogue, and complete repository verification remain authoritative.
- Supporting resources: Canonical OAK models, parser, renderer, resolver, source archive, and GitHub CI.

### Assumptions
- The user authorises implementation and modularisation in this branch; no merge is authorised.
- The newly tracked document supersedes the earlier inference about the user's general style.

### Constraints and Limitations
- Constraint: Preserve precedence, supported public behaviour, 120-character fallback width, small horizontal signatures, private-name conventions, and rare terse comments.
- Constraint: Author the resulting standards as pure OAK, with no Markdown rule bodies, Python knowledge generator, or duplicated monolith.
- Constraint: Keep the Pydantic skill and unrelated runtime architecture unchanged.
- Limitation: Passing structural checks does not prove subjective style compliance or execution of illustrative code snippets.

## 2. Mission

The assistant replaces the monolithic Python standard with modular OAK knowledge and verifies the completed branch during this task.

Task: Reassess the accepted suggestions against the actual standard, migrate the complete knowledge, connect repository routing and verification, and open a reviewable pull request.
Purpose: Preserve the user's compact, fully typed, data-oriented style while making ownership and review clearer.
End state: One OAK entry document routes to focused OAK modules; coverage evidence accounts for the original standard; verification passes; the branch is ready for review.

## 3. Execution

Intent: Preserve meaning before improving presentation. Retain existing preferences and add only refinements that survive comparison with the full standard.
Concept of operations: Inventory the authoritative source, migrate its knowledge into concern-specific OAK owners, then verify coverage, rendering, routing, and repository behaviour. Keep operational history separate from current policy.

### Phase 1: Establish the corrected baseline
Objective: Replace the earlier inferred standard with the complete tracked source.
- [ ] Key task: P01.01 Read the root and applicable scoped instructions plus the complete coding standard.
- [ ] Key task: P01.02 Fast-forward the conventions branch to the tracked-standard commit and verify the baseline archive tree.
- [ ] Key task: P01.03 Inventory every source section, code example, table, and checklist item; record retained, refined, and withdrawn suggestions.
Success criteria: Baseline revision and complete source coverage are recorded without treating OAK example rules as the general Python standard.
Transition trigger: The inventory and corrected interpretation are ready.

### Phase 2: Migrate the knowledge and integrations
Objective: Deliver one concern per OAK module with explicit routing and no parallel prose owner.
- [ ] Key task: P02.01 Replace coding-standards.md with a pure OAK entry and move its policy and teaching into focused OAK documents.
- [ ] Key task: P02.02 Preserve all original requirements and examples in structured OAK values; record exact source-to-destination coverage.
- [ ] Key task: P02.03 Add focused refinements for literal whitespace, operation snapshots, diagnostic separation, and independent expectations; retain small horizontal signatures.
- [ ] Key task: P02.04 Route Python work from root AGENTS and reconcile OAK-specific authoring rules without applying a blanket Pydantic or compatibility policy.
- [ ] Key task: P02.05 Integrate canonical, graph, routing, coverage, and rejection checks into the existing complete verification entry point.
Success criteria: The standards are maintained directly as OAK; examples and general Python rules remain distinct; no unrelated runtime change is present.
Transition trigger: The complete candidate is ready for verification.

### Phase 3: Verify and deliver
Objective: Demonstrate preservation and report only observed checks.
- [ ] Key task: P03.01 Validate every OAK document, both groupings, explicit dependency closure, examples, and negative cases.
- [ ] Key task: P03.02 Run compilation, both complete verification commands, regeneration, and repeated freshness checks; distinguish unavailable checks.
- [ ] Key task: P03.03 Inspect the complete diff and source coverage; remove the temporary snapshot workflow and any obsolete or duplicate policy.
- [ ] Key task: P03.04 Commit the completed candidate, open a pull request, inspect CI, and record the final result and any limitations.
Success criteria: Every applicable check is supported by observed evidence and the branch is ready for user review without merging main.
Transition trigger: The completion report and pull request are delivered.

### Coordinating Instructions
- Timeline: Complete the accepted change in this task.
- Boundaries: .agents/rules, routing owners, relevant verification, and this plan's records.
- Operating guidelines: Use existing OAK forms and existing dependencies; preserve unsupported illustrative snippets as labelled teaching rather than claiming they ran.
- Risk mitigation: Compare migrated source units and code literals against the pinned original; test rejected missing, duplicated, and escaping references.

### Contingencies
- If a proposed refinement conflicts with the full standard then preserve the standard and record the withdrawn suggestion.
- If local verification is constrained then record the exact limitation and use branch CI for independent evidence.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Canonical standard | 1 | Main commit 21c2dc5 | AVAILABLE |
| Pinned source archive | 1 | Read-only GitHub Actions artifact | AVAILABLE |
| OAK validation runtime | 1 | Verified baseline source and installed dependencies | AVAILABLE |
| Branch CI | 1 | Existing verification workflow | AVAILABLE |

Supply: Use existing dependencies. Do not add a formatter, type checker, or test framework just for this migration.
Transportation: Commit changes through the GitHub connector to the conventions branch.
Sustainment: Keep future edits in the owning OAK modules and verify them through the existing repository check registry.
Rollback: Revert the task commits on the branch. The original standard remains available at its pinned Git revision.

## 5. Command and Signal

1. User: owns preferences, scope changes, and merge approval.
2. Assistant: implements the accepted migration and reports evidence.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Conversation | Chat | Corrections and completion | Material milestones |
| Review | Pull request | Diff and CI evidence | Final candidate |

Reporting: Record source coverage, accepted refinements, withdrawn suggestions, verification results, and final review status in report.md and evidence.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Preserve the actual standard | User instruction | User |
| Implement the modular migration | Assistant | User on a genuine conflict |
| Merge to main | User | User |

### Acknowledgement
The user authorised the branch work and identified the canonical source. The assistant has read the source and accepts the preservation and verification gates.
