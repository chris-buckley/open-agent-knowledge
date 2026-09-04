<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Generators, repository checks, freshness, the authoring prompt, generated reference, and the complete verification entry point."

generator-map: CSV<<
source,output
build/ebnf.py,outputs/oak.ebnf
build/docs.py,outputs/docs
build/authoring.py,outputs/authoring.md
examples Python modules,sibling .oak.md snapshots
>>

full-verification-command: "python -m build.examples"

direct-verification-command: "python build/examples.py"

authoring-prompt-byte-limit: 18000

agent-graph-checks: ["exact path discovery", "canonical parse and render equality", "500-line maximum", "root router coverage", "one owned concern per file", "structured content before authored instructions", "duplicate authored-claim rejection", "obsolete owner rejection"]

freshness-rules: YAML<<
- Generate each product once from package sources.
- Require every generated path and byte to equal a fresh build.
- Remove stale generated pages during generation.
- Inspect generated changes before committing them.
- Treat EBNF as syntax documentation rather than validation authority.
>>
</constants>

<processes>
<process id="verify-repository" name="Verify repository">
ACT Use <GENERATORS> to regenerate every affected product from its source. (GENERATORS=$constant.generator-map)
ACT Enforce <PROMPT_LIMIT> and <AGENT_CHECKS> while validating generated and scoped knowledge products. (PROMPT_LIMIT=$constant.authoring-prompt-byte-limit, AGENT_CHECKS=$constant.agent-graph-checks)
ACT Run <MODULE_CHECK> and <DIRECT_CHECK> after compilation and generation. (MODULE_CHECK=$constant.full-verification-command, DIRECT_CHECK=$constant.direct-verification-command)
ACT Apply <FRESHNESS> and require repeated generation to leave no diff. (FRESHNESS=$constant.freshness-rules)
</process>
</processes>