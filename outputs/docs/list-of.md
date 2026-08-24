# ListOf

The bound value is items of one datatype joined by one separator.

## Examples

```json
[
  {
    "kind": "list_of",
    "item": "integer",
    "separator": ", "
  }
]
```

## Fields

### Kind

`kind`

The constraint discriminator.

```json
[
  "list_of"
]
```

### Item

`item`

The datatype of every item.

```json
[
  "integer"
]
```

### Separator

`separator`

The text between items.

```json
[
  ", "
]
```
