# LiteralValue

One authored JSON value.

## Examples

```json
[
  {
    "source": "literal",
    "value": "critical"
  }
]
```

## Fields

### Source

`source`

The process value source discriminator.

```json
[
  "literal"
]
```

### Value

`value`

The authored JSON value.

```json
[
  "critical",
  3,
  {
    "ready": true
  }
]
```
