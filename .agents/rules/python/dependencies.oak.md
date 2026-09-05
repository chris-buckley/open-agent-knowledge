<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Python imports and justified runtime dependency selection."

rules: YAML<<
- section: '10.1'
  title: Prefer the standard library
  requirements:
  - Add a dependency only when it provides substantial capability, correctness, performance,
    interoperability, or maintenance value.
  - Before adding one, check whether the standard library already provides an adequate
    primitive.
  examples: []
  tables: []
- section: '10.2'
  title: Keep imports explicit
  requirements:
  - Avoid wildcard imports.
  - Group standard library, third-party, and local imports.
  - Import symbols when it improves clarity.
  - Import modules when qualification carries useful context.
  - Avoid import-time side effects.
  examples: []
  tables: []
- section: '10.3'
  title: Pin and justify runtime dependencies
  requirements:
  - Use the repository's established dependency mechanism. Do not introduce packages
    for trivial helpers.
  examples: []
  tables: []
>>
</constants>