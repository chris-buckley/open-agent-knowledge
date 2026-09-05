---
name: oak-authoring
description: Author, review, or revise Open Agent Knowledge (OAK) documents from supplied
  knowledge. Choose justified parts and schema shapes with populated examples. Use
  when writing OAK; no installation is needed. Programmatic validation is optional
  and installation requires separate permission.
metadata:
  version: 1.0.0
  oak-revision: 3cf76d5fa8073774d88974f0396a5177d510fbc6
  validator-sha256: 1200a15c15f512c40dd79814d762f7e691ba431e75bcabcb339b34633f517888
---

~~~~instructions
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
~~~~

~~~~schemas
~~~schema;id="authoring-request"
SOURCE: <SOURCE>
VALIDATE: <VALIDATE>

WHERE:
- <SOURCE> is string; is non-empty.
- <VALIDATE> is boolean.
~~~

~~~schema;id="oak-candidate"
CANDIDATE: <CANDIDATE>

WHERE:
- <CANDIDATE> is string; is non-empty.
~~~

~~~schema;id="authoring-result"
OAK: <OAK>
VALIDATION: <VALIDATION>

WHERE:
- <OAK> is string; is non-empty.
- <VALIDATION> is string; is non-empty.
~~~

~~~schema;id="validator-check"
INSTALL_REQUIRED: <INSTALL_REQUIRED>
REPORT: <REPORT>

WHERE:
- <INSTALL_REQUIRED> is boolean.
- <REPORT> is string; is non-empty.
~~~

~~~schema;id="installation-consent"
APPROVED: <APPROVED>

WHERE:
- <APPROVED> is boolean.
~~~

~~~schema;id="validation-context"
CANDIDATE: <CANDIDATE>
REPORT: <REPORT>
ALLOW_INSTALL: <ALLOW_INSTALL>

WHERE:
- <CANDIDATE> is string; is non-empty.
- <REPORT> is string; is non-empty.
- <ALLOW_INSTALL> is boolean.
~~~
~~~~

~~~~triggers
trigger.authoring-requested.event := "OAK authoring is requested for supplied source material."
trigger.authoring-requested.process := process.capture-request

trigger.request-received.event := "A complete OAK authoring request is received."
trigger.request-received.source := interface.authoring-input
trigger.request-received.process := process.author-document
~~~~

~~~~processes
~~~process;id="capture-request";name="Capture request"
ACT output="schema.authoring-request": Capture the complete supplied source as <SOURCE> and set <VALIDATE> true only when programmatic validation was requested; otherwise false. () -> SOURCE, VALIDATE
CALL process.author-document (SOURCE=$SOURCE, VALIDATE=$VALIDATE)
~~~

~~~process;id="author-document";name="Author document";input="schema.authoring-request"
ACT Use <STRUCTURE> and the complete supplied <SOURCE> to establish <SCOPE>; consult the rest of that structure guide only as needed. (STRUCTURE=$references/00-structure.oak.md#constant.guidance, SOURCE=$SOURCE) -> SCOPE
ACT Apply <GUIDANCE> to <SCOPE> and <SOURCE> to decide schemas; omit unjustified entries and produce <DESIGN_1>. Use the supplied schema definitions and their <POPULATED> instances to preserve the requested information shape. (GUIDANCE=$references/01-schemas.oak.md#constant.guidance, SCOPE=$SCOPE, SOURCE=$SOURCE, POPULATED=$references/01-schemas.oak.md#constant.populated-shapes) -> DESIGN_1
ACT Apply <GUIDANCE> to <DESIGN_1> and <SOURCE> to decide constants; omit unjustified entries and produce <DESIGN_2>. (GUIDANCE=$references/02-constants.oak.md#constant.guidance, DESIGN_1=$DESIGN_1, SOURCE=$SOURCE) -> DESIGN_2
ACT Apply <GUIDANCE> to <DESIGN_2> and <SOURCE> to decide state; omit unjustified entries and produce <DESIGN_3>. (GUIDANCE=$references/03-state.oak.md#constant.guidance, DESIGN_2=$DESIGN_2, SOURCE=$SOURCE) -> DESIGN_3
ACT Apply <GUIDANCE> to <DESIGN_3> and <SOURCE> to decide interfaces; omit unjustified entries and produce <DESIGN_4>. (GUIDANCE=$references/04-interfaces.oak.md#constant.guidance, DESIGN_3=$DESIGN_3, SOURCE=$SOURCE) -> DESIGN_4
ACT Apply <GUIDANCE> to <DESIGN_4> and <SOURCE> to decide triggers; omit unjustified entries and produce <DESIGN_5>. (GUIDANCE=$references/05-triggers.oak.md#constant.guidance, DESIGN_4=$DESIGN_4, SOURCE=$SOURCE) -> DESIGN_5
ACT Apply <GUIDANCE> to <DESIGN_5> and <SOURCE> to decide processes; omit unjustified entries and produce <DESIGN_6>. (GUIDANCE=$references/06-processes.oak.md#constant.guidance, DESIGN_5=$DESIGN_5, SOURCE=$SOURCE) -> DESIGN_6
ACT Apply <GUIDANCE> to <DESIGN_6> and <SOURCE> to decide instructions; omit unjustified entries and produce <DESIGN_7>. (GUIDANCE=$references/07-instructions.oak.md#constant.guidance, DESIGN_6=$DESIGN_6, SOURCE=$SOURCE) -> DESIGN_7
ACT Review <DESIGN_7> against <REVIEW>, <GRAMMAR>, and the supplied teaching examples. Produce <CANDIDATE> as one OAK node in canonical section order, without claiming a programmatic check. (DESIGN_7=$DESIGN_7, REVIEW=$references/08-review.oak.md#constant.review, GRAMMAR=$references/08-review.oak.md#constant.oak-ebnf) -> CANDIDATE
IF $VALIDATE equals true:
  THEN:
    CALL process.validate-and-deliver (CANDIDATE=$CANDIDATE)
  ELSE:
    EMIT interface.authored-document (OAK=$CANDIDATE, VALIDATION="Programmatic validation was not performed (not requested).")
~~~

~~~process;id="validate-and-deliver";name="Check validator";input="schema.oak-candidate"
ACT output="schema.validator-check": Apply <POLICY> to check <CANDIDATE> with the exact <HELPER> without --allow-install. Reuse matching code when available. Return the actual <REPORT> and set <INSTALL_REQUIRED> true only for permission-required, not for invalid OAK or an unavailable execution tool. (POLICY=$references/09-validation.oak.md#constant.validation-policy, HELPER=$references/09-validation.oak.md#constant.validator-script, CANDIDATE=$CANDIDATE) -> INSTALL_REQUIRED, REPORT
IF $INSTALL_REQUIRED equals true:
  THEN:
    ACT output="schema.installation-consent": Ask the user for permission to download the OAK revision in <IDENTITY> and install its dependencies in an isolated retained environment. Set <APPROVED> true only after explicit approval; a validation request alone is not approval. (IDENTITY=$references/09-validation.oak.md#constant.identity) -> APPROVED
    IF $APPROVED equals true:
      THEN:
        CALL process.finalize-validation (CANDIDATE=$CANDIDATE, REPORT=$REPORT, ALLOW_INSTALL=true)
      ELSE:
        EMIT interface.authored-document (OAK=$CANDIDATE, VALIDATION="Programmatic validation was not performed (installation declined).")
  ELSE:
    CALL process.finalize-validation (CANDIDATE=$CANDIDATE, REPORT=$REPORT, ALLOW_INSTALL=false)
~~~

~~~process;id="finalize-validation";name="Report validation";input="schema.validation-context"
ACT output="schema.authoring-result": Use <REPORT> for <CANDIDATE> under <POLICY>. With <ALLOW_INSTALL> true, run the exact <HELPER> with --allow-install; otherwise never download or install. Repair reported authoring errors when possible and recheck changed documents under the same permission. Do not rerun an unchanged successful check. Produce <OAK> and truthful <VALIDATION>, including errors or why a check could not run. (REPORT=$REPORT, CANDIDATE=$CANDIDATE, ALLOW_INSTALL=$ALLOW_INSTALL, POLICY=$references/09-validation.oak.md#constant.validation-policy, HELPER=$references/09-validation.oak.md#constant.validator-script) -> OAK, VALIDATION
EMIT interface.authored-document
~~~
~~~~

~~~~interfaces
authoring-input RECEIVES schema.authoring-request
authored-document EMITS schema.authoring-result
~~~~
