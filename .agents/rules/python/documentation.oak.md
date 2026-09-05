<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<constants>
owned-concern: "Python terse comments, contractual docstrings, rationale, and change explanations."

rules: YAML<<
- section: '11.1'
  title: Use rare terse STE comments
  requirements:
  - 'Let names, types, helpers, and layout explain normal code. Add a comment only
    when it removes ambiguity about:'
  - a non-obvious invariant;
  - a required operation order;
  - a compatibility constraint;
  - a compact alias whose purpose is not obvious from its name;
  - a surprising algorithmic or performance reason;
  - a deliberate trade-off.
  - Prefer a same-line comment when it explains one short declaration or statement
    and the complete line stays within 120 characters. Separate code and comment with
    two spaces. Do not align comments into columns.
  - 'Keep the comment terse. Aim for two to seven words when that is enough. Write
    one short sentence in active voice and clear Simplified Technical English (STE):'
  - name the actor or operation;
  - state one idea;
  - use present tense or the imperative form;
  - use short, common words;
  - avoid vague pronouns and passive constructions;
  - explain the reason instead of narrating the next line.
  - Use a full-line comment only when the code spans multiple lines, the rationale
    applies to a block, or an inline comment would exceed the width or look cramped.
  - 'Provides: Keeps a short comment attached to the exact declaration or statement
    it explains without adding vertical noise.'
  - Do not narrate the next line, repeat a function name, use decorative headings,
    align trailing comments into columns, or add comments to meet a quota.
  examples:
  - constant.example-11-1-1
  - constant.example-11-1-2
  - constant.example-11-1-3
  - constant.example-11-1-4
  tables: []
- section: '11.2'
  title: Keep docstrings concise and contractual
  requirements:
  - Document public behaviour, important invariants, raised domain exceptions, units,
    and side effects. Avoid narrating implementation line by line.
  - Use active voice where practical. State what the caller can rely on.
  examples: []
  tables: []
- section: '11.3'
  title: Preserve rationale near unusual choices
  requirements:
  - Place the shortest useful rationale on the same line when it stays neat. Place
    a full-line rationale above the smallest relevant block when it explains more
    than one line. Explain why, not what.
  examples: []
  tables: []
- section: '11.4'
  title: Teach changes with focused before-and-after examples
  requirements:
  - When explaining a best practice, reviewing code, or proposing a nontrivial refactor,
    prefer a small before → after pair that isolates the change and states the coding
    behaviour it provides.
  - 'Use this shape:'
  - 'The examples should:'
  - preserve the relevant behaviour unless a behaviour change is intentional and stated;
  - demonstrate one primary idea at a time;
  - use realistic code rather than a contrived bad example;
  - be complete enough to understand without unrelated scaffolding;
  - show the resulting behaviour, not merely a cosmetic syntax difference;
  - avoid repeating an entire file when a focused excerpt communicates the change.
  - For a direct implementation request, provide the finished implementation first.
    Use before-and-after guidance when it materially helps the user or another agent
    understand a design decision; do not force it into trivial answers.
  examples:
  - constant.example-11-4-1
  tables: []
>>

example-index: YAML<<
- id: example-11-1-1
  section: '11.1'
  topic: Use rare terse STE comments
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-11-1-2
  section: '11.1'
  topic: Use rare terse STE comments
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-11-1-3
  section: '11.1'
  topic: Use rare terse STE comments
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-11-1-4
  section: '11.1'
  topic: Use rare terse STE comments
  language: python
  scope: illustrative excerpt; not an execution result
- id: example-11-4-1
  section: '11.4'
  topic: Teach changes with focused before-and-after examples
  language: markdown
  scope: illustrative excerpt; not an execution result
>>

example-11-1-1: TEXT<<
SearchHits: TypeAlias = tuple[SearchHit[_T], ...]  # Keep results ordered and immutable.
>>

example-11-1-2: TEXT<<
_require_unique_keys(batch)  # Reject duplicates before embedding.
return tuple(nsmallest(limit, hits, key=_rank_key))  # Avoid custom top-k logic.
>>

example-11-1-3: TEXT<<
# Preserve the old file until the replacement is complete.
temporary.replace(destination)
>>

example-11-1-4: TEXT<<
# Before: a short comment consumes a separate visual block.
# Keep results ordered and immutable.
SearchHits: TypeAlias = tuple[SearchHit[_T], ...]


# After: the terse rationale stays with the declaration.
SearchHits: TypeAlias = tuple[SearchHit[_T], ...]  # Keep results ordered and immutable.
>>

example-11-4-1: TEXT<<
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
>>
</constants>

<schemas>
<schema id="change-comparison" name="Change Comparison" purpose="Explain one observable coding improvement with a focused before-and-after pair.">
## <POINT>

Provides: <PROVIDES>

```python
# Before
<BEFORE>
```

```python
# After
<AFTER>
```

WHERE:
- <POINT> is string; is non-empty.
- <PROVIDES> is string; is non-empty.
- <BEFORE> is string; is non-empty.
- <AFTER> is string; is non-empty.
</schema>
</schemas>