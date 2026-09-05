~~~~instructions
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

Keep the proposed change limited to the supplied request.
~~~~

~~~~schemas
~~~schema;id="change-request"
<REQUEST>

WHERE:
- <REQUEST> is string; is non-empty.
~~~

~~~schema;id="guide-1-option-comparison";name="Option Comparison";purpose="Compare current and proposed behaviour for one criterion."
| Criterion | Current | Proposed |
| --- | --- | --- |
| <CRITERION> | <CURRENT> | <PROPOSED> |

WHERE:
- <CRITERION> is string; matches `^[^|\r\n]+$`.
- <CURRENT> is string; matches `^[^|\r\n]+$`.
- <PROPOSED> is string; matches `^[^|\r\n]+$`.
~~~

~~~schema;id="guide-1-decision-brief";name="Decision Brief";purpose="State one decision and explain its rationale."
## Decision
<DECISION>

### Rationale
<RATIONALE>

WHERE:
- <DECISION> is string; is non-empty.
- <RATIONALE> is string; is non-empty.
~~~

~~~schema;id="guide-1-work-outline";name="Work Outline";purpose="Nest one implementation step and its check beneath one goal."
1. <GOAL>
   1. <STEP>
      1. <CHECK>

WHERE:
- <GOAL> is string; is non-empty; is one line.
- <STEP> is string; is non-empty; is one line.
- <CHECK> is string; is non-empty; is one line.
~~~

~~~schema;id="guide-1-code-file";name="Code File";purpose="Present one Python file with its complete source."
### <FILE_PATH>

```python
<CODE>
```

WHERE:
- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\-]+$`.
- <CODE> is string; is non-empty.
~~~
~~~~

~~~~triggers
change-requested(
  event="A small code change needs explanation.",
  source=interface.request,
  process=process.prepare-change,
)
~~~~

~~~~processes
~~~process;id="compare-options";name="Compare options";input="schema.change-request";output="schema.guide-1-option-comparison"
ACT input="schema.change-request" output="schema.guide-1-option-comparison": Compare current and proposed behaviour for <REQUEST>; produce <CRITERION>, <CURRENT>, and <PROPOSED>. (
  REQUEST=$REQUEST,
) -> CRITERION, CURRENT, PROPOSED
~~~

~~~process;id="decide-change";name="Decide change";input="schema.guide-1-option-comparison";output="schema.guide-1-decision-brief"
ACT input="schema.guide-1-option-comparison" output="schema.guide-1-decision-brief": For <CRITERION>, weigh <CURRENT> against <PROPOSED> and produce <DECISION> and <RATIONALE>. (
  CRITERION=$CRITERION,
  CURRENT=$CURRENT,
  PROPOSED=$PROPOSED,
) -> DECISION, RATIONALE
~~~

~~~process;id="plan-change";name="Plan change";input="schema.guide-1-decision-brief";output="schema.guide-1-work-outline"
ACT input="schema.guide-1-decision-brief" output="schema.guide-1-work-outline": Plan <DECISION> under <RATIONALE>; produce one <GOAL>, implementation <STEP>, and nested <CHECK>. (
  DECISION=$DECISION,
  RATIONALE=$RATIONALE,
) -> GOAL, STEP, CHECK
~~~

~~~process;id="write-file";name="Write file";input="schema.guide-1-work-outline";output="schema.guide-1-code-file"
ACT input="schema.guide-1-work-outline" output="schema.guide-1-code-file": Implement <STEP> for <GOAL> and <CHECK>; produce <FILE_PATH> and complete Python <CODE>. (
  GOAL=$GOAL,
  STEP=$STEP,
  CHECK=$CHECK,
) -> FILE_PATH, CODE
~~~

~~~process;id="prepare-change";name="Prepare change";input="schema.change-request"
CALL process.compare-options (REQUEST=$REQUEST) -> CRITERION, CURRENT, PROPOSED
EMIT interface.comparison
CALL process.decide-change (
  CRITERION=$CRITERION,
  CURRENT=$CURRENT,
  PROPOSED=$PROPOSED,
) -> DECISION, RATIONALE
EMIT interface.decision
CALL process.plan-change (DECISION=$DECISION, RATIONALE=$RATIONALE) -> GOAL, STEP, CHECK
EMIT interface.outline
CALL process.write-file (GOAL=$GOAL, STEP=$STEP, CHECK=$CHECK) -> FILE_PATH, CODE
EMIT interface.file
~~~
~~~~

~~~~interfaces
request RECEIVES schema.change-request
comparison EMITS schema.guide-1-option-comparison
decision EMITS schema.guide-1-decision-brief
outline EMITS schema.guide-1-work-outline
file EMITS schema.guide-1-code-file
~~~~
