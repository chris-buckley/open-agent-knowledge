"""Independent profile manifests, bounded composition and delivered fixture acceptance."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
import json
from io import StringIO
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from pydantic import JsonValue
from oak import ActHandler, Arrival, BindingValue, Call, ExecutionResult, Node, Process, ResolvedGraph, ValueBinding, execute, parse, render, resolve
from build.checks.fixtures import ROOT
from build.checks.skill_profile_memory import MemoryFixture, digest, index_bytes, IndexRow, json_bytes
from build.skill_template import Profile, Resource, ResourceKind, populate, template
from examples.skill_profiles import classifier, example, memory, packages

_SHARED = {
    "classify-item": {"SKILL.md", "processes/classify-item.oak.md"},
    "review-items": {"SKILL.md", "references/memory.oak.md"},
}
_SCAFFOLDS = {".gitignore", "state/configuration.json", "state/policy/index.csv", "state/policy/priority.json",
              "state/history/index.csv", "state/runs/index.csv"}
_GENERATED = {"state/policy/(...)", "state/history/records/(...)", "state/runs/(...)"}
_TEACHING = ROOT / "generated/oak-authoring.skill/assets/examples/skill_profiles"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejects(operation: Callable[[], object], reason: str, *, match: str = "") -> None:
    try:
        operation()
    except (ValueError, RuntimeError) as error:
        if match and match not in str(error):
            raise RuntimeError(f"expected {reason}: {match}, got {error}") from error
        return
    raise RuntimeError("profile accepted " + reason)


def body(entry: str) -> str:
    return entry.split("---\n", 2)[2].lstrip("\n")


def delivered_packages() -> dict[str, dict[str, str]]:
    node = parse((_TEACHING / "packages.oak.md").read_text(encoding="utf-8"))
    files = next(constant.value for constant in node.constants if constant.id == "packages")
    require(isinstance(files, dict), "profile teaching needs complete file mappings")
    require(files == packages.package_files(), "profile teaching differs from its source")
    return files


def write_packages(root: Path, files: Mapping[str, Mapping[str, str]]) -> None:
    for package, entries in files.items():
        for relative, text in entries.items():
            target = root / package / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")


def package_graph(root: Path, name: str, expected: Mapping[str, Mapping[str, str]]) -> ResolvedGraph:
    """The fixture explicitly maps a bounded package set to stable logical identities."""
    documents = {}
    for package, entries in expected.items():
        observed = {path.relative_to(root / package).as_posix() for path in (root / package).rglob("*") if path.is_file()}
        require(observed == set(entries), "package static file set is missing or has extra files")
        for relative, wanted in entries.items():
            path = root / package / relative
            require(path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(), "package dependency escapes root")
            require(path.is_file() and path.read_bytes() == wanted.encode("utf-8"), "package dependency is missing or changed")
            logical = "SKILL.oak.md" if relative == "SKILL.md" else relative
            documents[f"profiles/{package}/{logical}"] = body(wanted) if relative == "SKILL.md" else wanted
    source = f"profiles/{name}/SKILL.oak.md"
    return resolve(parse(documents[source]), source=source, root="profiles", load=documents.get)


@contextmanager
def fixture() -> Iterator[tuple[Path, dict[str, dict[str, str]], ResolvedGraph, MemoryFixture]]:
    with TemporaryDirectory(prefix="oak-skill-profiles-") as temporary:
        root = Path(temporary)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        files = delivered_packages()
        write_packages(root / "shared", files)
        instances = {owner: root / "instances" / owner for owner in ("alpha", "beta")}
        for directory in instances.values():
            directory.mkdir(parents=True)
            for relative, text in files["review-items"].items():
                target = directory / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8", newline="\n")
        graph = package_graph(root / "shared", "review-items", files)
        host = MemoryFixture(instances, parse(body(files["review-items"]["SKILL.md"])),
                             parse(files["classify-item"]["processes/classify-item.oak.md"]),
                             parse(files["review-items"]["references/memory.oak.md"]))
        yield root, files, graph, host


def request(host: MemoryFixture, owner: str = "alpha", identifier: str = "item-1", *, mode: str = "summary") -> Arrival:
    return Arrival(interface="interface.request", values={
        "OWNER": owner, "INSTANCE": host.instances[owner].as_posix(), "ID": identifier,
        "TEXT": "Urgent: review the synthetic item", "POLICY_ID": "priority", "RETENTION": mode,
    })


def resume(host: MemoryFixture, owner: str = "alpha", identifier: str = "item-1") -> Arrival:
    return Arrival(interface="interface.resume", values={"OWNER": owner, "INSTANCE": host.instances[owner].as_posix(), "ID": identifier})


def initial_state(graph: ResolvedGraph) -> dict[str, JsonValue]:
    return {graph.display_target(document, "state", entry.id): deepcopy(entry.value)
            for document, node in graph.documents.items() for entry in node.state}


def run_cycle(graph: ResolvedGraph, arrival: Arrival, state: Mapping[str, JsonValue], *, act: ActHandler) -> ExecutionResult:
    return execute(graph.documents[graph.root], arrival, state, source=graph.root,
                   root="profiles", load=graph.documents.get, act=act)


def prepare(graph: ResolvedGraph, host: MemoryFixture, owner: str = "alpha", identifier: str = "item-1", *, mode: str = "summary") -> dict[str, JsonValue]:
    checkpoint = host.restore_checkpoint(owner) if (host.instances[owner] / "state/runs/pending.json").exists() else initial_state(graph)
    before = deepcopy(checkpoint)
    result = run_cycle(graph, request(host, owner, identifier, mode=mode), checkpoint, act=host)
    require(checkpoint == before and len(result.emissions) == 1
            and dict(result.emissions[0].values) == {"ID": identifier}, "preparation changed caller state or claimed completion")
    host.save_checkpoint(owner, result.state)
    return dict(result.state)


def finish(graph: ResolvedGraph, host: MemoryFixture, owner: str = "alpha", identifier: str = "item-1") -> dict[str, JsonValue]:
    checkpoint = host.restore_checkpoint(owner)
    result = run_cycle(graph, resume(host, owner, identifier), checkpoint, act=host)
    require(len(result.emissions) == 1, "review did not emit one completion")
    values = dict(result.emissions[0].values)
    require(values["OWNER"] == owner and values["ID"] == identifier and values["CATEGORY"] == "match"
            and values["REFERENCE"] == f"state/history/records/{identifier}.json", "review completion differs from fixed expectations")
    require(values["SHA256"] == digest((host.instances[owner] / str(values["REFERENCE"])).read_bytes()), "review digest does not cover its record")
    host.save_checkpoint(owner, result.state)
    return values


def state_files(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in (root / "state").rglob("*") if path.is_file()}


def _map_leaves(layout: str) -> set[str]:
    lines = layout.splitlines()
    require(lines[0] == "SKILL_TREE:", "package MAP lost its literal heading")
    parents: list[str] = []
    leaves: set[str] = set()
    for line in lines[1:]:
        indent = len(line) - len(line.lstrip(" "))
        require(indent >= 2 and indent % 2 == 0, "MAP indentation is not a two-space tree")
        depth = indent // 2
        name = line.strip()
        require(depth <= len(parents) + 1, "MAP skips a parent directory")
        if "→" not in name:
            require(name.endswith("/"), "MAP directory is malformed")
            parents = [*parents[:depth - 1], name[:-1]]
            continue
        leaf, purpose = name.split("→", 1)
        require(bool(purpose), "MAP leaf has no purpose")
        path = "/".join([*parents[:depth - 1], leaf])
        require(path not in leaves, "MAP duplicates a leaf")
        leaves.add(path)
    return leaves


def _package_description(name: str, files: Mapping[str, str]) -> None:
    expected = _SHARED[name]
    require(set(files) == expected, "profile static manifest differs from independent expectations")
    node = parse(body(files["SKILL.md"]))
    constants = {constant.id: constant.value for constant in node.constants}
    leaves = _map_leaves(constants["layout"])
    require(leaves == expected | (_SCAFFOLDS | _GENERATED if name == "review-items" else set()), "MAP misses or hides a static leaf")
    expected_roles = ("DEFINE", "ROUTE", "LOOP", "INDEX", "MAP", "ASSERT") if name == "review-items" else ("DEFINE", "LOOP", "INDEX", "MAP", "ASSERT")
    require(tuple(constants["roles"]) == expected_roles, "role presentation differs from the selected profile")
    references = {row["reference"] for row in constants["index"]}
    expected_index = {"references/memory.oak.md", "../classify-item/processes/classify-item.oak.md"} if name == "review-items" else {"processes/classify-item.oak.md"}
    require(references == expected_index and all(row["when"] for row in constants["index"]), "INDEX misses a selected resource or dependency")
    require(bool(node.state) == (name == "review-items"), "profile state ownership differs")
    for grouping in ("xml", "markdown"):
        text = render(node, grouping=grouping)
        require(render(parse(text), grouping=grouping) == text, "profile grouping changed its meaning")


def _profile_manifests(files: dict[str, dict[str, str]]) -> None:
    require(set(files) == set(_SHARED), "unexpected profile package")
    for name in _SHARED:
        _package_description(name, files[name])
    require(not any("SKILL.md" == path.name for path in _TEACHING.rglob("SKILL.md")), "teaching installed a nested example skill")
    require(template(Profile.STATEFUL).replace("<STATE_PART>\n", "") == template(), "profile templates duplicated their common source")
    require("<STATE_PART>" not in template(), "default scaffold retained a state slot")
    broken = [
        lambda: Resource("../escaped.oak.md", "Unapproved shared path"),
        lambda: Resource("state/private/(...)", "Hidden static file"),
        lambda: Resource("state/data.json", "Generated fixed leaf", kind=ResourceKind.GENERATED),
        lambda: Resource("state/index.csv", "Private discovery", "Every request", ResourceKind.SCAFFOLD),
        lambda: Resource("/absolute.oak.md", "Absolute resource"),
    ]
    for operation in broken:
        rejects(operation, "invalid resource declaration")
    roles = {"DEFINE": "purpose", "LOOP": "process", "INDEX": "index", "MAP": "layout", "ASSERT": "result"}
    rejects(lambda: populate(Profile.STATELESS, example.review_node(), packages.REVIEW_RESOURCES,
                             name="invalid", description="Invalid profile", title="Invalid", purpose="Invalid",
                             principle="Invalid", roles=roles), "state leakage")
    definition = {"name": "fixture", "description": "A fixture", "title": "Fixture", "purpose": "Check",
                  "principle": "Use supplied data", "roles": roles}
    for resources in (
        (*packages.CLASSIFY_RESOURCES, packages.CLASSIFY_RESOURCES[0]),
        (*packages.CLASSIFY_RESOURCES, Resource("processes", "A conflicting file")),
        (*packages.CLASSIFY_RESOURCES, Resource("unused/.gitkeep", "An unpopulated folder")),
    ):
        rejects(lambda: populate(Profile.STATELESS, packages.classify_entry(), resources, **definition), "invalid populated resources")
    rejects(lambda: populate(Profile.STATELESS, packages.classify_entry(), packages.CLASSIFY_RESOURCES,
                             **{**definition, "title": "<TITLE_JSON>"}), "unfilled definition")


def _stateless_execution() -> None:
    with fixture() as (root, files, _, host):
        graph = package_graph(root / "shared", "classify-item", files)
        source = {str(path): path.read_bytes() for path in (root / "shared").rglob("*") if path.is_file()}
        for text, term, expected in (("An URGENT item", "urgent", "match"), ("Ordinary item", "urgent", "other")):
            result = run_cycle(graph, Arrival(interface="interface.request", values={"TEXT": text, "TERM": term}), {}, act=host)
            require(not result.state and [dict(emission.values) for emission in result.emissions] == [{"CATEGORY": expected}], "stateless result differs")
        rejects(lambda: run_cycle(graph, Arrival(interface="interface.request", values={"TEXT": "", "TERM": "urgent"}), {}, act=host), "invalid input")
        rejects(lambda: run_cycle(graph, Arrival(interface="interface.request", values={"TEXT": "item", "TERM": "urgent"}), {},
                                act=lambda _action, _values: {"CATEGORY": "invalid"}), "invalid output")
        require(source == {str(path): path.read_bytes() for path in (root / "shared").rglob("*") if path.is_file()}
                and not any((directory / "state").exists() for directory in host.instances.values()), "stateless execution wrote persistent memory")


def _memory_lifecycle() -> None:
    with fixture() as (root, files, graph, host):
        alpha, beta = host.instances.values()
        original_entry = (alpha / "SKILL.md").read_bytes()
        prepare(graph, host)
        pending = state_files(alpha)
        require(not (alpha / "state/history/records/item-1.json").exists(), "preparation published a completed record")
        prepare(graph, host, "beta", mode="full")
        require(state_files(alpha) == pending, "another owner changed the first instance")
        finish(graph, host, "beta")
        beta_completed = state_files(beta)
        finish(graph, host)
        summary = json.loads((alpha / "state/history/records/item-1.json").read_bytes())
        full = json.loads((beta / "state/history/records/item-1.json").read_bytes())
        require("source" not in summary and full["source"] == "Urgent: review the synthetic item", "retention did not control future record payloads")
        require(state_files(beta) == beta_completed and (alpha / "SKILL.md").read_bytes() == original_entry, "review changed another owner or shared entry")
        require(host.events.index("write-record") < host.events.index("write-index"), "index preceded its record")
        prepare(graph, host, identifier="item-2", mode="")
        require(host.events.count("initialize") == 2, "saved settings were not reused")
        before_update = state_files(alpha)
        updated = deepcopy(files)
        updated["review-items"]["SKILL.md"] = updated["review-items"]["SKILL.md"].replace("Publish reviewed evidence", "Preserve reviewed evidence")
        write_packages(root / "shared", updated)
        for relative, text in updated["review-items"].items():
            (alpha / relative).write_text(text, encoding="utf-8", newline="\n")
        require(state_files(alpha) == before_update, "compatible source update changed owned memory")
        finish(graph, host, identifier="item-2")
        require((alpha / "SKILL.md").read_bytes() == updated["review-items"]["SKILL.md"].encode(), "run rewrote updated shared source")
        renamed = {"classify-item": updated["classify-item"], "review-renamed": dict(updated["review-items"])}
        renamed["review-renamed"]["SKILL.md"] = renamed["review-renamed"]["SKILL.md"].replace("name: review-items\n", "name: review-renamed\n", 1)
        stable_state = state_files(alpha)
        write_packages(root / "shared", renamed)
        current_graph = package_graph(root / "shared", "review-renamed", renamed)
        require(state_files(alpha) == stable_state, "renaming shared exposure changed the stable local owner")
        prepare(current_graph, host, identifier="item-3")
        finish(current_graph, host, identifier="item-3")


def _dependency_boundaries() -> None:
    with fixture() as (root, files, graph, host):
        shared = root / "shared"
        dependency = shared / "classify-item/processes/classify-item.oak.md"
        original = dependency.read_bytes()
        dependency.write_bytes(original + b"\n")
        rejects(lambda: package_graph(shared, "review-items", files), "changed dependency", match="missing or changed")
        dependency.unlink()
        rejects(lambda: package_graph(shared, "review-items", files), "missing dependency", match="missing or has extra")
        dependency.write_bytes(original)
        extra = shared / "review-items/unknown.oak.md"
        extra.write_bytes(b"unselected")
        rejects(lambda: package_graph(shared, "review-items", files), "unselected static file", match="extra files")
        extra.unlink()
        raw = body(files["review-items"]["SKILL.md"])
        escaped = raw.replace("../classify-item/processes/classify-item.oak.md", "../../outside.oak.md")
        rejects(lambda: resolve(parse(escaped), source=graph.root, root="profiles", load=graph.documents.get), "escaping graph dependency")
        rejects(lambda: resolve(parse(raw), source=graph.root, root="profiles/review-items", load=graph.documents.get), "unapproved sibling root")
        missing = raw.replace("#process.classify", "#process.absent")
        rejects(lambda: resolve(parse(missing), source=graph.root, root="profiles", load=graph.documents.get), "missing process export")
        wrong = raw.replace("#process.classify", "#schema.category")
        rejects(lambda: parse(wrong), "wrong dependency kind")
        foreign = raw.replace("$state.phase", "$../classify-item/processes/classify-item.oak.md#state.phase")
        rejects(lambda: parse(foreign), "cross-owner state access")
        def cyclic(target: str) -> Node:
            return Node(schemas=[classifier.item_schema, classifier.category_schema], processes=[
                Process(id="classify", name="Classify item", input="schema.item", output="schema.category", body=[
                    Call(process=target + "#process.classify",
                         inputs=[ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in ("TEXT", "TERM")],
                         outputs=["CATEGORY"]),
                ]),
            ])
        cycles = {"cycle/classifier.oak.md": cyclic("peer.oak.md"), "cycle/peer.oak.md": cyclic("classifier.oak.md")}
        rejects(lambda: resolve(cycles["cycle/classifier.oak.md"], source="cycle/classifier.oak.md", root="cycle", load=cycles.get), "cross-document call cycle")
        require(not host.events, "invalid dependency checks invoked a host action")


def _optional_validation() -> None:
    from build.authoring import validator_module

    with fixture() as (root, _, _, _):
        validator = validator_module()
        shared = root / "shared"
        for name in ("classify-item", "review-items"):
            with redirect_stdout(StringIO()) as output:
                status = validator.validate([shared / name / "SKILL.md"], shared)
            receipt = json.loads(output.getvalue())
            require(status == 0 and receipt["checks"] == ["parse", "resolve"], "selected package failed bounded optional validation")
        with redirect_stdout(StringIO()) as output:
            status = validator.validate([shared / "review-items/SKILL.md"], None)
        require(status == 1, "optional validator silently widened the graph root")


_DETACHED_DRIVER = '''
import importlib.abc, json, pathlib, sys
root, runtime, repository = map(pathlib.Path, sys.argv[1:])
sys.path[:0] = [str(root), str(runtime)]
class RejectRepositoryImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'build', 'examples'} or fullname.startswith(('build.', 'examples.')):
            raise ImportError('detached profile imported repository support')
sys.meta_path.insert(0, RejectRepositoryImports())
def no_network(event, args):
    if event in {'socket.connect', 'socket.getaddrinfo', 'socket.bind'}:
        raise RuntimeError('detached profile attempted network access')
sys.addaudithook(no_network)
from oak import Arrival, execute, parse
from profile_host import MemoryFixture
shared = root / 'shared'
def read_entry(name):
    return (shared / name / 'SKILL.md').read_text(encoding='utf-8').split('---\\n', 2)[2].lstrip('\\n')
review_text = read_entry('review-items')
classifier_text = (shared / 'classify-item/processes/classify-item.oak.md').read_text(encoding='utf-8')
memory_text = (shared / 'review-items/references/memory.oak.md').read_text(encoding='utf-8')
documents = {'profiles/review-items/SKILL.oak.md': parse(review_text),
             'profiles/classify-item/processes/classify-item.oak.md': parse(classifier_text),
             'profiles/review-items/references/memory.oak.md': parse(memory_text)}
review = documents['profiles/review-items/SKILL.oak.md']
instance = root / 'instances/alpha'
host = MemoryFixture({'alpha': instance}, review, parse(classifier_text), parse(memory_text))
state = {'state.' + entry.id: entry.value for entry in review.state}
initial_source = {str(p): p.read_bytes() for p in shared.rglob('*') if p.is_file()}
request = {'OWNER': 'alpha', 'INSTANCE': instance.as_posix(), 'ID': 'detached-1',
           'TEXT': 'URGENT synthetic item', 'POLICY_ID': 'priority', 'RETENTION': 'summary'}
prepared = execute(review, Arrival(interface='interface.request', values=request), state,
                   source='profiles/review-items/SKILL.oak.md', root='profiles', load=documents.get, act=host)
host.save_checkpoint('alpha', prepared.state)
resumed = execute(review, Arrival(interface='interface.resume', values={key: request[key] for key in ('OWNER','INSTANCE','ID')}),
                  host.restore_checkpoint('alpha'), source='profiles/review-items/SKILL.oak.md', root='profiles', load=documents.get, act=host)
assert len(resumed.emissions) == 1 and resumed.emissions[0].values['CATEGORY'] == 'match'
record = json.loads((instance / 'state/history/records/detached-1.json').read_bytes())
assert record['owner'] == 'alpha' and record['mode'] == 'summary' and 'source' not in record
assert initial_source == {str(p): p.read_bytes() for p in shared.rglob('*') if p.is_file()}
for module in tuple(sys.modules.values()):
    origin = getattr(module, '__file__', None)
    if origin and pathlib.Path(origin).resolve().is_relative_to(repository.resolve()):
        raise RuntimeError('detached profile imported original repository code')
print('Detached stateful composition and summary retention passed.')
'''


def _detached_packages() -> None:
    with fixture() as (root, _, _, _):
        runtime = root / "runtime"
        shutil.copytree(ROOT / "oak", runtime / "oak", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copyfile(Path(__file__).with_name("skill_profile_memory.py"), root / "profile_host.py")
        driver = root / "detached.py"
        driver.write_text(_DETACHED_DRIVER, encoding="utf-8")
        completed = subprocess.run([sys.executable, "-I", str(driver), str(root), str(runtime), str(ROOT)],
                                   cwd=root, capture_output=True, text=True, timeout=60, check=False)
        require(completed.returncode == 0, "detached profile failed: " + completed.stdout + completed.stderr)


def validate_skill_profiles() -> None:
    files = delivered_packages()
    _profile_manifests(files)
    _stateless_execution()
    _memory_lifecycle()
    _dependency_boundaries()
    _optional_validation()
    _detached_packages()
    from build.checks.skill_profile_cases import validate_memory_cases

    validate_memory_cases()


if __name__ == "__main__":
    validate_skill_profiles()
    print("Skill profile manifests, composition and memory lifecycle passed.")
