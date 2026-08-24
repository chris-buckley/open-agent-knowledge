# Where

One placeholder, its constraints, examples, and description.

## Examples

```json
[
  {
    "placeholder": "OUTLINE_TITLE",
    "constraints": [
      {
        "kind": "type",
        "of": "string"
      }
    ],
    "description": "title for the outline"
  }
]
```

## Fields

### Placeholder

`placeholder`

The bare placeholder name.

```json
[
  "OUTLINE_TITLE"
]
```

### Constraints

`constraints`

The constraints every bound value must satisfy.

```json
[
  [
    {
      "kind": "type",
      "of": "string"
    }
  ],
  [
    {
      "kind": "regex",
      "pattern": "^[0-9]+$"
    }
  ]
]
```

### Examples

`examples`

Values that satisfy every locally resolvable constraint.

```json
[
  [
    "1.1",
    "1.2"
  ]
]
```

### Description

`description`

What the placeholder holds, in one line.

```json
[
  "title for the outline"
]
```
