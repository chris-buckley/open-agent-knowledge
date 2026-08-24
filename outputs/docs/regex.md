# Regex

The bound value matches one anchored portable rust-regex pattern.

## Examples

```json
[
  {
    "kind": "regex",
    "pattern": "^[0-9]+$"
  }
]
```

## Fields

### Kind

`kind`

The constraint discriminator.

```json
[
  "regex"
]
```

### Pattern

`pattern`

The whole-value portable pattern.

```json
[
  "^[0-9]+$"
]
```
