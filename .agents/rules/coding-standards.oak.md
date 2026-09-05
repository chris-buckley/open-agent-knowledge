<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "General Python defaults, precedence, topic routing, and the standard application process."

status: "Canonical default"

applies-to: "All Python design, implementation, refactoring, review, examples, and generated repositories."

default: "Follow this standard unless the current request or repository conventions explicitly override it."

maintenance: "Edit these OAK documents directly. The original Markdown document and migration workbench are not source owners."

teaching-scope: "Examples are inert literal teaching excerpts, not evidence that their code ran. Respect the supported Python baseline and supply omitted imports and domain definitions before execution."

topic-router: CSV<<
path,concern
python/naming.oak.md,"Python semantic vocabulary, stable values, public names, and non-public naming."
python/layout.oak.md,"Python expression layout, horizontal signatures, conceptual grouping, and literal whitespace."
python/types.oak.md,"Python meaningful types, domain records, validation boundaries, and public input contracts."
python/design.oak.md,"Python helpers, control flow, abstraction levels, dependency direction, and compatibility."
python/effects.oak.md,"Python state, deterministic effects, errors, resources, numeric primitives, and logging."
python/dependencies.oak.md,Python imports and justified runtime dependency selection.
python/documentation.oak.md,"Python terse comments, contractual docstrings, rationale, and change explanations."
python/verification.oak.md,"Python behavioural verification, objective checks, independent expectations, and review."
>>

source-sections: ["1", "2", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "4.1", "4.2", "4.3", "4.4", "4.5", "5.1", "5.2", "5.3", "5.4", "5.5", "6.1", "6.2", "6.3", "6.4", "7.1", "7.2", "7.3", "7.4", "8.1", "8.2", "8.3", "9.1", "9.2", "9.3", "9.4", "10.1", "10.2", "10.3", "11.1", "11.2", "11.3", "11.4", "12.1", "12.2", "12.3", "12.4", "12.5", "13.1", "13.2", "14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7", "14.8", "14.9", "15", "16", "17", "18"]

rules: YAML<<
- section: '1'
  title: Governing principles
  requirements:
  - 'Write Python that is:'
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
  - Prefer code whose control flow follows the proof of the algorithm. Compress repeated
    ceremony, not meaning.
  examples: []
  tables: []
- section: '2'
  title: Precedence
  requirements:
  - 'Apply rules in this order:'
  - The user's current explicit instruction.
  - Existing repository conventions and public APIs.
  - Project formatter, linter, type-checker, and test configuration.
  - This document.
  - General Python convention.
  - Do not rewrite established project style merely to impose personal preference.
    Preserve public APIs unless explicitly asked to change them.
  examples: []
  tables: []
- section: '15'
  title: Patterns to avoid
  requirements:
  - 'Avoid by default:'
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
  examples: []
  tables: []
- section: '16'
  title: Preferred implementation flow
  requirements:
  - Keep external effects at visible boundaries. Make the centre of the program operate
    on explicit, trustworthy data.
  examples:
  - constant.example-16-1
  tables: []
- section: '18'
  title: Final judgement rule
  requirements:
  - Prefer the implementation a strong human maintainer can understand, verify, and
    safely modify years later. Elegant Python is explicit about meaning, restrained
    about abstraction, economical in ceremony, and honest about control flow.
  examples: []
  tables: []
>>

example-index: YAML<<
- id: example-16-1
  section: '16'
  topic: Preferred implementation flow
  language: text
  scope: illustrative excerpt; not an execution result
>>

example-16-1: TEXT<<
raw input
→ boundary parsing
→ validated domain values
→ pure computation
→ complete prepared change
→ atomic commit
→ deterministic output
>>
</constants>

<processes>
<process id="apply-standard" name="Apply standard">
ACT Apply <RULES> after the current request, supported repository contracts, and configured checks; resolve conflicts through the stated precedence. (
  RULES=$constant.rules,
)
ACT Apply the naming <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/naming.oak.md#constant.rules,
)
ACT Apply the layout <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/layout.oak.md#constant.rules,
)
ACT Apply the types <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/types.oak.md#constant.rules,
)
ACT Apply the design <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/design.oak.md#constant.rules,
)
ACT Apply the effects <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/effects.oak.md#constant.rules,
)
ACT Apply the dependencies <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/dependencies.oak.md#constant.rules,
)
ACT Apply the documentation <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/documentation.oak.md#constant.rules,
)
ACT Apply the verification <RULES> to the current Python task; read the same document for each referenced teaching example. (
  RULES=$python/verification.oak.md#constant.rules,
)
</process>
</processes>