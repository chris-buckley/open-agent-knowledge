<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Generators, repository checks, freshness, the authoring prompt, generated reference, and the complete verification entry point."

generator-map: CSV<<
source,output
build/ebnf.py,outputs/oak.ebnf
build/docs.py,outputs/docs
build/authoring.py and build/authoring_guides.py,skills/oak-authoring knowledge and outputs/oak-authoring.oak.md
examples/catalog.py and registered Python sources,"scenario siblings, local dependency copies, and examples/catalog.oak.md"
>>

full-verification-command: "python -m build.examples"

direct-verification-command: "python build/examples.py"

authoring-product-byte-limits: {"skill-entry": 10000, "standalone-agent": 64000}

agent-graph-checks: ["exact path discovery", "canonical parse and render equality", "500-line maximum", "root router coverage", "one owned concern per file", "structured content before authored instructions", "duplicate authored-claim rejection", "obsolete owner rejection"]

plan-checks: ["apply the storage and format policy owned by docs/AGENTS.md", "check unique named plan directories and required plan files", "derive SMEAC section order and phase labels from the referenced schema", "check populated sections and compact phase checkboxes with unique task identifiers", "preserve the named historical format exceptions", "exercise rejected plan structures as well as accepted examples"]

freshness-rules: YAML<<
- Generate each product once from package sources.
- Require every generated path and byte to equal a fresh build.
- Remove stale generated pages during generation.
- Inspect generated changes before committing them.
- Treat EBNF as syntax documentation rather than validation authority.
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
>>
</constants>

<processes>
<process id="verify-repository" name="Verify repository">
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