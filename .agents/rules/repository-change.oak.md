<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Preserve every original commit and its identity; make corrections as new commits and never amend, squash, rebase, or force-push history away.
Read the governing root AGENTS.md and its applicable scoped knowledge before Git operations; host-confirmed user authorization must cover the exact operation and targets.
</instructions>

<constants>
owned-concern: "Change naming, immutable Git history, and authorised branch operations."

change-type-meanings: CSV<<
type,meaning
feat,new capability or behavior
fix,correction of faulty behavior
refactor,internal restructuring that preserves behavior
perf,performance improvement
docs,"documentation, knowledge, or planning-only change"
test,verification coverage or test correction
build,build tooling or dependency change
ci,continuous integration configuration
chore,repository housekeeping
revert,reversal of an earlier change
>>

change-name-patterns: {"branch": "<TYPE>/<SUMMARY-AS-KEBAB-CASE>", "subject": "<TYPE>(<SCOPE>): <SUMMARY>", "sentence": "<IMPERATIVE_VERB> <OBJECT> [<NECESSARY_QUALIFIER>]"}

instruction-justification: "History preservation and authorization constrain every Git operation, including native host effects."
</constants>

<schemas>
<schema id="change-description" name="Change Description" purpose="Supply the facts needed to name one change.">
Type: <TYPE>
Scope: <SCOPE>
Summary: <SUMMARY>
Breaking: <BREAKING>
Migration: <MIGRATION>

WHERE:
- <TYPE> is string; is one of `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`, `revert`.
- <SCOPE> is string; the lowercase kebab-case area, empty when omitted.
- <SUMMARY> is string; is non-empty; an imperative verb, object and necessary qualifier.
- <BREAKING> is boolean; whether a supported contract changes.
- <MIGRATION> is string; the affected contract and migration, required for breaking changes.
</schema>

<schema id="change-name" name="Change Name">
Branch: <BRANCH>
Subject: <SUBJECT>
Body: <BODY>

WHERE:
- <BRANCH> is string; is non-empty; is one line.
- <SUBJECT> is string; is non-empty; is one line.
- <BODY> is string; the explanation and migration, empty when unnecessary.
</schema>

<schema id="branch-targets" name="Branch Targets">
Remote: <REMOTE>
Source: <SOURCE>
Destination: <DESTINATION>

WHERE:
- <REMOTE> is string; is non-empty.
- <SOURCE> is string; is non-empty.
- <DESTINATION> is string; is non-empty.
</schema>
</schemas>

<processes>
<process id="name-change" name="Name change" input="schema.change-description" output="schema.change-name">
IF $BREAKING equals true:
  ASSERT $MIGRATION does not equal ""
    MESSAGE "A breaking change needs its affected contract and migration."
ACT output="schema.change-name": Use <MEANINGS> and <PATTERNS> to produce <BRANCH>, <SUBJECT> and <BODY> for <TYPE>, <SCOPE> and <SUMMARY>. Use the approved type as the branch prefix, never a platform, tool or agent name; follow it with one slash and lowercase topic words separated by single hyphens. Start the summary with a lowercase imperative verb, its object and only necessary qualifiers; omit vague wording and a terminal period. Name the actual change at this artifact's scope, omitting empty scope parentheses. For <BREAKING>, put ! immediately before the subject colon and explain <MIGRATION> in the body. (
  TYPE=$TYPE,
  SCOPE=$SCOPE,
  SUMMARY=$SUMMARY,
  BREAKING=$BREAKING,
  MIGRATION=$MIGRATION,
  MEANINGS=$constant.change-type-meanings,
  PATTERNS=$constant.change-name-patterns,
) -> BRANCH, SUBJECT, BODY
</process>

<process id="update-branch" name="Update branch" input="schema.branch-targets">
ACT Update the authorised work branch <SOURCE> from its destination <DESTINATION> on <REMOTE> by merging, preserving both original commit histories. (
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
  REMOTE=$REMOTE,
)
</process>

<process id="merge-change" name="Merge change" input="schema.branch-targets">
ACT Merge the authorised pull request from <SOURCE> to <DESTINATION> on <REMOTE> with a merge commit, preserving every original commit and its identity. Never squash or rebase the merge. (
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
  REMOTE=$REMOTE,
)
</process>

<process id="clean-merged-branch" name="Clean branch" input="schema.branch-targets">
ACT After a confirmed merge on <REMOTE>, use host Git tools to verify that the current <SOURCE> tip is an ancestor of <DESTINATION>. Delete its remote and local branch references only while the source tip still equals the verified tip; retain both references if ancestry or identity checks fail. (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>
</processes>