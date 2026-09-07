---
name: oak-authoring
description: Author, review, or revise Open Agent Knowledge (OAK) documents from supplied
  knowledge. Choose justified parts and schema shapes with populated examples. Use
  when writing OAK; no installation is needed. Programmatic validation is optional
  and installation requires separate permission.
metadata:
  version: 3.2.0
  oak-revision: 85ddd5393fd4349632f728f5a05cb67f9bc5dbf5
  validator-sha256: 9bca0d69e12c26aac64d3e7218f4ccfc620e7a7196b569d324ff7ac8197053bc
---

<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<schemas>
<schema id="authoring-request">
SOURCE: <SOURCE>
VALIDATE: <VALIDATE>

WHERE:
- <SOURCE> is string; is non-empty.
- <VALIDATE> is boolean.
</schema>

<schema id="oak-candidate">
CANDIDATE: <CANDIDATE>

WHERE:
- <CANDIDATE> is string; is non-empty.
</schema>

<schema id="authoring-result">
OAK: <OAK>
VALIDATION: <VALIDATION>

WHERE:
- <OAK> is string; is non-empty.
- <VALIDATION> is string; is non-empty.
</schema>

<schema id="validator-check">
INSTALL_REQUIRED: <INSTALL_REQUIRED>
REPORT: <REPORT>

WHERE:
- <INSTALL_REQUIRED> is boolean.
- <REPORT> is string; is non-empty.
</schema>

<schema id="installation-consent">
APPROVED: <APPROVED>

WHERE:
- <APPROVED> is boolean.
</schema>

<schema id="validation-context">
CANDIDATE: <CANDIDATE>
REPORT: <REPORT>
ALLOW_INSTALL: <ALLOW_INSTALL>

WHERE:
- <CANDIDATE> is string; is non-empty.
- <REPORT> is string; is non-empty.
- <ALLOW_INSTALL> is boolean.
</schema>
</schemas>

<triggers>
authoring-requested(
  event="OAK authoring is requested for supplied source material.",
  process=process.capture-request,
)
request-received(
  event="A complete OAK authoring request is received.",
  source=interface.authoring-input,
  process=process.author-document,
)
</triggers>

<processes>
<process id="capture-request" name="Capture request">
ACT output="schema.authoring-request": Capture all <SOURCE>; set <VALIDATE> true only for requested programmatic validation, otherwise false. () -> SOURCE, VALIDATE
CALL process.author-document (SOURCE=$SOURCE, VALIDATE=$VALIDATE)
</process>

<process id="author-document" name="Author document" input="schema.authoring-request">
ACT Apply <AUTHORING> and <STRUCTURE> to all <SOURCE> for <SCOPE>. Use <TEMPLATE> under <TEMPLATE_USE> only for new skills; consult needed guides. (
  AUTHORING=$guides/authoring.oak.md#constant.guidance,
  STRUCTURE=$references/00-structure.oak.md#constant.guidance,
  SOURCE=$SOURCE,
  TEMPLATE=$guides/authoring.oak.md#constant.skill-template,
  TEMPLATE_USE=$guides/authoring.oak.md#constant.template-use,
) -> SCOPE
ACT Design justified schemas as <DESIGN_1> from <SOURCE> and <SCOPE> under <GUIDANCE>. Preserve requested shapes using the complete schemas and populated instances in <TEACHING>. (
  GUIDANCE=$references/01-schemas.oak.md#constant.guidance,
  SCOPE=$SCOPE,
  SOURCE=$SOURCE,
  TEACHING=$guides/review.oak.md#constant.teaching,
) -> DESIGN_1
ACT Design justified constants as <DESIGN_2> from <SOURCE> and <DESIGN_1> under <GUIDANCE>. (
  GUIDANCE=$references/02-constants.oak.md#constant.guidance,
  DESIGN_1=$DESIGN_1,
  SOURCE=$SOURCE,
) -> DESIGN_2
ACT Design justified state as <DESIGN_3> from <SOURCE> and <DESIGN_2> under <GUIDANCE>. (
  GUIDANCE=$references/03-state.oak.md#constant.guidance,
  DESIGN_2=$DESIGN_2,
  SOURCE=$SOURCE,
) -> DESIGN_3
ACT Design justified interfaces as <DESIGN_4> from <SOURCE> and <DESIGN_3> under <GUIDANCE>. (
  GUIDANCE=$references/04-interfaces.oak.md#constant.guidance,
  DESIGN_3=$DESIGN_3,
  SOURCE=$SOURCE,
) -> DESIGN_4
ACT Design justified triggers as <DESIGN_5> from <SOURCE> and <DESIGN_4> under <GUIDANCE>. (
  GUIDANCE=$references/05-triggers.oak.md#constant.guidance,
  DESIGN_4=$DESIGN_4,
  SOURCE=$SOURCE,
) -> DESIGN_5
ACT Design justified processes as <DESIGN_6> from <SOURCE> and <DESIGN_5> under <GUIDANCE>. Apply <DELEGATION> and <ORCHESTRATION> to delegation, <CODEX> and <DEFAULTS> to native Codex artifacts. (
  GUIDANCE=$references/06-processes.oak.md#constant.guidance,
  DESIGN_5=$DESIGN_5,
  SOURCE=$SOURCE,
  ORCHESTRATION=$guides/subagent-orchestration.oak.md#constant.orchestration,
  DELEGATION=$guides/subagent-orchestration.oak.md#constant.guidance,
  CODEX=$platforms/codex/adaptor.oak.md#constant.mapping,
  DEFAULTS=$platforms/codex/adaptor.oak.md#constant.native-defaults,
) -> DESIGN_6
ACT Design justified instructions as <DESIGN_7> from <SOURCE> and <DESIGN_6> under <GUIDANCE>. (
  GUIDANCE=$references/07-instructions.oak.md#constant.guidance,
  DESIGN_6=$DESIGN_6,
  SOURCE=$SOURCE,
) -> DESIGN_7
ACT Review <DESIGN_7> with <REVIEW>, <GRAMMAR> and <TEACHING> for canonical <CANDIDATE>, not programmatic validation. Use its catalogue to select complete scenarios. (
  DESIGN_7=$DESIGN_7,
  REVIEW=$guides/review.oak.md#constant.review,
  GRAMMAR=$references/00-structure.oak.md#constant.oak-ebnf,
  TEACHING=$guides/review.oak.md#constant.teaching,
) -> CANDIDATE
IF $VALIDATE equals true:
  CALL process.validate-and-deliver (CANDIDATE=$CANDIDATE)
ELSE:
  EMIT interface.authored-document (
    OAK=$CANDIDATE,
    VALIDATION="Programmatic validation was not performed (not requested).",
  )
</process>

<process id="validate-and-deliver" name="Check validator" input="schema.oak-candidate">
ACT output="schema.validator-check": Apply <POLICY> and exact <HELPER> to <CANDIDATE> without --allow-install. Return observed <REPORT>; <INSTALL_REQUIRED> means permission-required, not invalid OAK or unavailable execution. (
  POLICY=$guides/validation.oak.md#constant.validation-policy,
  HELPER=$guides/validation.oak.md#constant.validator-script,
  CANDIDATE=$CANDIDATE,
) -> INSTALL_REQUIRED, REPORT
IF $INSTALL_REQUIRED equals true:
  ACT output="schema.installation-consent": Request consent to download <IDENTITY> and install its dependencies in an isolated retained environment. <APPROVED> requires explicit installation consent, not a validation request. (
    IDENTITY=$guides/validation.oak.md#constant.identity,
  ) -> APPROVED
  IF $APPROVED equals true:
    CALL process.finalize-validation (CANDIDATE=$CANDIDATE, REPORT=$REPORT, ALLOW_INSTALL=true)
  ELSE:
    EMIT interface.authored-document (
      OAK=$CANDIDATE,
      VALIDATION="Programmatic validation was not performed (installation declined).",
    )
ELSE:
  CALL process.finalize-validation (CANDIDATE=$CANDIDATE, REPORT=$REPORT, ALLOW_INSTALL=false)
</process>

<process id="finalize-validation" name="Report validation" input="schema.validation-context">
ACT output="schema.authoring-result": Finalize <CANDIDATE> from <REPORT> under <POLICY> with exact <HELPER>. Only <ALLOW_INSTALL> true permits downloads/installation via --allow-install. Repair/recheck changes under the same permission, not unchanged successes. Return <OAK> and truthful <VALIDATION>. (
  REPORT=$REPORT,
  CANDIDATE=$CANDIDATE,
  ALLOW_INSTALL=$ALLOW_INSTALL,
  POLICY=$guides/validation.oak.md#constant.validation-policy,
  HELPER=$guides/validation.oak.md#constant.validator-script,
) -> OAK, VALIDATION
EMIT interface.authored-document
</process>
</processes>

<interfaces>
authoring-input RECEIVES schema.authoring-request
authored-document EMITS schema.authoring-result
</interfaces>
