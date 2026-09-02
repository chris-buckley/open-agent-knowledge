<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Trigger seeds fill the selected process input schema; each seeded value validates before the process runs.
A source-backed trigger fires on an arrival at its exact interface; its event text stays the semantic signpost.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact ingress interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.

Run a tool named agent.<name> as the custom agent <name> through the agent tool.
Treat a custom agent's final message as the outputs of its ACT line.
Start every PAR child in one turn before you wait for any result.
Do not research or verify claims yourself.
Report only claims that survived the challenge.
Write the report in plain words and expand each acronym the first time it appears.
End each finding with the link that proves it.
Keep the report brief: one line per finding.
</instructions>

<schemas>
<schema id="research-request" name="Research Request" purpose="Carry one question to research.">
Question: <QUESTION>

WHERE:
- <QUESTION> is string; is non-empty; the question the report must answer.
</schema>

<schema id="source-findings" name="Source Findings" purpose="Carry the findings of the three researchers for one question.">
Repository findings: <REPOSITORY_FINDINGS>
Web findings: <WEB_FINDINGS>
Docs findings: <DOCS_FINDINGS>

WHERE:
- <REPOSITORY_FINDINGS> is string; is non-empty; the cited repository findings.
- <WEB_FINDINGS> is string; is non-empty; the cited web findings.
- <DOCS_FINDINGS> is string; is non-empty; the cited documentation findings.
</schema>

<schema id="report-request" name="Report Request" purpose="Carry the question and the challenged findings the report is written from.">
Question: <QUESTION>
Confirmed findings: <CONFIRMED_FINDINGS>
Refuted claims: <REFUTED_CLAIMS>

WHERE:
- <QUESTION> is string; is non-empty; the question the report must answer.
- <CONFIRMED_FINDINGS> is string; the claims that survived the challenge, empty when none.
- <REFUTED_CLAIMS> is string; the claims the challenge refuted, with reasons, empty when none.
</schema>

<schema id="research-report" name="Research Report" purpose="Carry one brief, challenged, and linked answer with the TLDR first.">
TLDR: <TLDR>

Findings:
<FINDINGS>

Dropped claims:
<DROPPED_CLAIMS>

WHERE:
- <TLDR> is string; is non-empty; has at most 3 lines; is at most 400 characters; the answer in plain words.
- <FINDINGS> is string; has at most 12 lines; one confirmed finding per line, each ending with the link that proves it, empty when none.
- <DROPPED_CLAIMS> is string; has at most 6 lines; one refuted claim per line in plain words, empty when none.
</schema>
</schemas>

<triggers>
trigger.research-requested.event := "Accelerator research is requested."
trigger.research-requested.source := interface.research-request-input
trigger.research-requested.process := process.publish-report
trigger.research-requested.seed.QUESTION := $interface.research-request-input.QUESTION
</triggers>

<processes>
<process id="find-source-findings" name="Find source-findings" input="schema.research-request" output="schema.source-findings">
PAR:
  ACT TOOL "agent.github-researcher" input="github_researcher.oak.md#schema.research-request" output="github_researcher.oak.md#schema.repository-findings": Research GitHub repositories for <QUESTION> and produce <REPOSITORY_FINDINGS>. (QUESTION=$QUESTION) -> REPOSITORY_FINDINGS
  ACT TOOL "agent.web-researcher" input="web_researcher.oak.md#schema.research-request" output="web_researcher.oak.md#schema.web-findings": Research the web for <QUESTION> and produce <WEB_FINDINGS>. (QUESTION=$QUESTION) -> WEB_FINDINGS
  ACT TOOL "agent.docs-researcher" input="docs_researcher.oak.md#schema.research-request" output="docs_researcher.oak.md#schema.docs-findings": Research Microsoft Learn for <QUESTION> and produce <DOCS_FINDINGS>. (QUESTION=$QUESTION) -> DOCS_FINDINGS
JOIN
</process>

<process id="validate-findings" name="Validate findings" input="findings_challenger.oak.md#schema.challenge-request" output="findings_challenger.oak.md#schema.verified-findings">
ACT TOOL "agent.findings-challenger" input="findings_challenger.oak.md#schema.challenge-request" output="findings_challenger.oak.md#schema.verified-findings": Attack <REPOSITORY_FINDINGS>, <WEB_FINDINGS>, and <DOCS_FINDINGS> against <QUESTION> and their cited sources, then produce <CONFIRMED_FINDINGS> and <REFUTED_CLAIMS>. (QUESTION=$QUESTION, REPOSITORY_FINDINGS=$REPOSITORY_FINDINGS, WEB_FINDINGS=$WEB_FINDINGS, DOCS_FINDINGS=$DOCS_FINDINGS) -> CONFIRMED_FINDINGS, REFUTED_CLAIMS
</process>

<process id="write-report" name="Write report" input="schema.report-request" output="schema.research-report">
ACT Write <TLDR>, <FINDINGS>, and <DROPPED_CLAIMS> that answer <QUESTION> from <CONFIRMED_FINDINGS> and <REFUTED_CLAIMS>. (QUESTION=$QUESTION, CONFIRMED_FINDINGS=$CONFIRMED_FINDINGS, REFUTED_CLAIMS=$REFUTED_CLAIMS) -> TLDR, FINDINGS, DROPPED_CLAIMS
</process>

<process id="publish-report" name="Publish report" input="schema.research-request">
CALL process.find-source-findings (QUESTION=$QUESTION) -> REPOSITORY_FINDINGS, WEB_FINDINGS, DOCS_FINDINGS
CALL process.validate-findings (QUESTION=$QUESTION, REPOSITORY_FINDINGS=$REPOSITORY_FINDINGS, WEB_FINDINGS=$WEB_FINDINGS, DOCS_FINDINGS=$DOCS_FINDINGS) -> CONFIRMED_FINDINGS, REFUTED_CLAIMS
CALL process.write-report (QUESTION=$QUESTION, CONFIRMED_FINDINGS=$CONFIRMED_FINDINGS, REFUTED_CLAIMS=$REFUTED_CLAIMS) -> TLDR, FINDINGS, DROPPED_CLAIMS
EMIT interface.research-report-output (TLDR=$TLDR, FINDINGS=$FINDINGS, DROPPED_CLAIMS=$DROPPED_CLAIMS)
</process>
</processes>

<interfaces>
<interface id="research-request-input" direction="in" schema="schema.research-request">
The question supplied by the caller.
</interface>

<interface id="research-report-output" direction="out" schema="schema.research-report">
The challenged and linked report returned to the caller.
</interface>
</interfaces>