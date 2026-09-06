<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Generation, generated product ownership, portable authoring capability, scope-safe fusion, validator identity, and complete verification."

generator-map: CSV<<
source,output
build/ebnf.py,generated/oak.ebnf
build/definitions.py,generated/definitions/*.oak.md
build/authoring.py and build/authoring_guides.py,generated/oak-authoring.skill and generated/oak-authoring.oak.md
examples/catalog.py and registered Python sources,"scenario siblings, local dependency copies, and examples/catalog.oak.md"
>>

full-verification-command: "python -m build.examples"

direct-verification-command: "python build/examples.py"

authoring-product-byte-limits: {"skill-entry": 10000, "standalone-agent": 64000}

agent-graph-checks: ["exact path discovery", "canonical parse and render equality", "500-line maximum", "root router coverage", "one owned concern per file", "structured content before authored instructions", "duplicate authored-claim rejection", "obsolete owner rejection"]

plan-checks: ["apply the storage and format policy owned by docs/AGENTS.md", "check unique named plan directories and required plan files", "derive SMEAC section order, phase labels, and comparison fields from the referenced schema", "check populated sections and compact phase checkboxes with unique task identifiers", "validate paired current and desired specimens, comparison authority, unique example identifiers, and required comparison coverage in success criteria", "preserve the named historical format exceptions", "exercise rejected plan structures as well as accepted examples"]

freshness-rules: YAML<<
- Generate each product once from package sources.
- Require every generated path and byte to equal a fresh build.
- Remove stale generated pages during generation.
- Inspect generated changes before committing them.
- Treat EBNF as syntax documentation rather than validation authority.
>>

ebnf-presentation: YAML<<
- Keep reference ordering and outer whitespace in build/ebnf.py and its build-only
  formatter. Consume package productions and surface projections without a second
  language definition.
- Use component-to-document sections, canonical part subsections, local alignment,
  and vertical long alternatives. The EBNF soft width is 100 Unicode code points;
  it is independent of the authored OAK width policy.
- Preserve source-qualified occurrences, ordered grammar tokens, quoted terminals,
  and descriptive special-sequence bodies. Opaque productions are width exceptions.
- Place source-owned convention notes beside their concern. Review every claim when
  shortening commentary; do not reflow embedded literal bodies.
- Preserve the known duplicate constant_target pair and opaque surface definitions
  until a separately authorised grammar change. Reject unexplained new duplication.
- Run build/checks/ebnf.py through the complete checks. Keep fixed expectations independent
  of formatting, exercise corruption rejections, and cover both grouping selections
  and orders.
- Keep the two grammar files byte-identical and both embedded grammar values equal.
  Preserve non-grammar knowledge and the existing skill and agent byte limits.
>>

example-checks: YAML<<
- Run the catalogue-driven checks in build/checks/human_examples.py through the existing
  complete entry point, including original shared schema examples and the repeat-marker
  helper exception.
- Check actual scenario file sets, both canonical groupings, bounded document closure,
  source-derived snapshot equality, and all declared demonstrations in detached copies
  with repository imports and network blocked.
- Exercise rejected missing dependencies, escaping and symlink targets, stale or missing
  snapshots, duplicate registration, missing teaching stages, and changed sample deliveries.
- Use build/checks/authoring.py to verify detached teaching closure, literal preservation,
  refused operational fusion, and skill-agent execution parity; retain the existing
  consent, identity, and byte limits.
- Use build/checks/statements.py for statement-body migration, obsolete-API rejection,
  literal preservation, independent JSON-LD ordering, and flat authoring assembly
  checks. Keep historical before-and-after evidence distinct from current contracts.
>>

coding-standard-checks: ["validate the pure OAK entry and every routed Python topic in both groupings", "require exact bounded document closure, unique source sections, and complete inert example references", "exercise rejected missing, duplicate, escaping, noncanonical, and malformed knowledge plus symbolic-link inputs", "keep migration evidence historical and general style judgement distinct from structural validation"]

output-map: CSV<<
path,meaning,owner
generated/oak-authoring.oak.md,"standalone authoring agent assembled from the skill, including inert scenario documents",build/authoring.py
generated/oak.ebnf,generated grammar reference,build/ebnf.py
generated/definitions,generated OAK construct definitions,build/definitions.py
generated/oak-authoring.skill,modular authoring bundle; install as oak-authoring,build/authoring.py
>>

output-rules: ["treat generated products as deliveries, never source authority", "do not edit by hand", "change the owning package or build source", "regenerate through the owner", "require fresh bytes before completion"]

capability-sources: CSV<<
source,owns
build/authoring_guides.py,guide composition and the authoring workflow
oak/rules/guidance.py,shared package authoring rules
examples/catalog.py and its registered sources,"shared teaching selection, scenario documents, sample data, and catalogue; source layout is owned by examples/AGENTS.md"
build/authoring_validator.py,"optional runtime helper, skill version, immutable validator revision, and fingerprints"
build/authoring.py and build/fusion.py,"standard skill metadata, generated knowledge files, and agent assembly"
>>

delivery-contract: YAML<<
- 'Distribute generated/oak-authoring.skill as a normal Git-versioned product: SKILL.md
  routes work, numbered references own language knowledge, references/oak.ebnf supplies
  grammar, and guides owns authoring, review, and validation practice. Keep scripts/validate.py
  optional. Do not add provider-specific metadata or directory README indexes.'
- Treat generated knowledge guides as the identical input documents for the skill
  and agent, not independently maintained prompts. Keep grammar material in EBNF.
- Use the default OAK render for the skill entry, shared knowledge documents, and
  standalone agent. The representation defaults are owned by oak/AGENTS.md.
- Deliver the registered core under assets/examples with its generated catalogue.
  Embed the identical complete document mapping as literal JSON knowledge in the review
  guide and assembled agent; Python demonstration hosts stay in repository scenario
  bundles.
- Generate _template/SKILL.md as generic inert OAK scaffolding with metadata placeholders,
  purpose, optional parts, and a literal SKILL_TREE block. Retain the deliberately
  empty references, assets/constants, assets/schemas, guides, processes, and scripts
  folders with empty .gitkeep files. Explain population and omission of unused resources
  without shipping a completed domain skill.
- Share the exact template entry as literal knowledge in guides/authoring.oak.md and
  the assembled agent. Keep template and teaching documents outside the operational
  fusion graph; displayed paths are not imports.
- Keep the skill entry as the only operational scope. Supporting fusion documents
  may define constants and schemas only. Refuse authored policy, state, arrivals,
  processes, or interfaces in supporting documents instead of widening their scope.
- Namespace supporting definitions and rewrite typed targets after explicit resolution.
  Never rewrite literal payloads, templates, scripts, tool names, or embedded teaching
  documents.
- Check source and dependency fingerprints against the immutable validator revision
  before accepting a new version. A package version string alone is not proof of a
  matching validator.
- Leave runtime validation inactive unless requested, and require separate explicit
  approval before downloads or dependency installation. Preserve no-install authoring
  and honest not-performed results.
>>

generated-layout: "Deliver only oak.ebnf, definitions/*.oak.md, oak-authoring.oak.md, and the oak-authoring.skill directory under generated. Keep maintained sources and repository guidance outside that tree."

skill-installation: "The .skill suffix identifies the repository bundle directory, not an archive or skill metadata name. Install its contents in a directory named oak-authoring to match name: oak-authoring in SKILL.md. The Agent Skills naming contract is https://agentskills.io/specification#name-field."

regeneration-checks: ["Generate the optional validator delivery byte-for-byte from build/authoring_validator.py; never load the delivered helper as build source.", "Require complete generated file and directory sets, reject symlinks before writing, and prune only each generator-owned subtree.", "Run cold generation and repair in disposable snapshots without previous products, then compare complete path and byte manifests.", "Verify detached installed-name skill and standalone-agent closure without sibling definitions or repository build imports."]
</constants>

<processes>
<process id="verify-repository" name="Verify repository">
ACT Use a Python environment outside the checkout that satisfies pyproject.toml and has no editable repository install; detached checks reject all imports from repository paths. ()
ACT Use a clean working snapshot when ignored local checkouts affect repository ownership scans; include pending source changes and preserve the local checkouts. ()
ACT Run <RULES> before accepting generated product changes. (RULES=$constant.regeneration-checks)
ACT Preserve <RULES> when generating the modular bundle and assembled authoring agent. (
  RULES=$constant.delivery-contract,
)
ACT Apply <RULES> to every generated product; use constant.output-map to locate its owning source. (
  RULES=$constant.output-rules,
)
ACT Use <GENERATORS> to regenerate every affected product from its source. (
  GENERATORS=$constant.generator-map,
)
ACT Enforce <PRODUCT_LIMITS> and <AGENT_CHECKS> while validating generated and scoped knowledge products. (
  PRODUCT_LIMITS=$constant.authoring-product-byte-limits,
  AGENT_CHECKS=$constant.agent-graph-checks,
)
ACT Apply <PLAN_CHECKS> to persistent plan records and their verification examples. (
  PLAN_CHECKS=$constant.plan-checks,
)
ACT Apply <CHECKS> when Python convention knowledge or its root routing changes. (
  CHECKS=$constant.coding-standard-checks,
)
ACT Apply <EBNF> when changing the grammar reference or its source presentation. (
  EBNF=$constant.ebnf-presentation,
)
ACT Apply <EXAMPLES> when source registration, fixture delivery, or shared teaching changes. (
  EXAMPLES=$constant.example-checks,
)
ACT Run <MODULE_CHECK> and <DIRECT_CHECK> after compilation and generation. (
  MODULE_CHECK=$constant.full-verification-command,
  DIRECT_CHECK=$constant.direct-verification-command,
)
ACT Apply <FRESHNESS> and require repeated generation to leave no diff. (
  FRESHNESS=$constant.freshness-rules,
)
</process>
</processes>