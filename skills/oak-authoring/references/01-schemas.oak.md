~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
~~~~

~~~~constants
guidance: YAML<<
- Map reusable information shapes and contracts to schemas.
- 'Choose schema templates by information relationships: tables for comparison, outlines
  for hierarchy, sections for explanation, and fenced blocks for code; use lists only
  for list-shaped information.'
- Preserve requested layouts; the demonstrated shapes are examples, not a closed catalogue
  or a reason to force every schema into labelled fields.
- Keep templates and WHERE constraints in schema definitions; populated outputs fill
  its slots rather than copying the schema definition.
- A binding supplies one value per placeholder; repeated names reuse that value, and
  an ellipsis alone does not create independently typed rows or sections.
- Bind constants, state, processes, actions, and interfaces to schemas where values
  must validate; role names alone are not types.
>>

populated-shapes: TEXT<<
Option Comparison
| Criterion | Current | Proposed |
| --- | --- | --- |
| Blank title | Accepted | Rejected |

Decision Brief
## Decision
Reject blank titles.

### Rationale
A title must identify the task.

Work Outline
1. Require meaningful titles.
   1. Check the stripped title.
      1. Test empty, whitespace, and valid titles.

Code File
### title.py

```python
def valid_title(title: str) -> bool:
    return bool(title.strip())
```
>>

shape-notes: TEXT<<
populated-shapes shows filled instances of these four reusable schemas without WHERE or schema wrappers. The one-row table is fixed-cardinality. Extend templates explicitly when justified; apply the schema guidance above.
>>
~~~~

~~~~schemas
~~~schema;id="option-comparison";name="Option Comparison";purpose="Compare current and proposed behaviour for one criterion."
| Criterion | Current | Proposed |
| --- | --- | --- |
| <CRITERION> | <CURRENT> | <PROPOSED> |

WHERE:
- <CRITERION> is string; matches `^[^|\r\n]+$`.
- <CURRENT> is string; matches `^[^|\r\n]+$`.
- <PROPOSED> is string; matches `^[^|\r\n]+$`.
~~~

~~~schema;id="decision-brief";name="Decision Brief";purpose="State one decision and explain its rationale."
## Decision
<DECISION>

### Rationale
<RATIONALE>

WHERE:
- <DECISION> is string; is non-empty.
- <RATIONALE> is string; is non-empty.
~~~

~~~schema;id="work-outline";name="Work Outline";purpose="Nest one implementation step and its check beneath one goal."
1. <GOAL>
   1. <STEP>
      1. <CHECK>

WHERE:
- <GOAL> is string; is non-empty; is one line.
- <STEP> is string; is non-empty; is one line.
- <CHECK> is string; is non-empty; is one line.
~~~

~~~schema;id="code-file";name="Code File";purpose="Present one Python file with its complete source."
### <FILE_PATH>

```python
<CODE>
```

WHERE:
- <FILE_PATH> is path; matches `^[A-Za-z0-9_./\-]+$`.
- <CODE> is string; is non-empty.
~~~
~~~~
