# Interface

One crossing of information at the tree boundary.

## Examples

```json
[
  {
    "id": "request",
    "part": "interfaces",
    "direction": "in",
    "schema": "request-shape",
    "description": "The request supplied to the tree."
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
  "interfaces"
]
```

### Direction

`direction`

The direction across the tree boundary.

```json
[
  "in",
  "out",
  "inout"
]
```

### Schema

`schema_id`

The schema entry that defines the information shape.

```json
[
  "request-shape"
]
```

### Description

`description`

What the tree boundary crossing means.

```json
[
  "The request supplied to the tree."
]
```
