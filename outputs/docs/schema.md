# Schema

One reusable information shape: a template and one Where per placeholder.

## Examples

```json
[
  {
    "id": "outline",
    "part": "schemas",
    "name": "Hierarchical Outline",
    "purpose": "Generate a numbered outline.",
    "template": "## <OUTLINE_TITLE>\n",
    "where": [
      {
        "placeholder": "OUTLINE_TITLE",
        "constraints": [
          {
            "kind": "type",
            "of": "string"
          }
        ]
      }
    ]
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
  "schemas"
]
```

### Name

`name`

The display name.

```json
[
  "Hierarchical Outline"
]
```

### Purpose

`purpose`

What the information shape is for.

```json
[
  "Generate a semantic multilevel numbered outline."
]
```

### Template

`template`

The literal shape with variable parts written as <PLACEHOLDER>.

```json
[
  "## <OUTLINE_TITLE>\n\n<LEVEL_1_NUMBER> <STATEMENT>\n...\n"
]
```

### Where

`where`

One Where per distinct template placeholder, in authored order.

```json
[
  [
    {
      "placeholder": "OUTLINE_TITLE",
      "constraints": [
        {
          "kind": "type",
          "of": "string"
        }
      ],
      "examples": [],
      "description": null
    }
  ]
]
```
