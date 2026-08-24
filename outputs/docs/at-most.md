# AtMost

The bound value is at most a number or another placeholder value.

## Examples

```json
[
  {
    "kind": "at_most",
    "value": 160
  }
]
```

## Fields

### Kind

`kind`

The constraint discriminator.

```json
[
  "at_most"
]
```

### Value

`value`

A number or a placeholder of the same schema.

```json
[
  160,
  "LINE_TO"
]
```
