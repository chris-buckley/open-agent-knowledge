"""Optional, consent-gated OAK validation. The authoring skill needs no Python.

Run: python scripts/validate.py document.oak.md [--root document-directory]
Exit 0: valid; 1: invalid; 2: not performed (including permission required).
Only --allow-install permits downloads and an isolated dependency installation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from urllib.request import urlopen
import venv
from zipfile import BadZipFile, ZipFile

SKILL_VERSION = "2.2.0"
REPOSITORY = "chris-buckley/open-agent-knowledge"
REVISION = "2b542c613c5d1a7e64b597884fae4f444ac34916"
SOURCE_SHA256 = "e9c301a254ec8897698816091bac99cc117d8e0fa052192e728d356d19c27bd1"
PROJECT_SHA256 = "2412c436c0ffaa05c604da2d58be4b72c443b37efcaa094380845fd0fe3a3702"
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024


def package_digest(package: Path) -> str:
    """Identify all validator Python sources, not the project's placeholder version."""
    digest = hashlib.sha256()
    files = sorted(package.rglob("*.py"))
    if not files or not (package / "__init__.py").is_file():
        raise ValueError("OAK package sources are missing")
    for path in files:
        digest.update(path.relative_to(package).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def activate(source: Path | None) -> None:
    """Verify matching code before importing it in the selected interpreter."""
    if source is not None:
        package = source.resolve() / "oak"
    else:
        spec = importlib.util.find_spec("oak")
        if spec is None or spec.origin is None:
            raise ValueError("no OAK installation in this interpreter")
        package = Path(spec.origin).parent
    if package_digest(package) != SOURCE_SHA256:
        raise ValueError("OAK source fingerprint does not match this skill")
    if source is not None:
        sys.path.insert(0, str(source.resolve()))
    import oak  # Imports and dependency checks happen only after identity verification.

    if Path(oak.__file__).resolve().parent != package.resolve():
        raise ValueError("a different OAK installation was imported")


def report(status: str, **details: object) -> None:
    print(json.dumps({"status": status, "revision": REVISION, **details}, ensure_ascii=False))


def cache_directory() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "oak" / "validators"


def environment_python(directory: Path) -> Path:
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def command(python: Path, source: Path | None, *arguments: str) -> list[str]:
    values = [str(python), "-I", str(Path(__file__).resolve()), *arguments]
    if source is not None:
        values.extend(("--source", str(source.resolve())))
    return values


def matches(python: Path, source: Path | None) -> bool:
    try:
        result = subprocess.run(
            command(python, source, "--probe"), capture_output=True, text=True,
            timeout=30, check=False,
        )
        return result.returncode == 0 and json.loads(result.stdout).get("status") == "matching"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def installation_path(cache: Path) -> Path:
    return cache / f"{REVISION}-py{sys.version_info.major}.{sys.version_info.minor}"


def discover(args: argparse.Namespace, destination: Path) -> tuple[Path, Path | None] | None:
    """Check only explicit, adjacent, current-interpreter, and exact-cache locations."""
    python = Path(args.python or sys.executable)
    candidates: list[tuple[Path, Path | None]] = []
    if args.source is not None:
        candidates.append((python, args.source))
    else:
        script = Path(__file__).resolve()
        if len(script.parents) >= 4:
            adjacent = script.parents[3]
            if (adjacent / "oak" / "__init__.py").is_file():
                candidates.append((python, adjacent))
        candidates.append((python, None))
    candidates.append((environment_python(destination / "environment"), destination / "source"))
    for candidate in candidates:
        if matches(*candidate):
            return candidate
    return None


def extract_archive(archive: Path, destination: Path) -> None:
    """Extract pinned source without traversal, symlinks, or zip-bomb expansion."""
    prefix = f"open-agent-knowledge-{REVISION}"
    with ZipFile(archive) as bundle:
        if sum(item.file_size for item in bundle.infolist()) > MAX_ARCHIVE_BYTES:
            raise ValueError("OAK source archive exceeds the extraction limit")
        for item in bundle.infolist():
            path = PurePosixPath(item.filename)
            if (not path.parts or path.parts[0] != prefix or path.is_absolute()
                    or ".." in path.parts or "\\" in item.filename
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError("unsafe or unexpected OAK source archive entry")
            relative = Path(*path.parts[1:])
            # Only the validator and its dependency declaration are needed at runtime.
            if not relative.parts or relative.parts[0] not in {"oak", "pyproject.toml"}:
                continue
            target = destination / relative
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(item) as incoming, target.open("wb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
    if package_digest(destination / "oak") != SOURCE_SHA256:
        raise ValueError("downloaded OAK sources do not match the pinned revision")
    if hashlib.sha256((destination / "pyproject.toml").read_bytes()).hexdigest() != PROJECT_SHA256:
        raise ValueError("downloaded dependency declaration does not match the pin")


def install(cache: Path) -> tuple[Path, Path]:
    """Install only after caller consent; keep a ready environment for later calls."""
    destination = installation_path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    lock = destination.with_name(destination.name + ".lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError(f"another installation owns {lock}; validation was not performed") from None
    created = False
    try:
        python = environment_python(destination / "environment")
        source = destination / "source"
        if matches(python, source):
            return python, source
        if destination.exists():
            # Never delete an unrecognized user directory or silently repair a broken cache.
            raise RuntimeError(f"inspect and remove the incomplete cache before retrying: {destination}")
        destination.mkdir()
        created = True
        with tempfile.TemporaryDirectory(prefix="oak-download-", dir=cache) as temporary:
            archive = Path(temporary) / "source.zip"
            url = f"https://codeload.github.com/{REPOSITORY}/zip/{REVISION}"
            with urlopen(url, timeout=60) as incoming, archive.open("wb") as outgoing:
                total = 0
                while chunk := incoming.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_ARCHIVE_BYTES:
                        raise ValueError("OAK download exceeds the archive limit")
                    outgoing.write(chunk)
            extract_archive(archive, source)
        project = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        dependencies = project["dependencies"]
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            raise ValueError("invalid pinned dependency list")
        venv.EnvBuilder(with_pip=True).create(destination / "environment")
        subprocess.run(
            [str(python), "-I", "-m", "pip", "--isolated", "install",
             "--disable-pip-version-check", *dependencies],
            check=True, stdout=sys.stderr, stderr=sys.stderr, timeout=600,
        )
        if not matches(python, source):
            raise RuntimeError("installed validator failed its identity or dependency check")
        (destination / "installation.json").write_text(
            json.dumps({"revision": REVISION, "source_sha256": SOURCE_SHA256,
                        "project_sha256": PROJECT_SHA256}, indent=2) + "\n", encoding="utf-8",
        )
        return python, source
    except BaseException:
        if created:
            shutil.rmtree(destination, ignore_errors=True)
        raise
    finally:
        lock.rmdir()


def oak_body(text: str, path: Path) -> str:
    """The standard skill entry may wrap its OAK body in YAML frontmatter."""
    if path.name == "SKILL.md" and text.startswith("---\n"):
        _metadata, separator, body = text[4:].partition("\n---\n")
        if not separator:
            raise ValueError("SKILL.md frontmatter is not closed")
        return body.lstrip("\n")
    return text


def validate(paths: list[Path], boundary: Path | None) -> int:
    """Parse and resolve data only. Never execute an authored process or tool."""
    from oak import parse, resolve

    results = []
    for path in paths:
        path = path.resolve()
        root = boundary.resolve() if boundary is not None else path.parent
        try:
            if not path.is_relative_to(root):
                raise ValueError("document is outside the explicit document root")

            def load(name: str) -> str | None:
                target = Path(name).resolve()
                if not target.is_relative_to(root):
                    raise ValueError("document reference escapes the document root")
                return target.read_text(encoding="utf-8") if target.is_file() else None

            node = parse(oak_body(path.read_text(encoding="utf-8"), path))
            # SKILL.md has a virtual OAK identity in the same directory, not an import.
            identity = path if path.name.endswith(".oak.md") else path.with_name(path.stem + ".oak.md")
            graph = resolve(node, source=identity.as_posix(), load=load, root=root.as_posix())
            results.append({"path": str(path), "status": "valid", "documents": len(graph.documents)})
        except Exception as error:
            results.append({"path": str(path), "status": "invalid", "error": str(error)})
    valid = all(item["status"] == "valid" for item in results)
    report("valid" if valid else "invalid", checks=["parse", "resolve"], results=results)
    return 0 if valid else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents", type=Path, nargs="*")
    parser.add_argument("--root", type=Path, help="allowed root for explicit document references")
    parser.add_argument("--source", type=Path, help="existing matching OAK repository root")
    parser.add_argument("--python", type=Path, help="interpreter for an existing validator installation")
    parser.add_argument("--cache-dir", type=Path, default=cache_directory())
    parser.add_argument("--allow-install", action="store_true", help="user approved the download and isolated installation")
    parser.add_argument("--probe", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.probe or args.worker:
            activate(args.source)
            if args.probe:
                report("matching")
                return 0
            if not args.documents:
                raise ValueError("no document was supplied")
            return validate(args.documents, args.root)
        if not args.documents:
            parser.error("supply at least one OAK document or SKILL.md")
        destination = installation_path(args.cache_dir.resolve())
        selected = discover(args, destination)
        if selected is None:
            if not args.allow_install:
                report("not-performed", reason="permission-required", detail=(
                    "Programmatic validation was not performed. Ask permission to download "
                    "the pinned OAK revision and install dependencies in an isolated cached "
                    "environment. Continue authoring if permission is declined."))
                return 2
            selected = install(args.cache_dir.resolve())
        arguments = ["--worker"]
        if args.root is not None:
            arguments.extend(("--root", str(args.root.resolve())))
        arguments.extend(str(path.resolve()) for path in args.documents)
        return subprocess.run(command(*selected, *arguments), check=False).returncode
    except (OSError, ValueError, RuntimeError, BadZipFile, subprocess.SubprocessError) as error:
        report("not-performed", reason="validator-unavailable", detail=str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
