# Python Coding Standard

Status: Canonical default
Applies to: All Python design, implementation, refactoring, review, examples, and generated repositories
Default: Follow this document unless the current request or repository conventions explicitly override it

## 1. Governing principles

Write Python that is:

- fully typed;
- flat and data-oriented;
- standard-library-first;
- compact without becoming cryptic;
- explicit at boundaries;
- deterministic by default;
- low in cyclomatic complexity;
- easy for a human maintainer to inspect;
- named with consistent domain language;
- organized by stable abstraction levels and dependency direction;
- compatible by default at supported public boundaries;
- structured so data carries the architecture;
- verified by tests and objective checks.

Prefer code whose control flow follows the proof of the algorithm. Compress repeated ceremony, not meaning.

## 2. Precedence

Apply rules in this order:

1. The user's current explicit instruction.
2. Existing repository conventions and public APIs.
3. Project formatter, linter, type-checker, and test configuration.
4. This document.
5. General Python convention.

Do not rewrite established project style merely to impose personal preference. Preserve public APIs unless explicitly asked to change them.

## 3. Core style

### 3.1 Type everything meaningful

Type public APIs, stored state, callbacks, collections, return values, and domain identifiers.

```python
from collections.abc import Iterable


def total(values: Iterable[int]) -> int:
    return sum(values)
```

Avoid untyped dictionaries, implicit `Any`, and JSON-shaped internal plumbing when a named type expresses the domain better.

### 3.2 Keep structures flat and data-oriented

Prefer:

- `dataclass(frozen=True, slots=True)` for immutable records;
- tuples, lists, sets, mappings, heaps, and enums;
- small functions operating on explicit values;
- composition over inheritance;
- classes only when they own coherent state or define a useful boundary.

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchDocument:
    key: str
    text: str
```

Do not introduce service layers, factories, abstract base classes, or object hierarchies without a concrete need.

### 3.3 Put stable values near the top

Use named constants for limits, defaults, protocol values, thresholds, and repeated literals.

```python
from typing import Final

DEFAULT_LIMIT: Final = 10
MAX_RETRIES: Final = 3
```

Constants should explain domain meaning, not merely rename obvious values.

### 3.4 Use enums for finite semantic choices

Use `Enum`, `IntEnum`, or `StrEnum` when values represent a closed set with domain meaning.

```python
from enum import StrEnum


class Fit(StrEnum):
    CONTAIN = "contain"
    COVER = "cover"
```

Do not replace simple booleans with enums unless the boolean is ambiguous or likely to grow into more modes.

### 3.5 Write short descriptive helpers

Extract a helper when it:

- removes meaningful duplication;
- names a domain rule;
- isolates validation or conversion;
- reduces branching or nesting;
- makes the caller read as a sequence of ideas.

Name helpers for `what` they establish, not `how` they perform it.

```python
def _require_limit(limit: int) -> None:
    if limit < 1:
        raise ValueError("limit must be at least 1")
```

Avoid helpers that merely wrap one obvious expression and add navigation cost.

### 3.6 Keep one line per coherent idea

Prefer compact expressions where the meaning remains immediate.

```python
ranked = sorted(hits, key=lambda hit: (-hit.score, hit.key))
```

Split expressions when intermediate names reveal domain meaning, errors require separation, or the line becomes visually dense.

### 3.7 Mark non-public names explicitly

Use one leading underscore for implementation details that are not part of the supported public API.

This applies to:

- module-level helper functions;
- internal classes and records;
- instance and class attributes;
- internal constants and type aliases;
- modules whose contents are not a supported import surface.

```python
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
```

Keep public names unprefixed. Do not prefix local variables or parameters merely because they are internal to a function; their scope already communicates that.

Use:

- `_name` for ordinary non-public names;
- `name_` only to avoid a Python keyword or a genuinely harmful collision;
- `__name` only when name mangling is intentionally needed to prevent subclass collisions;
- `__dunder__` only for Python-defined data-model and protocol methods, never as invented decoration.

A private module may be named `_ranking.py` or `_codec.py` when callers should not import it directly. Use `__all__` only when an explicit export surface adds value; do not use it to disguise an otherwise unclear module boundary.

### 3.8 Separate conceptual groups with blank lines

Use one blank line when adjacent declarations or statements change purpose. Keep one concept together.

Separate groups such as:

- public API values and private implementation values;
- defaults and validation bounds;
- public and private type aliases;
- validation, preparation, mutation, and output phases inside a function.

Do not split a pair, range, or small group that readers must inspect together. Use whitespace as light structure, not decoration.

```python
# Before: different roles appear as one visual group.
DEFAULT_LIMIT: Final = 10
_MIN_COSINE_SCORE: Final = -1.0
_MAX_COSINE_SCORE: Final = 1.0


# After: one blank line exposes the change in purpose.
DEFAULT_LIMIT: Final = 10

_MIN_COSINE_SCORE: Final = -1.0
_MAX_COSINE_SCORE: Final = 1.0
```

### 3.9 Use one semantic vocabulary

Use clear semantic names that expose the role and meaning of each thing. Treat naming as part of the domain model, not as surface polish.

#### Keep one noun for one concept

Reuse one exact domain noun for one concept across code, models, schemas, logs, errors, tests, and documentation. Prefer consistent vocabulary over synonyms.

```python
# Before: synonyms hide that both names mean the same concept.
def load_record(user_name: str) -> UserProfile:
    ...


# After: one noun keeps the concept stable.
def load_user_profile(user_name: str) -> UserProfile:
    ...
```

#### Name actions by operation and object

Use `<verb>_<object>[_<outcome-or-context>]` for functions and methods.

```python
publish_report()
build_search_index()
read_configuration_file()
```

Use a specific verb that states the operation. Avoid vague actions such as `handle`, `process`, `manage`, or `do` when the real operation is known.

#### Name values by role, object, shape, or unit

Use `<role>_<object>_<kind-or-unit>` when each added word removes ambiguity.

```python
source_directory = Path("input")
report_output_file = Path("reports/summary.json")
published_report_ids = (...)
filename_to_document_id = {...}
poll_interval_seconds = 5
document_size_bytes = 1_024
```

Apply these rules:

- Name collections by their contents and collection shape: `report_names`, `published_report_ids`.
- Name mappings with the key concept and value concept when useful: `filename_to_document_id`.
- Name booleans as positive conditions or controls: `is_ready`, `allow_overwrite`.
- Name quantities with their units: `poll_interval_seconds`, `document_size_bytes`.
- Name identifiers with the object they identify: `document_id`, `request_id`.
- Name destinations and sources by role: `source_directory`, `report_output_file`.
- Name by purpose or result, not by the current implementation.

#### Remove generic placeholders

Replace generic names such as `data`, `item`, `result`, `value`, `config`, `response`, and `path` when the domain noun is known.

```python
# Before: the names force the reader to reconstruct the domain.
def save_item(item: object, path: Path) -> None:
    result = encode(item)
    path.write_bytes(result)


# After: each name exposes its role.
def save_report(report: Report, report_file: Path) -> None:
    report_bytes = encode_report(report)
    report_file.write_bytes(report_bytes)
```

Keep the shortest name that remains unambiguous in its scope. Do not repeat context already made clear by the containing function, class, or module.

```python
class ReportCatalog:
    def add(self, report: Report) -> None:
        ...
```

Prefer `report` over `report_catalog_report` because the class already supplies the catalog context.

#### Use standard Python casing

- Variables and functions: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.

Apply the non-public prefix before the normal casing, such as `_load_table`, `_Table`, or `_MAX_RETRIES`.

#### Review important names before finalizing

Ask:

1. Does the name use the correct domain noun?
2. Does it reveal the value's role, shape, or unit where needed?
3. Is it consistent with related code and documentation?
4. Can any word be removed without losing clarity?

## 4. Domain modelling

### 4.1 Validate once at the boundary

Convert raw external input into validated internal values as early as possible. Internal functions should operate on trustworthy values rather than repeatedly rechecking raw strings and dictionaries.

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Amount:
    value: Decimal


def parse_amount(text: str) -> Amount:
    value = Decimal(text)

    if value < 0:
        raise ValueError("amount must be non-negative")

    return Amount(value)
```

### 4.2 Make invalid states difficult or impossible to construct

Prefer distinct variants over records containing contradictory flags and optional fields.

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PendingJob:
    identifier: int


@dataclass(frozen=True, slots=True)
class FinishedJob:
    identifier: int
    finished_at: datetime


type Job = PendingJob | FinishedJob
```

### 4.3 Distinguish interchangeable primitives

Use `NewType`, enums, or small value objects where the type checker should distinguish semantically different values with the same runtime representation.

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)
```

### 4.4 Preserve the meaning of absence

Do not collapse a missing key, a stored `None`, an empty sequence, and an invalid value into the same state.

```python
def cached_name(cache: Mapping[str, str | None], key: str) -> str | None:
    if key not in cache:
        raise KeyError(key)

    return cache[key]
```

### 4.5 Prefer immutable values at boundaries

Use tuples, frozen dataclasses, and frozensets for returned snapshots or values that should not be mutated through aliases.

Copy caller-owned mutable input when the implementation must retain it.

## 5. Function and API design

### 5.1 Use the narrowest useful input protocol

- Use `Iterable[T]` for a single pass.
- Use `Collection[T]` when length or membership is required.
- Use `Sequence[T]` when ordering and indexing are required.
- Use `Mapping[K, V]` when mutation is unnecessary.
- Use concrete mutable types only when mutation is part of the contract.

```python
def count_errors(lines: Iterable[str]) -> int:
    return sum("ERROR" in line for line in lines)
```

### 5.2 Make ambiguous parameters keyword-only

```python
def render(
    path: Path,
    *,
    fit: Fit,
    cache: bool = True,
) -> None:
    ...
```

Avoid calls such as `render(path, True, False)` where argument meaning is invisible.

### 5.3 Keep public APIs small and explicit

Expose the few operations the caller needs. Keep validation, normalization, ranking, and storage details private unless they form a genuine reusable contract.

### 5.4 Depend on behaviour at real boundaries

Use `Protocol` for a genuine interchangeable dependency such as storage, a clock, an embedder, or a transport.

```python
from typing import Protocol


class UserStore(Protocol):
    def get(self, user_id: UserId) -> User:
        ...
```

Do not add protocols for every class or function. A callable type alias is often enough.

### 5.5 Preserve public signatures during refactors

Do not break exported names, parameter order, return types, exception contracts, or serialization shapes unless explicitly authorised.

## 6. Control flow and complexity

### 6.1 Use guard clauses

Invert invalid or exceptional conditions and return or raise early. Keep the successful path visually flat.

```python
def normalize(text: str) -> str:
    text = text.strip()

    if not text:
        raise ValueError("text must not be blank")

    return text.casefold()
```

### 6.2 Keep cyclomatic complexity low

Count decision points per function:

- `if` and `elif`;
- loops;
- `match` cases;
- `except` clauses;
- ternaries;
- boolean `and` and `or` inside conditions.

Use project thresholds when configured. Otherwise:

| Complexity | Action |
|---:|---|
| 1–5 | Fine; leave alone |
| 6–10 | Watch; refactor when touching nearby code |
| 11–15 | Refactor now |
| 16+ | Split immediately |

Refactor in this order:

1. Guard clauses.
2. Extract a named function.
3. Replace repeated branches with a lookup table.
4. Extract named predicates.
5. Use a strategy only when type switching repeats in multiple places.
6. Flatten loops with `continue` or an extracted loop body.

Do not game the metric with dense expressions that hide branches.

### 6.3 Make finite branching exhaustive

```python
from typing import assert_never


def timeout(mode: Mode) -> int:
    match mode:
        case Mode.FAST:
            return 1
        case Mode.SAFE:
            return 10

    assert_never(mode)
```

### 6.4 Keep one responsibility per function

A function name containing “and” is a signal to inspect whether the function should be split. Small functions with precise names are preferable to large functions divided by comments.

## 7. State, effects, and determinism

### 7.1 Keep pure computation separate from I/O

Read, parse, compute, and write as distinct stages.

```python
def parse_dates(text: str) -> tuple[date, ...]:
    return tuple(date.fromisoformat(line) for line in text.splitlines())


def find_overdue(
    due_dates: Iterable[date],
    today: date,
) -> tuple[date, ...]:
    return tuple(due_date for due_date in due_dates if due_date < today)
```

### 7.2 Inject nondeterministic inputs

Pass clocks, random generators, identifiers, external clients, and environment-derived values into the function that needs them.

```python
def choose_worker(workers: Sequence[str], rng: Random) -> str:
    return rng.choice(workers)
```

### 7.3 Prepare before committing

Validate and compute the complete update before mutating shared state.

```python
def update_many(self, updates: Iterable[tuple[str, str]]) -> None:
    prepared = {key: normalize(value) for key, value in updates}
    validate_updates(prepared)
    self._values.update(prepared)
```

Batch operations should be atomic where practical.

### 7.4 Define deterministic ordering

Use explicit tie-breakers for rankings, stable output ordering, generated files, logs, and tests.

```python
ranked = sorted(hits, key=lambda hit: (-hit.score, hit.key))
```

Never rely on set order or incidental arrival order when output is externally visible.

## 8. Errors and validation

### 8.1 Catch only expected exceptions

Catch exceptions in the narrowest scope that can handle them correctly. Translate them into domain errors with exception chaining.

```python
def read_price(path: Path) -> Decimal:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise PriceFileMissing(path) from error

    try:
        return Decimal(text)
    except InvalidOperation as error:
        raise PriceError(text) from error
```

Do not use broad `except Exception` unless at a true process boundary that logs and re-raises or deliberately terminates.

### 8.2 Use exceptions for caller errors and assertions for invariants

```python
def take(items: Sequence[T], limit: int) -> Sequence[T]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    return items[:limit]
```

Use `assert` only for internal states believed impossible after validation, never for public input validation.

### 8.3 Write actionable error messages

State the violated rule and, when useful, the received value or expected range. Do not expose secrets, tokens, full credentials, or sensitive payloads.

## 9. Resources, performance, and numerical behaviour

### 9.1 Express resource lifetimes with context managers

```python
with path.open(encoding="utf-8") as stream:
    process(stream)
```

Use context managers for files, locks, temporary resources, transactions, and connections.

### 9.2 Stream when materialization is unnecessary

Avoid reading whole files or datasets into memory when a single pass is sufficient.

Materialize deliberately when atomic validation, repeated traversal, stable snapshots, sorting, or length checks require it.

### 9.3 Choose domain-correct numeric and time primitives

- Use `Decimal` for money and contractual decimal arithmetic.
- Use `Fraction` for exact rational arithmetic.
- Use `monotonic()` for elapsed time and timeouts.
- Use UTC-aware `datetime` values for real-world instants.
- Avoid binary floats when exact decimal equality is part of the contract.

### 9.4 Optimize after measuring

Prefer clear `O(n)` or `O(n log k)` algorithms and appropriate data structures before micro-optimizing syntax.

Measure hotspots with representative inputs. Preserve correctness and readability unless profiling demonstrates a material need.

## 10. Imports and dependencies

### 10.1 Prefer the standard library

Add a dependency only when it provides substantial capability, correctness, performance, interoperability, or maintenance value.

Before adding one, check whether the standard library already provides an adequate primitive.

### 10.2 Keep imports explicit

- Avoid wildcard imports.
- Group standard library, third-party, and local imports.
- Import symbols when it improves clarity.
- Import modules when qualification carries useful context.
- Avoid import-time side effects.

### 10.3 Pin and justify runtime dependencies

Use the repository's established dependency mechanism. Do not introduce packages for trivial helpers.

## 11. Documentation

### 11.1 Use rare terse STE comments

Let names, types, helpers, and layout explain normal code. Add a comment only when it removes ambiguity about:

- a non-obvious invariant;
- a required operation order;
- a compatibility constraint;
- a compact alias whose purpose is not obvious from its name;
- a surprising algorithmic or performance reason;
- a deliberate trade-off.

Prefer a same-line comment when it explains one short declaration or statement and the complete line stays within 120 characters. Separate code and comment with two spaces. Do not align comments into columns.

```python
SearchHits: TypeAlias = tuple[SearchHit[_T], ...]  # Keep results ordered and immutable.
```

Keep the comment terse. Aim for two to seven words when that is enough. Write one short sentence in active voice and clear Simplified Technical English (STE):

- name the actor or operation;
- state one idea;
- use present tense or the imperative form;
- use short, common words;
- avoid vague pronouns and passive constructions;
- explain the reason instead of narrating the next line.

```python
_require_unique_keys(batch)  # Reject duplicates before embedding.
return tuple(nsmallest(limit, hits, key=_rank_key))  # Avoid custom top-k logic.
```

Use a full-line comment only when the code spans multiple lines, the rationale applies to a block, or an inline comment would exceed the width or look cramped.

```python
# Preserve the old file until the replacement is complete.
temporary.replace(destination)
```

Provides: Keeps a short comment attached to the exact declaration or statement it explains without adding vertical noise.

```python
# Before: a short comment consumes a separate visual block.
# Keep results ordered and immutable.
SearchHits: TypeAlias = tuple[SearchHit[_T], ...]


# After: the terse rationale stays with the declaration.
SearchHits: TypeAlias = tuple[SearchHit[_T], ...]  # Keep results ordered and immutable.
```

Do not narrate the next line, repeat a function name, use decorative headings, align trailing comments into columns, or add comments to meet a quota.

### 11.2 Keep docstrings concise and contractual

Document public behaviour, important invariants, raised domain exceptions, units, and side effects. Avoid narrating implementation line by line.

Use active voice where practical. State what the caller can rely on.

### 11.3 Preserve rationale near unusual choices

Place the shortest useful rationale on the same line when it stays neat. Place a full-line rationale above the smallest relevant block when it explains more than one line. Explain `why`, not `what`.

### 11.4 Teach changes with focused before-and-after examples

When explaining a best practice, reviewing code, or proposing a nontrivial refactor, prefer a small `before → after` pair that isolates the change and states the coding behaviour it provides.

Use this shape:

````markdown
## <Point>

Provides: <observable improvement in coding behaviour>

```python
# Before
...
```

```python
# After
...
```
````

The examples should:

- preserve the relevant behaviour unless a behaviour change is intentional and stated;
- demonstrate one primary idea at a time;
- use realistic code rather than a contrived bad example;
- be complete enough to understand without unrelated scaffolding;
- show the resulting behaviour, not merely a cosmetic syntax difference;
- avoid repeating an entire file when a focused excerpt communicates the change.

For a direct implementation request, provide the finished implementation first. Use before-and-after guidance when it materially helps the user or another agent understand a design decision; do not force it into trivial answers.

## 12. Testing and verification

### 12.1 Reduce the test surface before adding tests

Design rule: Make correctness obvious by construction before adding tests.

Before writing a test for a difficult private detail, redesign that detail. Prefer code that makes the rule impossible to break, delegates mechanics to a trusted standard-library primitive, or exposes one small pure decision.

Do not use this rule to skip verification. Remove avoidable implementation risk, then test the remaining public behaviour.

Ask:

- Can a type or constructor remove an invalid state?
- Can a standard-library primitive replace custom control flow?
- Can a pure function replace I/O-coupled logic?
- Can injected inputs remove timing, randomness, or environment cases?
- Can deterministic ordering remove flaky branches?
- Can a data structure or named predicate replace repeated conditions?

#### Delegate mechanics to the standard library

Provides: Removes custom selection branches, so tests focus on ranking policy.

```python
# Before: custom selection creates extra behaviour to verify.
def _top_hits(
    hits: Iterable[SearchHit[_T]],
    limit: int,
) -> tuple[SearchHit[_T], ...]:
    selected: list[SearchHit[_T]] = []

    for hit in hits:
        selected.append(hit)
        selected.sort(key=_rank_key)

        if len(selected) > limit:
            selected.pop()

    return tuple(selected)
```

```python
# After: the standard library handles top-result selection.
def _top_hits(
    hits: Iterable[SearchHit[_T]],
    limit: int,
) -> tuple[SearchHit[_T], ...]:
    return tuple(nsmallest(limit, hits, key=_rank_key))
```

Test the public score order, tie-break rule, and limit. Do not recreate tests for the standard-library heap algorithm.

#### Make invalid combinations unrepresentable

Provides: Removes contradictory states, so tests do not need to enumerate them.

```python
# Before: callers can construct conflicting fields.
@dataclass(slots=True)
class Job:
    identifier: int
    finished: bool
    finished_at: datetime | None
```

```python
# After: each state contains only valid fields.
@dataclass(frozen=True, slots=True)
class PendingJob:
    identifier: int


@dataclass(frozen=True, slots=True)
class FinishedJob:
    identifier: int
    finished_at: datetime


type Job = PendingJob | FinishedJob
```

Test parsing and state transitions. No test is required for a state the model cannot construct.

### 12.2 Test observable behaviour

Prefer tests against the public contract rather than private helpers or implementation details.

```python
def test_equal_scores_are_ordered_by_key() -> None:
    search = SemanticSearch(embed_equal)
    search.add_many(
        (
            SearchDocument("b", "second", None),
            SearchDocument("a", "first", None),
        )
    )

    assert tuple(hit.key for hit in search.search("query")) == ("a", "b")
```

### 12.3 Cover the important behavioural classes

Test:

1. Normal behaviour.
2. Boundary values.
3. Invalid input.
4. State after a failed operation.
5. Determinism under ties and repeated execution.
6. Public API compatibility during refactors.

### 12.4 Run checks before and after refactoring

Use project commands when available. Common checks include:

```text
python -m unittest
python -m pytest
python -m compileall .
ruff check .
ruff format --check .
mypy .
pyright
radon cc -s -a <path>
```

Do not claim tests passed unless they were run. State clearly when verification was unavailable.

### 12.5 Report complexity after nontrivial refactors

Use this format:

```markdown
## Complexity report
| Function | Before | After |
|----------|-------:|------:|
| parse_order | 14 | 4 |

Extracted: validate_header, resolve_discount
Behavior verified: all tests passed
```

## 13. Formatting and layout

### 13.1 Keep small signatures horizontal

Provides: Shows one small API as one coherent idea instead of a vertical parameter inventory.

When no repository formatter rule exists, keep a function signature on one line when:

- it has at most four caller-supplied parameters, excluding `self` or `cls`;
- each annotation and default is short and simple;
- the complete line is at most 120 characters.

```python
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
```

Keep the keyword-only marker inline. Use a named return alias only when it describes a useful domain shape; never create an alias solely to cheat the width limit. Do not introduce an options object merely to shorten a simple signature.

Use vertical layout when the signature exceeds the width, contains complex annotations or defaults, or has enough parameters that grouping improves comprehension. Repository formatter settings still take precedence.

### 13.2 Group code by concept

- Follow the project's formatter.
- Keep related constants, types, public functions, and private helpers grouped coherently.
- Separate conceptual groups with one blank line; keep each group compact.
- Avoid giant files, but do not fragment a small cohesive module across many files.
- Avoid deeply nested packages and ceremonial `__init__.py` exports without a real API need.
- Keep the repository tree minimal and predictable.

A preferred module shape is:

```text
module docstring
imports
constants
type aliases
enums
public records
private records
public functions or primary class
private helpers
```

Use the shape as a guide, not an inflexible template.

## 14. Maintainability architecture

### 14.1 Keep one abstraction level per function

An orchestration function should name the domain steps. A helper should contain the mechanics of one step. Do not make one function move repeatedly between business language, parsing, subprocess arguments, storage details, and error formatting.

Provides: Lets the reader understand the plan without first decoding each implementation detail.

```python
# Before: orchestration and command mechanics compete for attention.
def _publish_artifacts(artifact_uploads: ArtifactUploads) -> None:
    _require_upload_credentials()

    for artifact, source_file in artifact_uploads:
        remote_file = f"{_UPLOAD_FOLDER}/{artifact.name}.zip"
        _run_uploader(("copy", str(source_file), remote_file, "--overwrite"))
        _run_uploader(("verify", remote_file))
```

```python
# After: orchestration reads as domain steps.
def _publish_artifacts(artifact_uploads: ArtifactUploads) -> None:
    _prepare_upload_destination()

    for artifact_upload in artifact_uploads:
        _publish_artifact(artifact_upload)
```

Apply these rules:

- Keep orchestration functions short enough to read as a plan.
- Extract mechanics only when the helper names a real step or boundary.
- Keep one small pure decision inline when extraction would add navigation without meaning.
- Move downward in abstraction as the reader moves downward through the module.

### 14.2 Give each domain rule one authoritative home

Use one constant, predicate, value object, constructor, or function as the authoritative expression of each domain rule.

Provides: One change updates every use of the rule and prevents implementations from drifting apart.

```python
# Before: one retry rule appears as unrelated literals.
for attempt in range(1, 4):
    ...

    if attempt == 3:
        ...
```

```python
# After: one constant owns the retry limit.
_MAX_UPLOAD_ATTEMPTS: Final = 3

for attempt in range(1, _MAX_UPLOAD_ATTEMPTS + 1):
    ...

    if attempt == _MAX_UPLOAD_ATTEMPTS:
        ...
```

Deduplicate `meaning`, not merely matching text. Two equal expressions do not automatically need a helper. Two locations enforcing the same domain rule should share one authoritative definition.

Pair this rule with semantic naming:

```text
one noun for one concept
one authoritative home for one rule
```

### 14.3 Separate queries from commands

A query returns information without changing externally visible state. A command changes state and uses an action name that exposes the effect.

Provides: Callers can see whether an operation observes or mutates the system.

```python
# Before: one vague operation both asks and acts.
def _ensure_output_directory(output_directory: Path) -> bool:
    if _output_directory_exists(output_directory):
        return False

    _create_output_directory(output_directory)
    return True
```

```python
# After: each contract is explicit.
def _output_directory_exists(output_directory: Path) -> bool:
    ...


def _create_output_directory(output_directory: Path) -> None:
    ...
```

Use:

- query names such as `is_ready`, `has_access`, `find_document`, or `read_manifest`;
- command names such as `create_directory`, `write_manifest`, `publish_artifact`, or `delete_record`;
- combined names only when the combined action is a real domain operation and the mutation is visible, such as `create_folder_if_missing`.

Avoid vague names such as `ensure`, `check`, `resolve`, or `get_or_create` when they conceal a state change. Keep an established domain verb when its contract is already precise and consistent.

### 14.4 Make dependency direction explicit

High-level workflow code may call lower-level adapters. Lower-level adapters must not import or call the workflow that coordinates them.

Provides: Infrastructure can change without forcing unrelated workflow changes or circular dependencies.

```text
CLI boundary
    → workflow
        → filesystem adapter
        → archive adapter
        → remote storage adapter
```

For a small cohesive script, keep the direction visible through file order:

```text
module contract
constants and records
workflow functions
adapter functions
CLI boundary
```

Split modules only when areas have different reasons to change:

```text
artifact_publisher/
├── workflow.py
├── archive.py
├── storage.py
└── cli.py
```

Apply these rules:

- Keep domain records independent from CLI and infrastructure modules.
- Keep workflow code free from argument-parser and process-exit mechanics.
- Configure concrete adapters at the application boundary.
- Avoid circular imports and upward imports from adapters into workflows.
- Do not create interfaces or modules solely to imitate a layered architecture.

### 14.5 Make objective conventions executable

Put mechanically checkable rules in repository configuration. Run the same checks locally and in continuous integration.

Provides: The standard remains consistent across editors, developers, agents, and build pipelines.

```toml
[tool.ruff]
line-length = 120
```

```text
ruff check .
ruff format --check .
pyright
python -m unittest
radon cc -s -a .
```

Apply these rules:

- Let prose explain `why` a rule exists.
- Let tool configuration enforce what a tool can check objectively.
- Use the repository's established formatter, linter, type checker, and test runner.
- Run the same required checks locally and in CI.
- Keep generated code subject to the same checks as human-written code.
- Do not claim compliance with a check that was not run.

### 14.6 Treat public behaviour as a compatibility contract

For reusable code, the public contract includes:

- exported names;
- parameter names, kinds, order, defaults, and accepted types;
- return values and ordering;
- documented exceptions;
- visible side effects;
- serialized or emitted shapes;
- user-visible output relied on by callers or automation.

Provides: Refactors improve internals without silently breaking callers.

```python
# Before: a direct rename breaks existing callers.
def load_data(source_folder: Path) -> None:
    ...
```

```python
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
```

Apply these rules:

- Define `__all__` only when a reusable module benefits from an explicit export surface.
- Keep private scripts and internal modules free from unnecessary compatibility machinery.
- Deprecate a supported API before removal when callers need a migration period.
- Preserve behaviour during refactors unless a change is explicitly approved.
- Document deliberate compatibility breaks and update tests, examples, and migration guidance together.
- Use `warnings.deprecated` when the supported Python baseline provides it and static deprecation metadata adds value.

### 14.7 Use type-system guards during refactoring

#### Mark genuine overrides

Use `@override` for every method intended to override a base-class or protocol method.

Provides: The type checker catches misspelled, renamed, or stale overrides.

```python
# Before: a base-method rename can silently break the override.
class RecordingStorageClient(StorageClient):
    def upload_artifact(self, artifact_upload: ArtifactUpload) -> None:
        ...
```

```python
# After: the type checker verifies the relationship.
from typing import override


class RecordingStorageClient(StorageClient):
    @override
    def upload_artifact(self, artifact_upload: ArtifactUpload) -> None:
        ...
```

Use `typing_extensions.override` only when the supported Python baseline requires it. Continue to avoid inheritance unless it models a real relationship.

#### Make swappable record fields keyword-only

Use `kw_only=True` when two or more record fields have similar types or easily confused roles.

Provides: Constructor calls expose each field's role and prevent positional reversal.

```python
# Before: two paths can be reversed silently.
artifact_upload = ArtifactUpload(local_file, remote_file)
```

```python
# After: the call names both roles.
@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactUpload:
    local_file: Path
    remote_file: Path


artifact_upload = ArtifactUpload(
    local_file=local_file,
    remote_file=remote_file,
)
```

Do not make every record keyword-only. Use it when the call-site clarity or safety is material.

### 14.8 Separate user output from operational logging

Use `print` for direct command-line results intended for the user. Use logging for diagnostics, retries, operational events, and exception traces.

Provides: CLI output stays stable and readable while operations remain observable.

```python
# Before: results and diagnostics share one channel.
print(f"published {artifact_name}")
print(f"retrying after {error}")
print(f"Publish complete: {destination}")
```

```python
# After: each channel has one purpose.
logger = logging.getLogger(__name__)

logger.info("artifact_published artifact=%s", artifact_name)
logger.warning("publish_retry_started attempt=%d", attempt)
print(f"Publish complete: {destination}")
```

Apply these rules:

- Create module loggers with `logging.getLogger(__name__)`.
- Configure logging only at the application boundary.
- Pass variable values as logging arguments instead of interpolating eagerly.
- Use stable semantic event names that match the domain vocabulary.
- Use `logger.exception()` only inside an exception handler when a stack trace helps.
- Keep secrets, credentials, tokens, and sensitive payloads out of logs.
- Keep simple scripts on `print` until operational logging provides real value.

### 14.9 Name tests as a behaviour index

Name tests so the collected test names describe the system's contract without opening each body.

Provides: The test suite becomes searchable documentation and failure reports become actionable.

Use this pattern when each part adds information:

```text
test_<action>_<condition>_<outcome>
```

```python
# Before: the name reveals little behaviour.
def test_retry() -> None:
    ...
```

```python
# After: the name states the condition and outcome.
def test_publish_retries_after_transient_failure() -> None:
    ...
```

Prefer names such as:

```python
def test_dry_run_skips_remote_publish() -> None:
    ...


def test_checksum_mismatch_fails_before_publish() -> None:
    ...


def test_equal_scores_use_key_as_tiebreaker() -> None:
    ...
```

Keep the shortest test name that uniquely states the behaviour. Reuse the same domain nouns as the production code, errors, logs, and documentation.


## 15. Patterns to avoid

Avoid by default:

- untyped dictionaries passed through many layers;
- JSON as an internal domain model;
- mutable default arguments;
- shared global mutable state;
- broad exception swallowing;
- deeply nested branching;
- boolean parameter soup;
- inheritance for code reuse alone;
- one class per file by convention;
- “manager”, “service”, or “utils” modules with unclear ownership;
- clever one-liners hiding multiple decisions;
- comments that compensate for poor names;
- premature abstraction;
- premature optimization;
- mocks of internal implementation details;
- nondeterministic result order;
- import-time network, filesystem, or process work;
- silent fallback that hides invalid input or configuration;
- orchestration functions that mix domain steps with low-level mechanics;
- duplicated domain rules with no authoritative home;
- query names that conceal mutation;
- lower-level adapters that import or call higher-level workflows;
- objective conventions documented only in prose;
- immediate removal of supported public APIs without migration;
- operational diagnostics mixed into stable CLI output;
- vague test names that hide the condition or outcome.

## 16. Preferred implementation flow

```text
raw input
→ boundary parsing
→ validated domain values
→ pure computation
→ complete prepared change
→ atomic commit
→ deterministic output
```

Keep external effects at visible boundaries. Make the centre of the program operate on explicit, trustworthy data.

## 17. Review checklist

Before considering Python work complete, check:

- [ ] Does the current repository convention take precedence where necessary?
- [ ] Are public APIs and externally visible behaviour preserved?
- [ ] Are public names unprefixed and non-public implementation details marked with a single leading underscore?
- [ ] Does one exact domain noun represent each concept across code, models, schemas, logs, errors, tests, and documentation?
- [ ] Do actions, values, collections, booleans, quantities, identifiers, and mappings expose their role, shape, or unit where needed?
- [ ] Are generic placeholder names replaced when the domain noun is known?
- [ ] Has each important name passed the four-question naming review?
- [ ] Do small signatures stay horizontal instead of becoming mechanical parameter lists?
- [ ] Do blank lines separate different concepts without splitting related values?
- [ ] Are meaningful inputs, outputs, callbacks, and state fully typed?
- [ ] Are raw inputs validated once at the boundary?
- [ ] Are invalid states difficult to construct?
- [ ] Are data structures carrying the architecture without needless classes?
- [ ] Are stable values represented as named constants?
- [ ] Are finite semantic choices represented clearly?
- [ ] Are functions flat, single-purpose, and below the complexity threshold?
- [ ] Are I/O and nondeterminism kept at explicit boundaries?
- [ ] Are batch mutations prepared before state is changed?
- [ ] Are ordering and tie-breaking deterministic?
- [ ] Are exceptions narrow, specific, and chained where translated?
- [ ] Are resource lifetimes explicit?
- [ ] Are mutable defaults and ownership leaks absent?
- [ ] Are domain-correct numeric and time primitives used?
- [ ] Are dependencies necessary and standard-library alternatives considered?
- [ ] Does each orchestration function stay at one abstraction level and read as a sequence of domain steps?
- [ ] Does each domain rule have one authoritative home?
- [ ] Do query names remain free of hidden mutation, and do command names expose their effects?
- [ ] Does dependency flow move from the application boundary through workflows to lower-level adapters without upward imports?
- [ ] Are objective rules encoded in repository tools and run consistently locally and in CI?
- [ ] Does reusable public code preserve or deliberately migrate its complete compatibility contract?
- [ ] Does every intended override use `@override` when inheritance is present?
- [ ] Do easily confused record fields use keyword-only construction where it materially improves safety?
- [ ] Are direct CLI results separated from operational logging when logging is warranted?
- [ ] Did the design remove avoidable custom logic and invalid states before tests were added?
- [ ] Do tests verify public behaviour, failure state, and boundary cases?
- [ ] Do test names state the action, condition, and outcome using the production domain vocabulary?
- [ ] Were formatter, type, lint, test, and complexity checks run when available?
- [ ] Is the result compact without hiding meaning?
- [ ] Do short comments explain only non-obvious aliases, invariants, order, safeguards, or trade-offs?
- [ ] Does each comment use terse active STE and stay inline when one short line remains neat?
- [ ] Do full-line comments explain a multiline construct or block rather than one short line?
- [ ] When guidance is nontrivial, does a focused before-and-after example show the behaviour gained?

## 18. Final judgement rule

Prefer the implementation a strong human maintainer can understand, verify, and safely modify years later. Elegant Python is explicit about meaning, restrained about abstraction, economical in ceremony, and honest about control flow.
