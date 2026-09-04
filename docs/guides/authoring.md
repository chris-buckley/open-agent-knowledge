# Authoring OAK

This guide explains how to turn source knowledge into one OAK document. Exact fields and syntax remain in the package and generated reference.

## 1. Start with the knowledge boundary

State what the document knows, what can enter it, what can leave it, and what work it can perform.

Do not add a state machine, interface, trigger, process, or relative target unless the source justifies it.

## 2. Place each item in one part

| Source knowledge | OAK part |
|---|---|
| Required rule, policy, method, or safety behaviour | instructions |
| Fixed value used during operation | constants |
| Reusable information shape | schemas |
| Value that persists and can change across arrivals | state |
| Outside occurrence that selects work | triggers |
| Ordered invocation-local work | processes |
| Complete information crossing the document boundary | interfaces |

Omit a part when the source gives it no justified entry.

## 3. Define information shapes before work

Use schemas for complete reusable contracts.

A schema template shows the complete shape. Each placeholder has one `WHERE` entry with its datatype and constraints.

Reuse the same schema for an interface, process, action, or call when they share one contract. Do not copy the shape into each consumer.

## 4. Choose values by lifetime

- Use a constant for a fixed value.
- Use state for a mutable value that persists across arrivals.
- Use a process binding for an immutable value local to one invocation.
- Use an interface for one complete boundary occurrence.

A receive interface payload becomes process input bindings. A process does not read ambient interface values.

## 5. Route outside occurrences through triggers

Use a source-backed trigger when a receive interface starts work. The receive interface schema and selected process input schema are the same resolved schema.

Use an event-backed trigger when exact event text starts work without a receive payload. Seed a typed process from literals, constants, and state.

Use a guard only for state conditions that decide whether the matched occurrence can run.

## 6. Keep process work local

Use plain `ACT` when the interpreter performs the instruction with native capabilities.

Use `ACT TOOL` only when one exact supplied tool must perform the action. Preserve its registry name exactly.

Use `CALL` for another OAK process in the same interpreter and transaction. Do not use `ACT TOOL` to call an OAK process.

Decompose multi-stage work into typed phase processes. Keep the trigger-selected process as a short orchestrator of calls and emissions.

Use state only when a value must persist beyond the invocation.

## 7. Emit complete results

Use an `EMITS` interface for each outgoing contract.

Use bindingless `EMIT interface.result` when same-named visible bindings satisfy the complete interface schema.

Use explicit emit bindings when projection or renaming is required.

## 8. Name for meaning

Use the shortest unambiguous domain term. Reuse the same noun across schemas, state, processes, and interfaces.

Use an action-first process id such as `review-amendment` or `publish-report`.

Avoid vague names such as `data`, `item`, `handle`, or `process` when the domain supplies an exact term.

## 9. Validate and inspect

Author through Pydantic or parse OAK text into a `Node`.

Run local validation before resolution. Supply an explicit path and loader when the document uses relative targets.

Render the node and inspect the canonical OAK. Repair every validation failure before using or emitting the document.

Use `outputs/oak.ebnf` for exact grammar and `outputs/docs` for exact model and surface reference.

## Complete example

The following document receives one support request, classifies it, updates temporary workflow state, and emits one validated result.

```oak
<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Classify each support request by urgency.
</instructions>

<constants>
urgent-terms: ["outage", "security"]
</constants>

<schemas>
<schema id="support-request" name="Support Request" purpose="Carry one support request into classification.">
Message: <MESSAGE>

WHERE:
- <MESSAGE> is string; is non-empty; the support request text.
</schema>

<schema id="support-result" name="Support Result" purpose="Carry one classified support request.">
Priority: <PRIORITY>
Summary: <SUMMARY>

WHERE:
- <PRIORITY> is string; is one of `urgent`, `normal`; the assigned urgency.
- <SUMMARY> is string; is non-empty; the concise request summary.
</schema>

<schema id="workflow-state" name="Workflow State" purpose="Constrain the persistent classification state.">
Status: <STATUS>

WHERE:
- <STATUS> is string; is one of `idle`, `running`; the current workflow status.
</schema>
</schemas>

<state>
review-status AS schema.workflow-state.STATUS: "idle"
</state>

<triggers>
trigger.support-requested.event := "A support request is supplied."
trigger.support-requested.source := interface.request
trigger.support-requested.guard := $state.review-status equals "idle"
trigger.support-requested.process := process.classify-request
</triggers>

<processes>
<process id="classify-request" name="Classify request" input="schema.support-request" output="schema.support-result">
SET state.review-status = "running"
ACT output="schema.support-result": Classify <MESSAGE> using <URGENT_TERMS>, then produce <PRIORITY> and <SUMMARY>. (MESSAGE=$MESSAGE, URGENT_TERMS=$constant.urgent-terms) -> PRIORITY, SUMMARY
EMIT interface.result
SET state.review-status = "idle"
</process>
</processes>

<interfaces>
request RECEIVES schema.support-request
result EMITS schema.support-result
</interfaces>
```
