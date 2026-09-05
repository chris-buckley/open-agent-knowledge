<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<constants>
option-comparison-instance: TEXT<<
| Criterion | Current | Proposed |
| --- | --- | --- |
| Blank title | Accepted | Rejected |
>>

decision-brief-instance: TEXT<<
## Decision
Reject blank titles.

### Rationale
A title must identify the task.
>>

work-outline-instance: TEXT<<
1. Require meaningful titles.
   1. Check the stripped title.
      1. Test empty, whitespace, and valid titles.
>>

code-file-instance: TEXT<<
### title.py

```python
def valid_title(title: str) -> bool:
    return bool(title.strip())
```
>>
</constants>

<schemas>
<schema id="option-comparison" name="Option Comparison" purpose="Compare current and proposed behaviour for one criterion.">
| Criterion | Current | Proposed |
| --- | --- | --- |
| <CRITERION> | <CURRENT> | <PROPOSED> |

WHERE:
- <CRITERION> is string; matches `^[^|\r\n]+$`.
- <CURRENT> is string; matches `^[^|\r\n]+$`.
- <PROPOSED> is string; matches `^[^|\r\n]+$`.
</schema>

<schema id="decision-brief" name="Decision Brief" purpose="State one decision and explain its rationale.">
## Decision
<DECISION>

### Rationale
<RATIONALE>

WHERE:
- <DECISION> is string; is non-empty.
- <RATIONALE> is string; is non-empty.
</schema>

<schema id="work-outline" name="Work Outline" purpose="Nest one implementation step and its check beneath one goal.">
1. <GOAL>
   1. <STEP>
      1. <CHECK>

WHERE:
- <GOAL> is string; is non-empty; is one line.
- <STEP> is string; is non-empty; is one line.
- <CHECK> is string; is non-empty; is one line.
</schema>

<schema id="code-file" name="Code File" purpose="Present one Python file with its complete source.">
### <FILE_PATH>

```python
<CODE>
```

WHERE:
- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\-]+$`.
- <CODE> is string; is non-empty.
</schema>
</schemas>
