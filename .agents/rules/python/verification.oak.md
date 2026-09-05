<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<constants>
owned-concern: "Python behavioural verification, objective checks, independent expectations, and review."

rules: YAML<<
- section: '12.1'
  title: Reduce the test surface before adding tests
  requirements:
  - 'Design rule: Make correctness obvious by construction before adding tests.'
  - Before writing a test for a difficult private detail, redesign that detail. Prefer
    code that makes the rule impossible to break, delegates mechanics to a trusted
    standard-library primitive, or exposes one small pure decision.
  - Do not use this rule to skip verification. Remove avoidable implementation risk,
    then test the remaining public behaviour.
  - 'Ask:'
  - Can a type or constructor remove an invalid state?
  - Can a standard-library primitive replace custom control flow?
  - Can a pure function replace I/O-coupled logic?
  - Can injected inputs remove timing, randomness, or environment cases?
  - Can deterministic ordering remove flaky branches?
  - Can a data structure or named predicate replace repeated conditions?
  - Delegate mechanics to the standard library
  - 'Provides: Removes custom selection branches, so tests focus on ranking policy.'
  - Test the public score order, tie-break rule, and limit. Do not recreate tests
    for the standard-library heap algorithm.
  - Make invalid combinations unrepresentable
  - 'Provides: Removes contradictory states, so tests do not need to enumerate them.'
  - Test parsing and state transitions. No test is required for a state the model
    cannot construct.
  examples:
  - constant.example-12-1-1
  - constant.example-12-1-2
  - constant.example-12-1-3
  - constant.example-12-1-4
  tables: []
- section: '12.2'
  title: Test observable behaviour
  requirements:
  - Prefer tests against the public contract rather than private helpers or implementation
    details.
  examples:
  - constant.example-12-2-1
  tables: []
- section: '12.3'
  title: Cover the important behavioural classes
  requirements:
  - 'Test:'
  - Normal behaviour.
  - Boundary values.
  - Invalid input.
  - State after a failed operation.
  - Determinism under ties and repeated execution.
  - Public API compatibility during refactors.
  examples: []
  tables: []
- section: '12.4'
  title: Run checks before and after refactoring
  requirements:
  - 'Use project commands when available. Common checks include:'
  - Do not claim tests passed unless they were run. State clearly when verification
    was unavailable.
  examples:
  - constant.example-12-4-1
  tables: []
- section: '12.5'
  title: Report complexity after nontrivial refactors
  requirements:
  - 'Use this format:'
  examples:
  - constant.example-12-5-1
  tables: []
- section: '14.5'
  title: Make objective conventions executable
  requirements:
  - Put mechanically checkable rules in repository configuration. Run the same checks
    locally and in continuous integration.
  - 'Provides: The standard remains consistent across editors, developers, agents,
    and build pipelines.'
  - 'Apply these rules:'
  - Let prose explain why a rule exists.
  - Let tool configuration enforce what a tool can check objectively.
  - Use the repository's established formatter, linter, type checker, and test runner.
  - Run the same required checks locally and in CI.
  - Keep generated code subject to the same checks as human-written code.
  - Do not claim compliance with a check that was not run.
  examples:
  - constant.example-14-5-1
  - constant.example-14-5-2
  tables: []
- section: '14.9'
  title: Name tests as a behaviour index
  requirements:
  - Name tests so the collected test names describe the system's contract without
    opening each body.
  - 'Provides: The test suite becomes searchable documentation and failure reports
    become actionable.'
  - 'Use this pattern when each part adds information:'
  - 'Prefer names such as:'
  - Keep the shortest test name that uniquely states the behaviour. Reuse the same
    domain nouns as the production code, errors, logs, and documentation.
  examples:
  - constant.example-14-9-1
  - constant.example-14-9-2
  - constant.example-14-9-3
  - constant.example-14-9-4
  tables: []
- section: '17'
  title: Review checklist
  requirements:
  - 'Before considering Python work complete, check:'
  - Does the current repository convention take precedence where necessary?
  - Are public APIs and externally visible behaviour preserved?
  - Are public names unprefixed and non-public implementation details marked with
    a single leading underscore?
  - Does one exact domain noun represent each concept across code, models, schemas,
    logs, errors, tests, and documentation?
  - Do actions, values, collections, booleans, quantities, identifiers, and mappings
    expose their role, shape, or unit where needed?
  - Are generic placeholder names replaced when the domain noun is known?
  - Has each important name passed the four-question naming review?
  - Do small signatures stay horizontal instead of becoming mechanical parameter lists?
  - Do blank lines separate different concepts without splitting related values?
  - Are meaningful inputs, outputs, callbacks, and state fully typed?
  - Are raw inputs validated once at the boundary?
  - Are invalid states difficult to construct?
  - Are data structures carrying the architecture without needless classes?
  - Are stable values represented as named constants?
  - Are finite semantic choices represented clearly?
  - Are functions flat, single-purpose, and below the complexity threshold?
  - Are I/O and nondeterminism kept at explicit boundaries?
  - Are batch mutations prepared before state is changed?
  - Are ordering and tie-breaking deterministic?
  - Are exceptions narrow, specific, and chained where translated?
  - Are resource lifetimes explicit?
  - Are mutable defaults and ownership leaks absent?
  - Are domain-correct numeric and time primitives used?
  - Are dependencies necessary and standard-library alternatives considered?
  - Does each orchestration function stay at one abstraction level and read as a sequence
    of domain steps?
  - Does each domain rule have one authoritative home?
  - Do query names remain free of hidden mutation, and do command names expose their
    effects?
  - Does dependency flow move from the application boundary through workflows to lower-level
    adapters without upward imports?
  - Are objective rules encoded in repository tools and run consistently locally and
    in CI?
  - Does reusable public code preserve or deliberately migrate its complete compatibility
    contract?
  - Does every intended override use @override when inheritance is present?
  - Do easily confused record fields use keyword-only construction where it materially
    improves safety?
  - Are direct CLI results separated from operational logging when logging is warranted?
  - Did the design remove avoidable custom logic and invalid states before tests were
    added?
  - Do tests verify public behaviour, failure state, and boundary cases?
  - Do test names state the action, condition, and outcome using the production domain
    vocabulary?
  - Were formatter, type, lint, test, and complexity checks run when available?
  - Is the result compact without hiding meaning?
  - Do short comments explain only non-obvious aliases, invariants, order, safeguards,
    or trade-offs?
  - Does each comment use terse active STE and stay inline when one short line remains
    neat?
  - Do full-line comments explain a multiline construct or block rather than one short
    line?
  - When guidance is nontrivial, does a focused before-and-after example show the
    behaviour gained?
  examples: []
  tables: []
- section: refinement-independent-expectations
  title: Keep expected results independent
  requirements:
  - Give repeated fixture setup decisions one owner, but keep expected results independent
    of the implementation under test.
  - Do not generate the oracle by calling the same executor, renderer, or algorithm
    being checked.
  examples:
  - constant.example-independent-expectations-before
  - constant.example-independent-expectations-after
  tables: []
>>

example-index: YAML<<
- id: example-12-1-1
  section: '12.1'
  topic: Delegate mechanics to the standard library
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-12-1-2
  section: '12.1'
  topic: Delegate mechanics to the standard library
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-12-1-3
  section: '12.1'
  topic: Make invalid combinations unrepresentable
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-12-1-4
  section: '12.1'
  topic: Make invalid combinations unrepresentable
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-12-2-1
  section: '12.2'
  topic: Test observable behaviour
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-12-4-1
  section: '12.4'
  topic: Run checks before and after refactoring
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-12-5-1
  section: '12.5'
  topic: Report complexity after nontrivial refactors
  language: markdown
  scope: illustrative excerpt; not an execution result
- id: example-14-5-1
  section: '14.5'
  topic: Make objective conventions executable
  language: toml
  scope: illustrative excerpt; not an execution result
- id: example-14-5-2
  section: '14.5'
  topic: Make objective conventions executable
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-14-9-1
  section: '14.9'
  topic: Name tests as a behaviour index
  language: text
  scope: illustrative excerpt; not an execution result
- id: example-14-9-2
  section: '14.9'
  topic: Name tests as a behaviour index
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-9-3
  section: '14.9'
  topic: Name tests as a behaviour index
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-9-4
  section: '14.9'
  topic: Name tests as a behaviour index
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-independent-expectations-before
  section: refinement-independent-expectations
  topic: Reuse the intended count without deriving expected outputs from the loop.
  language: python
  scope: illustrative excerpt; requires the shown domain context
- id: example-independent-expectations-after
  section: refinement-independent-expectations
  topic: Reuse the intended count without deriving expected outputs from the loop.
  language: python
  scope: illustrative excerpt; requires the shown domain context
>>

example-12-1-1: TEXT<<
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
>>

example-12-1-2: TEXT<<
# After: the standard library handles top-result selection.
def _top_hits(
    hits: Iterable[SearchHit[_T]],
    limit: int,
) -> tuple[SearchHit[_T], ...]:
    return tuple(nsmallest(limit, hits, key=_rank_key))
>>

example-12-1-3: TEXT<<
# Before: callers can construct conflicting fields.
@dataclass(slots=True)
class Job:
    identifier: int
    finished: bool
    finished_at: datetime | None
>>

example-12-1-4: TEXT<<
# After: each state contains only valid fields.
@dataclass(frozen=True, slots=True)
class PendingJob:
    identifier: int


@dataclass(frozen=True, slots=True)
class FinishedJob:
    identifier: int
    finished_at: datetime


type Job = PendingJob | FinishedJob
>>

example-12-2-1: TEXT<<
def test_equal_scores_are_ordered_by_key() -> None:
    search = SemanticSearch(embed_equal)
    search.add_many(
        (
            SearchDocument("b", "second", None),
            SearchDocument("a", "first", None),
        )
    )

    assert tuple(hit.key for hit in search.search("query")) == ("a", "b")
>>

example-12-4-1: TEXT<<
python -m unittest
python -m pytest
python -m compileall .
ruff check .
ruff format --check .
mypy .
pyright
radon cc -s -a <path>
>>

example-12-5-1: TEXT<<
## Complexity report
| Function | Before | After |
|----------|-------:|------:|
| parse_order | 14 | 4 |

Extracted: validate_header, resolve_discount
Behavior verified: all tests passed
>>

example-14-5-1: TEXT<<
[tool.ruff]
line-length = 120
>>

example-14-5-2: TEXT<<
ruff check .
ruff format --check .
pyright
python -m unittest
radon cc -s -a .
>>

example-14-9-1: TEXT<<
test_<action>_<condition>_<outcome>
>>

example-14-9-2: TEXT<<
# Before: the name reveals little behaviour.
def test_retry() -> None:
    ...
>>

example-14-9-3: TEXT<<
# After: the name states the condition and outcome.
def test_publish_retries_after_transient_failure() -> None:
    ...
>>

example-14-9-4: TEXT<<
def test_dry_run_skips_remote_publish() -> None:
    ...


def test_checksum_mismatch_fails_before_publish() -> None:
    ...


def test_equal_scores_use_key_as_tiebreaker() -> None:
    ...
>>

example-independent-expectations-before: TEXT<<
for cycle in range(2):
    run_cycle(cycle)

if len(emissions) != 2:
    raise RuntimeError("wrong emission count")
>>

example-independent-expectations-after: TEXT<<
_ARRIVAL_COUNT: Final = 2

for cycle in range(_ARRIVAL_COUNT):
    run_cycle(cycle)

if len(emissions) != _ARRIVAL_COUNT:
    raise RuntimeError("wrong emission count")
>>
</constants>

<schemas>
<schema id="complexity-comparison" name="Complexity Comparison" purpose="Report one measured function comparison with its method and observed verification.">
| Function | Before | After |
| --- | ---: | ---: |
| <FUNCTION> | <BEFORE> | <AFTER> |

Method: <METHOD>
Extracted: <EXTRACTED>
Behaviour verified: <VERIFICATION>

WHERE:
- <FUNCTION> is string.
- <BEFORE> is integer.
- <AFTER> is integer.
- <METHOD> is string.
- <EXTRACTED> is string.
- <VERIFICATION> is string.
</schema>
</schemas>