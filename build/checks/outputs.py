"""Complete generated-product freshness, cold rebuild, and detached delivery checks."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from build.checks.fixtures import ROOT

_ROOT_ENTRIES = {"oak.ebnf", "definitions", "oak-authoring.oak.md", "oak-authoring.skill", "oak.agents"}
_GENERATE = """
import socket, sys
sys.path.insert(0, sys.argv[1])
def refuse_network(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('generation attempted network access')
sys.addaudithook(refuse_network)
# Keep socket a class: SSL must remain importable after the test guard is installed.
import ssl
try:
    socket.socket()
except RuntimeError:
    pass
else:
    raise RuntimeError('network test guard was not installed')
from build.ebnf import write as write_grammar
from build.definitions import write as write_definitions
from build.authoring import write as write_authoring
from build.agents import write as write_agents
write_grammar()
write_definitions()
write_authoring()
write_agents()
"""
_DETACHED = """
import importlib.abc, importlib.util, pathlib, socket, sys, tomllib, yaml
root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / 'runtime'))
class RejectBuildImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'build' or fullname.startswith('build.'):
            raise RuntimeError('detached delivery imported repository build code')
sys.meta_path.insert(0, RejectBuildImports())
def refuse_network(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('detached validation attempted network access')
sys.addaudithook(refuse_network)
# Keep socket a class: SSL must remain importable after the test guard is installed.
import ssl
try:
    socket.socket()
except RuntimeError:
    pass
else:
    raise RuntimeError('network test guard was not installed')
from oak import parse, resolve
skill = root / 'oak-authoring'
metadata = yaml.safe_load((skill / 'SKILL.md').read_text().split('---\\n', 2)[1])
assert metadata['name'] == skill.name == 'oak-authoring'
spec = importlib.util.spec_from_file_location('delivered_validator', skill / 'scripts' / 'validate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.activate(root / 'runtime')
assert module.validate([skill / 'SKILL.md'], skill) == 0
agent = root / 'standalone' / 'oak-authoring.oak.md'
assert len(resolve(parse(agent.read_text())).documents) == 1
assert {p.name for p in agent.parent.iterdir()} == {'oak-authoring.oak.md'}
native = root / 'native-only'
codex = tomllib.loads((native / 'oak-authoring.toml').read_text())
claude = (native / 'oak-authoring.md').read_text()[4:].split('---\\n\\n', 1)[1]
assert codex['developer_instructions'] == claude == agent.read_text()
assert len(resolve(parse(claude)).documents) == 1
assert {p.name for p in native.iterdir()} == {'oak-authoring.toml', 'oak-authoring.md'}
assert not (root / 'definitions').exists()
assert not any(name == 'build' or name.startswith('build.') for name in sys.modules)
"""


def _files(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


def _verify_outputs(root: Path, expected: Mapping[str, bytes]) -> None:
    if root.is_symlink() or any(path.is_symlink() for path in root.rglob("*")):
        raise RuntimeError("generated products contain a symbolic link")
    if not root.is_dir() or {path.name for path in root.iterdir()} != _ROOT_ENTRIES:
        raise RuntimeError("generated root entry set is stale")
    actual = _files(root)
    if actual.keys() != expected.keys():
        raise RuntimeError("generated product file set is stale")
    for name, content in expected.items():
        if actual[name] != content:
            raise RuntimeError(f"generated product bytes are stale: {name}")
    directories = {parent.as_posix() for name in expected for parent in Path(name).parents if parent != Path('.')}
    actual_directories = {path.relative_to(root).as_posix() for path in root.rglob('*')
                          if path.is_dir() and '__pycache__' not in path.parts}
    if actual_directories != directories:
        raise RuntimeError("generated product directory set is stale")


def _run_isolated(script: str, root: Path) -> None:
    result = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(root)], cwd=root,
                            capture_output=True, text=True, check=False, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"isolated product check failed:\n{result.stdout}\n{result.stderr}")


def _copy_sources(root: Path) -> None:
    for name in ("oak", "build", "examples"):
        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in ("pyproject.toml", "AGENTS.md"):
        shutil.copyfile(ROOT / name, root / name)


def _reject_stale(root: Path, expected: Mapping[str, bytes]) -> None:
    try:
        _verify_outputs(root, expected)
    except RuntimeError:
        return
    raise RuntimeError("corrupted generated products were accepted")


def _repair_products(root: Path, expected: Mapping[str, bytes]) -> None:
    generated = root / "generated"
    mutations = (
        ("oak-authoring.skill/scripts/validate.py", None),
        ("oak-authoring.skill/scripts/validate.py", b"raise RuntimeError('generated helper must not be build input')\n"),
        ("oak.ebnf", None),
        ("definitions/stale.oak.md", b"stale definition"),
        ("definitions/stale.md", b"stale markdown"),
        ("oak.agents/parallel_exploration/codex/.codex/agents/oak-explorer.toml", None),
        ("oak.agents/parallel_exploration/codex/.codex/agents/oak-explorer.toml", b"stale native artifact"),
        ("oak-authoring.skill/platforms/codex/templates/.codex/agents/oak-authoring.toml", None),
        ("oak-authoring.skill/platforms/claude/templates/.claude/agents/oak-authoring.md", b"stale authoring body"),
        ("oak-authoring.skill/assets/constants/artifact-kinds.oak.md", None),
        ("oak-authoring.skill/_template/stateful.oak.md", None),
        ("oak-authoring.skill/assets/examples/skill_profiles/packages.oak.md", b"stale profile mapping"),
    )
    for relative, content in mutations:
        path = generated / relative
        if content is None:
            path.unlink()
        else:
            path.write_bytes(content)
        _reject_stale(generated, expected)
        _run_isolated(_GENERATE, root)
        _verify_outputs(generated, expected)
    (generated / "unowned").mkdir()
    _reject_stale(generated, expected)
    (generated / "unowned").rmdir()


def _reject_link_writes(root: Path, expected: Mapping[str, bytes]) -> None:
    generated = root / "generated"
    sentinel = root / "sentinel.txt"
    sentinel.write_text("preserve")
    for name in ("oak.ebnf", "oak-authoring.skill/scripts/validate.py", "definitions/act.oak.md", "oak.agents/parallel_exploration/explorer.oak.md",
                 "oak-authoring.skill/platforms/codex/templates/.codex/agents/oak-authoring.toml",
                 "oak-authoring.skill/platforms/claude/templates/.claude/agents/oak-authoring.md",
                 "oak-authoring.skill/_template/stateful.oak.md"):
        link = generated / name
        original = link.read_bytes()
        link.unlink()
        link.symlink_to(sentinel)
        _reject_stale(generated, expected)
        try:
            _run_isolated(_GENERATE, root)
        except RuntimeError as error:
            if "symbolic link" not in str(error):
                raise
        else:
            raise RuntimeError("generation followed an escaping symbolic link")
        if sentinel.read_text() != "preserve":
            raise RuntimeError("generation overwrote an external file")
        link.unlink()
        link.write_bytes(original)
    directory = generated / "definitions" / "escape"
    directory.symlink_to(root, target_is_directory=True)
    try:
        _run_isolated(_GENERATE, root)
    except RuntimeError as error:
        if "symbolic link" not in str(error):
            raise
    else:
        raise RuntimeError("generation followed a directory symbolic link")
    directory.unlink()
    sentinel.unlink()


def _cold_regeneration(expected: Mapping[str, bytes]) -> None:
    with TemporaryDirectory(prefix="oak-generated-cold-") as temporary:
        root = Path(temporary)
        _copy_sources(root)
        sources = _files(root)
        if any((root / name).exists() for name in ("generated", "outputs", "skills")):
            raise RuntimeError("cold generation fixture contains previous products")
        _run_isolated(_GENERATE, root)
        _verify_outputs(root / "generated", expected)
        _run_isolated(_GENERATE, root)
        _verify_outputs(root / "generated", expected)
        _repair_products(root, expected)
        _reject_link_writes(root, expected)
        remaining_sources = {name: content for name, content in _files(root).items() if not name.startswith('generated/')}
        if remaining_sources != sources:
            raise RuntimeError("generation modified maintained source inputs")


def _detached_delivery() -> None:
    from build.authoring import PACKAGE, TARGET
    with TemporaryDirectory(prefix="oak-generated-detached-") as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / "oak", root / "runtime" / "oak", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(PACKAGE, root / "oak-authoring", ignore=shutil.ignore_patterns("__pycache__"))
        (root / "standalone").mkdir()
        shutil.copyfile(TARGET, root / "standalone" / TARGET.name)
        (root / "native-only").mkdir()
        for relative in ("platforms/codex/templates/.codex/agents/oak-authoring.toml",
                         "platforms/claude/templates/.claude/agents/oak-authoring.md"):
            shutil.copyfile(PACKAGE / relative, root / "native-only" / Path(relative).name)
        _run_isolated(_DETACHED, root)


def validate_outputs() -> None:
    """Verify exact deliveries, source-only regeneration, safety, and portability."""
    from build.authoring import SCRIPT, VALIDATOR_SOURCE, artifacts
    from build.definitions import documents
    from build.ebnf import grammar
    from build.agents import artifacts as agent_artifacts

    root = ROOT / "generated"
    expected = {"oak.ebnf": grammar().encode(),
                **{path.relative_to(root).as_posix(): text.encode() for path, text in agent_artifacts().items()},
                **{path.relative_to(root).as_posix(): text.encode() for path, text in artifacts().items()},
                **{"definitions/" + name: text.encode() for name, text in documents().items()}}
    if any((ROOT / name).exists() for name in ("outputs", "skills")):
        raise RuntimeError("obsolete generated product roots remain")
    if any(not name.endswith('.oak.md') for name in documents()):
        raise RuntimeError("construct definitions need .oak.md filenames")
    _verify_outputs(root, expected)
    if SCRIPT.read_bytes() != VALIDATOR_SOURCE.read_bytes():
        raise RuntimeError("generated validator differs from its maintained source")
    _cold_regeneration(expected)
    _detached_delivery()


__all__ = ["validate_outputs"]
