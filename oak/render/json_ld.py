"""The JSON-LD render: ids become @id, kinds become @type, ordered lists become @list."""

from oak.node.parts.schemas import AtLeast, AtMost, Schema, Where

OAK = "https://open-agent-knowledge.org/vocab#"

CONTEXT = {
    "oak": {"@id": OAK, "@prefix": True},
    "xsd": {"@id": "http://www.w3.org/2001/XMLSchema#", "@prefix": True},
    "name": "oak:name",
    "purpose": "oak:purpose",
    "template": {"@id": "oak:template", "@type": "xsd:string"},
    "where": {"@id": "oak:where", "@container": "@list"},
    "placeholder": "oak:placeholder",
    "constraints": {"@id": "oak:constraint", "@container": "@list"},
    "examples": {"@id": "oak:example", "@container": "@list"},
    "description": "oak:description",
    "of": "oak:of",
    "values": "oak:values",
    "pattern": "oak:pattern",
    "n": "oak:n",
    "item": "oak:item",
    "separator": "oak:separator",
    "min": "oak:min",
    "max": "oak:max",
    "value": "oak:value",
}

TYPES = {
    "type": "oak:Type",
    "one_of": "oak:OneOf",
    "regex": "oak:Regex",
    "non_empty": "oak:NonEmpty",
    "max_chars": "oak:MaxChars",
    "lines": "oak:Lines",
    "list_of": "oak:ListOf",
    "at_least": "oak:AtLeast",
    "at_most": "oak:AtMost",
}


def where_id(schema: Schema, placeholder: str) -> str:
    """The Where id derived from its schema id and placeholder."""
    return f"{schema.id}#{placeholder}"


def _constraint(schema: Schema, constraint) -> dict:
    data = constraint.model_dump(exclude={"kind"}, exclude_unset=True)
    if isinstance(constraint, (AtLeast, AtMost)) and isinstance(constraint.value, str):
        data["value"] = {"@id": where_id(schema, constraint.value)}
    return {"@type": TYPES[constraint.kind], **data}


def _where(schema: Schema, where: Where) -> dict:
    node = {
        "@id": where_id(schema, where.placeholder),
        "@type": "oak:Where",
        "placeholder": where.placeholder,
        "constraints": [_constraint(schema, c) for c in where.constraints],
    }
    if where.examples:
        node["examples"] = list(where.examples)
    if where.description is not None:
        node["description"] = where.description
    return node


def schema_json_ld(schema: Schema) -> dict:
    """One schema as a compact JSON-LD node object."""
    node: dict = {"@context": CONTEXT, "@id": schema.id, "@type": "oak:Schema"}
    node.update(schema.model_dump(include={"name", "purpose", "template"}, exclude_unset=True))
    node["where"] = [_where(schema, w) for w in schema.where]
    return node
