---
title: Prepare reusable OAK skill templates with optional state
prepared: '2026-09-08T11:06:16+00:00'
classification: PUBLIC
plan: 0018-oak-skill-template-profiles
readiness: Contracts settled under the approved implementation scope. Final acceptance remains pending.
authorisation: End-to-end implementation, verification, commits, pushes and review delivery on
  docs/prepare-skill-template-profiles are authorised. Installation, live-instance changes,
  unrelated deployment work and merging are not authorised.
execution: Planning format is delivered. Profile sources and fixtures are implemented; complete delivery verification is in progress.
publication: Continue on docs/prepare-skill-template-profiles through draft PR 26.
  Publication is not product completion; final-head verification and human review remain required.
baseline: 1e21b227faae9a4f5ead997047af718db84ffd8d
---

## Intent

The intent is to give OAK one reusable skill-template foundation, with an optional stateful extension, rather than maintaining two separate templates. Stateless skills should contain no unnecessary state machinery. Stateful skills should add explicitly owned, instance-local memory, while keeping shared source separate. Both should have accurate INDEX/MAP descriptions, worked examples and verification, without requiring a new runtime framework.

## 1. Situation

### Operating Environment

OAK owns the portable knowledge standard and its reusable authoring template. This change prepares the common template, optional stateful extension, authoring guidance, worked examples, generated deliveries and checks for any consuming skill. Deployment-specific configuration and unrelated downstream work are outside this plan.

### Current State

The product baseline is repository revision `1e21b227faae9a4f5ead997047af718db84ffd8d`, which includes the delivered Intent-first planning format and sanitised plan. The root, documentation, example and build owners were read at this baseline. The current build owner describes one generic inert template with optional OAK parts, source-derived generation, a stateless authoring entry and scope-safe fusion. The supplied proposal describes the gap as explicit base/extension selection, complete per-profile package MAPs and an ordinary indexed-memory example. P01.01 confirmed the template, guide, catalogue and checker observations against that checkout. The complete baseline verification and the planning-format verification passed before profile implementation.

### Requirements and Source Authority

The requirements and acceptance criteria are self-contained in this plan. Current contracts belong to the linked repository owners, not this proposal. The table retains the supplied proposal's component-level assessment, with current source ownership corrected where the pinned governing documents establish it. Historical byte counts, artifact counts and validator fingerprints are not current verification evidence. Read the actual sources, measure the selected deliveries and pin their identities in P01.01 and P01.04; record executed results only in the eventual completion report.

| Owner or delivery | Contract or reported capability | Gap or implication for this change |
| --- | --- | --- |
| [Root knowledge](../../../AGENTS.md), [build owner](../../../build/AGENTS.md), [docs owner](../../AGENTS.md), [example owner](../../../examples/AGENTS.md) | Scoped ownership, generated/source separation, compact SMEAC plans and verification gates | Record the approved template convention under the build owner; keep this plan separate from current product contracts. |
| [Template source](../../../build/authoring_guides.py), `TEMPLATE_ENTRY` and `TEMPLATE_DIRECTORIES` | Generic scaffold with quoted metadata markers, purpose, literal `SKILL_TREE`, optional part slots and six retained empty resource directories | The proposal reports no named profile selection and `<STATE_PART>` in the common scaffold. Recheck this at implementation baseline. A populated skill must describe its complete selected static files, not just broad directories. |
| [Delivered template](../../../generated/oak-authoring.skill/_template/SKILL.md) | Exact source-derived inert entry | It is an output to regenerate, never the source to edit. |
| [Authoring workflow](../../../build/authoring_agent.py) and [shared guidance](../../../build/authoring_guides.py) | Current ownership separates the stateless operational entry and its local public contracts from shared declarative guidance and template knowledge | Add profile choice, selected resources, INDEX/MAP review, state ownership and memory practice without giving the authoring workflow persistent state. Preserve direct and guided authoring, host-owned conversational drafts, consent and shared-knowledge parity. |
| [Authoring generator](../../../build/authoring.py), with [entry source](../../../build/authoring_agent.py) | Standard metadata, generated references, guides, literal examples, optional helper, template and standalone authoring agent | Build both selections from one source; extend the exact artifact inventory and shared knowledge once. Establish freshness by rerunning the current owner checks, not by relying on an earlier artifact count. |
| [Fusion](../../../build/fusion.py) | One operational entry; supporting documents may supply constants and schemas only; literal examples are preserved | Stateful extension recipes and worked examples stay inert in authoring fusion. Composed operational skills remain separate documents. Do not relax fusion to combine their state. |
| [Package boundary](../../../oak/AGENTS.md), [node](../../../oak/node/AGENTS.md), [resolution](../../../oak/resolve/AGENTS.md), [execution](../../../oak/execute/AGENTS.md) | Value lifetimes, local state/interface operations, typed `CALL`, explicit document graphs, staged state and emissions | No new OAK language construct or persistence service is needed. File writes and external effects remain host responsibilities; staged OAK state is not an atomic filesystem transaction. |
| [Example catalogue](../../../examples/catalog.py) | Four core stages: fixed knowledge, shaped information, typed stateless work and persistent state | `shape_writer` and `compound_growth` teach semantics, but do not demonstrate complete skill packages, instance bindings, CSV memory or state-preserving source updates. Preserve these stages. |
| [Authoring checks](../../../build/checks/authoring.py) | Metadata, exact files and directories, template markers, literal tree, minimal population, parse/resolve/round trips, inertness, parity and rejection cases | Current populated template fixture contains only purpose and layout. Add two realistic selected variants and independent omission/MAP/INDEX/state checks. |
| [Optional validator source](../../../build/authoring_validator.py), [validator checks](../../../build/checks/optional_validator.py) | Optional parse/resolve helper with a source-owned version, immutable revision and package/dependency fingerprints | Read and reconcile the actual identity against the selected implementation baseline. Do not present the helper as proof of memory integrity, retention, host enforcement or successful effects. |
| [Generated-output checks](../../../build/checks/outputs.py), [safe writer](../../../build/generated.py), [complete entry point](../../../build/examples.py) | Exact manifests, cold builds, repair, repeat generation, detached delivery and unsafe-path rejection | Extend these existing checks to the profile deliveries; do not create an alternative generation pipeline. |
| [Plan checker](../../../build/checks/plans.py), [SMEAC schema source](../../../examples/schemas/smeac_plan.py), [OAK schema](../../../examples/schemas/smeac_plan.oak.md) | Source-owned planning shape, compact phases, stable task IDs, paired comparisons, Directory Changes and storage/navigation checks | Use the requested Intent-first body and metadata frontmatter. The planning-format source, owner policy, checks and generated siblings must be updated together; the format change is authorised separately from the product phases below. |

### Confirmed Requirements

The following confirmed direction and retained requirements govern interpretation of the illustrative designs. The implementation choices are resolved in D01-D05 below. The user has now authorised the complete implementation and review delivery; a published plan alone remains neither permission nor completion evidence.

| ID | Requirement | Acceptance link |
| --- | --- | --- |
| R01 | Maintain one OAK-owned template with a stateless foundation and an optional stateful extension. Share common functional/template content rather than maintaining independent templates. | E01 |
| R02 | A produced stateless skill omits its own state directory, state-only settings, retention prompts, declarations, schemas, processes, migrations, exclusions, references, INDEX/MAP entries and postconditions. Preserve justified ordinary inputs, outputs, functional configuration, authority and verification. | E02 |
| R03 | Stateful skills reuse the foundation and can call approved existing stateless or stateful capabilities through explicit contracts. A call never transfers state or policy ownership. | E05 |
| R04 | Present DEFINE, optional ROUTE, LOOP, INDEX, MAP and ASSERT roles in SKILL.md. These are presentation roles carried by OAK, not new language constructs. Retain canonical OAK part ordering. | E04 |
| R05 | MAP names every selected static file and fixed instance scaffold. Use `(...)` only for contents generated during use. Ordinary runs do not rewrite shared SKILL.md or enumerate private state into it. MAP is neither an import nor an access grant. | E04 |
| R06 | Mutable skill-owned memory belongs in the local skill instance, separate from shared functional source. The agreed purpose vocabulary is `state/policy`, `state/history`, `state/runs` and `state/runtime`; include areas only where justified. Preserve logical owner/capability identity through source updates and names. | E03 |
| R07 | Ordinary memory uses agent-maintained compact CSV indexes and referenced records. State does not mandate Python infrastructure. Preserve tool ownership of operational journals, locks, verified outcomes and protected datasets. | E03 |
| R08 | Omit state from default context and ignore it in Git unless explicitly configured otherwise. Loading, Git tracking, retention and backup are separate controls. Preserve existing authorisation and pending work. | E03 and the loading/Git/retention validation boundary |
| R09 | OAK owns the generic convention. Consumers reuse it and separately own deployment-specific naming, resource discovery, permissions and update policies. Generated deliveries are not independently maintained sources. | E01 and E05 |

R02 applies to the selected capability's operational state machinery. A stateless authoring toolkit can still teach how to author stateful skills through inert extension knowledge; that teaching must not create state for the toolkit itself. Statefulness and external effects are independent: a stateless capability can read changing sources or perform an explicitly authorised write.

### Illustrations and Selected Details

The generic `classify-item` and `review-items` packages in E06 are worked design illustrations, not existing package inventories or universal minimums. Helper-script names, `configuration.json`, checkpoint/journal formats, extra CSV columns and configuration field names remain reviewable examples. The four purpose-based state area names are retained requirements; they do not require every area in every stateful skill.

The selected minimal CSV header `id,name,reference`, reference resolution from the containing CSV, single-writer practice and record-before-index update sequence are useful concrete defaults for this plan. D01-D05 settle schemas, single-writer practice, first-use decisions, future-record retention, dependency packaging and compatible updates for the examples. These are template application contracts, not new OAK APIs. No universal `SKILL.state` file is adopted.

### Challenges

- Size: the pinned [build owner](../../../build/AGENTS.md) sets repository byte budgets of 24,000 for the skill entry and 128,000 for the standalone authoring agent. The baseline measured 22,256 and 95,579 bytes respectively. The selected complete profile delivery measured 22,518 and 122,175 bytes before final verification. Add complete guidance and examples through source factoring and concise expression without losing required knowledge or silently changing the budgets.

- Presentation: the desired role sequence must remain navigable while the OAK document preserves its canonical part order and one owner per instruction or contract.

- Composition: relative executable targets are `.oak.md` documents. The optional validator gives SKILL.md a virtual OAK identity for validation; it does not make every other skill's SKILL.md an importable process document or a registry.

- File state: ordinary agent edits can maintain memory, but multi-file recovery, competing writers and uncertain external effects require explicit limits and evidence. A schema or natural-language instruction does not supply atomicity.

- Integration: the operational authoring entry, declarative guides, catalogue, build owner, generated deliveries and checks may evolve before implementation. Pin and inspect the approved source revision; preserve unrelated changes and reconcile overlapping edits rather than overwriting them.

### Supporting Factors

- Higher intent: make reusable OAK skills equally clear and maintainable whether they need no persistent memory or explicitly owned instance-local state.

- Adjacent capabilities: preserve the current stateless authoring entry, native artifact knowledge, local public contracts and existing scenario catalogue. These are integration boundaries, not permission to expand this plan into deployment work.

- Supporting resources: existing source generators, resolver/executor semantics, optional-validator safeguards, scenario registration and the verification commands owned by build/AGENTS.md. An implementation environment must satisfy the dependencies declared at the selected revision; availability is not assumed from an earlier environment.

### Assumptions

- Existing OAK syntax, `Node` models, explicit `CALL` and native file-tool actions can express the required workflows. Any demonstrated language gap needs a separate proposal.

- The first implementation examples use synthetic local records and deterministic demonstration adapters. They require no private source records, live service, global skill installation or live model call.

- The final implementation baseline and selected dependencies will be pinned after inspecting current source owners and reconciling relevant changes. Historical proposal observations are not substituted for current governing knowledge.

### Constraints and Limitations

- Constraint: the present authorisation covers this sanitised plan, the shared planning-format update, all skill-template product phases, verification, commits, pushes and review-PR delivery on `docs/prepare-skill-template-profiles`. It does not authorise installation, changes to live state, unrelated deployment configuration or merging.

- Constraint: no installer, sync engine, generic state framework, deployment-specific naming policy, unrelated capability, provider metadata change or live integration enters this product scope.

- Constraint: preserve one source per concern, existing authoring knowledge and teaching, no-install use, validator consent and identity checks, scope-safe fusion and current byte limits. Add no README index or runtime dependency by default.

- Constraint: work directly without subagents. Preserve unrelated work and existing history. Use only the authorised continuation branch; do not amend, squash, rebase, force-push or merge. Confirm each authorised publication checkpoint from the remote before continuing implementation.

- Limitation: platform documentation is evidence of documented controls, not installed compatibility or context isolation. Host-specific visibility, linking, persistence and external-effect enforcement remain separately authorised acceptance work.

## 2. Mission

The OAK maintainer delivers one reusable template foundation and optional stateful extension in this repository under the approved end-to-end scope.

Task: complete the template convention, authoring route, two populated variants, composition example, generation integration and validation in one authorised OAK-scoped change.

Purpose: provide a validated shared authoring foundation without duplicating OAK or requiring infrastructure for ordinary memory.

End state: a new skill can select stateless or stateful authoring from one maintained source, obtain a complete accurate INDEX/MAP, and understand its contracts, state boundaries and observable postconditions. Both authoring deliveries teach the same capability. Consumers can identify the exact verified source revision and remaining host obligations.

### Proposed Design

1. Extract the existing template concern into a small build-owned module, proposed as `build/skill_template.py`. Keep one base entry and a declarative optional extension. Compose selected entries into canonical parts before rendering; do not concatenate two operational documents or maintain two complete common skeletons. The build code assembles repository deliveries; users can still author from the same knowledge without Python.

2. Keep `_template/SKILL.md` as the inert stateless starting point. A proposed `_template/stateful.oak.md` carries the optional extension recipe and fragments as inert knowledge. It is selected deliberately and never automatically becomes another operational fusion input. D01 selects this filename and constants-only recipe representation.

3. Carry the presentation through existing OAK parts. Metadata and a named purpose define identity. An ordered role overview locates optional routing, the main process, a compact task-to-resource index, the literal `layout`/`SKILL_TREE` value and completion conditions. Keep the role overview navigational, with actual meaning owned by the corresponding OAK definitions. Do not reorder canonical parts or add DEFINE/INDEX/MAP as OAK statements. D02 records the selected rendered roles and the common source-owned definition fields.

4. Derive file membership, INDEX entries and MAP from the selected static resource declarations. Reuse the existing artifact mappings and safe generation primitives. Distinguish shared functional files, instance-local fixed scaffolding, external declared dependencies and variable contents. Check map coverage without following private directories. Remove unused resources and `.gitkeep` files during population; do not ship empty operational state by accident.

5. Give composable capabilities real `.oak.md` process exports. Prefer a small stateless callable under `processes/`, invoked by both its own entry and the stateful example. Resolve the declared dependency inside a bounded approved fixture root. Do not fabricate CALL-to-SKILL.md support, copy a dependency beneath the caller, scan global skills, or treat a display path as a loader instruction. Runtime resource discovery and installation policy stay with the consuming host.

6. Put the stateful lifecycle and instance binding in the consuming skill's main process. Require a stable owner/capability identity and explicit local instance root, separate from shared source and a script's resolved location. Bind declared state through existing host contracts; never rewrite the shared declaration after each run. Supporting operational documents receive explicit inputs and keep their own scope.

7. Teach ordinary memory maintenance as bounded reads and normal file edits: load selected index rows, resolve permitted records, establish evidence/authority, check for intervening changes, write a record, update its stable index entry and read both back. Recover orphan records and interrupted index publication; refuse an unknown writer conflict. Never manufacture a tool-owned receipt or hand-edit a journal to claim success.

8. Teach first-use retention choice and saved preferences separately from active loading and actual Git rules. Reuse an applicable saved decision. Default to context omission and Git exclusion; do not assume configuration text enforces either. Preserve existing policy, evidence, pending work and operational identities when retention changes. D04 selects full and summary modes for future records, with explicit bounded Git exceptions.

9. Add compact synthetic worked variants through the existing example catalogue. Reuse the new stateless example from the stateful example. Keep worked document/package mappings inert in the authoring skill and standalone agent; materialise install-shaped skill fixtures in disposable directories for tests. Avoid accidentally discoverable nested example skills in the authoring installation.

### Affected Source Owners

| Owner | Proposed work |
| --- | --- |
| `build/AGENTS.md` | Record approved generic template ownership, selected-profile omission, presentation/MAP policy and verification responsibilities. Preserve existing limits and host boundaries. |
| `build/skill_template.py` (proposed) | Sole base/extension assembly, selected static-resource declarations and derived layout knowledge. This is build support, not a consumer state runtime. |
| `build/authoring_guides.py` | Consume the template owner; route profile choice, composition, INDEX/MAP and memory guidance. Supporting guide documents remain declarative. |
| `build/authoring.py`, `build/authoring_agent.py` | Generate the selected template deliveries and identical shared knowledge in both authoring forms. Keep the standard installed name, metadata contract and single stateless operational entry. Update routing at its current owner rather than moving it back into declarative guides. |
| `examples/AGENTS.md`, `examples/catalog.py`, `examples/skill_profiles/` (proposed) | Register one focused profile/composition scenario, source-owned sample records and canonical siblings; preserve the four core stages and detached-host disclosures. |
| `build/checks/skill_profiles.py` (proposed), `build/checks/__init__.py` | Profile manifests, positive and rejected selections, typed execution fixtures, ordinary-memory preservation and package-map checks. |
| `build/checks/authoring.py`, `build/checks/authoring_agent.py`, `build/checks/authoring_intent.py`, `build/checks/human_examples.py`, `build/checks/outputs.py` | Update affected inventories, selected-template population, authoring routing, teaching parity, detached closure, fresh bytes and cold-generation coverage. Preserve direct/guided authoring safeguards and host-owned draft continuity. Split checks only where the concern needs its own module. |
| `build/authoring_validator.py`, `build/checks/optional_validator.py` | Assess version/identity changes against the final baseline; preserve optional parse/resolve scope and no-install paths. Extend tests for actual selected graph roots without inventing a state API. |
| `oak/rules/guidance.py` and scoped package owners | Inspect for reused language meaning. No core change is planned; place template application conventions in build guidance rather than duplicating existing package rules. |
| `docs/plans/0018-oak-skill-template-profiles/` | Maintain this task's decisions and observed verification. Add `report.md` only for the eventual implemented outcome. No preparatory inspection file is part of this plan. |

Generated effects include `generated/oak-authoring.skill/_template/`, its authoring/review guidance and selected example deliveries, `generated/oak-authoring.skill/SKILL.md`, and `generated/oak-authoring.oak.md`. Refresh the helper only when its source changes. `examples/catalog.oak.md` and new canonical example siblings remain generated from their owners. No independently maintained consumer template is created.

### Directory Changes

The product views cover the selected profile implementation. The completed planning-format milestone is retained in repository history and the final PR change manifest.

Baseline: product checkout `1e21b227faae9a4f5ead997047af718db84ffd8d`, inspected before profile changes.

Legend: [add] new; [modify] changed; [move from PATH] relocated; [remove] deleted; [keep] unchanged context; [check] verify and change only if needed.

Current:

```text
open-agent-knowledge/
  build/
    AGENTS.md                           # Owns generated authoring products and verification
    authoring_guides.py                  # Owns the original generic template and shared guidance
    authoring.py                         # Generates modular and standalone authoring
    authoring_agent.py                   # Owns the stateless operational entry
    authoring_validator.py               # Owns optional validator identity
    checks/
      __init__.py                       # Registers repository checks
      authoring.py                      # Checks one minimal template population
      authoring_agent.py                # Checks direct and guided authoring parity
      human_examples.py                 # Checks registered scenario closure
      outputs.py                        # Checks complete generation and repair
  examples/
    AGENTS.md                           # Owns scenario authoring and teaching
    catalog.py                          # Registers four core stages and other scenarios
  generated/oak-authoring.skill/
    _template/SKILL.md                   # Original scaffold with an optional state slot
    guides/authoring.oak.md              # Original template as literal knowledge
  generated/oak-authoring.oak.md         # Original complete standalone authoring knowledge
```

Planned:

```text
open-agent-knowledge/
  build/
    AGENTS.md                           # [modify] Profile ownership and checks
    skill_template.py                   # [add] Common foundation, selected extension and resource descriptions
    authoring_guides.py                  # [modify] Shared profile knowledge
    authoring.py                         # [modify] Template and teaching deliveries
    authoring_agent.py                   # [modify] Explicit profile knowledge in draft maintenance
    authoring_validator.py               # [modify] Skill 3.4.0, unchanged validator source identity
    checks/
      __init__.py                       # [modify] Register complete profile checks
      authoring.py                      # [modify] Template, teaching, inertness and manifest checks
      authoring_agent.py                # [modify] Verify extension knowledge reaches both forms
      human_examples.py                 # [modify] Validate selected supplementary teaching
      outputs.py                        # [modify] Extend cold repair and unsafe-link coverage
      skill_profiles.py                 # [add] Package, composition and detached acceptance
      skill_profile_memory.py           # [add] Disposable normal-file fixture host
      skill_profile_cases.py            # [add] Failure, retention, writer and Git cases
  examples/
    AGENTS.md                           # [modify] Profile scenario and inert package ownership
    catalog.py                          # [modify] Register profile scenario without changing core stages
    catalog.oak.md                      # [modify] Regenerate catalogue from its source
    skill_profiles/
      example.py                        # [add] Stateful prepare/resume workflow
      example.oak.md                    # [add] Regenerate review workflow
      classifier.py                     # [add] Separate stateless callable
      classifier.oak.md                 # [add] Regenerate classifier
      memory.py                         # [add] Example memory schemas and generic policy reference
      memory.oak.md                     # [add] Regenerate memory contracts
      packages.py                       # [add] Complete selected package mappings
      packages.oak.md                   # [add] Regenerate inert package mappings
      sample.oak.md                     # [add] Regenerate synthetic input and expected outcome
  generated/
    oak-authoring.skill/
      SKILL.md                          # [modify] Regenerate stateless authoring entry
      _template/
        SKILL.md                        # [modify] Regenerate stateless foundation
        stateful.oak.md                  # [add] Regenerate inert extension
      guides/
        authoring.oak.md                 # [modify] Regenerate shared template knowledge
        review.oak.md                    # [modify] Regenerate full inert teaching
        validation.oak.md                # [modify] Regenerate skill version and identical helper
      assets/examples/
        catalog.oak.md                   # [modify] Regenerate supplementary profile entry
        skill_profiles/
          packages.oak.md                # [add] Regenerate complete inert package mappings
          sample.oak.md                  # [add] Regenerate synthetic input
      scripts/validate.py                # [modify] Regenerate versioned optional helper
      platforms/codex/templates/.codex/agents/oak-authoring.toml
                                        # [modify] Regenerate identical native authoring body
      platforms/claude/templates/.claude/agents/oak-authoring.md
                                        # [modify] Regenerate identical native authoring body
    oak-authoring.oak.md                 # [modify] Regenerate complete standalone authoring
  docs/plans/0018-oak-skill-template-profiles/
    plan.md                             # [modify] Selected decisions and evidence-backed task state
    report.md                           # [add] Final outcome, manifests and verification
```

Ownership: build/skill_template.py owns the common convention. Registered example sources own each scenario sibling and the four shared files inside the inert package mappings. The catalogue selects only packages.oak.md and sample.oak.md for supplementary installed teaching. Build checks own the disposable file host. Local configuration, policy/history/run indexes and generated instance records are fixture products, never repository or authoring installation state. All generated paths are regenerated through their listed source owners; the six unchanged empty template resource directories remain.

Verification: compare this view with the final product diff, independently declared package and scaffold manifests, complete generated paths and Git's staged manifest. Preserve the four original core stages and their literal teaching. Run actual file recovery, owner isolation, bounded loading, Git exclusion and detached acceptance fixtures before claiming delivery.

### State Comparisons

P01.01 confirmed the E01-E05 baseline descriptions against the continuation checkout. The before states describe the product before this change; completion evidence belongs in the report.

#### E01: One foundation and selected extension

Authority: required

Current state:

The delivered generic scaffold contains optional `<STATE_PART>` beside the other part markers. Its populated test deletes all optional parts and retains purpose and a directory-level tree; no stateful population is tested.

Desired state:

One maintained foundation produces both selections. The default population has no state-only artifacts or behaviour; the stateful selection adds only its justified extension. The authoring skill and standalone agent carry the same inert source knowledge.

Acceptance: trace each selection to one common source, populate both, compare shared content and prove the extension cannot leak into the stateless selection. Preserve metadata placeholders until population, then reject unfilled or duplicated markers. Prove the extension and examples never activate in authoring fusion.

#### E02: Stateless capability with an accurate package description

Authority: required

Current state:

`shape_writer` demonstrates typed stateless execution, but there is no populated stateless skill with an independently checked complete INDEX and MAP.

Desired state:

A small selected capability declares explicit inputs, outputs, failures and any effects; its INDEX resolves to its selected resources and its MAP enumerates every static file. No state path, setup, retention, migration, writer, exclusion or state-only assertion survives.

Acceptance: canonical parse/resolve/round trips in both groupings, a detached invocation, invalid input/output cases, exact static file and reference checks, and an observable assertion that the invocation creates no persistent skill state. Inspect declarations and behaviour rather than banning the word state from unrelated explanatory text.

#### E03: Stateful instance using ordinary memory

Authority: required

Current state:

`compound_growth` carries committed values between arrivals. It does not model instance-local indexed records, retention preferences, writer ownership or source-update preservation.

Desired state:

The stateful population binds one local owner, loads only needed records, uses the existing stateless fixture, maintains permitted CSV indexes and records with normal file tools, and resumes without losing policy evidence or pending work. Shared definition changes never overwrite local state. Tool-owned records retain their writer.

Acceptance: use two synthetic instances and test initialise, saved-preference reuse, resume, compatible update, renamed exposure, interrupted record/index publication, wrong owner and competing writer. Verify stable IDs, scoped references, read-back consistency and preserved state hashes. Reconcile simulated uncertain effects; do not claim filesystem atomicity or real external-action proof.

#### E04: Presentation, INDEX and complete MAP

Authority: required

Current state:

The current literal tree lists broad resource directories. Neither the role overview nor full static-file coverage is checked.

Desired state:

Preserve this agreed presentation sequence as navigational roles while retaining canonical OAK:

```text
SKILL.md
├── DEFINE     # Name, description, title, purpose and operating principle
├── ROUTE      # Entry conditions, instance selection and permitted dependencies
├── LOOP       # Main OAK process and resumable lifecycle
├── INDEX      # When to load each process, reference, example or recovery guide
├── MAP        # Full static package and fixed instance layout; (...) for generated contents
└── ASSERT     # Observable success, verification, preservation and delivery conditions
```

ROUTE is omitted when unnecessary. The stateless LOOP has no resume/state requirement. INDEX and MAP contain only the selected variant; static files cannot be hidden by `(...)`, and private generated names cannot enter shared SKILL.md.

Acceptance: review the populated role mapping, compare MAP to an independently declared static manifest and scaffold contract, resolve every INDEX entry with its loading condition, and compare SKILL.md bytes before/after synthetic runs. Reject missing/extra/static files concealed by `(...)`, dangling resources and live IDs in the shared map. Retain the existing `SKILL_TREE:` literal notation unless a separately reviewed presentation decision changes it.

#### E05: Composition and honest verification boundaries

Authority: required

Current state:

The resolver supports explicit cross-document calls and local state. Fusion refuses supporting operational scopes, and the optional validator reports parse/resolve only.

Desired state:

The stateful fixture calls the same stateless process through a declared `.oak.md` target without copying it. Each document retains its state and policy identity. The result distinguishes authoring guidance, structural checks, executed fixtures and untested host behaviour.

Acceptance: reject missing or changed dependencies, escaping or unapproved roots, wrong contracts, call cycles and attempted cross-owner state access. Prove failed work does not emit a successful result. Retain fusion rejections and no-install authoring; no interpretation or effect is inferred from schema validity alone.

#### E06: Illustrative populated maps

Authority: illustrative

Current state:

The proposed packages have no verified baseline inventory in this preparation. E06 illustrates their design; it does not claim that the packages already exist or prescribe a universal minimum template.

Desired state:

The following is a proposed small teaching pair. Names and exact file boundaries may change under D05; each final map must still be complete for its chosen package.

```text
SKILL_TREE:
  SKILL.md→Stateless classify-item entry and task index
  processes/
    classify-item.oak.md→Typed reusable operation and its local contracts
```

```text
SKILL_TREE:
  SKILL.md→Shared review-items entry, lifecycle, owner binding and task index
  references/
    state-and-policy.oak.md→Shared indexed-memory and preservation knowledge
  assets/
    schemas/
      instance-state.oak.md→Shared instance/settings and record contracts
    templates/
      configuration.json→Shared initial settings, never an overwrite source
      policy-index.csv→Shared empty index seed
      history-index.csv→Shared empty index seed
      runs-index.csv→Shared empty index seed
  troubleshooting/
    reconcile-update.oak.md→Shared interrupted-update guidance
  .gitignore→Local exclusions derived from saved settings
  state/→Instance-local mutable material, omitted from default context
    configuration.json→Local saved settings
    policy/
      index.csv→Local rule lookup
      (...)→Generated learned records
    history/
      index.csv→Local evidence lookup
      records/
        (...)→Generated decision and evidence records
      raw/
        (...)→Generated originals owned by this instance, only when needed
    runs/
      index.csv→Local run lookup
      (...)→Generated runs, checkpoints and pending work
    runtime/
      (...)→Generated tool-owned recovery records, only when justified
```

Acceptance: use the pair to settle exact artifact boundaries. `classify-item` is an external approved fixture dependency, not a copied subtree of `review-items`. No Python helper or fixed record filename is implied. Final variants omit every unselected optional area; the illustrative runtime area is not mandatory for ordinary memory.

## 3. Execution

Execution approach: deliver the complete OAK template change under one source authority. Establish contracts and rendered examples before changing generation, preserve simple file-based memory, and prove both selections against independent expectations. Make remaining host responsibilities explicit.

Concept of operations: under the existing implementation approval, reconcile the integration baseline and open decisions, implement shared assembly and guidance, complete synthetic variants and composition, then regenerate and verify the entire affected delivery. Each phase is a gate within one complete change, not a deferred replacement design.

### Phase 1: Settle contracts and integration
Objective: Make the approved implementation inputs concrete before editing product sources.
- [x] Key task: P01.01 Confirm the authorised branch and integration baseline, pin complete governing content, reconcile remote/local state and inspect the current source/check contracts without replaying unrelated completed work.
- [x] Key task: P01.02 Resolve D01-D05, including exact base/extension delivery, canonical role presentation, callable dependency boundary, memory/retention contract and full example file sets.
- [x] Key task: P01.03 Prepare paired populated specimens and independent expected manifests for E01-E05; retain E06 as illustrative until exact filenames are accepted.
- [x] Key task: P01.04 Measure projected shared knowledge and both authoring deliveries against the current build-owned byte budgets; agree meaning-preserving factoring for the selected baseline.
Success criteria: E01 and E04 have reviewable exact specimens, E02/E03/E05 have explicit contracts and expected outcomes, D01-D05 are resolved, and a credible measured size allocation preserves all existing required knowledge.
Transition trigger: The user has authorised the exact implementation scope and the resolved contracts, baseline and size design contain no outstanding conflict.


### Phase 2: Implement the shared template and authoring route
Objective: Select both variants from one source with accurate presentation and resources.
- [ ] Key task: P02.01 Record the approved durable template convention in build/AGENTS.md and reference other semantic owners instead of copying them.
- [ ] Key task: P02.02 Implement one base and optional selected extension with canonical part assembly, complete static-resource declarations and no compulsory consumer runtime.
- [ ] Key task: P02.03 Update authoring guidance and request routing to select a profile, preserve contracts, omit unused parts and derive the selected INDEX/MAP and observable postconditions.
- [ ] Key task: P02.04 Preserve template inertness, shared guide/standalone identity and scope-safe fusion; implement focused positive and rejection checks alongside the source.
Success criteria: E01 and E04 pass with source-derived artifacts and independent manifest expectations; shared authoring remains stateless and no state-only content enters the produced stateless selection.
Transition trigger: Both profile selections and their presentation are represented once, and the targeted assembly/inertness checks pass.


### Phase 3: Complete worked variants and memory behaviour
Objective: Demonstrate practical composition and state ownership with synthetic local data.
- [ ] Key task: P03.01 Register the populated stateless capability and stateful consumer under the existing catalogue with canonical siblings, complete sample data and explicit fixture-host disclosures.
- [ ] Key task: P03.02 Demonstrate calls to the same stateless export through a bounded dependency graph; retain document-local state and contract ownership.
- [ ] Key task: P03.03 Implement the stateful knowledge for owner binding, saved retention choice, bounded index-first loading, permitted file edits, read-back checks and interrupted-update recovery.
- [ ] Key task: P03.04 Add deterministic fixtures for owner isolation, renamed exposure, compatible source updates, pending-work preservation, writer conflicts and protected tool-owned records; add no generic state subsystem.
Success criteria: E02, E03 and E05 pass for complete selected packages, with records and command traces showing what ran and what remains host guidance.
Transition trigger: Both variants work in disposable fixtures and every demonstrated recovery path preserves the intended records and authority boundaries.


### Phase 4: Generate and verify the deliveries
Objective: Deliver the identical complete capability through the existing build pipeline.
- [ ] Key task: P04.01 Integrate the selected template recipes, guides and inert examples into authoring artifacts and the existing exact file/directory expectations.
- [ ] Key task: P04.02 Reconcile skill version and immutable validator fingerprints with the selected source/dependency baseline; preserve parse/resolve reporting and all no-install/consent cases.
- [ ] Key task: P04.03 Regenerate affected examples and authoring outputs from their owners; extend cold-generation, repair, detached installed-name and standalone checks.
- [ ] Key task: P04.04 Measure final bytes and preserve literal specimens, complete teaching, grammar, optional validator and fusion safeguards in both authoring forms.
Success criteria: E01-E05 pass in the delivered artifacts, complete manifests match fresh generation, both byte limits hold and no proposed helper or profile file is missing from its declared MAP.
Transition trigger: Targeted profile checks, delivery closure, identity and regeneration checks pass for the exact candidate revision.


### Phase 5: Verify and deliver the reusable capability
Objective: Establish an evidenced completion point for OAK authors and consuming hosts.
- [ ] Key task: P05.01 Run `python -m compileall oak build examples`, regenerate through the current owners, and run the complete build/AGENTS.md verification process, including `python -m build.examples` and `python build/examples.py`; then confirm repeat generation leaves no diff.
- [ ] Key task: P05.02 Review the actual diff, replaced scaffold markers and contracts, source ownership, original intent, required comparisons, all scoped AGENTS line bounds and integration with the selected baseline.
- [ ] Key task: P05.03 Write report.md with observed commands, revisions, selected file sets, state-preservation evidence, size results, limitations and each completed task's evidence.
- [ ] Key task: P05.04 Deliver the verified OAK source/validator identities, template selection instructions, examples and checks through PR 26 on the same branch for human review. Verify its final head and existing CI before marking it ready; do not merge. Identify remaining installation, visibility, linking and host acceptance work without executing it.
Success criteria: E01-E05 have observed evidence for the final candidate, every applicable implementation checkbox passes, and the handoff claims only tested OAK/template capabilities.
Transition trigger: The reusable OAK template capability is complete at the verified revision. Any deployment or live-host acceptance remains separately authorised.


### Validation Matrix

| Boundary | Stateless acceptance | Stateful acceptance | Rejected or failed cases and evidence |
| --- | --- | --- | --- |
| Shared source and population | Base only, no residual markers or state machinery | Same base plus selected extension | Unexpected/duplicate markers, inconsistent common content, unfilled scaffold accepted as operational knowledge; exact source/artifact comparison. |
| OAK contracts and composition | Complete inputs/outputs and declared effects | Same contracts plus owner and lifecycle; actual shared stateless call | Missing target, wrong type/binding, undeclared dependency, cycle, escaped root, foreign state access; parse/resolve and executed fixture results. |
| INDEX and MAP | Every selected static file; no state-only route | Static files plus fixed local scaffolds; `(...)` for generated contents | Missing/extra files, unused references, static files hidden by ellipsis, unbounded loading; independent manifests and bounded-read traces. |
| State and source separation | No state directory or persistent memory after use | Two owners remain isolated; compatible source update/rename preserves local state | Wrong instance, resolved script path used as state root, initial defaults overwriting existing data, unsupported schema; before/after hashes and explicit failure results. |
| CSV records and authority | Supplied policy remains input only | Stable IDs, escaping, required columns, scoped relative references, evidence links, one authoritative record and read-back checks | Duplicate IDs, dangling/escaping references, malformed quoting, stale index, intervening edits, orphaned record, interrupted publication and tool-owned write attempt; fixture records and reconciliation traces. |
| Loading, Git and retention | No state prompts, exclusions or retention steps | Saved choice reused, index-first active loading, real default exclusions and bounded opt-in exceptions | Configuration-only ignore claim, inherited/tracked-file conflicts, loaded private state at discovery, cleanup losing pending work or receipts; use disposable Git fixtures and actual `git check-ignore`/tracked-file inspection. |
| Execution and recovery | Invalid output/failure cannot masquerade as success | Explicit commit/resume and uncertainty handling preserve progress | Interrupted write or simulated external effect, writer conflict and failed verification; separately identify in-memory rollback, filesystem reconciliation and untested real effects. |
| Authoring delivery | Stateless authoring can produce base without installation | Same authoring can select inert stateful knowledge without acquiring runtime state | Operational extension entering fusion, teaching arrival firing, changed literal template, unapproved install, unavailable validator reported as pass; retain existing rejection/parity checks. |
| Regeneration and portability | Closed materialised skill at matching installed name | Closed selected graph with explicit owner boundary | Stale/missing/extra/symlink artifacts, source imports in detached checks, changed bytes after repeat generation; record complete manifests and sizes. |

The optional consumer validator remains distinct from repository profile checks. Repository fixtures may use Python and disposable files to establish observable behaviour; ordinary use of the authored memory workflow does not require those test helpers. Native host discovery, permissions, links and persistence need their own later evidence.

### Coordinating Instructions

- Timeline: implementation is authorised; make the identified decisions concrete and preserve the phase gates before their dependent product edits. Unrelated exploratory runtime work and live-client certification are not prerequisites for this plan.

- Boundaries: preserve unrelated work and private records. Do not create unrelated capabilities, configure global skills, modify live instances or perform unapproved external operations.

- Operating guidelines: use current owning sources and existing dependencies; apply routed Python and specialist guidance when implementing relevant formats. Keep new application contracts in justified structured OAK parts.

- Risk mitigation: establish the size and integration baseline first, exercise failure cases, keep state fixtures synthetic, and never infer actual host enforcement from template text or a valid schema.

### Contingencies

- If a shared owner or planning convention changes before implementation, then inspect the completed source, reconcile the proposal and pin the approved governing revision for the implementation task. Do not overwrite unrelated work or silently substitute revised governing inputs.

- If the complete shared knowledge cannot fit the current byte limits without losing required content, then report the measured conflict and seek a specific design decision before proceeding. Do not silently raise a limit or omit an authoring form.

- If a dependency cannot resolve within the approved boundary, then report it as a missing/changed dependency. Do not search arbitrary global skills or copy their source as a fallback.

- If file-tool guarantees cannot support a demonstrated memory case, then bound the workflow to one writer and explicit reconciliation, or propose the smallest justified helper with evidence of the need.

- If the chosen retention policy is ambiguous for existing or pending state, then preserve the data and return the unresolved decision rather than deleting it.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Retained requirements | R01-R09, E01-E06 and D01-D06 | This self-contained plan | AVAILABLE |
| Governing OAK/planning knowledge | Root and relevant scoped owners | Linked repository owners read at the pinned planning revision; re-pin for implementation | AVAILABLE |
| Selected implementation decisions | D01-D05 | Resolved within the approved scope below | AVAILABLE |
| Verification environment | Python 3.13.2 and declared dependencies | External environment, no editable repository install; baseline verification passed | AVAILABLE |
| Two populated profile packages | Synthetic examples and fixtures | Registered skill_profiles sources and inert package mappings | AVAILABLE |
| Installed-host verification | Each selected host variant | Separately authorised deployment acceptance, outside this product change | PENDING |

Supply: use existing OAK models, YAML support, standard-library CSV/path/JSON facilities and current build tooling. No new package, state service, provider backend, model asset or agent installation is proposed.

Transportation: regenerate examples and authoring products from their owning sources. Consumers use the verified delivery and revision rather than maintaining a second generic template. Actual installation, linking and synchronisation belong to a separately authorised host task.

Sustainment: retain concise durable template lessons under build/AGENTS.md during the approved implementation, example lessons under examples/AGENTS.md, and decisions and observed verification in this numbered plan. Do not duplicate package semantics or store private operational preferences in repository-wide guidance.

Rollback: preserve unrelated files and committed history. During product implementation regenerate deliveries from their prior source revision when needed, retaining all instance state and recovery evidence. Plan publication does not authorise a merge, history rewrite or live-instance rollback.

## 5. Command and Signal

1. The user owns acceptance of open choices and authorisation for product implementation or any separate deployment.

2. The implementing agent owns direct execution, scoped source updates, verification and delivery after approval. It preserves unrelated work and raises material scope or ownership conflicts instead of silently resolving them by expansion.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Conversation | Short progress/result messages | Material findings, decisions and final locations | During work and at delivery |
| This plan | Versioned Markdown | Proposed scope and later evidenced task state | On an approved decision or observed transition |
| Future report | report.md and necessary evidence | Actual implemented outcome and limitations | After implementation checks |

Reporting: distinguish confirmed requirements, proposed filenames, inspected sources, executed checks, deterministic demonstrations and untested platform behaviour. A prepared or published plan does not complete its product tasks. Report actual branch and commit confirmation separately from local draft preparation; neither a proposed revision nor an issued push is a confirmed checkpoint.

### Decisions and Boundaries

| ID | Decision | Selected resolution and rationale | Authority and remaining boundary |
| --- | --- | --- | --- |
| D01 | Template assembly and extension | build/skill_template.py owns one base and canonical population. _template/SKILL.md is stateless; _template/stateful.oak.md contains constants-only extension knowledge and the selected state slot. Common functional content is maintained once. | Selected within the approved implementation; no consumer runtime or new language construct. |
| D02 | Role presentation | Metadata plus title, purpose and principle define the skill. A roles constant presents DEFINE, optional ROUTE, LOOP, INDEX, MAP and ASSERT in that order, pointing to actual OAK definitions. The resource declarations derive INDEX and the complete SKILL_TREE. | Concrete rendered package specimens are in examples/skill_profiles/packages.oak.md; canonical OAK part order is preserved. |
| D03 | Dependency and instance identity | review-items calls the separate classify-item/processes/classify-item.oak.md export within an explicitly selected root. The stable capability is review-items/v1; the host separately binds owner and instance root and retains the complete pending checkpoint. Display names and compatible shared updates do not change ownership. | Host tools, source/dependency pinning and durable checkpoint storage remain explicit obligations. No global discovery, copied dependency or CALL-to-SKILL.md is introduced. |
| D04 | Memory, retention and recovery | Exact UTF-8 CSV id,name,reference columns, containing-index-relative references, JSON records and one active writer. First use requires a retention decision if none is saved. Full retains future source text; summary retains its digest, result and policy evidence. Pending work keeps its prepared mode. Existing records are preserved. Record-before-index publication reconciles exact orphans or completed pairs and rejects unknown conflicts. | Retention is a user choice when an instance is used. Git defaults to verified exclusions, with separately explicit bounded opt-in; loading, tracking and backup remain distinct. Tool-owned records are preserved. These tests use synthetic local data only. |
| D05 | Package leaves and size | The stateless package has SKILL.md and processes/classify-item.oak.md. The stateful shared package has SKILL.md and references/memory.oak.md. Its fixed local scaffold is .gitignore, state/configuration.json, policy/index.csv and priority.json, history/index.csv and runs/index.csv. Policy, history records and run contents are generated locally. Runtime and raw directories are omitted because this example does not need them. The inert package mapping preserves the complete graph without nested installed skills. | Baseline 1e21b227faae9a4f5ead997047af718db84ffd8d. Measured selected outputs fit the unchanged 24,000/128,000-byte budgets. Final acceptance rechecks sizes and manifests. |
| D06 | Host deployment outside this change | Storage/discovery, link mechanisms, update adoption, naming qualifiers, promotion and cross-repository permissions belong to the consuming host. No live installation, provider configuration or integration is included. | Separately authorised host work; not a prerequisite for this product delivery. |

### Public Design References

The supplied design cites the [Agent Skills specification](https://agentskills.io/specification), the [SKILL.state paper](https://arxiv.org/abs/2608.26263) and its [versioned text](https://arxiv.org/html/2608.26263v3). Retain them as public design context, not source authority for this plan, a dependency, or a mandate to reproduce a particular runtime. This plan adopts no universal `SKILL.state` file or portable state-file API. Its single-writer and explicit-reconciliation requirements stand independently of any paper's implementation. These external pages were not reverified during this privacy and planning-format task.

The proposal also cites public [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) and [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) documentation for discovery, invocation and resource conventions. They are retained references, not evidence of installed compatibility. Verify any platform-specific claim against its current owner documentation before relying on it. This plan makes no all-platform visibility, context-isolation or persistence-enforcement claim.

### Acknowledgement

This plan retains the reusable technical requirements and explicit open decisions. The user has authorised preparation, publication, the complete skill-template implementation, verification and review delivery. Earlier preparation-only wording is superseded; no merge or installation is authorised. The current root and scoped planning owners were read, but full source regeneration, repository checks and live-host acceptance are not established by this document. Do not mark any implementation task complete without revision-matched evidence.
