# ExecutionResult

The committed result of one arrival cycle.

## Examples

```json
[
  {
    "process": "pwd",
    "state": {
      "mode": "open"
    },
    "emissions": [
      {
        "interface": "stdout",
        "values": {
          "OUTPUT": "/oak"
        }
      }
    ]
  }
]
```

## Fields

### Process

`process`

The selected process, or null when none matched.

```json
[
  "pwd"
]
```

### State

`state`

The state after successful completion.

```json
[
  {
    "mode": "open"
  }
]
```

### Emissions

`emissions`

The emissions in execution order.

```json
[
  [
    {
      "interface": "stdout",
      "values": {
        "OUTPUT": "/oak"
      }
    }
  ]
]
```
