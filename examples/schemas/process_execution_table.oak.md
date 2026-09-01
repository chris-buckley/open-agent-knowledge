<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="process-execution-table" name="Process Execution Table" purpose="Summarize process execution across processes in lexical order, one row per process.">
| ProcessId | Name | Status | StartedAt | EndedAt | DurationMs | Outcome | Artifacts | Errors |
| <PROCESS_ID> | <PROCESS_NAME> | <STATUS> | <STARTED_AT> | <ENDED_AT> | <DURATION_MS> | <OUTCOME> | <ARTIFACTS> | <ERRORS> |

WHERE:
- <PROCESS_ID> is string; is non-empty; the process identifier.
- <PROCESS_NAME> is string; is non-empty; the process display name.
- <STATUS> is string; is one of `PENDING`, `RUNNING`, `OK`, `WARN`, `ERROR`; the execution status.
- <STARTED_AT> is datetime; when the process started.
- <ENDED_AT> is datetime; when the process ended.
- <DURATION_MS> is integer; the run duration in milliseconds.
- <OUTCOME> is string; is non-empty; the result in one clause.
- <ARTIFACTS> is string; the produced artifacts, empty when none.
- <ERRORS> is string; the errors, empty when none.
</schema>
</schemas>