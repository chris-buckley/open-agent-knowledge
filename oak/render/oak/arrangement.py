"""The OAK arrangement of a schema: the template verbatim, then WHERE:, then one generated line per Where."""

from oak.node.parts.schemas import AtLeast, AtMost, Lines, ListOf, MaxChars, NonEmpty, OneOf, Regex, Schema, Type, Where
from oak.vocabulary.text.placeholder import token


def _bound(value: int | float | str) -> str:
    return token(value) if isinstance(value, str) else str(value)


def _lines(c: Lines) -> str:
    if c.min is not None and c.max is not None:
        return "is one line" if c.min == c.max == 1 else f"has {c.min} to {c.max} lines"
    if c.max is not None:
        return "is one line" if c.max == 1 else f"has at most {c.max} lines"
    return f"has at least {c.min} lines"


def sentence(constraint: Type | OneOf | Regex | NonEmpty | MaxChars | Lines | ListOf | AtLeast | AtMost) -> str:
    """The text the renderer writes for one constraint."""
    match constraint:
        case Type():
            return f"is {constraint.of}"
        case OneOf():
            return "is one of " + ", ".join(f"`{v}`" for v in constraint.values)
        case Regex():
            return f"matches `{constraint.pattern}`"
        case NonEmpty():
            return "is non-empty"
        case MaxChars():
            return f"is at most {constraint.n} characters"
        case Lines():
            return _lines(constraint)
        case ListOf():
            return f"is a list of {constraint.item} joined by `{constraint.separator}`"
        case AtLeast():
            return f"is at least {_bound(constraint.value)}"
        case AtMost():
            return f"is at most {_bound(constraint.value)}"


def where_line(where: Where) -> str:
    """One WHERE line: the delimited placeholder, constraints in authored order, examples, then the description, joined by `; `."""
    parts = [sentence(c) for c in where.constraints]
    parts += [f"example: `{e}`" for e in where.examples]
    if where.description is not None:
        parts.append(where.description)
    return f"- {token(where.placeholder)} " + "; ".join(parts) + "."


def schema_text(schema: Schema) -> str:
    """The template verbatim, one `WHERE:` line, then the Where lines in authored order."""
    template = schema.template if schema.template.endswith("\n") else schema.template + "\n"
    return template + "WHERE:\n" + "".join(where_line(w) + "\n" for w in schema.where)
