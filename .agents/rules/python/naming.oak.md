<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Python semantic vocabulary, stable values, public names, and non-public naming."

rules: YAML<<
- section: '3.3'
  title: Put stable values near the top
  requirements:
  - Use named constants for limits, defaults, protocol values, thresholds, and repeated
    literals.
  - Constants should explain domain meaning, not merely rename obvious values.
  examples:
  - constant.example-3-3-1
  tables: []
- section: '3.7'
  title: Mark non-public names explicitly
  requirements:
  - Use one leading underscore for implementation details that are not part of the
    supported public API.
  - 'This applies to:'
  - module-level helper functions;
  - internal classes and records;
  - instance and class attributes;
  - internal constants and type aliases;
  - modules whose contents are not a supported import surface.
  - Keep public names unprefixed. Do not prefix local variables or parameters merely
    because they are internal to a function; their scope already communicates that.
  - 'Use:'
  - _name for ordinary non-public names;
  - name_ only to avoid a Python keyword or a genuinely harmful collision;
  - __name only when name mangling is intentionally needed to prevent subclass collisions;
  - __dunder__ only for Python-defined data-model and protocol methods, never as invented
    decoration.
  - A private module may be named _ranking.py or _codec.py when callers should not
    import it directly. Use __all__ only when an explicit export surface adds value;
    do not use it to disguise an otherwise unclear module boundary.
  examples:
  - constant.example-3-7-1
  tables: []
- section: '3.9'
  title: Use one semantic vocabulary
  requirements:
  - Use clear semantic names that expose the role and meaning of each thing. Treat
    naming as part of the domain model, not as surface polish.
  - Keep one noun for one concept
  - Reuse one exact domain noun for one concept across code, models, schemas, logs,
    errors, tests, and documentation. Prefer consistent vocabulary over synonyms.
  - Name actions by operation and object
  - Use <verb>_<object>[_<outcome-or-context>] for functions and methods.
  - Use a specific verb that states the operation. Avoid vague actions such as handle,
    process, manage, or do when the real operation is known.
  - Name values by role, object, shape, or unit
  - Use <role>_<object>_<kind-or-unit> when each added word removes ambiguity.
  - 'Apply these rules:'
  - 'Name collections by their contents and collection shape: report_names, published_report_ids.'
  - 'Name mappings with the key concept and value concept when useful: filename_to_document_id.'
  - 'Name booleans as positive conditions or controls: is_ready, allow_overwrite.'
  - 'Name quantities with their units: poll_interval_seconds, document_size_bytes.'
  - 'Name identifiers with the object they identify: document_id, request_id.'
  - 'Name destinations and sources by role: source_directory, report_output_file.'
  - Name by purpose or result, not by the current implementation.
  - Remove generic placeholders
  - Replace generic names such as data, item, result, value, config, response, and
    path when the domain noun is known.
  - Keep the shortest name that remains unambiguous in its scope. Do not repeat context
    already made clear by the containing function, class, or module.
  - Prefer report over report_catalog_report because the class already supplies the
    catalog context.
  - Use standard Python casing
  - 'Variables and functions: snake_case.'
  - 'Classes: PascalCase.'
  - 'Constants: UPPER_SNAKE_CASE.'
  - Apply the non-public prefix before the normal casing, such as _load_table, _Table,
    or _MAX_RETRIES.
  - Review important names before finalizing
  - 'Ask:'
  - Does the name use the correct domain noun?
  - Does it reveal the value's role, shape, or unit where needed?
  - Is it consistent with related code and documentation?
  - Can any word be removed without losing clarity?
  examples:
  - constant.example-3-9-1
  - constant.example-3-9-2
  - constant.example-3-9-3
  - constant.example-3-9-4
  - constant.example-3-9-5
  tables: []
>>

example-index: YAML<<
- id: example-3-3-1
  section: '3.3'
  topic: Put stable values near the top
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-7-1
  section: '3.7'
  topic: Mark non-public names explicitly
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-9-1
  section: '3.9'
  topic: Keep one noun for one concept
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-9-2
  section: '3.9'
  topic: Name actions by operation and object
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-9-3
  section: '3.9'
  topic: Name values by role, object, shape, or unit
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-9-4
  section: '3.9'
  topic: Remove generic placeholders
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-9-5
  section: '3.9'
  topic: Remove generic placeholders
  language: python
  scope: illustrative excerpt; not an execution result
>>

example-3-3-1: TEXT<<
from typing import Final

DEFAULT_LIMIT: Final = 10
MAX_RETRIES: Final = 3
>>

example-3-7-1: TEXT<<
# Before: implementation details look public.

@dataclass(frozen=True, slots=True)
class Entry:
    document: SearchDocument
    vector: Vector


def score(entry: Entry, query: Vector) -> SearchHit:
    ...


class SemanticSearch:
    def __init__(self) -> None:
        self.entries: dict[str, Entry] = {}


# After: the public boundary is visible from the names.

@dataclass(frozen=True, slots=True)
class _Entry:
    document: SearchDocument
    vector: Vector


def _score(entry: _Entry, query: Vector) -> SearchHit:
    ...


class SemanticSearch:
    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}
>>

example-3-9-1: TEXT<<
# Before: synonyms hide that both names mean the same concept.
def load_record(user_name: str) -> UserProfile:
    ...


# After: one noun keeps the concept stable.
def load_user_profile(user_name: str) -> UserProfile:
    ...
>>

example-3-9-2: TEXT<<
publish_report()
build_search_index()
read_configuration_file()
>>

example-3-9-3: TEXT<<
source_directory = Path("input")
report_output_file = Path("reports/summary.json")
published_report_ids = (...)
filename_to_document_id = {...}
poll_interval_seconds = 5
document_size_bytes = 1_024
>>

example-3-9-4: TEXT<<
# Before: the names force the reader to reconstruct the domain.
def save_item(item: object, path: Path) -> None:
    result = encode(item)
    path.write_bytes(result)


# After: each name exposes its role.
def save_report(report: Report, report_file: Path) -> None:
    report_bytes = encode_report(report)
    report_file.write_bytes(report_bytes)
>>

example-3-9-5: TEXT<<
class ReportCatalog:
    def add(self, report: Report) -> None:
        ...
>>
</constants>