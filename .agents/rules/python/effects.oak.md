<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Python state, deterministic effects, errors, resources, numeric primitives, and logging."

rules: YAML<<
- section: '7.1'
  title: Keep pure computation separate from I/O
  requirements:
  - Read, parse, compute, and write as distinct stages.
  examples:
  - constant.example-7-1-1
  tables: []
- section: '7.2'
  title: Inject nondeterministic inputs
  requirements:
  - Pass clocks, random generators, identifiers, external clients, and environment-derived
    values into the function that needs them.
  examples:
  - constant.example-7-2-1
  tables: []
- section: '7.3'
  title: Prepare before committing
  requirements:
  - Validate and compute the complete update before mutating shared state.
  - Batch operations should be atomic where practical.
  examples:
  - constant.example-7-3-1
  tables: []
- section: '7.4'
  title: Define deterministic ordering
  requirements:
  - Use explicit tie-breakers for rankings, stable output ordering, generated files,
    logs, and tests.
  - Never rely on set order or incidental arrival order when output is externally
    visible.
  examples:
  - constant.example-7-4-1
  tables: []
- section: '8.1'
  title: Catch only expected exceptions
  requirements:
  - Catch exceptions in the narrowest scope that can handle them correctly. Translate
    them into domain errors with exception chaining.
  - Do not use broad except Exception unless at a true process boundary that logs
    and re-raises or deliberately terminates.
  examples:
  - constant.example-8-1-1
  tables: []
- section: '8.2'
  title: Use exceptions for caller errors and assertions for invariants
  requirements:
  - Use assert only for internal states believed impossible after validation, never
    for public input validation.
  examples:
  - constant.example-8-2-1
  tables: []
- section: '8.3'
  title: Write actionable error messages
  requirements:
  - State the violated rule and, when useful, the received value or expected range.
    Do not expose secrets, tokens, full credentials, or sensitive payloads.
  examples: []
  tables: []
- section: '9.1'
  title: Express resource lifetimes with context managers
  requirements:
  - Use context managers for files, locks, temporary resources, transactions, and
    connections.
  examples:
  - constant.example-9-1-1
  tables: []
- section: '9.2'
  title: Stream when materialization is unnecessary
  requirements:
  - Avoid reading whole files or datasets into memory when a single pass is sufficient.
  - Materialize deliberately when atomic validation, repeated traversal, stable snapshots,
    sorting, or length checks require it.
  examples: []
  tables: []
- section: '9.3'
  title: Choose domain-correct numeric and time primitives
  requirements:
  - Use Decimal for money and contractual decimal arithmetic.
  - Use Fraction for exact rational arithmetic.
  - Use monotonic() for elapsed time and timeouts.
  - Use UTC-aware datetime values for real-world instants.
  - Avoid binary floats when exact decimal equality is part of the contract.
  examples: []
  tables: []
- section: '9.4'
  title: Optimize after measuring
  requirements:
  - Prefer clear O(n) or O(n log k) algorithms and appropriate data structures before
    micro-optimizing syntax.
  - Measure hotspots with representative inputs. Preserve correctness and readability
    unless profiling demonstrates a material need.
  examples: []
  tables: []
- section: '14.8'
  title: Separate user output from operational logging
  requirements:
  - Use print for direct command-line results intended for the user. Use logging for
    diagnostics, retries, operational events, and exception traces.
  - 'Provides: CLI output stays stable and readable while operations remain observable.'
  - 'Apply these rules:'
  - Create module loggers with logging.getLogger(__name__).
  - Configure logging only at the application boundary.
  - Pass variable values as logging arguments instead of interpolating eagerly.
  - Use stable semantic event names that match the domain vocabulary.
  - Use logger.exception() only inside an exception handler when a stack trace helps.
  - Keep secrets, credentials, tokens, and sensitive payloads out of logs.
  - Keep simple scripts on print until operational logging provides real value.
  examples:
  - constant.example-14-8-1
  - constant.example-14-8-2
  tables: []
- section: refinement-operation-snapshot
  title: Capture shared inputs once per operation
  requirements:
  - Capture dependency documents, configuration, clocks, and other shared inputs once
    for phases that must operate on the same values.
  - Keep the snapshot local to the operation and pass it explicitly; do not introduce
    a global cache or change an API that promises live reads.
  examples:
  - constant.example-operation-snapshot-before
  - constant.example-operation-snapshot-after
  tables: []
- section: refinement-diagnostic-contracts
  title: Identify each failed contract
  requirements:
  - Separate independently meaningful checks when one combined error hides which promise
    failed.
  - Report bounded, safe expected and observed evidence where it helps diagnosis;
    retain the sensitive-data exclusions from the error and logging rules.
  examples:
  - constant.example-diagnostic-contracts-before
  - constant.example-diagnostic-contracts-after
  tables: []
>>

example-index: YAML<<
- id: example-7-1-1
  section: '7.1'
  topic: Keep pure computation separate from I/O
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-7-2-1
  section: '7.2'
  topic: Inject nondeterministic inputs
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-7-3-1
  section: '7.3'
  topic: Prepare before committing
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-7-4-1
  section: '7.4'
  topic: Define deterministic ordering
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-8-1-1
  section: '8.1'
  topic: Catch only expected exceptions
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-8-2-1
  section: '8.2'
  topic: Use exceptions for caller errors and assertions for invariants
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-9-1-1
  section: '9.1'
  topic: Express resource lifetimes with context managers
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-8-1
  section: '14.8'
  topic: Separate user output from operational logging
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-14-8-2
  section: '14.8'
  topic: Separate user output from operational logging
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-operation-snapshot-before
  section: refinement-operation-snapshot
  topic: Use one dependency snapshot for execution and resolution.
  language: python
  scope: illustrative excerpt; requires the shown domain context
- id: example-operation-snapshot-after
  section: refinement-operation-snapshot
  topic: Use one dependency snapshot for execution and resolution.
  language: python
  scope: illustrative excerpt; requires the shown domain context
- id: example-diagnostic-contracts-before
  section: refinement-diagnostic-contracts
  topic: Name the failed contract without disclosing fixture payloads.
  language: python
  scope: illustrative excerpt; requires the shown domain context
- id: example-diagnostic-contracts-after
  section: refinement-diagnostic-contracts
  topic: Name the failed contract without disclosing fixture payloads.
  language: python
  scope: illustrative excerpt; requires the shown domain context
>>

example-7-1-1: TEXT<<
def parse_dates(text: str) -> tuple[date, ...]:
    return tuple(date.fromisoformat(line) for line in text.splitlines())


def find_overdue(
    due_dates: Iterable[date],
    today: date,
) -> tuple[date, ...]:
    return tuple(due_date for due_date in due_dates if due_date < today)
>>

example-7-2-1: TEXT<<
def choose_worker(workers: Sequence[str], rng: Random) -> str:
    return rng.choice(workers)
>>

example-7-3-1: TEXT<<
def update_many(self, updates: Iterable[tuple[str, str]]) -> None:
    prepared = {key: normalize(value) for key, value in updates}
    validate_updates(prepared)
    self._values.update(prepared)
>>

example-7-4-1: TEXT<<
ranked = sorted(hits, key=lambda hit: (-hit.score, hit.key))
>>

example-8-1-1: TEXT<<
def read_price(path: Path) -> Decimal:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise PriceFileMissing(path) from error

    try:
        return Decimal(text)
    except InvalidOperation as error:
        raise PriceError(text) from error
>>

example-8-2-1: TEXT<<
def take(items: Sequence[T], limit: int) -> Sequence[T]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    return items[:limit]
>>

example-9-1-1: TEXT<<
with path.open(encoding="utf-8") as stream:
    process(stream)
>>

example-14-8-1: TEXT<<
# Before: results and diagnostics share one channel.
print(f"published {artifact_name}")
print(f"retrying after {error}")
print(f"Publish complete: {destination}")
>>

example-14-8-2: TEXT<<
# After: each channel has one purpose.
logger = logging.getLogger(__name__)

logger.info("artifact_published artifact=%s", artifact_name)
logger.warning("publish_retry_started attempt=%d", attempt)
print(f"Publish complete: {destination}")
>>

example-operation-snapshot-before: TEXT<<
execution = execute(node, arrival, state, load=documents().get)
graph = resolve(node, load=documents().get)
>>

example-operation-snapshot-after: TEXT<<
load_document = documents().get

execution = execute(node, arrival, state, load=load_document)
graph = resolve(node, load=load_document)
>>

example-diagnostic-contracts-before: TEXT<<
if observed_states != expected_states or observed_emissions != expected_emissions:
    raise RuntimeError("states or emissions differ")
>>

example-diagnostic-contracts-after: TEXT<<
if observed_states != expected_states:
    raise RuntimeError("state history differs from the expected states")

if observed_emissions != expected_emissions:
    raise RuntimeError("emissions differ from the expected emissions")
>>
</constants>