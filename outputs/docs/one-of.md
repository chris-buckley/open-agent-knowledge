# OneOf

The bound value is one of the listed values.

## Examples

```json
[
  {
    "kind": "one_of",
    "values": [
      "draft",
      "final"
    ]
  }
]
```

## Fields

### Kind

`kind`

The constraint discriminator.

```json
[
  "one_of"
]
```

### Values

`values`

The allowed values.

```json
[
  [
    "draft",
    "final"
  ]
]
```
