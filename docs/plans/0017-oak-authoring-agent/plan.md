# Build OAK authoring agents

Prepared: 2026-09-08T08:44:47+10:00
Classification: INTERNAL
Plan identity: 0017-oak-authoring-agent
Readiness: Discussion draft. Confirmed intent and proposed design are distinguished below.
Authorisation: Converse, inspect relevant sources and maintain this plan. Product implementation has not started.

## 1. Situation

### Operating Environment

OAK already supplies shared authoring knowledge, a modular skill, a standalone authoring document and native Codex explorer artifacts. This plan develops the authoring agent's responsibilities and workflow, with Codex as the primary platform and Claude as another adaptor.

### Current State

The inspected baseline is main at `8a5d160b3c2a29af111fc662d473191d9b4a092e`. Existing OAK authoring knowledge and native Codex explorer artifacts provide inputs for this design.

### Confirmed Intent

- Support create, read, update and delete operations on OAK.
- Help a user clarify what the OAK must do, building a draft abstract syntax tree (AST) as that conversation progresses.
- When developing intent collaboratively, produce the OAK once the user is satisfied with the intended behavior.
- Also accept direct requests, including creating OAK from scratch and transforming supplied material into OAK.
- Keep direct operations available independently of the intent-elicitation workflow. A clear direct request does not require a compulsory interview.
- Show the evolving AST as a readable tree, with unresolved decisions marked. Use it to communicate the knowledge and behavior the OAK is intended to express.
- Define the conversational response format as an OAK schema and use that structure to guide intent development.
- Establish what kind of OAK artifact the user needs, including an agent, a single-shot prompt, a compact knowledge definition, an AGENTS.md file, a skill or a stateful skill.
- Keep artifact-kind definitions in one extensible constant catalogue, fixed during each run and maintained between versions.
- Establish the artifact's tool requirements and intended execution context, including relevant tools and MCP servers. Focus this discovery on tools rather than adding a skill-discovery workflow.
- Preserve the proposed process AST, including its shared draft, transformation, review, rendering, validation and response processes, when adding artifact-kind and tool-context discovery.
- Use the APS authoring agents as legacy interaction references and improve the design rather than porting their workflow unchanged.
- Use Codex as primary and Claude as another adaptor.
- Keep platform adaptors separate and deliver them with the authoring skill under its platforms directory. Move maintained product adaptor knowledge out of repository-support .agents paths into build-owned skill resources.
- Deliver agents and their native definitions. Platform implementation code is outside scope.

### Working Process Structure

The user has retained the conceptual AST below as the design direction. Artifact-kind and tool-context discovery extend that structure. Labels are working names; exact process contracts and draft representation still need design. This is a readable plan view, not a canonical OAK AST instance.

```text
oak-authoring-agent
  delivery                              # One authoring capability with native adaptors
    oak-authoring.skill                 # Shared authoring knowledge and workflow
      platforms                         # Separate platform-specific resources
        codex                           # Primary adaptor and native agent definition
        claude                          # Another adaptor and native agent definition
  constants
    artifact-kinds                      # Extensible catalogue, fixed during each run
      agent                             # A role with defined behavior and execution context
      single-shot-prompt                # Instructions for one bounded invocation
      compact-knowledge                 # A concise definition of knowledge
      agents-md                         # Scoped repository or directory knowledge
      skill                             # A reusable capability with its supporting resources
      stateful-skill                    # A skill with explicit persistent-state ownership
  request-routing                       # Select the operation and interaction path
    direct-request                      # Use clear supplied intent and known context
    guided-request                      # Develop unresolved intent with the user
  processes
    determine-artifact-kind             # Establish what the requested OAK is for
      read artifact-kinds               # Reuse the catalogue rather than repeat a fixed list
      select-kind                       # Use clear intent or resolve a material ambiguity
      apply-kind-guidance               # Select justified structure and delivery requirements
    establish-tool-context              # Establish needed and available capabilities
      required-capabilities             # Work the artifact needs tools to perform
      tools-and-mcp-servers             # Relevant providers and their exact tool operations
      contracts-and-effects             # Inputs, outputs, read/write effects and permission limits
      availability                      # Distinguish confirmed tools from unverified requirements
      no-tools-needed                   # An explicit valid outcome when tools add no purpose
    create-oak                          # Create OAK from a clear request or agreed draft
    read-oak                            # Inspect and explain existing OAK
    update-oak                          # Change specified meaning and retain unrelated content
    delete-oak                          # Check affected references and remove requested content
    elicit-intent                       # Guide the user while intent is developing
      incorporate-user-input            # Capture decisions, corrections and requirements
      resolve-artifact-and-tool-gaps    # Use the two context processes when information is missing
      call maintain-draft-ast           # Update the same evolving model
      call review-draft                 # Find gaps, contradictions and assumptions
      call compose-response             # Show the model and the next useful decision
      continue-or-handoff                # Continue discussion or invoke the requested operation
    transform-source                    # Interpret source material before Create or Update
      extract-meaning                   # Identify knowledge, behavior and constraints
      identify-ambiguity                # Expose interpretation gaps
    maintain-draft-ast                   # Shared by direct and guided requests
      apply-decisions                   # Add, revise or remove affected draft nodes
      retain-unaffected-meaning         # Preserve established decisions
      track-unresolved-meaning          # Keep uncertainty explicit
    review-draft                        # Check the model against the requested intent
      check-completeness                # Find information needed for the operation
      check-consistency                 # Find contradictory requirements or relationships
      assess-readiness                  # Explain remaining work; readiness is not authorization
    render-and-validate                 # Produce OAK from the agreed model
      render-oak                        # Preserve meaning rather than reinterpret it
      check-output                      # Report checks actually performed and their results
    compose-response                    # Use the response schema to shape each reply
      derive-readable-ast-view          # Present a useful level of detail
      explain-changes                   # Show what the latest exchange changed
      select-next-step                  # Ask, propose, explain readiness or report a result
  schemas
    authoring-draft                     # Draft AST plus decision annotations
      artifact-kind                     # Intended use of this OAK output
      tool-context                      # Needed tools, providers, contracts and availability
      intended-knowledge-and-behavior   # Meaning the resulting OAK must express
      confirmed-decisions              # Meaning established by the request or user decisions
      proposed-decisions               # Suggestions awaiting agreement
      unresolved-decisions             # Gaps connected to the affected draft nodes
    conversation-response              # Schema-guided interaction; exact fields remain open
      understanding                    # Address the latest contribution and intended outcome
      intent-ast                       # Show relevant structure and decision status
      change                           # Explain changes to the draft
      next-decision                    # Connect the question to the meaning it affects
      readiness                        # Explain whether the requested operation can proceed
```

Independent CRUD processes and optional intent elicitation remain directly callable. Transforming material into OAK must preserve the source's meaning and disclose unresolved interpretation. Its exact handoff to Create or Update, formal input and output shapes, and write boundaries remain design decisions.

### Artifact Kind and Tool Context

The authoring agent can produce several kinds of OAK output. Its own Codex and Claude delivery adaptors are distinct from the intended consumer and execution environment of the artifact being authored. Artifact kinds come from a shared catalogue, with the following initial entries.

| Catalogue entry | Intended output |
| --- | --- |
| agent | An agent role with defined behavior, interfaces and execution context. |
| single-shot-prompt | Instructions for one bounded invocation. |
| compact-knowledge | A compact representation of knowledge using justified OAK parts. |
| agents-md | Host-scoped repository or directory knowledge in AGENTS.md; directory inheritance does not imply OAK imports. |
| skill | A reusable capability packaged with its supporting resources, without owned persistent state by default. |
| stateful-skill | A skill with justified persistent state, explicit ownership and lifecycle behavior. |

Proposed catalogue records contain an identifier, purpose, structure guidance, state expectations and delivery conventions. Keep one maintained source and derive its skill and standalone-agent representations from it. Adding or revising a kind is a source change between versions, not a mutation of the catalogue during an authoring run. Extend associated guidance and verification when a new kind needs them. The authoring agent can describe stateful skills without making its own shared functional definition mutable or introducing a persistence service.

Artifact-kind discovery should reuse clear intent from the request and ask when the distinction changes the design. The selected kind guides the necessary OAK parts, entry points, lifetime, outputs and delivery form. Include only justified parts; a compact knowledge definition does not automatically need executable processes, mutable state or tools.

Tool-context discovery should establish the capabilities needed by the intended artifact, the relevant native tools or MCP servers, and the exact operations and input/output contracts when available. Record read/write effects and applicable permission limits. A server name alone does not establish that a particular operation is available or authorized. Tools available to the authoring agent are not automatically available to the artifact's eventual consumer.

Use existing declarations or supported read-only inspection to confirm availability where possible. Keep requested or unverified tools distinct from confirmed capabilities, and accept that no tools may be needed. Ask about material gaps rather than repeating facts already supplied. This process defines requirements and bindings; it does not install tools, connect accounts or implement MCP servers or platform services.

Both direct requests and guided conversations use these context processes. A direct request can supply enough information to continue immediately. During elicitation, an unresolved artifact-kind or tool-context node can determine the next question and is updated by the user's answer.

### Platform Adaptor Ownership and Layout

The inspected repository already delivers `generated/oak-authoring.skill/platforms/codex/adaptor.oak.md`, derived from `.agents/adaptors/codex/adaptor.oak.md`. The plan moves that maintained product knowledge into build-owned authoring resources and adds a separate Claude adaptor. Repository support can refer to those sources without owning a second copy.

APS keeps each platform's adaptor and optional native templates beneath the skill's `platforms/` directory, separate from its shared language references. Use that separation as a layout reference while retaining OAK contracts and scope rules. The proposed OAK locations are `platforms/codex/adaptor.oak.md` and `platforms/claude/adaptor.oak.md`, with native authoring-agent definitions in each platform's `templates/` subtree.

The shared authoring core owns CRUD, intent elicitation, the AST, the response schema and artifact-kind meaning. Each platform adaptor owns native file conventions, metadata shapes, tool naming, supported host interaction and declared capability limits. Platform knowledge stays declarative and separate from shared OAK meaning. Keep role-specific settings distinct from platform contracts so the existing explorer's read-only profile does not become the authoring agent's profile by accident.

Use `build/authoring_resources/` as the proposed maintained resource tree, mirrored into the delivered skill where applicable. Existing build generators remain responsible for loading resources, assembling OAK and rendering native metadata. This is artifact generation; no Codex or Claude runtime, MCP server implementation, account connector or installation service is added. Generated files remain outputs and are not edited as sources.

### Conversation Schema Direction

The user wants the response schema to help drive the conversation. The working proposal is that each reply updates the draft AST, derives a readable view from it, and selects the next useful decision from unresolved or contradictory intent. The AST carries the intended meaning; any prose summary is a view of that meaning rather than a second independently maintained specification.

| Candidate response component | Role in the conversation |
| --- | --- |
| Understanding | Briefly answer or acknowledge the user's latest contribution and relate it to the intended outcome. |
| Intent AST | Show the relevant draft structure, including artifact kind and tool context, and distinguish confirmed, proposed and unresolved meaning. |
| Change | Explain what the latest input changed in the draft. |
| Next decision | Identify the affected part of the AST, explain why the decision matters, and ask the next useful question or present a concrete proposal. |
| Readiness | State what remains before the requested operation can proceed, without treating the agent's assessment as user authorization. |

These are proposed component responsibilities, not approved field names or a finished schema. Do not force questions or empty sections when a direct request is already clear. Suggested answers should help the particular decision rather than satisfy a fixed option count.

Proposed continuity rule: the same agreed draft feeds the requested CRUD operation and subsequent OAK rendering. Do not reconstruct the intended behavior from a looser summary after the user has reviewed it. The exact representation of incomplete AST nodes and their relationship to the canonical OAK model still needs design; unresolved intent must not become invented executable content.

### APS Interaction Reference

Read-only inspection covered the installed [APS v1.2.1 authoring agent](C:/Users/User/.claude/agents/aps-v1.2.1.md) and the [APS v1.2.2 Claude agent template](C:/Users/User/.codex/skills/agnostic-prompt-standard/platforms/claude-code/templates/.claude/agents/aps-v1.2.2.md). Their `ASK_V1` format shows a state label, an intent block, questions and reply instructions; `INTENT` is a string. The v1.2.2 `refine` process infers intent, blockers and readiness, while its question rules require four suggestions plus a fifth catch-all choice.

Use the visible evolving intent and focused questioning as reference points. The proposed OAK improvement ties questions, corrections and readiness to identifiable parts of the draft AST, supports meaningful choices without a fixed option count, and preserves the direct-operation route. These observations describe the inspected files, not a claim about every APS version or measured runtime behavior.

### Challenges

- Draft completeness: distinguish unresolved intent from facts already represented in the AST.
- Approval: preserve the difference between an authorized direct request and a conversation still developing the requested behavior.
- Shared meaning: retain one authoring definition across the Codex and Claude adaptors.
- Delivery size: preserve the current skill-entry and standalone-agent byte limits while retaining required teaching, grammar and validation safeguards.

### Supporting Factors

- Higher intent: make OAK authoring useful both as guided assistance and as a directly callable capability.
- Adjacent efforts: the existing authoring skill and standalone authoring document share the knowledge this agent will consume.
- Supporting resources: existing authoring sources, canonical OAK models, examples, rendering and validation knowledge.

### Assumptions

- Existing OAK constructs can represent the required agent behavior; this has not yet been checked against a complete design.
- Native agent definitions can carry the shared instructions using each platform's existing capabilities.

### Constraints and Limitations

- Constraint: create agent artifacts without implementing Codex, Claude, a replacement host, or platform runtime services.
- Constraint: preserve existing authorization; ask for missing intent or scope when it affects the requested operation.
- Limitation: AST detail level and incomplete-node representation, exact response and catalogue schemas, native adaptor contracts, tool contracts, CRUD scope, transformation fidelity and acceptance tests still need discussion.

## 2. Mission

The maintainer and user define a complete OAK authoring-agent design in this repository before authorizing its implementation, so direct requests and guided intent development lead to clear OAK outcomes.

Task: settle the behavior, artifact-kind and tool-context discovery, shared AST workflow, native adaptor boundaries and acceptance criteria through this conversation.
Purpose: support practical OAK creation and maintenance while helping users make uncertain intent precise.
End state: the user agrees to a complete implementation plan for shared authoring behavior, a primary Codex agent and a Claude adaptor, with no platform implementation code.

### Directory Changes

Baseline: main at `8a5d160b3c2a29af111fc662d473191d9b4a092e`, inspected source files and the generated authoring-skill inventory. The planned tree is the proposed source and delivery layout for this design. It is not a claim that the future files exist or that implementation is authorized.
Legend: [add] new; [modify] changed; [move from PATH] relocated; [remove] deleted; [keep] unchanged context; [check] verify and change only if needed.
Current:
```text
open-agent-knowledge/
  .agents/
    adaptors/codex/adaptor.oak.md       # Maintained product adaptor in repository support
    rules/context.oak.md               # Routes native-artifact knowledge to that source
  build/
    AGENTS.md                          # Authoring, adaptor and generation ownership
    agents.py                          # Explorer bundle and Codex metadata rendering
    authoring.py                       # Skill generation and standalone assembly
    authoring_guides.py                # Shared knowledge and current authoring workflow
    authoring_validator.py             # Optional validator and product identity
    fusion.py                          # Existing scope-safe assembly
    checks/
      __init__.py                      # Registered verification entry points
      authoring.py                     # Skill/agent parity, teaching and size checks
      agent_deliveries.py              # Explorer and native artifact checks
      outputs.py                       # Complete generated inventories and freshness
  generated/
    oak-authoring.oak.md               # Standalone authoring output
    oak-authoring.skill/
      SKILL.md                         # Shared operational authoring entry
      references/
        00-structure.oak.md            # OAK structure and ownership
        01-schemas.oak.md              # Information shapes
        02-constants.oak.md            # Fixed knowledge
        03-state.oak.md                # Persistent state semantics
        04-interfaces.oak.md           # Public information boundaries
        05-triggers.oak.md             # Arrival routing
        06-processes.oak.md            # Ordered work and composition
        07-instructions.oak.md         # Instruction placement
        oak.ebnf                      # Grammar reference
      guides/
        authoring.oak.md               # Authoring method and template knowledge
        review.oak.md                  # Review and complete literal teaching
        validation.oak.md              # Optional validator use and evidence limits
        subagent-orchestration.oak.md  # Existing delegation knowledge
      assets/examples/
        catalog.oak.md                 # Teaching selection and source mapping
        fixed_knowledge/example.oak.md # Fixed-knowledge teaching
        shape_gallery/example.oak.md   # Schema shape teaching
        shape_writer/
          example.oak.md               # Stateless process teaching
          sample.oak.md                # Complete sample input
          shape_gallery.oak.md         # Local teaching dependency
        compound_growth/
          example.oak.md               # Persistent-state teaching
          sample.oak.md                # Complete sample input
      platforms/codex/adaptor.oak.md    # Generated copy of the maintained adaptor
      scripts/validate.py              # Optional helper delivery
      _template/
        SKILL.md                       # Generic inert skill scaffold
        references/.gitkeep            # Reserved reference area
        assets/constants/.gitkeep      # Reserved fixed-knowledge area
        assets/schemas/.gitkeep        # Reserved shape area
        guides/.gitkeep                # Reserved guidance area
        processes/.gitkeep             # Reserved process area
        scripts/.gitkeep               # Reserved helper area
    oak.agents/
      adaptors/codex/adaptor.oak.md     # Derived adaptor copy for the explorer bundle
      parallel_exploration/
        coordinator.oak.md             # Existing coordinator
        explorer.oak.md                # Existing leaf worker
        sample.oak.md                  # Existing complete fixture input
        codex/.codex/agents/oak-explorer.toml # Existing native explorer
```
Planned:
```text
open-agent-knowledge/
  .agents/
    adaptors/codex/adaptor.oak.md       # [remove] Retire the old maintained source location
    rules/context.oak.md               # [modify] Route to build-owned platform resources
  build/
    AGENTS.md                          # [modify] Catalogue and skill-owned platform contracts
    agents.py                          # [modify] Reuse platform resources; render native metadata
    authoring.py                       # [modify] Assemble shared resources and native outputs
    authoring_guides.py                # [modify] CRUD, intent AST, schemas and catalogue use
    authoring_validator.py             # [check] Reconcile version and validator identity
    fusion.py                          # [keep] Preserve existing scope-safe assembly
    authoring_resources/
      assets/constants/
        artifact-kinds.oak.md          # [add] Sole maintained artifact-kind catalogue
      platforms/
        codex/
          adaptor.oak.md               # [move from .agents/adaptors/codex/adaptor.oak.md] Separate Codex platform knowledge
        claude/
          adaptor.oak.md               # [add] Separate Claude platform knowledge
    checks/
      __init__.py                      # [modify] Register authoring-agent behavior checks
      authoring.py                     # [modify] Catalogue, resource closure and parity checks
      authoring_agent.py               # [add] Direct/guided CRUD, transformation and draft checks
      agent_deliveries.py              # [modify] Platform contracts and native authoring outputs
      outputs.py                       # [modify] Complete inventories and regeneration checks
  docs/plans/0017-oak-authoring-agent/
    plan.md                            # [add] Agreed authoring design and implementation plan
  generated/
    oak-authoring.oak.md               # [modify] Same complete shared authoring knowledge
    oak-authoring.skill/
      SKILL.md                         # [modify] Shared operational authoring entry
      references/
        00-structure.oak.md            # [keep] OAK structure and ownership
        01-schemas.oak.md              # [keep] Information shapes
        02-constants.oak.md            # [keep] Fixed knowledge
        03-state.oak.md                # [keep] Persistent state semantics
        04-interfaces.oak.md           # [keep] Public information boundaries
        05-triggers.oak.md             # [keep] Arrival routing
        06-processes.oak.md            # [keep] Ordered work and composition
        07-instructions.oak.md         # [keep] Instruction placement
        oak.ebnf                      # [keep] Grammar reference
      guides/
        authoring.oak.md               # [modify] Catalogue, intent and platform selection
        review.oak.md                  # [modify] Intent fidelity and draft review guidance
        validation.oak.md              # [check] Preserve consent and actual-check reporting
        subagent-orchestration.oak.md  # [keep] Existing delegation knowledge
      assets/
        constants/
          artifact-kinds.oak.md        # [add] Generated copy of the shared catalogue
        examples/
          catalog.oak.md               # [keep] Teaching selection and source mapping
          fixed_knowledge/example.oak.md # [keep] Fixed-knowledge teaching
          shape_gallery/example.oak.md # [keep] Schema shape teaching
          shape_writer/
            example.oak.md             # [keep] Stateless process teaching
            sample.oak.md              # [keep] Complete sample input
            shape_gallery.oak.md       # [keep] Local teaching dependency
          compound_growth/
            example.oak.md             # [keep] Persistent-state teaching
            sample.oak.md              # [keep] Complete sample input
      platforms/
        codex/
          adaptor.oak.md               # [modify] Codex-only native conventions and contracts
          templates/.codex/agents/
            oak-authoring.toml         # [add] Generated native Codex authoring agent
        claude/
          adaptor.oak.md               # [add] Claude-only native conventions and contracts
          templates/.claude/agents/
            oak-authoring.md           # [add] Generated native Claude authoring agent
      scripts/validate.py              # [check] Regenerate only through its source owner
      _template/
        SKILL.md                       # [keep] Generic inert skill scaffold
        references/.gitkeep            # [keep] Reserved reference area
        assets/constants/.gitkeep      # [keep] Reserved fixed-knowledge area
        assets/schemas/.gitkeep        # [keep] Reserved shape area
        guides/.gitkeep                # [keep] Reserved guidance area
        processes/.gitkeep             # [keep] Reserved process area
        scripts/.gitkeep               # [keep] Reserved helper area
    oak.agents/
      adaptors/codex/adaptor.oak.md     # [modify] Derived from the same skill-owned source
      parallel_exploration/
        coordinator.oak.md             # [keep] Existing coordinator
        explorer.oak.md                # [keep] Existing leaf worker
        sample.oak.md                  # [keep] Existing complete fixture input
        codex/.codex/agents/oak-explorer.toml # [keep] Existing read-only native explorer
```
Ownership: docs/AGENTS.md owns this plan. build/AGENTS.md owns the catalogue, authoring workflow, platform resources, generators and checks. build/authoring.py generates the skill and standalone authoring output; build/agents.py supplies native rendering and the existing explorer bundle. Maintained resource files under build/authoring_resources are the sole source for their generated copies. The listed file names and source split are a concrete proposal for review; product implementation is not authorized by recording them here.
Verification: compare the declared skill tree with complete generated file and directory manifests, including hidden native-template directories and retained scaffold files. Check one-source catalogue/adaptor identity, native instruction fidelity, both platform metadata contracts, direct and guided behavior, actual validation reporting, existing explorer behavior, scope-safe assembly, byte limits and unchanged literal teaching. Search consumers of the retired .agents adaptor source, run both complete verification entry points, and require repeated generation to leave no diff before accepting implementation. This discussion draft receives structural plan checks only.

### State Comparisons

#### E01: An AST-guided conversation turn
Authority: illustrative
Current state:
The inspected APS `ASK_V1` format presents free-text intent and questions. It does not define an AST field or a question-to-node relationship in that response contract.
Desired state:
The following is a readable illustration for this authoring-agent discussion. It is not a canonical OAK AST instance or the final response schema.
```text
Understanding
The agent supports direct OAK operations and guided intent development.

Intent AST
authoring-agent
  processes
    create-oak        [confirmed responsibility]
    read-oak          [confirmed responsibility]
    update-oak        [confirmed responsibility]
    delete-oak        [confirmed responsibility]
    elicit-intent     [confirmed responsibility]
  conversation
    draft AST         [confirmed: visible and progressively refined]
    response schema   [open: exact content and structure]
  authoring context
    artifact kind     [confirmed: establish the output's intended use]
    tools and MCP     [confirmed: establish needs and verify availability where possible]
  delivery
    Codex             [confirmed: primary]
    Claude            [confirmed: another adaptor]

Change
The conversation response is now an explicit schema concern.

Next decision
Which information must every guided response show so the user can
understand and correct what the OAK is intended to do?

Readiness
The process separation is agreed. The conversation schema is still being designed.
```
Acceptance: Review whether the specimen makes intended behavior, unresolved meaning and the next decision clear. Field names, display depth and layout remain open; do not adopt this illustrative rendering as a new OAK language construct.

## 3. Execution

Intent: Help the user settle what the authoring agent should do and how people or other agents will use it. Keep confirmed requirements distinct from design suggestions and unresolved questions.
Concept of operations: Discuss the independent operations, intent workflow and AST interaction before fixing the native deliveries. Record decisions here and turn them into one complete implementation plan once the user is happy with the behavior.

### Phase 1: Agree the authoring behavior
Objective: Resolve the agent's responsibilities, interaction model and delivery boundaries.
- [x] Key task: P01.01 Agree independent CRUD processes and their use of intent elicitation.
- [ ] Key task: P01.02 Define how the draft AST develops, is presented and records unresolved decisions, including the response schema that guides each exchange.
- [ ] Key task: P01.03 Specify direct creation and source-to-OAK transformation outcomes for the six initial catalogue entries and define how the catalogue evolves.
- [ ] Key task: P01.04 Define shared knowledge, separate skill-owned Codex and Claude adaptor contracts, tool-context discovery and acceptance examples.
- [ ] Key task: P01.05 Prepare the complete implementation design and affected-file diagram for user review.
Success criteria: Every confirmed requirement has an agreed behavior and acceptance criterion; unresolved design choices are settled before implementation approval.
Transition trigger: The user approves the complete implementation plan and its scope.

### Coordinating Instructions

- Timeline: proceed through the conversation without a preset implementation deadline.
- Boundaries: maintain this authoring-agent design draft; do not begin platform or product implementation.
- Operating guidelines: answer direct questions, offer concrete proposals and record the user's decisions.
- Risk mitigation: use examples to distinguish requested behavior from assumptions before encoding it in the AST.

### Contingencies

- If a direct request lacks material intent or scope, ask for that information and update the draft instead of inventing it.
- If the design needs a platform capability that is unavailable, identify the exact gap and revise the design with the user.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| OAK authoring knowledge | One shared foundation | Existing package, build and example sources | AVAILABLE |
| Agent adaptor designs | Codex and Claude | Native agent definition contracts, to inspect during design | PENDING |

Supply: reuse existing authoring knowledge and inspect additional sources only as the design requires.
Transportation: record the conversation's decisions in this plan before producing agent artifacts.
Sustainment: maintain one shared meaning and record native differences with their adaptor owner.
Rollback: reverse only plan edits that introduce an error, preserving the user's confirmed requirements.

## 5. Command and Signal

1. The user owns intended behavior, scope and implementation approval.
2. The main agent facilitates the discussion, inspects evidence and maintains the plan.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Design discussion | This conversation | Clarify intent and settle decisions | As needed |
| Plan record | This document | Retain confirmed scope and open design work | After material decisions |

Reporting: distinguish confirmed intent, proposed design and completed verification. Do not report a discussion draft as an implemented agent.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Intended behavior and native delivery scope | User | Return unresolved choices to the user |
| Source interpretation and design proposal | Main agent | Ask when evidence cannot settle a material ambiguity |
| Product implementation | User approval of a complete plan | Preserve the planning boundary until approved |

### Acknowledgement

The user's confirmed requirements are recorded above. Independent CRUD and optional intent elicitation are agreed; detailed schemas, process contracts and delivery design remain under discussion. Implementation is not yet authorized.
