"""Run the single supplied shape-writing fixture with an installed OAK runtime.

Run `python run.py` inside a copied scenario. No repository, schema-library
Python import, network, or live model is used. The host rejects other requests.
"""
from collections.abc import Mapping
from pathlib import Path
import re
from oak import Act, Arrival, Interface, Schema, execute, parse, resolve


def fixture_host(action: Act, values: Mapping[str, object], fixture: Mapping[str, object]) -> dict:
    for step in fixture["steps"]:
        if action.output == step["schema"]:
            if dict(values) != step["input"]:
                raise ValueError("this demonstration host only implements the declared sample")
            return dict(step["output"])
    raise ValueError("unexpected demonstration action")


def run(directory: Path | None = None) -> tuple[str, ...]:
    directory = (directory or Path(__file__).parent).resolve()
    entry = directory / "example.oak.md"
    fixture = {c.id: c.value for c in parse((directory / "sample.oak.md").read_text(encoding="utf-8")).constants}
    def load(name: str) -> str | None:
        path = Path(name).resolve()
        if not path.is_relative_to(directory):
            raise ValueError("reference escapes the scenario")
        return path.read_text(encoding="utf-8") if path.is_file() else None
    node = parse(entry.read_text(encoding="utf-8"))
    graph = resolve(node, source=entry.as_posix(), root=directory.as_posix(), load=load)
    result = execute(node, Arrival(interface="interface.request", values=fixture["request"]), {},
                     source=entry.as_posix(), root=directory.as_posix(), load=load,
                     act=lambda action, values: fixture_host(action, values, fixture))
    if [item.interface for item in result.emissions] != [step["interface"] for step in fixture["steps"]]:
        raise RuntimeError("shape writer emitted the wrong boundary instances")
    texts = []
    for emission, expected in zip(result.emissions, fixture["steps"], strict=True):
        _, interface = graph.entry(graph.root, emission.interface, Interface)
        document, schema = graph.entry(graph.root, interface.schema_id, Schema)
        schema.bind(emission.values)
        if dict(emission.values) != expected["output"]:
            raise RuntimeError("the fixture output changed")
        # This is one substitution pass for these validated fixed text fixtures,
        # not a general Markdown renderer or repetition facility.
        text = re.sub(r"<([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)>",
                      lambda match: emission.values[match[1]], schema.template)
        expected_text = next(c.value for c in graph.documents[document].constants
                             if c.id == schema.id + "-instance")
        if text != expected_text:
            raise RuntimeError("the populated layout changed")
        texts.append(text)
    return tuple(texts)


if __name__ == "__main__":
    print("\n\n".join(run()))
