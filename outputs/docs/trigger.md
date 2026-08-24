# Trigger

One arrival reason, optional state guard, and selected process.

## Examples

```json
[
  {
    "id": "write-oak-trigger",
    "part": "triggers",
    "given": {
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
    "when": "The interpreter arrives to write OAK.",
    "process": "write-oak"
  }
]
```

## Fields

### Id

`id`

The entry id, unique across the tree.

```json
[
  "example"
]
```

### Part

`part`

The entry part discriminator.

```json
[
  "triggers"
]
```

### Given

`given`

The optional state condition checked after when matches.

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

### When

`when`

Why the interpreter enters the knowledge.

```json
[
  "The interpreter arrives to write OAK."
]
```

### Process

`process`

The process entry selected by the trigger.

```json
[
  "write-oak"
]
```
