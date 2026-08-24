# ValueBinding

One placeholder bound to one process value.

## Examples

```json
[
  {
    "placeholder": "REQUEST",
    "value": {
      "source": "interface",
      "interface": "request",
      "placeholder": "REQUEST"
    }
  }
]
```

## Fields

### Placeholder

`placeholder`

The placeholder receiving the process value.

```json
[
  "REQUEST"
]
```

### Value

`value`

The process value bound to the placeholder.

```json
[
  {
    "source": "literal",
    "value": "ready"
  },
  {
    "source": "binding",
    "binding": "RESULT"
  }
]
```
