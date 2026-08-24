# Condition

One structural JSON comparison.

## Examples

```json
[
  {
    "left": {
      "source": "state",
      "state": "status"
    },
    "operator": "equals",
    "right": {
      "source": "literal",
      "value": "ready"
    }
  }
]
```

## Fields

### Left

`left`

The value on the left of the comparison.

```json
[
  {
    "source": "state",
    "state": "status"
  }
]
```

### Operator

`operator`

The structural JSON comparison operator.

```json
[
  "equals",
  "not_equals"
]
```

### Right

`right`

The value on the right of the comparison.

```json
[
  {
    "source": "literal",
    "value": "ready"
  }
]
```
