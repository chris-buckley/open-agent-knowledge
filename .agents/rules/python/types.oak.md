<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Python meaningful types, domain records, validation boundaries, and public input contracts."

rules: YAML<<
- section: '3.1'
  title: Type everything meaningful
  requirements:
  - Type public APIs, stored state, callbacks, collections, return values, and domain
    identifiers.
  - Avoid untyped dictionaries, implicit Any, and JSON-shaped internal plumbing when
    a named type expresses the domain better.
  examples:
  - constant.example-3-1-1
  tables: []
- section: '3.2'
  title: Keep structures flat and data-oriented
  requirements:
  - 'Prefer:'
  - dataclass(frozen=True, slots=True) for immutable records;
  - tuples, lists, sets, mappings, heaps, and enums;
  - small functions operating on explicit values;
  - composition over inheritance;
  - classes only when they own coherent state or define a useful boundary.
  - Do not introduce service layers, factories, abstract base classes, or object hierarchies
    without a concrete need.
  examples:
  - constant.example-3-2-1
  tables: []
- section: '3.4'
  title: Use enums for finite semantic choices
  requirements:
  - Use Enum, IntEnum, or StrEnum when values represent a closed set with domain meaning.
  - Do not replace simple booleans with enums unless the boolean is ambiguous or likely
    to grow into more modes.
  examples:
  - constant.example-3-4-1
  tables: []
- section: '4.1'
  title: Validate once at the boundary
  requirements:
  - Convert raw external input into validated internal values as early as possible.
    Internal functions should operate on trustworthy values rather than repeatedly
    rechecking raw strings and dictionaries.
  examples:
  - constant.example-4-1-1
  tables: []
- section: '4.2'
  title: Make invalid states difficult or impossible to construct
  requirements:
  - Prefer distinct variants over records containing contradictory flags and optional
    fields.
  examples:
  - constant.example-4-2-1
  tables: []
- section: '4.3'
  title: Distinguish interchangeable primitives
  requirements:
  - Use NewType, enums, or small value objects where the type checker should distinguish
    semantically different values with the same runtime representation.
  examples:
  - constant.example-4-3-1
  tables: []
- section: '4.4'
  title: Preserve the meaning of absence
  requirements:
  - Do not collapse a missing key, a stored None, an empty sequence, and an invalid
    value into the same state.
  examples:
  - constant.example-4-4-1
  tables: []
- section: '4.5'
  title: Prefer immutable values at boundaries
  requirements:
  - Use tuples, frozen dataclasses, and frozensets for returned snapshots or values
    that should not be mutated through aliases.
  - Copy caller-owned mutable input when the implementation must retain it.
  examples: []
  tables: []
- section: '5.1'
  title: Use the narrowest useful input protocol
  requirements:
  - Use Iterable[T] for a single pass.
  - Use Collection[T] when length or membership is required.
  - Use Sequence[T] when ordering and indexing are required.
  - Use Mapping[K, V] when mutation is unnecessary.
  - Use concrete mutable types only when mutation is part of the contract.
  examples:
  - constant.example-5-1-1
  tables: []
- section: '5.2'
  title: Make ambiguous parameters keyword-only
  requirements:
  - Avoid calls such as render(path, True, False) where argument meaning is invisible.
  examples:
  - constant.example-5-2-1
  tables: []
- section: '5.3'
  title: Keep public APIs small and explicit
  requirements:
  - Expose the few operations the caller needs. Keep validation, normalization, ranking,
    and storage details private unless they form a genuine reusable contract.
  examples: []
  tables: []
- section: '5.4'
  title: Depend on behaviour at real boundaries
  requirements:
  - Use Protocol for a genuine interchangeable dependency such as storage, a clock,
    an embedder, or a transport.
  - Do not add protocols for every class or function. A callable type alias is often
    enough.
  examples:
  - constant.example-5-4-1
  tables: []
- section: '5.5'
  title: Preserve public signatures during refactors
  requirements:
  - Do not break exported names, parameter order, return types, exception contracts,
    or serialization shapes unless explicitly authorised.
  examples: []
  tables: []
- section: '14.7'
  title: Use type-system guards during refactoring
  requirements:
  - Mark genuine overrides
  - Use @override for every method intended to override a base-class or protocol method.
  - 'Provides: The type checker catches misspelled, renamed, or stale overrides.'
  - Use typing_extensions.override only when the supported Python baseline requires
    it. Continue to avoid inheritance unless it models a real relationship.
  - Make swappable record fields keyword-only
  - Use kw_only=True when two or more record fields have similar types or easily confused
    roles.
  - 'Provides: Constructor calls expose each field''s role and prevent positional
    reversal.'
  - Do not make every record keyword-only. Use it when the call-site clarity or safety
    is material.
  examples:
  - constant.example-14-7-1
  - constant.example-14-7-2
  - constant.example-14-7-3
  - constant.example-14-7-4
  tables: []
- section: refinement-inferred-locals
  title: Keep meaningful typing without redundant annotations
  requirements:
  - Use unambiguous type inference for short-lived local values. Explicitly type public
    boundaries, stored state, callbacks, domain identifiers, and collections whose
    element type would otherwise be unknown.
  - A type annotation or frozen record is not proof of runtime validation or deep
    immutability. Preserve each required trust-boundary check, including validated
    tool outputs.
  examples: []
  tables: []
>>

example-index: YAML<<
- id: example-3-1-1
  section: '3.1'
  topic: Type everything meaningful
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-2-1
  section: '3.2'
  topic: Keep structures flat and data-oriented
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-3-4-1
  section: '3.4'
  topic: Use enums for finite semantic choices
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-4-1-1
  section: '4.1'
  topic: Validate once at the boundary
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-4-2-1
  section: '4.2'
  topic: Make invalid states difficult or impossible to construct
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-4-3-1
  section: '4.3'
  topic: Distinguish interchangeable primitives
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-4-4-1
  section: '4.4'
  topic: Preserve the meaning of absence
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-5-1-1
  section: '5.1'
  topic: Use the narrowest useful input protocol
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-5-2-1
  section: '5.2'
  topic: Make ambiguous parameters keyword-only
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-5-4-1
  section: '5.4'
  topic: Depend on behaviour at real boundaries
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-7-1
  section: '14.7'
  topic: Mark genuine overrides
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-7-2
  section: '14.7'
  topic: Mark genuine overrides
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-7-3
  section: '14.7'
  topic: Make swappable record fields keyword-only
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-7-4
  section: '14.7'
  topic: Make swappable record fields keyword-only
  language: python
  scope: illustrative excerpt; not an execution result
>>

example-3-1-1: TEXT<<
from collections.abc import Iterable


def total(values: Iterable[int]) -> int:
    return sum(values)
>>

example-3-2-1: TEXT<<
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchDocument:
    key: str
    text: str
>>

example-3-4-1: TEXT<<
from enum import StrEnum


class Fit(StrEnum):
    CONTAIN = "contain"
    COVER = "cover"
>>

example-4-1-1: TEXT<<
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
>>

example-4-2-1: TEXT<<
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
>>

example-4-3-1: TEXT<<
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)
>>

example-4-4-1: TEXT<<
def cached_name(cache: Mapping[str, str | None], key: str) -> str | None:
    if key not in cache:
        raise KeyError(key)

    return cache[key]
>>

example-5-1-1: TEXT<<
def count_errors(lines: Iterable[str]) -> int:
    return sum("ERROR" in line for line in lines)
>>

example-5-2-1: TEXT<<
def render(
    path: Path,
    *,
    fit: Fit,
    cache: bool = True,
) -> None:
    ...
>>

example-5-4-1: TEXT<<
from typing import Protocol


class UserStore(Protocol):
    def get(self, user_id: UserId) -> User:
        ...
>>

example-14-7-1: TEXT<<
# Before: a base-method rename can silently break the override.
class RecordingStorageClient(StorageClient):
    def upload_artifact(self, artifact_upload: ArtifactUpload) -> None:
        ...
>>

example-14-7-2: TEXT<<
# After: the type checker verifies the relationship.
from typing import override


class RecordingStorageClient(StorageClient):
    @override
    def upload_artifact(self, artifact_upload: ArtifactUpload) -> None:
        ...
>>

example-14-7-3: TEXT<<
# Before: two paths can be reversed silently.
artifact_upload = ArtifactUpload(local_file, remote_file)
>>

example-14-7-4: TEXT<<
# After: the call names both roles.
@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactUpload:
    local_file: Path
    remote_file: Path


artifact_upload = ArtifactUpload(
    local_file=local_file,
    remote_file=remote_file,
)
>>
</constants>