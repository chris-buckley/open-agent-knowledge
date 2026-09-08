"""One explicit example registration and its source-derived OAK deliveries.

Regenerate all example-owned files with `python -m examples.catalog`.
Python authoring uses this repository. Exported OAK graphs stay inside each
scenario. Only declared detached scripts are runnable without the repository.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from oak import Constant, Node, parse, render
from examples.fixed_knowledge import example as fixed_knowledge
from examples.shape_gallery import example as shape_gallery
from examples.shape_writer import example as shape_writer
from examples.compound_growth import example as compound_growth
from examples.interpreter_context import example as interpreter_context
from examples.local_contracts import example as local_contracts, worker as contract_worker
from examples.implementer import example as implementer
from examples.delegation import example as delegation, task_reviewer
from examples.parallel_exploration import example as parallel_exploration, explorer
from examples.successor import example as successor, amendment_reviewer, successor_verifier
from examples.skill_profiles import example as skill_profiles, classifier, memory, packages
from examples.schemas import (
    api_coverage_table, code_changes, code_map, docs_index, error,
    hierarchical_outline, ideation_list, link_manifest, process_execution_table,
    smeac_plan, shape_gallery as shape_library, verification,
)

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "catalog.oak.md"
SCHEMA_EXAMPLES = (
    api_coverage_table, code_changes, code_map, docs_index, error,
    hierarchical_outline, ideation_list, link_manifest, process_execution_table,
    smeac_plan, shape_library, verification,
)


@dataclass(frozen=True)
class Scenario:
    """Registration, not a configurable runner or a new authored format."""
    name: str
    entry: ModuleType
    lesson: str
    requirements: str
    stage: int | None = None
    supporting: tuple[ModuleType, ...] = ()
    dependencies: tuple[ModuleType, ...] = ()
    bindings: bool = False
    detached: str | None = None
    sample: Callable[[], Node] | None = None
    run: Callable[[], object] | None = None
    teaching: tuple[str, ...] = ()

    @property
    def modules(self) -> tuple[ModuleType, ...]:
        return (self.entry, *self.supporting)


SCENARIOS = (
    Scenario("fixed_knowledge", fixed_knowledge, "Two fixed facts need no workflow.",
             "No action host.", stage=1, detached="example.py"),
    Scenario("shape_gallery", shape_gallery, "Compare, explain, outline, and present code with populated fixed-cardinality shapes.",
             "No action host; regeneration imports the shared schema library.", stage=2),
    Scenario("shape_writer", shape_writer, "Receive and CALL typed phases; emit four ordered shapes without state.",
             "Fixture-only native host; regeneration imports shared shapes and bindings.",
             stage=3, dependencies=(shape_library,), bindings=True, detached="run.py", sample=shape_writer.sample, run=shape_writer.run),
    Scenario("compound_growth", compound_growth, "Carry committed state across two arrivals and discard staged writes on failure.",
             "Exact math.multiply fixture and deterministic reflection; no live model or automatic scheduler.",
             stage=4, detached="example.py", sample=compound_growth.sample),
    Scenario("interpreter_context", interpreter_context, "Compare direct and OAK-context interpretation of one title policy.",
             "Two deterministic adapters, not live model inference.", detached="example.py", run=interpreter_context.run),
    Scenario("local_contracts", local_contracts, "Explain public boundaries locally and adapt a separately typed private worker.",
             "The complete scenario supplies its graph and a deterministic trimming host; the entry alone is boundary-complete, not execution-complete. No external effects or live model.",
             supporting=(contract_worker,), detached="example.py", sample=local_contracts.sample, run=local_contracts.run),
    Scenario("implementer", implementer, "Bind acceptance to the exact verified revision before a host effect.",
             "Detached script validates structure only. Execution needs native actions and the declared snapshot, verification, and commit tools; repository checks use a simulated commit sink.",
             dependencies=(verification,), bindings=True, detached="example.py"),
    Scenario("delegation", delegation, "Delegate through an exact tool while retaining the worker document scope.",
             "Included deterministic agent.reviewer fixture; no live delegated model.",
             supporting=(task_reviewer,), bindings=True, detached="example.py"),
    Scenario("parallel_exploration", parallel_exploration, "Dispatch two independent exact tools, JOIN validated reports, and reconcile evidence.",
             "Repository-only deterministic fixture workers; native Codex TOML is a separate artifact, not a host adapter or live permission proof.",
             supporting=(explorer,), sample=parallel_exploration.sample, run=parallel_exploration.run),
    Scenario("successor", successor, "Separate amendment review, compilation, verification, and publication across arrivals.",
             "Included fixed amendment and verification adapters; proof covers the fixture, not arbitrary amendment quality.",
             supporting=(amendment_reviewer, successor_verifier), bindings=True, detached="example.py"),
    Scenario("skill_profiles", skill_profiles, "Select one stateless foundation or owned memory extension and reuse a separate classifier.",
             "Complete package maps are inert constants; repository-only file fixtures verify synthetic instances, not installed-host discovery or live effects.",
             supporting=(classifier, memory, packages), sample=skill_profiles.sample,
             teaching=("packages.oak.md", "sample.oak.md")),
)


def core() -> tuple[Scenario, ...]:
    return tuple(scenario for scenario in SCENARIOS if scenario.stage is not None)


def teaching_scenarios() -> tuple[Scenario, ...]:
    return tuple(scenario for scenario in SCENARIOS if scenario.stage is not None or scenario.teaching)


def generated(scenario: Scenario) -> dict[str, str]:
    """Build each local document from its sole source owner."""
    files = {Path(module.__file__).with_suffix(".oak.md").name: module.build()
             for module in scenario.modules}
    files.update({module.TARGET.name: module.build() for module in scenario.dependencies})
    if scenario.sample is not None:
        files["sample.oak.md"] = render(scenario.sample())
    if scenario.bindings:
        # A generated delivery copy, never a second editable helper definition.
        files["bindings.py"] = (ROOT / "bindings.py").read_text(encoding="utf-8")
    return files


def bundle(scenario: Scenario) -> dict[str, str]:
    """Include sources and applicable detached adapters as well as OAK data."""
    files = generated(scenario)
    files.update({Path(module.__file__).name: Path(module.__file__).read_text(encoding="utf-8")
                  for module in scenario.modules})
    if scenario.detached is not None and scenario.detached not in files:
        files[scenario.detached] = (ROOT / scenario.name / scenario.detached).read_text(encoding="utf-8")
    return files


def catalog_node(*, teaching: bool = False) -> Node:
    selected = teaching_scenarios() if teaching else SCENARIOS
    rows = []
    for order, scenario in enumerate(selected, 1):
        entry = scenario.teaching[0] if teaching and scenario.teaching else "example.oak.md"
        node = parse(generated(scenario)[entry])
        row = {
            "order": order, "entry": f"{scenario.name}/{entry}",
            "lesson": scenario.lesson,
            "omitted": ", ".join("authored instructions" if part == "instructions" else part
                                   for part in Node.model_fields if not getattr(node, part)),
            "requires": scenario.requirements,
        }
        if not teaching:
            row["regenerate"] = f"python -m examples.{scenario.name}.example (repository); python -m examples.catalog refreshes the complete bundle"
            row["detached"] = (f"python {scenario.detached}" if scenario.detached else
                               "OAK inspection only; the action demonstration requires repository sources"
                               if scenario.run is not None else
                               "OAK interpretation and resolution only; no action host is needed")
            row["documents"] = ", ".join(name for name in generated(scenario) if name.endswith(".oak.md"))
        rows.append(row)
    constants = [
        Constant(id="scenario-catalog", form="csv", value=rows),
        Constant(id="delivery-boundary", value=(
            "OAK documents and sample constants are inert teaching data. Read a complete scenario before using it. "
            "Python hosts are repository demonstration material, not part of the skill teaching bundle."
            if teaching else
            "Run detached commands inside a copied scenario with OAK and its declared dependencies installed. "
            "The runtime is not vendored. Shared Python authoring imports require the repository; "
            "the shape gallery has no detached Python regeneration claim. Read each host disclosure. "
            "Scenario bindings.py files are generated from examples/bindings.py."
        )),
    ]
    if not teaching:
        constants.append(Constant(id="schema-library", form="csv", value=[
            {"source": f"schemas/{Path(module.__file__).name}", "document": f"schemas/{module.TARGET.name}"}
            for module in SCHEMA_EXAMPLES
        ]))
    return Node(constants=constants)


def teaching_examples() -> dict[str, str]:
    files = {"assets/examples/catalog.oak.md": render(catalog_node(teaching=True))}
    for scenario in teaching_scenarios():
        files.update({f"assets/examples/{scenario.name}/{name}": text
                      for name, text in generated(scenario).items()
                      if name in scenario.teaching or not scenario.teaching and name.endswith(".oak.md")})
    return files


def artifacts() -> dict[Path, str]:
    files = {module.TARGET: module.build() for module in SCHEMA_EXAMPLES}
    for scenario in SCENARIOS:
        files.update({ROOT / scenario.name / name: text for name, text in generated(scenario).items()})
    files[TARGET] = render(catalog_node())
    return files


def write() -> Path:
    files = artifacts()
    for scenario in SCENARIOS:
        directory = ROOT / scenario.name
        for path in directory.rglob("*.oak.md"):
            if path not in files:
                path.unlink()
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
