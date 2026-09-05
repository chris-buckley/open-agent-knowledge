<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Python expression layout, horizontal signatures, conceptual grouping, and literal whitespace."

rules: YAML<<
- section: '3.6'
  title: Keep one line per coherent idea
  requirements:
  - Prefer compact expressions where the meaning remains immediate.
  - Split expressions when intermediate names reveal domain meaning, errors require
    separation, or the line becomes visually dense.
  examples:
  - constant.example-3-6-1
  tables: []
- section: '3.8'
  title: Separate conceptual groups with blank lines
  requirements:
  - Use one blank line when adjacent declarations or statements change purpose. Keep
    one concept together.
  - 'Separate groups such as:'
  - public API values and private implementation values;
  - defaults and validation bounds;
  - public and private type aliases;
  - validation, preparation, mutation, and output phases inside a function.
  - Do not split a pair, range, or small group that readers must inspect together.
    Use whitespace as light structure, not decoration.
  examples:
  - constant.example-3-8-1
  tables: []
- section: '13.1'
  title: Keep small signatures horizontal
  requirements:
  - 'Provides: Shows one small API as one coherent idea instead of a vertical parameter
    inventory.'
  - 'When no repository formatter rule exists, keep a function signature on one line
    when:'
  - it has at most four caller-supplied parameters, excluding self or cls;
  - each annotation and default is short and simple;
  - the complete line is at most 120 characters.
  - Keep the keyword-only marker inline. Use a named return alias only when it describes
    a useful domain shape; never create an alias solely to cheat the width limit.
    Do not introduce an options object merely to shorten a simple signature.
  - Use vertical layout when the signature exceeds the width, contains complex annotations
    or defaults, or has enough parameters that grouping improves comprehension. Repository
    formatter settings still take precedence.
  examples:
  - constant.example-13-1-1
  tables: []
- section: '13.2'
  title: Group code by concept
  requirements:
  - Follow the project's formatter.
  - Keep related constants, types, public functions, and private helpers grouped coherently.
  - Separate conceptual groups with one blank line; keep each group compact.
  - Avoid giant files, but do not fragment a small cohesive module across many files.
  - Avoid deeply nested packages and ceremonial __init__.py exports without a real
    API need.
  - Keep the repository tree minimal and predictable.
  - 'A preferred module shape is:'
  - Use the shape as a guide, not an inflexible template.
  examples:
  - constant.example-13-2-1
  tables: []
- section: refinement-literal-whitespace
  title: Preserve exact literal whitespace
  requirements:
  - Show a multiline information shape with adjacent string literals when that improves
    reading without changing its bytes.
  - Do not add strip, dedent, a trailing newline, or another normalization solely
    to make source layout attractive when whitespace is contractual.
  examples:
  - constant.example-literal-whitespace-before
  - constant.example-literal-whitespace-after
  tables: []
>>

example-index: YAML<<
- id: example-3-6-1
  section: '3.6'
  topic: Keep one line per coherent idea
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-8-1
  section: '3.8'
  topic: Separate conceptual groups with blank lines
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-13-1-1
  section: '13.1'
  topic: Keep small signatures horizontal
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-13-2-1
  section: '13.2'
  topic: Group code by concept
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-literal-whitespace-before
  section: refinement-literal-whitespace
  topic: Expose the template shape without changing its bytes.
  language: python
  scope: illustrative excerpt; requires the shown domain context
- id: example-literal-whitespace-after
  section: refinement-literal-whitespace
  topic: Expose the template shape without changing its bytes.
  language: python
  scope: illustrative excerpt; requires the shown domain context
>>

example-3-6-1: TEXT<<
ranked = sorted(hits, key=lambda hit: (-hit.score, hit.key))
>>

example-3-8-1: TEXT<<
# Before: different roles appear as one visual group.
DEFAULT_LIMIT: Final = 10
_MIN_COSINE_SCORE: Final = -1.0
_MAX_COSINE_SCORE: Final = 1.0


# After: one blank line exposes the change in purpose.
DEFAULT_LIMIT: Final = 10

_MIN_COSINE_SCORE: Final = -1.0
_MAX_COSINE_SCORE: Final = 1.0
>>

example-13-1-1: TEXT<<
# Before: mechanical wrapping makes a small API look complex.
def search(
    self,
    query: str,
    *,
    limit: int = DEFAULT_LIMIT,
    min_score: float = _MIN_SCORE,
) -> SearchHits[_T]:
    ...


# After: one line presents one small API.
def search(self, query: str, *, limit: int = DEFAULT_LIMIT, min_score: float = _MIN_SCORE) -> SearchHits[_T]:
    ...
>>

example-13-2-1: TEXT<<
module docstring
imports
constants
type aliases
enums
public records
private records
public functions or primary class
private helpers
>>

example-literal-whitespace-before: TEXT<<
template = "Balance: <BALANCE>\nFactor: <FACTOR>"
>>

example-literal-whitespace-after: TEXT<<
template = (
    "Balance: <BALANCE>\n"
    "Factor: <FACTOR>"
)
>>
</constants>