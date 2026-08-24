# If

One condition with a required then branch and an optional otherwise branch.

## Examples

```json
[
  {
    "kind": "if",
    "condition": {
      "left": {
        "source": "state",
        "state": "status"
      },
      "operator": "equals",
      "right": {
        "source": "literal",
        "value": "ready"
      }
    },
    "then": [
      {
        "kind": "set",
        "state": "status",
        "value": {
          "source": "literal",
          "value": "complete"
        }
      }
    ],
    "otherwise": [
      {
        "kind": "fail",
        "message": "The state is not ready."
      }
    ]
  }
]
```

## Fields

### Kind

`kind`

The process step discriminator.

```json
[
  "if"
]
```

### Condition

`condition`

The comparison that selects the branch.

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

### Then

`then`

The steps run when the condition is true.

```json
[
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
]
```

### Otherwise

`otherwise`

The steps run when the condition is false.

```json
[
  [
    {
      "kind": "fail",
      "message": "The state is not ready."
    }
  ]
]
```
