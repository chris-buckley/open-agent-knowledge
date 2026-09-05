<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Python helpers, control flow, abstraction levels, dependency direction, and compatibility."

rules: YAML<<
- section: '3.5'
  title: Write short descriptive helpers
  requirements:
  - 'Extract a helper when it:'
  - removes meaningful duplication;
  - names a domain rule;
  - isolates validation or conversion;
  - reduces branching or nesting;
  - makes the caller read as a sequence of ideas.
  - Name helpers for what they establish, not how they perform it.
  - Avoid helpers that merely wrap one obvious expression and add navigation cost.
  examples:
  - constant.example-3-5-1
  tables: []
- section: '6.1'
  title: Use guard clauses
  requirements:
  - Invert invalid or exceptional conditions and return or raise early. Keep the successful
    path visually flat.
  examples:
  - constant.example-6-1-1
  tables: []
- section: '6.2'
  title: Keep cyclomatic complexity low
  requirements:
  - 'Count decision points per function:'
  - if and elif;
  - loops;
  - match cases;
  - except clauses;
  - ternaries;
  - boolean and and or inside conditions.
  - 'Use project thresholds when configured. Otherwise:'
  - 'Refactor in this order:'
  - Guard clauses.
  - Extract a named function.
  - Replace repeated branches with a lookup table.
  - Extract named predicates.
  - Use a strategy only when type switching repeats in multiple places.
  - Flatten loops with continue or an extracted loop body.
  - Do not game the metric with dense expressions that hide branches.
  examples: []
  tables:
  - columns:
    - Complexity
    - Action
    rows:
    - - 1–5
      - Fine; leave alone
    - - 6–10
      - Watch; refactor when touching nearby code
    - - 11–15
      - Refactor now
    - - 16+
      - Split immediately
- section: '6.3'
  title: Make finite branching exhaustive
  requirements: []
  examples:
  - constant.example-6-3-1
  tables: []
- section: '6.4'
  title: Keep one responsibility per function
  requirements:
  - A function name containing “and” is a signal to inspect whether the function should
    be split. Small functions with precise names are preferable to large functions
    divided by comments.
  examples: []
  tables: []
- section: '14.1'
  title: Keep one abstraction level per function
  requirements:
  - An orchestration function should name the domain steps. A helper should contain
    the mechanics of one step. Do not make one function move repeatedly between business
    language, parsing, subprocess arguments, storage details, and error formatting.
  - 'Provides: Lets the reader understand the plan without first decoding each implementation
    detail.'
  - 'Apply these rules:'
  - Keep orchestration functions short enough to read as a plan.
  - Extract mechanics only when the helper names a real step or boundary.
  - Keep one small pure decision inline when extraction would add navigation without
    meaning.
  - Move downward in abstraction as the reader moves downward through the module.
  examples:
  - constant.example-14-1-1
  - constant.example-14-1-2
  tables: []
- section: '14.2'
  title: Give each domain rule one authoritative home
  requirements:
  - Use one constant, predicate, value object, constructor, or function as the authoritative
    expression of each domain rule.
  - 'Provides: One change updates every use of the rule and prevents implementations
    from drifting apart.'
  - Deduplicate meaning, not merely matching text. Two equal expressions do not automatically
    need a helper. Two locations enforcing the same domain rule should share one authoritative
    definition.
  - 'Pair this rule with semantic naming:'
  examples:
  - constant.example-14-2-1
  - constant.example-14-2-2
  - constant.example-14-2-3
  tables: []
- section: '14.3'
  title: Separate queries from commands
  requirements:
  - A query returns information without changing externally visible state. A command
    changes state and uses an action name that exposes the effect.
  - 'Provides: Callers can see whether an operation observes or mutates the system.'
  - 'Use:'
  - query names such as is_ready, has_access, find_document, or read_manifest;
  - command names such as create_directory, write_manifest, publish_artifact, or delete_record;
  - combined names only when the combined action is a real domain operation and the
    mutation is visible, such as create_folder_if_missing.
  - Avoid vague names such as ensure, check, resolve, or get_or_create when they conceal
    a state change. Keep an established domain verb when its contract is already precise
    and consistent.
  examples:
  - constant.example-14-3-1
  - constant.example-14-3-2
  tables: []
- section: '14.4'
  title: Make dependency direction explicit
  requirements:
  - High-level workflow code may call lower-level adapters. Lower-level adapters must
    not import or call the workflow that coordinates them.
  - 'Provides: Infrastructure can change without forcing unrelated workflow changes
    or circular dependencies.'
  - 'For a small cohesive script, keep the direction visible through file order:'
  - 'Split modules only when areas have different reasons to change:'
  - 'Apply these rules:'
  - Keep domain records independent from CLI and infrastructure modules.
  - Keep workflow code free from argument-parser and process-exit mechanics.
  - Configure concrete adapters at the application boundary.
  - Avoid circular imports and upward imports from adapters into workflows.
  - Do not create interfaces or modules solely to imitate a layered architecture.
  examples:
  - constant.example-14-4-1
  - constant.example-14-4-2
  - constant.example-14-4-3
  tables: []
- section: '14.6'
  title: Treat public behaviour as a compatibility contract
  requirements:
  - 'For reusable code, the public contract includes:'
  - exported names;
  - parameter names, kinds, order, defaults, and accepted types;
  - return values and ordering;
  - documented exceptions;
  - visible side effects;
  - serialized or emitted shapes;
  - user-visible output relied on by callers or automation.
  - 'Provides: Refactors improve internals without silently breaking callers.'
  - 'Apply these rules:'
  - Define __all__ only when a reusable module benefits from an explicit export surface.
  - Keep private scripts and internal modules free from unnecessary compatibility
    machinery.
  - Deprecate a supported API before removal when callers need a migration period.
  - Preserve behaviour during refactors unless a change is explicitly approved.
  - Document deliberate compatibility breaks and update tests, examples, and migration
    guidance together.
  - Use warnings.deprecated when the supported Python baseline provides it and static
    deprecation metadata adds value.
  examples:
  - constant.example-14-6-1
  - constant.example-14-6-2
  tables: []
>>

example-index: YAML<<
- id: example-3-5-1
  section: '3.5'
  topic: Write short descriptive helpers
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-6-1-1
  section: '6.1'
  topic: Use guard clauses
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-6-3-1
  section: '6.3'
  topic: Make finite branching exhaustive
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-1-1
  section: '14.1'
  topic: Keep one abstraction level per function
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-1-2
  section: '14.1'
  topic: Keep one abstraction level per function
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-2-1
  section: '14.2'
  topic: Give each domain rule one authoritative home
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-2-2
  section: '14.2'
  topic: Give each domain rule one authoritative home
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-2-3
  section: '14.2'
  topic: Give each domain rule one authoritative home
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-14-3-1
  section: '14.3'
  topic: Separate queries from commands
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-3-2
  section: '14.3'
  topic: Separate queries from commands
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-4-1
  section: '14.4'
  topic: Make dependency direction explicit
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-14-4-2
  section: '14.4'
  topic: Make dependency direction explicit
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-14-4-3
  section: '14.4'
  topic: Make dependency direction explicit
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-14-6-1
  section: '14.6'
  topic: Treat public behaviour as a compatibility contract
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-6-2
  section: '14.6'
  topic: Treat public behaviour as a compatibility contract
  language: python
  scope: illustrative excerpt; not an execution result
>>

example-3-5-1: TEXT<<
def _require_limit(limit: int) -> None:
    if limit < 1:
        raise ValueError("limit must be at least 1")
>>

example-6-1-1: TEXT<<
def normalize(text: str) -> str:
    text = text.strip()

    if not text:
        raise ValueError("text must not be blank")

    return text.casefold()
>>

example-6-3-1: TEXT<<
from typing import assert_never


def timeout(mode: Mode) -> int:
    match mode:
        case Mode.FAST:
            return 1
        case Mode.SAFE:
            return 10

    assert_never(mode)
>>

example-14-1-1: TEXT<<
# Before: orchestration and command mechanics compete for attention.
def _publish_artifacts(artifact_uploads: ArtifactUploads) -> None:
    _require_upload_credentials()

    for artifact, source_file in artifact_uploads:
        remote_file = f"{_UPLOAD_FOLDER}/{artifact.name}.zip"
        _run_uploader(("copy", str(source_file), remote_file, "--overwrite"))
        _run_uploader(("verify", remote_file))
>>

example-14-1-2: TEXT<<
# After: orchestration reads as domain steps.
def _publish_artifacts(artifact_uploads: ArtifactUploads) -> None:
    _prepare_upload_destination()

    for artifact_upload in artifact_uploads:
        _publish_artifact(artifact_upload)
>>

example-14-2-1: TEXT<<
# Before: one retry rule appears as unrelated literals.
for attempt in range(1, 4):
    ...

    if attempt == 3:
        ...
>>

example-14-2-2: TEXT<<
# After: one constant owns the retry limit.
_MAX_UPLOAD_ATTEMPTS: Final = 3

for attempt in range(1, _MAX_UPLOAD_ATTEMPTS + 1):
    ...

    if attempt == _MAX_UPLOAD_ATTEMPTS:
        ...
>>

example-14-2-3: TEXT<<
one noun for one concept
one authoritative home for one rule
>>

example-14-3-1: TEXT<<
# Before: one vague operation both asks and acts.
def _ensure_output_directory(output_directory: Path) -> bool:
    if _output_directory_exists(output_directory):
        return False

    _create_output_directory(output_directory)
    return True
>>

example-14-3-2: TEXT<<
# After: each contract is explicit.
def _output_directory_exists(output_directory: Path) -> bool:
    ...


def _create_output_directory(output_directory: Path) -> None:
    ...
>>

example-14-4-1: TEXT<<
CLI boundary
    → workflow
        → filesystem adapter
        → archive adapter
        → remote storage adapter
>>

example-14-4-2: TEXT<<
module contract
constants and records
workflow functions
adapter functions
CLI boundary
>>

example-14-4-3: TEXT<<
artifact_publisher/
├── workflow.py
├── archive.py
├── storage.py
└── cli.py
>>

example-14-6-1: TEXT<<
# Before: a direct rename breaks existing callers.
def load_data(source_folder: Path) -> None:
    ...
>>

example-14-6-2: TEXT<<
# After: the new API is explicit and the old API migrates safely.
__all__ = ["load_tables"]


def load_tables(source_folder: Path) -> None:
    ...


def load_data(source_folder: Path) -> None:
    warn(
        "load_data() is deprecated; use load_tables()",
        DeprecationWarning,
        stacklevel=2,
    )
    load_tables(source_folder)
>>
</constants>