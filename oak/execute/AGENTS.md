<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "One execution cycle, arrivals, trigger selection, process frames, steps, tools, state, emissions, failures, and transaction behavior."

execution-inputs: ["root node or resolved graph", "one arrival", "complete state mapping", "optional direct native action handler or OAK-context interpreter", "exact tool registry"]

arrival-forms: ["exact event text without values", "one local receive interface with one complete schema instance"]

trigger-selection: CSV<<
case,match,result
event arrival,source-less trigger event text,evaluate matching guards
receive arrival,source-backed trigger interface target,evaluate matching guards
zero matches,none,return without process or emission
one match,one eligible trigger,run selected process
many matches,multiple eligible triggers,fail as ambiguous
>>

step-contracts: CSV<<
step,contract
ACT,native handler or exact named tool with validated inputs and exact validated outputs
SET,stage one valid local state write
CALL,run one process synchronously in a fresh frame and promote declared outputs
EMIT,stage one complete valid local output-interface instance
IF ASSERT FAIL,select one branch or stop the transaction
FOREACH WHILE,bounded ordered iteration with fresh child scopes
PAR JOIN,"validate before launch, isolate child outputs, then promote in authored order"
>>

native-action-contract: ["accept either the existing direct act callback or the context interpreter, never both", "give the context interpreter a detached native OAK invocation with literal inputs and original schema identities", "preserve all source documents and their separate policy scopes for runtime interpretation", "keep source instructions in their source document rather than transplanting local references", "snapshot the current staged state without exposing mutable execution objects", "validate interpreter outputs before binding promotion just like direct action outputs", "leave exact named-tool dispatch unchanged"]

transaction-contract: YAML<<
- Do not mutate the caller state mapping.
- Keep local bindings immutable inside each process frame.
- Share staged state and emissions across called processes in one top-level transaction.
- Commit staged state and emissions only after successful top-level completion.
- Discard staged values after failure without claiming rollback for external tool
  effects.
- Return the selected process target, committed state, and ordered emissions after
  success.
>>
</constants>

<processes>
<process id="change-execution" name="Change execution">
ACT Validate <INPUTS> and one of <ARRIVALS> before trigger selection. (INPUTS=$constant.execution-inputs, ARRIVALS=$constant.arrival-forms)
ACT Apply <SELECTION> after exact event or source matching and authored-order guard evaluation. (SELECTION=$constant.trigger-selection)
ACT Preserve <STEPS> across process frames, tools, calls, branches, loops, parallel work, and emissions. (STEPS=$constant.step-contracts)
ACT Apply <NATIVE> to interpreter-native action dispatch. (NATIVE=$constant.native-action-contract)
ACT Apply <TRANSACTION> to every success and failure path. (TRANSACTION=$constant.transaction-contract)
ACT Use stable execution error codes and retain suppressed parallel child failures when available. ()
</process>
</processes>