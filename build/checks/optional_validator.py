"""Offline consent, identity, cache, extraction, and failure-path checks."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from unittest.mock import Mock, patch
from zipfile import BadZipFile, ZipFile, ZipInfo

from build.authoring import SCRIPT, validator_module
from build.checks.authoring import require
from build.checks.fixtures import ROOT


def _invoke(module, arguments: list[str]) -> tuple[int, dict]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.main(arguments)
    return code, json.loads(output.getvalue())


def _archive(module) -> bytes:
    output = io.BytesIO()
    prefix = f"open-agent-knowledge-{module.REVISION}/"
    with ZipFile(output, "w") as archive:
        for path in sorted((ROOT / "oak").rglob("*.py")):
            archive.writestr(prefix + path.relative_to(ROOT).as_posix(), path.read_bytes())
        archive.writestr(prefix + "pyproject.toml", (ROOT / "pyproject.toml").read_bytes())
    return output.getvalue()


def validate_optional_validator() -> None:
    module = validator_module()
    with tempfile.TemporaryDirectory(prefix="oak-validator-check-") as temporary:
        root = Path(temporary)
        valid = root / "valid.oak.md"
        valid.write_text('<constants>\nname: "Example"\n</constants>', encoding="utf-8")
        invalid = root / "invalid.oak.md"
        invalid.write_text("not OAK", encoding="utf-8")
        cache = root / "cache"
        # A validation request alone cannot create caches, download, or install.
        with patch.object(module, "urlopen", side_effect=AssertionError("unapproved network")), patch.object(module, "install", side_effect=AssertionError("unapproved install")):
            code, result = _invoke(module, [str(valid), "--source", str(root / "missing"), "--cache-dir", str(cache)])
            require(code == 2 and result["reason"] == "permission-required", "missing consent did not produce not-performed")
            require(not cache.exists(), "unapproved validation created an installation")

        # Actual subprocess checks use the matching repository and import its dependencies.
        for path, expected in ((valid, 0), (invalid, 1)):
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--source", str(ROOT), "--cache-dir", str(cache)], capture_output=True, text=True, check=False)
            require(result.returncode == expected, f"real validator returned the wrong outcome: {result.stdout} {result.stderr}")
            require(json.loads(result.stdout)["status"] == ("valid" if expected == 0 else "invalid"), "incorrect validator result")
        require(not cache.exists(), "reusing an existing validator created a cache")
        # The explicit reuse path is preferred even when installation is permitted.
        fake_python = root / "python"
        with patch.object(module, "discover", return_value=(fake_python, ROOT)), patch.object(module, "install", side_effect=AssertionError("reuse installed again")), patch.object(module.subprocess, "run", return_value=Mock(returncode=0)) as run:
            require(module.main([str(valid), "--allow-install", "--cache-dir", str(cache)]) == 0, "reuse failed")
            require(run.call_args.args[0][0] == str(fake_python), "selected interpreter was not reused")

        # Explicit consent is the only CLI route to installation.
        with patch.object(module, "discover", return_value=None), patch.object(module, "install", return_value=(fake_python, ROOT)) as install, patch.object(module.subprocess, "run", return_value=Mock(returncode=1)):
            require(module.main([str(valid), "--allow-install", "--cache-dir", str(cache)]) == 1, "worker failure was hidden")
            install.assert_called_once_with(cache.resolve())
        for error in (OSError("offline"), RuntimeError("dependencies unavailable"), BadZipFile("damaged download")):
            with patch.object(module, "discover", return_value=None), patch.object(module, "install", side_effect=error):
                code, result = _invoke(module, [str(valid), "--allow-install", "--cache-dir", str(cache)])
                require(code == 2 and result["status"] == "not-performed", "installer failure was reported as validation")

        # A complete mocked download checks real extraction and retained-source identity.
        archive = _archive(module)
        builder = Mock()
        def environment(path):
            module.environment_python(Path(path)).parent.mkdir(parents=True)
        builder.create.side_effect = environment
        with patch.object(module, "urlopen", return_value=io.BytesIO(archive)) as download, patch.object(module, "matches", side_effect=[False, True]), patch.object(module.venv, "EnvBuilder", return_value=builder), patch.object(module.subprocess, "run", return_value=Mock(returncode=0)) as pip:
            python, source = module.install(cache)
            require(module.REVISION in download.call_args.args[0], "installer did not fetch the matching revision")
            require(source == module.installation_path(cache) / "source", "source cache location drifted")
            require(python == module.environment_python(module.installation_path(cache) / "environment"), "dependencies were not isolated")
            require(pip.call_args.args[0][:6] == [str(python), "-I", "-m", "pip", "--isolated", "install"], "pip was not isolated")
            require((source.parent / "installation.json").is_file(), "successful installation was not retained")
        # Cached installations are discovered and reused without invoking the downloader.
        args = Mock(python=None, source=root / "missing")
        with patch.object(module, "matches", side_effect=lambda py, src: py == python and src == source):
            require(module.discover(args, source.parent) == (python, source), "matching cache was not discovered")
        with patch.object(module, "matches", return_value=True), patch.object(module, "urlopen", side_effect=AssertionError("cache downloaded again")):
            require(module.install(cache) == (python, source), "matching cache was not reused")

        # Never leave partial installs ready, or delete unrelated cache directories.
        failed_cache = root / "failed"
        with patch.object(module, "matches", return_value=False), patch.object(module, "urlopen", side_effect=OSError("offline")):
            try:
                module.install(failed_cache)
            except OSError:
                pass
            else:
                raise RuntimeError("failed download was accepted")
        require(not module.installation_path(failed_cache).exists(), "failed installation survived")
        require(not list(failed_cache.glob("*.lock")), "failed installation left a lock")
        sentinel = source.parent / "unrelated"
        sentinel.write_text("preserve")
        with patch.object(module, "matches", return_value=False):
            try:
                module.install(cache)
            except RuntimeError:
                pass
            else:
                raise RuntimeError("broken cache silently overwritten")
        require(sentinel.read_text() == "preserve", "unrecognized cache was deleted")
        _unsafe_archives(module, root)
        # Reference traversal is rejected before reading outside the allowed root.
        outside = root / "outside.oak.md"
        outside.write_text('<constants>\nvalue: "secret"\n</constants>')
        inside = root / "inside"
        inside.mkdir()
        escaped = inside / "escape.oak.md"
        escaped.write_text('<processes>\n<process id="read" name="Read value">\nACT Use <VALUE>. (VALUE=$../outside.oak.md#constant.value)\n</process>\n</processes>')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = module.validate([escaped], inside)
        require(code == 1, "validator allowed document-root traversal")


def _unsafe_archives(module, root: Path) -> None:
    prefix = f"open-agent-knowledge-{module.REVISION}/"
    cases = [(prefix + "../escape", 0), ("/absolute", 0), (prefix + "oak/link", stat.S_IFLNK << 16), (prefix + "oak\\escape", 0)]
    for index, (name, mode) in enumerate(cases):
        path = root / f"unsafe-{index}.zip"
        with ZipFile(path, "w") as archive:
            info = ZipInfo(name)
            info.external_attr = mode
            archive.writestr(info, "not trusted")
        try:
            module.extract_archive(path, root / f"extracted-{index}")
        except ValueError:
            pass
        else:
            raise RuntimeError("unsafe source archive was extracted")
    good = root / "good.zip"
    good.write_bytes(_archive(module))
    with patch.object(module, "MAX_ARCHIVE_BYTES", 1):
        try:
            module.extract_archive(good, root / "oversized")
        except ValueError:
            pass
        else:
            raise RuntimeError("archive expansion limit was ignored")
    with patch.object(module, "SOURCE_SHA256", "0" * 64):
        try:
            module.extract_archive(good, root / "mismatch")
        except ValueError:
            pass
        else:
            raise RuntimeError("mismatched source revision was accepted")
