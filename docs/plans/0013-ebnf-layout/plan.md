# Improve OAK EBNF layout

Prepared: 2026-09-06T17:23:33+10:00
Classification: PUBLIC
Status: Complete. All 29 tasks are evidenced and checked; PR #19 is open for review.
Delivery: [PR #19](https://github.com/chris-buckley/open-agent-knowledge/pull/19). See [report](report.md) and [independent review](evidence/independent-review.md).
Authorisation: The user explicitly authorised end-to-end implementation and a review-ready pull request into main on 2026-09-06T17:53:49+10:00. Merge into main is not authorised.
Repository: chris-buckley/open-agent-knowledge
Branch: docs/plan-ebnf-layout
Destination: main
Inspected baseline: bf0975dd7959320fd6727cee926370eca1808e07
Plan format: [SMEAC planning brief](../../../examples/schemas/smeac_plan.oak.md)

## 1. Situation

### Operating Environment
OAK publishes generated EBNF as syntax documentation for human and agent readers, not as validation authority. This change borrows the readable grouping, local alignment, and component-to-composition progression of the legacy APS grammar without importing APS language rules or changing OAK behaviour.

### Current State
The inspected main snapshot is bf0975dd7959320fd6727cee926370eca1808e07, and its newest plan directory is 0012-flat-python-authoring. The current grammar starts with document wrappers, continues through expressions and statements, inserts mixed explanatory notes, then appends constants, lexical rules, and surface descriptions. Its production definitions are assembled from package-owned syntax and vocabulary plus build-owned document scaffolding.

Observed source and delivery ownership:

| Path | Current responsibility | Treatment in this change |
| --- | --- | --- |
| [build/ebnf.py](../../../build/ebnf.py) | Assemble grammar text, grouping scaffolding, and outputs/oak.ebnf | Own the readable document organisation and presentation |
| [build/surfaces.py](../../../build/surfaces.py) | Project surface descriptors into grammar aliases or descriptive special sequences | Reuse the source projection; change only if presentation requires a narrow adapter |
| [oak/surface/syntax.py](../../../oak/surface/syntax.py) | Shared expression productions, conventions, surface aliases, and authored-layout constants | Preserve expression meaning and authored-layout constants; keep any necessary note organisation at its existing owner |
| [oak/vocabulary/text](../../../oak/vocabulary/text/value_reference.py) | Lexical productions and value-reference syntax | Consume the existing productions rather than copy or redesign them |
| [build/authoring.py](../../../build/authoring.py) | Generate the packaged grammar and assembled authoring agent | Regenerate affected products from the same grammar function |
| [build/authoring_guides.py](../../../build/authoring_guides.py) | Embed grammar in the structure guide as constant.oak-ebnf | Preserve this shared skill-agent knowledge path |
| [build/checks/__init__.py](../../../build/checks/__init__.py) | Register complete repository verification | Register focused EBNF presentation and preservation checks |
| [build/checks/plans.py](../../../build/checks/plans.py) | Check SMEAC structure, paired comparisons, and plan storage | Use the existing plan checks; do not change the plan format |
| [outputs/AGENTS.md](../../../outputs/AGENTS.md) | Generated-only output ownership | Do not patch generated files by hand |

The generated grammar occurs in four affected delivery paths: outputs/oak.ebnf, skills/oak-authoring/references/oak.ebnf, the grammar constant in skills/oak-authoring/references/00-structure.oak.md, and that same constant in outputs/oak-authoring.oak.md. At the inspected Git tree, the grammar file is 13,284 bytes and the standalone agent is 63,974 bytes. The existing standalone limit is 64,000 bytes, so increased grammar whitespace and commentary must be budgeted rather than treated as free.

Planning evidence: Root AGENTS.md, applicable scoped knowledge, the SMEAC schema, grammar sources, generator consumers, and the legacy grammar were inspected through the GitHub connector. No repository checks were run during plan preparation: the local checkout attempt failed because github.com could not be resolved. The implementation phases below must obtain and record actual execution evidence.

### Challenges
- Mixed levels of detail: Document wrappers, lexical rules, executable-looking productions, and descriptive templates are interleaved, which makes the reference difficult to scan.
- Accidental grammar changes: Splitting arbitrary text on commas, pipes, semicolons, or question marks can corrupt quoted terminals, nested expressions, regular-expression fragments, and special sequences.
- Embedded size pressure: The standalone agent has only 26 bytes of headroom at the inspected baseline. Decoration and global padding can exceed its existing limit.
- Existing descriptive gaps: Several surface productions are opaque special sequences, and constant_target has two existing definitions with different terminal segmentation. A layout change must not silently repair, remove, or reinterpret them.
- Freshness is not preservation: Regenerated snapshots can agree with an accidentally changed generator. Independent comparisons and existing parser, renderer, and execution checks are also required.

### Supporting Factors
- Higher intent: Make one compact, validated knowledge standard easier to author and inspect without creating another source of language meaning.
- Adjacent efforts: Main already contains the flat Python Statement/body authoring change. This plan preserves that API and the current OAK syntax rather than revisiting it.
- Supporting resources: Existing surface descriptors, expression grammar, vocabulary productions, model examples, both OAK groupings, generated-output checks, SMEAC comparisons, and the complete build verification entry points.

### Assumptions
- The accepted change concerns EBNF presentation, not a new OAK language version, a new validation authority, or APS compatibility.
- The implementation uses this branch and the inspected baseline. Any later destination-branch changes are integrated with a merge, then the baseline impact and plan-directory identity are rechecked.
- Existing grammar commentary can be made more concise at its source owner while preserving every claim. Production terminals and special-sequence bodies cannot be shortened to meet a size target.
- The existing repository environment and dependencies are sufficient. No new parsing framework, formatter dependency, task-specific data language, or installer is required.

### Constraints and Limitations
- Constraint: Read [root AGENTS.md](../../../AGENTS.md) and every applicable routed owner before implementation, including the Python standard and its applicable topic documents for Python changes.
- Constraint: Preserve OAK production names, alternatives and their order, repetition, optionality, punctuation terminals, token adjacency, special sequences, and the seven-part canonical order. Keep snake_case production names.
- Constraint: Preserve the grammar() and ebnf_text() callable contracts, supported grouping selections, caller-supplied grouping order, LF output, and one trailing newline.
- Constraint: Keep one generated reference with identical packaged bytes and shared embedded knowledge. Do not create a hand-maintained grammar, a compact second grammar, or independent skill and agent variants.
- Constraint: Keep EBNF as documentation. Do not change parser acceptance, model validation, runtime behaviour, JSON-LD representation, authoring examples, surface shapes, or authored OAK canonical formatting to improve the EBNF file.
- Constraint: Keep the 10,000-byte skill-entry and 64,000-byte standalone-agent limits. Do not raise limits, remove embedded grammar, strip teaching examples, or rewrite unrelated guidance to make room.
- Constraint: Treat APS as read-only legacy inspiration. Do not introduce its RUN, USE, CAPTURE, engine-defined expressions, naming conventions, or extension policy into OAK.
- Limitation: This is not a completeness audit or formal proof of the existing EBNF. Known baseline duplication and opaque grammar portions remain explicitly recorded, not newly endorsed as complete grammar.
- Limitation: Repository verification was not available during preparation. No unchecked implementation task or desired specimen below represents an observed passing result.

## 2. Mission

The implementation agent reorganises OAK's generated EBNF on docs/plan-ebnf-layout after explicit authorisation, preserving language meaning and all delivery contracts so readers can navigate it as clearly as the legacy APS reference.

Task: Deliver the complete presentation change, preservation checks, regenerated products, completion report, and reviewable pull request in one implementation effort before declaring completion.
Purpose: Improve readability through conceptual grouping and restrained formatting without making the language or its maintenance more complicated.
End state: One readable generated grammar has stable sections, locally aligned compact rules, vertically expanded long alternatives, and nearby qualified notes; every affected delivery is fresh, all preservation and repository checks pass, and no runtime or authored-language change is present.

### Accepted Design

Use one generated document with a short scope-and-notation preamble followed by six numbered sections: lexical tokens and whitespace; values, targets and bindings; conditions; part contents; XML and Markdown grouping; complete document. Within part contents, use the existing canonical order: instructions, constants, schemas, state, triggers, processes, interfaces. This is the order of a grammar reference, not a change to document or authoring order.

Keep organisation and formatting in build/ebnf.py. Use a small build-only helper module only if the formatting code needs a cohesive separate owner; do not introduce a general grammar parser or a second language model. Assemble source-derived production records with presentation metadata, not independent handwritten copies of their right-hand sides. Treat source-qualified occurrences distinctly so the existing repeated constant_target production is not overwritten in a dictionary keyed only by name.

Align equals signs within small adjacent groups of compact productions. Do not align the whole file to its longest name. Use a 100-code-point soft width for the EBNF presentation, independent of OAK's authored-expression width constant. For long alternatives, put the name and equals sign on their own line and put one alternative on each continuation line; preserve alternative order. Break long sequences only at safe outer grammar boundaries. Keep final semicolons on the final expression line and one blank line between related groups.

Preserve every byte inside quoted terminals and descriptive special sequences, including embedded indentation and the current escaped-question-mark convention. Do not parse or reflow an opaque lexical or regular-expression production merely to satisfy the soft width. Such lines are documented width exceptions. Grammar comments describe the reference and do not make comments legal in authored OAK.

Place each surface alias or descriptive surface production beside the construct it explains. Put schema constraints with schemas, condition surfaces with conditions, and statement surfaces with processes. Distinguish expanded productions from descriptive special sequences in nearby concise commentary; retain both kinds wherever they are currently referenced.

Move lexical conventions beside lexical rules, condition semantics beside conditions, trigger validation and canonical-order notes beside triggers, and suite and statement notes beside processes. Keep shared list-layout notes in one nearby home. Every existing commentary claim must retain one source owner and an identifiable location. Concise source-owned wording is permitted for size control, with a claim-by-claim preservation review; do not create a second paraphrase registry in the build layer.

Implementation refinement observed during execution: the optional validator fingerprints every Python byte under oak, including unused grammar commentary. Keep that package byte-identical rather than changing the validator identity or weakening its check. Emit the original convention wording verbatim where it carries additional meaning; avoid repeating seven claims already expressed by the existing productions. The evidence claim map identifies every retained prose location or exact structural counterpart. Build metadata only selects and places source contributions; it defines no replacement prose registry. This supersedes the tentative option to shorten package-owned commentary, not the language-preservation or four-delivery contracts.

The duplicate constant_target definitions and further expansion of opaque special sequences are out of scope. Preserve their current production content and multiplicity, record them as known baseline limitations, and reject new unexplained duplication. This avoids disguising a grammar-correction project as layout work.

### State Comparisons

#### E01: Component-to-composition reading order
Authority: required
Current state:
The following is a summary of the observed assembly order, not headings claimed to exist in the current file.
```text
Document entry and XML/Markdown wrappers
Body-entry wrappers
Conditions, values, bindings, triggers and statements
Mixed explanatory comment
Constants, state and basic text rules
Vocabulary and regular-expression rules
Appended surface aliases and descriptive templates
```
Desired state:
```text
Scope and notation
01. Lexical tokens and whitespace
02. Values, targets and bindings
03. Conditions
04. Part contents
    Instructions
    Constants
    Schemas
    State
    Triggers
    Processes
    Interfaces
05. XML and Markdown grouping
06. Complete document
```
Acceptance: Generate these section names in this order and the seven part subsections in canonical order. Every baseline production occurrence and surface projection must have a documented placement. Heading decoration may be compact to meet the existing size limits; the names and order are required. Check full and single-grouping outputs and inspect the complete rendered reference.

#### E02: Local alignment without renaming
Authority: required
Current state:
This excerpt is from outputs/oak.ebnf at the inspected baseline.
```ebnf
process_value = json_value | "$", value_target ;
value_target = constant_target | local_state_target | placeholder ;
value_binding = placeholder, "=", process_value ;
binding_list = "(", [ value_binding, { ",", value_binding }, [ "," ] ], ")" ;
output_bindings = "->", placeholder, { ",", placeholder } ;
```
Desired state:
```ebnf
process_value   = json_value | "$", value_target ;
value_target    = constant_target | local_state_target | placeholder ;

value_binding   = placeholder, "=", process_value ;
binding_list    = "(", [ value_binding, { ",", value_binding }, [ "," ] ], ")" ;
output_bindings = "->", placeholder, { ",", placeholder } ;
```
Acceptance: Preserve the five names and their exact grammar token sequences. Match the shown local alignment and blank-line separation while allowing target definitions to occupy their own adjacent group. No global name padding or change to process-value syntax is permitted. Compare a fixed expected specimen and independently compare production content.

#### E03: Readable trigger alternatives and nearby notes
Authority: required
Current state:
```ebnf
trigger_declaration = slug_id, "(", trigger_field, { ",", trigger_field }, [ "," ], ")", logical_nl ;
trigger_field = "event", "=", json_string | "source", "=", local_interface_target | "guard", "=", condition | "process", "=", process_target | "seed", "=", binding_list ;
```
Desired state:
```ebnf
trigger_declaration =
    slug_id, "(",
    trigger_field, { ",", trigger_field }, [ "," ],
    ")", logical_nl ;

trigger_field =
      "event",   "=", json_string
    | "source",  "=", local_interface_target
    | "guard",   "=", condition
    | "process", "=", process_target
    | "seed",    "=", binding_list ;
```
Validation notes and canonical-rendering notes appear immediately with the trigger group. They preserve required event and process fields, unique names, unrestricted authored field order, event/source/guard/process/seed canonical order, omitted absent fields, state-reading guards, non-blank single-line events, ordered seeds, and the existing restrictions on guard=true, empty seeds, and source-backed seeds.
Acceptance: Match the shown production layout and preserve every token and alternative in order. Verify the notes against their existing owners without converting validation conditions into broader or narrower productions. Authored trigger text, field-order acceptance, and canonical rendering must remain unchanged.

#### E04: Visible statement vocabulary
Authority: required
Current state:
```ebnf
process_statement = if_statement | while_statement | assert_statement | call_statement | emit_statement | set_statement | fail_statement | surface_act_native | surface_act_tool | surface_statement_foreach | surface_statement_par | surface_statement_join ;
```
Desired state:
```ebnf
process_statement =
      if_statement
    | while_statement
    | assert_statement
    | call_statement
    | emit_statement
    | set_statement
    | fail_statement
    | surface_act_native
    | surface_act_tool
    | surface_statement_foreach
    | surface_statement_par
    | surface_statement_join ;
```
Acceptance: Match the shown layout, names, alternatives, and order exactly. Keep statement details and suite notes in the Processes subsection. Do not replace surface references with invented productions or revive Step/steps terminology in the Python API. Use a fixed specimen check plus parser, renderer, and execution regressions.

#### E05: Descriptive templates remain literal
Authority: required
Current state:
The current surface tail includes this special sequence, separate from the statement group.
```ebnf
surface_statement_foreach = ? FOREACH <BINDING> IN <VALUE>:
  <BODY> ? ;
```
Desired state:
The same production is located in the Processes subsection and identified as descriptive, not expanded grammar.
```ebnf
(* Descriptive surface; its body is preserved literally. *)
surface_statement_foreach = ? FOREACH <BINDING> IN <VALUE>:
  <BODY> ? ;
```
Acceptance: The exact text between the question-mark delimiters, including its two-space body indentation and newline, must match the source projection. The explanatory comment may use shorter equivalent wording. Apply literal-preservation checks to all surface.shape projections, quoted terminals, embedded templates, and opaque lexical productions, including commas, pipes, semicolons, escaped quotes, and question marks that are data rather than formatting boundaries.

#### E06: Preservation is stronger than a fresh snapshot
Authority: required
Current state:
The generated output contains both of the following existing constant_target definitions from different source contributors.
```ebnf
constant_target = [ relative_document_path, "#" ], "constant.", slug_id ;
constant_target = [ relative_document_path, "#" ], "constant", ".", slug_id ;
```
Desired state:
The layout-only output retains both source-qualified occurrences and their respective grammar content. Verification accounts for the known repeated name without collapsing definitions or accepting arbitrary new duplicates. A separate review record identifies this as pre-existing grammar debt, not something fixed by the layout change.
Acceptance: Compare source-qualified production occurrences as a multiset, preserve right-hand-side token order within each occurrence, and preserve quoted and special-sequence content verbatim. Permit only placement, outer formatting, and reviewed commentary changes. Tests must reject a removed alternative, renamed production, changed terminal, changed special-sequence body, lost occurrence, unassigned surface, and new unexplained duplicate. Do not use a blanket whitespace-removal comparison that ignores meaningful text.

#### E07: Identical deliveries within existing budgets
Authority: required
Current state:
```text
outputs/oak.ebnf                                  generated grammar
skills/oak-authoring/references/oak.ebnf           same grammar bytes
references/00-structure.oak.md: constant.oak-ebnf   embedded grammar value
outputs/oak-authoring.oak.md                       same knowledge after fusion
```
The two grammar files share blob 9957853c5da52fa29926ba9e73b67d3a93ff473f at the inspected baseline. The standalone agent is 63,974 bytes against the 64,000-byte limit. These are inspected Git artifact facts, not results of a fresh build in this planning turn.
Desired state:
The same four delivery paths contain the new layout from the existing grammar generator. The two .ebnf files are byte-identical; parsed embedded grammar values match grammar().rstrip("\n"). All other skill-agent knowledge, teaching documents, metadata, validator identity, operational meaning, and authored OAK examples remain unchanged.
Acceptance: Regenerate through build/ebnf.py and build/authoring.py, verify the four deliveries and the existing 10,000/64,000-byte limits, compare unrelated generated content with the baseline, and run generation twice with no second diff. Use compact headings, selective alignment, and concise source-owned grammar commentary to stay within budget. Raising limits, deleting grammar or examples, independently compressing the embedded copy, or changing unrelated guidance is not an acceptable substitute.

## 3. Execution

Intent: Make the reference navigable without changing the language it describes. Prefer small explicit presentation code, preserve existing ownership, and use before-and-after specimens as testable contracts. Finish only when actual evidence covers every required comparison and all generated consumers.
Concept of operations: Freeze an observed baseline and classify every production and note. Implement sectioned presentation with guarded literal handling, then integrate focused preservation checks and regenerate the skill and agent. Complete repository verification, review the final diff independently, and deliver a pull request with a truthful completion report. The phases are dependency gates within one complete change, not deferred releases.

### Phase 1: Establish baseline and preservation contracts
Objective: Record the exact starting grammar, its consumers, constraints, and independent comparison data before implementation.
- [x] Key task: P01.01 Confirm explicit implementation authorisation, inspect the branch and destination refs, and read all applicable AGENTS documents plus the routed Python conventions before changing sources.
- [x] Key task: P01.02 Obtain a real checkout and run the existing complete verification entry points before changes; record the commit, environment, commands, exit codes, and any baseline failures without attributing them to this work.
- [x] Key task: P01.03 Inventory build/ebnf.py scaffolding, EXPRESSION_GRAMMAR, EXPRESSION_SURFACES, OPERATOR_TEXT, vocabulary productions, and every SURFACES projection; capture source-qualified occurrences and existing duplicate definitions.
- [x] Key task: P01.04 Map every current grammar commentary claim to its source owner and intended section; distinguish token conventions, validation restrictions, runtime semantics, canonical rendering, and descriptive surfaces.
- [x] Key task: P01.05 Capture full and single-grouping baseline outputs, both grouping orders where supported, delivered file hashes and sizes, embedded grammar values, and representative literal-sensitive fixtures in evidence only where supporting files are needed.
Success criteria: The baseline is pinned and actually inspected in the execution environment; E01 and E06 have complete placement and preservation inventories; E07 has measured starting sizes and delivery identities; no baseline failure is hidden.
Transition trigger: The baseline, owner map, and evidence requirements are recorded and sufficient to distinguish presentation changes from grammar changes.

### Phase 2: Implement sectioned presentation
Objective: Generate the accepted readable layout from existing grammar and surface sources.
- [x] Key task: P02.01 Replace assembly-order presentation with the six named sections and canonical seven-part subsections; keep grouping scaffolding and document composition near the end without altering PART_ORDER or supported grouping behaviour.
- [x] Key task: P02.02 Add restrained local alignment and safe multiline formatting for the specified compact groups, long alternatives, and trigger sequence; preserve source-derived right-hand sides instead of maintaining alternate grammar strings.
- [x] Key task: P02.03 Keep quoted terminals, special-sequence bodies, escaped-question-mark projections, and opaque lexical productions intact; preserve multiline template indentation and allow explicit soft-width exceptions.
- [x] Key task: P02.04 Place each surface projection and convention beside its owning construct, distinguish descriptive material from expanded productions, and retain every commentary claim with one existing source owner.
- [x] Key task: P02.05 Rehearse complete authoring generation against the fixed size limits early; use short section comments and reviewed concise grammar commentary rather than widening budgets or changing unrelated knowledge.
Success criteria: E01, E02, E03, E04, and E05 match their required layout and content criteria; E06's occurrence inventory is unchanged; E07's budget has an observed passing result before integration is considered complete.
Transition trigger: The generated candidate is readable, source-derived, literal-safe, and within the existing delivery budgets.

### Phase 3: Add focused regression coverage
Objective: Make the presentation contract executable without treating EBNF as the OAK validator.
- [x] Key task: P03.01 Add focused checks in build/checks/ebnf.py and register them through the existing complete verification entry point; keep test helpers narrow and use existing dependencies.
- [x] Key task: P03.02 Check the exact section and subsection order, local alignment specimens, long-alternative specimens, continuation and terminator layout, one final LF, deterministic output, and documented opaque-width exceptions.
- [x] Key task: P03.03 Compare the full source-qualified baseline occurrence inventory and fixed expected specimens independently of the formatter; preserve alternative order, terminals, special sequences, and the known duplicate pair without a blanket name-uniqueness assertion.
- [x] Key task: P03.04 Add negative fixtures that remove or reorder alternatives, change punctuation or quoted text, reindent a descriptive body, drop a production occurrence, introduce a duplicate, or leave a source surface unassigned; require each corruption to fail for the intended reason.
- [x] Key task: P03.05 Exercise XML-only, Markdown-only, default combined, and supported reversed grouping order; verify selected wrapper productions and document composition without misclassifying existing XML text inside descriptive surfaces as an extra grouping.
- [x] Key task: P03.06 Review existing grammar-sensitive substring and snapshot assertions, including compact-syntax and authoring checks; update only presentation assumptions and retain their semantic coverage.
Success criteria: E01 through E06 have positive and negative regression evidence; checks detect grammar-content drift independently of generated freshness; no parser, runtime, or surface descriptor is changed to make the checks pass.
Transition trigger: Focused checks pass, intentional corruptions are rejected, and the formatter cannot silently drop or rewrite a source contribution.

### Phase 4: Regenerate all affected deliveries
Objective: Publish the layout consistently and keep durable presentation rules with their owner.
- [x] Key task: P04.01 Record the durable EBNF presentation, literal-preservation, known-limitation, and verification contract in build/AGENTS.md without duplicating language policy or changing product byte limits.
- [x] Key task: P04.02 Regenerate outputs/oak.ebnf and all authoring products through their owning generators; refresh the packaged .ebnf file, structure-guide grammar constant, and assembled-agent grammar constant in the same pass.
- [x] Key task: P04.03 Compare grammar-file bytes and parsed embedded values; verify fusion preserves all non-grammar knowledge, teaching instances, tool names, metadata, optional-validator identity, and operational scope.
- [x] Key task: P04.04 Verify the skill-entry and standalone-agent byte limits, unchanged unrelated generated reference and example outputs, and zero diff after a repeated generation pass.
Success criteria: E07 passes across all four delivery locations; generation is repeatable; all non-grammar deliveries and canonical example behaviour remain unchanged except for deliberately updated build-owned operating knowledge.
Transition trigger: Generated products are fresh, equivalent in content, within budget, and ready for complete repository verification.

### Phase 5: Verify and independently review
Objective: Demonstrate the change is complete, readable, and behaviour-preserving on the final candidate.
- [x] Key task: P05.01 Run Python compilation for changed modules, focused EBNF checks, SMEAC plan checks, python -m build.examples, and python build/examples.py on the candidate; record actual commands, revisions, outputs, and exit codes.
- [x] Key task: P05.02 Confirm existing parsing, rendering, round-trip, model, execution, JSON-LD, detached-example, skill-agent, and generated-freshness gates remain covered by the complete checks and pass without weakened assertions.
- [x] Key task: P05.03 Inspect the entire generated grammar, all required specimens, note placement, both groupings, literal-sensitive fragments, and size results; review every old commentary claim against its new location and wording.
- [x] Key task: P05.04 Have an independent review of the candidate diff and evidence check scope, owner boundaries, source coverage, preservation, and readability; record the review method honestly and fix findings before freezing the final candidate.
- [x] Key task: P05.05 Rerun affected and complete checks after corrections, inspect git diff --check, and verify that no runtime changes, new dependencies, APS syntax, silent duplicate cleanup, changed width contracts, or hand-edited outputs entered the diff.
Success criteria: Actual verification evidence covers E01 through E07; every applicable check passes on the reviewed final candidate; the final review verdict is Approved with no unresolved in-scope finding.
Transition trigger: The reviewed revision and its passing evidence agree, and the complete implementation is ready for delivery.

### Phase 6: Record and deliver the completed change
Objective: Close the implementation record and submit the verified branch for review without merging it.
- [x] Key task: P06.01 Create report.md with the outcome, changed paths, baseline and final revision identities, actual verification evidence, final sizes, E01 through E07 observed results, known out-of-scope grammar limitations, and review verdict.
- [x] Key task: P06.02 Mark each implementation checkbox complete only after its acceptance and evidence requirements pass; retain all original commits and keep any corrections as new commits.
- [x] Key task: P06.03 Commit and push the complete change on this branch, confirm the remote file set and history, and create a pull request into main using the root change-naming rules; include preservation and size evidence in its description.
- [x] Key task: P06.04 Verify the pull request head and final checks, report the exact plan, report, branch, commit, and pull request, and leave main unchanged until separately authorised to merge.
Success criteria: All applicable tasks are evidenced and checked, the report records E01 through E07 and an Approved verdict, and the verified pull request is available for review with original history preserved.
Transition trigger: Mission complete; the completed branch is delivered for review, not merged automatically.

### Coordinating Instructions
- Timeline: Implementation was authorised on 2026-09-06T17:53:49+10:00 and proceeds through every phase in one effort. No elapsed-time commitment is invented.
- Boundaries: Change generated-reference presentation, its narrowly scoped source organisation, build-owned guidance, and verification only. Do not change the OAK language, runtime, public Python model API, skill packaging layout, validator identity, or APS snapshot.
- Operating guidelines: Keep plain short documentation, small cohesive Python code, unchanged source authority, exact specimen fences, and the existing generated-file workflow. Read additional scoped owners before inspecting or changing files under them.
- Risk mitigation: Compare independent baseline content as well as generated freshness, keep source occurrence identities, protect literal regions, budget embedded output early, and review commentary meaning rather than equating successful formatting with correctness.

### Contingencies
- If main advances then merge it into this branch without rebasing, check plan-number collisions and affected ownership, record the integration, and refresh baseline comparisons for the actual candidate without overwriting the historical inspected baseline.
- If a formatter cannot safely classify an opaque production then preserve that production's original body, document the width exception, and improve its surrounding organisation rather than guessing its internal grammar.
- If the generated agent exceeds 64,000 bytes then shorten build-owned heading decoration and source-owned grammar commentary without deleting claims or grammar content; do not raise budgets or alter unrelated guidance. Treat any unavoidable contract conflict as requiring user authorisation rather than an implicit scope expansion.
- If a check reveals pre-existing grammar duplication or incompleteness then preserve and report it separately; do not fold a grammar correction into this layout change.
- If a check reveals a new grammar or behaviour change then repair the presentation implementation and rerun the affected evidence and complete checks; do not accept new snapshots as the correction.
- If repository execution or an independent review environment is unavailable then record the exact limitation, keep the relevant checkboxes open, and do not claim verification, Approved status, or completed delivery.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Inspected baseline | One immutable commit | bf0975dd7959320fd6727cee926370eca1808e07 | AVAILABLE |
| Planning branch | One branch | docs/plan-ebnf-layout | AVAILABLE |
| Source grammar and surface descriptors | Existing repository owners | build/ebnf.py, build/surfaces.py, oak/surface/syntax.py, oak/vocabulary/text | AVAILABLE |
| Readability reference | One read-only legacy document | legacy-snapshot-aps/references/05-grammar.md | AVAILABLE |
| SMEAC format and plan checks | Existing schema and checker | examples/schemas/smeac_plan.oak.md, build/checks/plans.py | AVAILABLE |
| Executable repository checkout | One isolated working tree | Verified Git bundle from Actions run 34020468020 | AVAILABLE |
| Final verification and independent review | One final-candidate evidence set | Passing declared-dependency CI and independent Approved audit | AVAILABLE |

Supply: Reuse existing dependencies, descriptors, examples, and repository checks. Create evidence files only for observed baselines, fixed expected specimens, preservation comparisons, and actual verification results that support the final report.
Transportation: Move work through normal commits on docs/plan-ebnf-layout. Generate every downstream grammar copy from its owner and submit the completed branch through a pull request into main.
Sustainment: Keep presentation rules with build/AGENTS.md and regression checks in the build verification path. Leave language meaning with its existing package owners and retain the skill-agent shared-source contract.
Rollback: Revert the implementation commits with new commits and regenerate affected outputs from the reverted sources. Never amend, squash, rebase, or force-push away original history; no state or authored-document migration is part of this change.

## 5. Command and Signal

1. The repository owner authorises implementation, scope changes, acceptance, and any later merge.
2. The implementation agent executes this plan after authorisation and reports only observed evidence; an independent reviewer assesses the final candidate without substituting for the owner's merge authority.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| User conversation | Short progress messages | Report decisions, material findings, blockers, and delivery | At meaningful progress and completion |
| Plan and report | Git-versioned Markdown | Track task state, specimen acceptance, and observed evidence | At verified phase gates and final delivery |
| Pull request | GitHub review | Review the complete diff, checks, preservation results, and history | After implementation and verification |

Reporting: The report records observed results for E01 through E07, the independent Approved audit, preserved product fingerprint, and passing declared-dependency CI for implementation d44ba304 and review-integration head 7e4cfe15. The documentation-only closeout commit has its exact head and subsequent CI recorded in PR #19 before handoff; this document does not claim its own future check result. Local recovery full-suite timeouts are disclosed, not counted as passes.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Start implementation | Repository owner | Granted on 2026-09-06T17:53:49+10:00 |
| Presentation details within required specimens and contracts | Implementation agent | Independent review, then repository owner for conflicts |
| Change syntax, grammar definitions, package limits, or validation authority | Repository owner | Outside this plan; require explicit authorisation |
| Approve final review | Independent reviewer using actual candidate evidence | Repository owner for unresolved disagreement |
| Merge into main | Repository owner | Require separate merge authorisation |

### Acknowledgement
The implementation agent acknowledges the presentation-only scope, all seven required comparisons, and the explicit implementation and pull-request authorisation received on 2026-09-06T17:53:49+10:00. Completion still requires observed evidence; merge authority remains with the repository owner.
