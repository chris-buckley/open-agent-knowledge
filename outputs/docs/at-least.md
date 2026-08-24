# AtLeast

The bound value is at least a number or another placeholder value.

## Examples

```json
[
  {
    "kind": "at_least",
    "value": 1
  }
]
```

## Fields

### Kind

`kind`

The constraint discriminator.

```json
[
  "at_least"
]
```

### Value

`value`

A number or a placeholder of the same schema.

```json
[
  1,
  "LINE_FROM"
]
```
