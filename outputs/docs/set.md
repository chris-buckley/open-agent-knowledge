# Set

One state write.

## Examples

```json
[
  {
    "kind": "set",
    "state": "status",
    "value": {
      "source": "literal",
      "value": "complete"
    }
  }
]
```

## Fields

### Kind

`kind`

The process step discriminator.

```json
[
  "set"
]
```

### State

`state`

The state entry to write.

```json
[
  "status"
]
```

### Value

`value`

The process value written to the state entry.

```json
[
  {
    "source": "literal",
    "value": "complete"
  }
]
```
