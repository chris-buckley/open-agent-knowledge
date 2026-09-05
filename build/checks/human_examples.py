"""Registered example snapshots, closed bundles, and detached fixture checks."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from oak import Constant, Node, Schema, Type, parse, render, resolve, where
from examples import catalog
from build.checks.fixtures import ROOT


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_registry(scenarios: Sequence[catalog.Scenario]) -> None:
    names = [scenario.name for scenario in scenarios]
    require(len(set(names)) == len(names), "duplicate scenario registration")
    require(all(re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", name) for name in names),
            "invalid scenario name")
    stages = [scenario.stage for scenario in scenarios if scenario.stage is not None]
    require(stages == [1, 2, 3, 4], "missing or unordered teaching stage")
    modules = [module for scenario in scenarios for module in scenario.modules]
    require(len({module.__file__ for module in modules}) == len(modules), "duplicate source registration")
    for scenario in scenarios:
        directory = catalog.ROOT / scenario.name
        require(all(Path(module.__file__).parent == directory for module in scenario.modules),
                "scenario source is outside its registered directory")
        require(Path(scenario.entry.__file__).name == "example.py", "scenario needs its canonical entry source")
        files = catalog.bundle(scenario)
        require("example.oak.md" in files, "scenario has no entry document")
        require(all(Path(name).name == name for name in files), "bundle filename escapes its scenario")
        if scenario.detached is not None:
            require(scenario.detached in files, "detached command is missing")


def validate_snapshots(directory: Path, expected: Mapping[str, str]) -> None:
    actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*.oak.md")}
    require(actual == {name for name in expected if name.endswith(".oak.md")},
            "missing or unowned example snapshot")
    for name, text in expected.items():
        path = directory / name
        require(path.is_file() and path.read_text(encoding="utf-8") == text,
                f"missing or stale example snapshot: {path}")


def validate_closed_bundle(directory: Path) -> None:
    directory = directory.resolve()
    def load(name: str) -> str | None:
        target = Path(name).resolve()
        if not target.is_relative_to(directory):
            raise ValueError("document reference escapes the scenario")
        return target.read_text(encoding="utf-8") if target.is_file() else None
    for path in directory.rglob("*.oak.md"):
        node = parse(path.read_text(encoding="utf-8"))
        for grouping in ("xml", "markdown"):
            text = render(node, grouping=grouping)
            require(render(parse(text), grouping=grouping) == text, "scenario changed during round-trip")
        graph = resolve(node, source=path.as_posix(), root=directory.as_posix(), load=load)
        require(all(Path(name).is_relative_to(directory) for name in graph.documents),
                "scenario resolution escaped the copied bundle")


def _write_bundle(directory: Path, files: Mapping[str, str]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (directory / name).write_text(text, encoding="utf-8")


def _run_detached(directory: Path, script: str, runtime: Path) -> None:
    # -I ignores PYTHONPATH and the original working directory. The only added
    # import paths are the copied scenario and a copied, unchanged OAK runtime.
    driver = """
import importlib.abc, pathlib, runpy, sys
runtime, directory, script, repository = map(pathlib.Path, sys.argv[1:])
sys.path[:0] = [str(directory), str(runtime)]
class RejectRepositoryImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'examples' or fullname.startswith('examples.') or fullname == 'build' or fullname.startswith('build.'):
            raise ImportError('detached demo reached back into the repository: ' + fullname)
sys.meta_path.insert(0, RejectRepositoryImports())
def no_network(event, args):
    if event in {'socket.connect', 'socket.getaddrinfo', 'socket.bind'}:
        raise RuntimeError('detached demonstration attempted network access')
sys.addaudithook(no_network)
runpy.run_path(str(directory / script), run_name='__main__')
for module in tuple(sys.modules.values()):
    origin = getattr(module, '__file__', None)
    if origin and pathlib.Path(origin).resolve().is_relative_to(repository.resolve()):
        raise RuntimeError('detached demo imported repository code: ' + str(origin))
"""
    result = subprocess.run([sys.executable, "-I", "-c", driver, str(runtime), str(directory), script, str(ROOT)],
                            cwd=directory, capture_output=True, text=True, timeout=60, check=False)
    require(result.returncode == 0,
            f"detached {directory.name}/{script} failed:\n{result.stdout}\n{result.stderr}")


def _rejects(operation, reason: str) -> None:
    try:
        operation()
    except (ValueError, RuntimeError):
        return
    raise RuntimeError(f"invalid scenario was accepted: {reason}")


def _rejections() -> None:
    _rejects(lambda: validate_registry((*catalog.SCENARIOS, catalog.SCENARIOS[0])), "duplicate registration")
    _rejects(lambda: validate_registry(tuple(s for s in catalog.SCENARIOS if s.stage != 4)), "missing teaching stage")
    writer = next(scenario for scenario in catalog.SCENARIOS if scenario.name == "shape_writer")
    with TemporaryDirectory(prefix="oak-invalid-bundle-") as temporary:
        root = Path(temporary)
        directory = root / "writer"
        files = catalog.bundle(writer)
        _write_bundle(directory, files)
        dependency = directory / "shape_gallery.oak.md"
        original = dependency.read_text(encoding="utf-8")
        dependency.unlink()
        _rejects(lambda: validate_closed_bundle(directory), "missing local dependency")
        _rejects(lambda: validate_snapshots(directory, catalog.generated(writer)), "missing snapshot")
        dependency.write_text(original + "\n", encoding="utf-8")
        _rejects(lambda: validate_snapshots(directory, catalog.generated(writer)), "stale snapshot")
        dependency.write_text(original, encoding="utf-8")
        sample = directory / "sample.oak.md"
        sample.write_text(sample.read_text().replace("Blank title", "Changed fixture"), encoding="utf-8")
        _rejects(lambda: validate_snapshots(directory, catalog.generated(writer)), "source-to-delivery drift")
        _write_bundle(directory, files)
        outside = root / "outside.oak.md"
        outside.write_text(render(Node(schemas=[Schema(id="value", template="<VALUE>",
                                 where=[where("VALUE", Type(of="string"))])])), encoding="utf-8")
        escaped = Node(constants=[Constant(id="escaped", schema="../outside.oak.md#schema.value",
                                           placeholder="VALUE", value="unchanged literal")])
        (directory / "example.oak.md").write_text(render(escaped), encoding="utf-8")
        _rejects(lambda: validate_closed_bundle(directory), "escaping target with an existing outside document")
        link = directory / "linked.oak.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            pass  # Lexical escape coverage above remains mandatory on all platforms.
        else:
            escaped.constants[0].schema_id = "linked.oak.md#schema.value"
            (directory / "example.oak.md").write_text(render(escaped), encoding="utf-8")
            _rejects(lambda: validate_closed_bundle(directory), "symlink escape")


def validate_human_examples() -> None:
    """Keep every previous registration and verify the actual exported bundles."""
    validate_registry(catalog.SCENARIOS)
    directories = {path.name for path in catalog.ROOT.iterdir()
                   if path.is_dir() and path.name not in {"schemas", "__pycache__"}}
    require(directories == {scenario.name for scenario in catalog.SCENARIOS}, "unregistered scenario directory")
    schema_sources = {path for path in (catalog.ROOT / "schemas").glob("*.py") if path.name not in {"__init__.py", "repeat_marker.py"}}
    require(schema_sources == {Path(module.__file__) for module in catalog.SCHEMA_EXAMPLES},
            "unregistered or missing schema example")
    for module in catalog.SCHEMA_EXAMPLES:
        require(module.TARGET.is_file() and module.TARGET.read_text(encoding="utf-8") == module.build(),
                f"schema snapshot is missing or stale: {module.TARGET}")
    require(catalog.TARGET.read_text(encoding="utf-8") == render(catalog.catalog_node()), "stale example catalogue")
    with TemporaryDirectory(prefix="oak-detached-examples-") as temporary:
        root = Path(temporary)
        runtime = root / "runtime"
        shutil.copytree(ROOT / "oak", runtime / "oak", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for scenario in catalog.SCENARIOS:
            expected = catalog.generated(scenario)
            original = catalog.ROOT / scenario.name
            validate_snapshots(original, expected)
            files = catalog.bundle(scenario)
            actual_files = {p.relative_to(original).as_posix() for p in original.rglob("*")
                            if p.is_file() and "__pycache__" not in p.parts}
            require(actual_files == set(files), f"missing or unowned scenario files: {scenario.name}")
            directory = root / scenario.name
            # Copy committed candidate files, not independently rebuilt replacements.
            _write_bundle(directory, {name: (original / name).read_text(encoding="utf-8") for name in files})
            validate_closed_bundle(directory)
            if scenario.detached is not None:
                _run_detached(directory, scenario.detached, runtime)
                validate_snapshots(directory, expected)
            if scenario.run is not None:
                scenario.run()
    _rejections()


__all__ = ["validate_human_examples"]
