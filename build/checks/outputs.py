"""Generated-output freshness and repository-architecture verification."""

from __future__ import annotations

import ast
import importlib
from collections.abc import Iterator
from pathlib import Path

from build.checks.fixtures import ROOT
from oak.parse.document import parse
from oak.render import render
from oak.rules.guidance import (
    ACT_GUIDANCE,
    DECOMPOSITION_GUIDANCE,
    DELEGATION_GUIDANCE,
    ENTRY_ID_GUIDANCE,
    NAMING_GUIDANCE,
)

_EXPECTED_ROOT_EXPORTS = (
    # The baseline root __all__ is computed and also names the seven submodules; Phase 14 rules on them.
    "ACT",
    "Act",
    "ActHandler",
    "All",
    "Any",
    "Arrival",
    "Assert",
    "AtLeast",
    "AtMost",
    "AuthoringRule",
    "BindingFailure",
    "BindingValue",
    "Call",
    "Compare",
    "Condition",
    "ConditionOperator",
    "Constant",
    "ConstantForm",
    "ConstantValue",
    "DATATYPE_ADAPTERS",
    "DECIMAL_SEPARATOR",
    "Datatype",
    "DateTime",
    "Direction",
    "DocumentLoader",
    "DottedPath",
    "Emission",
    "Emit",
    "ExecutionError",
    "ExecutionResult",
    "Fail",
    "Foreach",
    "GroupingName",
    "If",
    "Instruction",
    "Interface",
    "InterfaceValue",
    "Join",
    "Lines",
    "ListOf",
    "LiteralValue",
    "MaxChars",
    "Node",
    "NonBlankLine",
    "NonEmpty",
    "Not",
    "OakParseError",
    "OneOf",
    "Par",
    "ParseFailure",
    "Part",
    "Placeholder",
    "Process",
    "ProcessName",
    "Quantity",
    "RULES",
    "Regex",
    "RegexPattern",
    "RenderName",
    "ResolutionError",
    "ResolutionFailure",
    "ResolvedGraph",
    "SURFACES",
    "Schema",
    "SchemaBindingError",
    "Set",
    "SlugId",
    "State",
    "StateValue",
    "Step",
    "StyleName",
    "Surface",
    "SurfaceField",
    "THIN_SPACE",
    "TargetPath",
    "ToolContract",
    "ToolHandler",
    "Trigger",
    "Type",
    "Unit",
    "Value",
    "ValueBinding",
    "ValueReference",
    "Where",
    "While",
    "authoring",
    "base",
    "datetime_text",
    "defaults",
    "execute",
    "node",
    "node_json_ld",
    "node_markdown",
    "node_xml",
    "number_text",
    "parse",
    "parse_oak",
    "quantity_text",
    "render",
    "resolve",
    "rules",
    "schema_json_ld",
    "schema_markdown",
    "schema_xml",
    "surface",
    "surface_for",
    "vocabulary",
    "where",
)

_OBSOLETE_MODULE_PATHS = (
    "oak/parse.py",
    "oak/resolve.py",
    "oak/execute.py",
    "oak/rules.py",
    "oak/surface.py",
    "oak/node/graph.py",
    "oak/node/parts/processes.py",
    "oak/node/parts/schemas.py",
    "oak/render/oak/syntax.py",
    "oak/render/json_ld.py",
)

_OBSOLETE_IMPORTS = (
    "oak.node.graph",
    "oak.render.oak.syntax",
)


def validate_outputs() -> None:
    """Verify authoring, grammar, documentation, and output path freshness."""
    from build.authoring import authoring, tree
    from build.docs import documents
    from build.ebnf import grammar

    authoring_text = authoring()

    if (
        render(
            parse(authoring_text),
            grouping="xml",
        )
        + "\n"
        != authoring_text
    ):
        raise RuntimeError(
            "authoring output is not canonical XML OAK"
        )

    bodies = [
        instruction.body
        for instruction in tree().instructions
    ]

    for guidance in (
        *ENTRY_ID_GUIDANCE,
        *NAMING_GUIDANCE,
        *DECOMPOSITION_GUIDANCE,
        *ACT_GUIDANCE,
        *DELEGATION_GUIDANCE,
    ):
        if bodies.count(
            guidance.instruction
        ) != 1:
            raise RuntimeError(
                "authoring output does not contain guidance "
                f"exactly once: {guidance.id}"
            )

    expected = {
        ROOT / "outputs" / "oak.ebnf": grammar(),
        ROOT / "outputs" / "authoring.md": authoring_text,
        **{
            ROOT / "outputs" / "docs" / name: text
            for name, text in documents().items()
        },
    }

    for path, text in expected.items():
        if (
            not path.is_file()
            or path.read_text(
                encoding="utf-8"
            )
            != text
        ):
            raise RuntimeError(
                "generated output is missing or stale: "
                f"{path}"
            )

    actual = set(
        (
            ROOT
            / "outputs"
            / "docs"
        ).glob("*.md")
    )
    documented = {
        path
        for path in expected
        if path.parent
        == ROOT / "outputs" / "docs"
    }

    if actual != documented:
        raise RuntimeError(
            "documentation output path set is stale"
        )

    actual_root = {
        path
        for path in (
            ROOT
            / "outputs"
        ).iterdir()
        if path.is_file()
    }
    expected_root = {
        ROOT / "outputs" / "oak.ebnf",
        ROOT / "outputs" / "authoring.md",
    }

    if actual_root != expected_root:
        raise RuntimeError(
            "generated root output path set is stale"
        )


def _python_files(
    directory: Path,
) -> Iterator[Path]:
    yield from sorted(
        directory.rglob("*.py")
    )


def _syntax_tree(
    path: Path,
) -> ast.Module:
    return ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )


def _imported_modules(
    path: Path,
) -> tuple[str, ...]:
    modules: list[str] = []

    for node in ast.walk(
        _syntax_tree(path)
    ):
        if isinstance(node, ast.Import):
            modules.extend(
                alias.name
                for alias in node.names
            )

        elif (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module is not None
        ):
            modules.append(node.module)

    return tuple(modules)


def _reject_import_prefixes(
    path: Path,
    prefixes: tuple[str, ...],
) -> None:
    for module in _imported_modules(path):
        if any(
            module == prefix
            or module.startswith(
                prefix + "."
            )
            for prefix in prefixes
        ):
            relative = path.relative_to(
                ROOT
            ).as_posix()
            raise RuntimeError(
                f"{relative} imports forbidden {module}"
            )


def _validate_dependency_direction() -> None:
    for path in _python_files(
        ROOT / "oak" / "parse"
    ):
        _reject_import_prefixes(
            path,
            ("oak.render",),
        )

    for path in _python_files(
        ROOT / "oak" / "render"
    ):
        _reject_import_prefixes(
            path,
            ("oak.parse",),
        )

    for path in _python_files(
        ROOT / "oak" / "node"
    ):
        _reject_import_prefixes(
            path,
            (
                "oak.parse",
                "oak.render",
                "oak.resolve",
                "oak.execute",
            ),
        )

    for path in _python_files(
        ROOT / "oak" / "resolve"
    ):
        _reject_import_prefixes(
            path,
            ("oak.execute",),
        )

    for path in _python_files(
        ROOT / "oak"
    ):
        for module in _imported_modules(path):
            if module == "oak":
                relative = path.relative_to(
                    ROOT
                ).as_posix()
                raise RuntimeError(
                    f"{relative} imports the root oak barrel"
                )

            if module in _OBSOLETE_IMPORTS:
                relative = path.relative_to(
                    ROOT
                ).as_posix()
                raise RuntimeError(
                    f"{relative} imports obsolete {module}"
                )


def _validate_fragment_imports() -> None:
    for path in _python_files(
        ROOT / "build" / "checks"
    ):
        for node in ast.walk(
            _syntax_tree(path)
        ):
            if not (
                isinstance(
                    node,
                    ast.ImportFrom,
                )
                and node.level == 0
                and node.module is not None
                and (
                    node.module == "oak.parse"
                    or node.module.startswith(
                        "oak.parse."
                    )
                )
            ):
                continue

            private = [
                alias.name
                for alias in node.names
                if alias.name.startswith("_")
            ]

            if private:
                relative = path.relative_to(
                    ROOT
                ).as_posix()
                raise RuntimeError(
                    f"{relative} imports private parser names: "
                    + ", ".join(private)
                )


def _validate_root_exports() -> None:
    oak = importlib.import_module(
        "oak"
    )
    authored = tuple(
        getattr(
            oak,
            "__all__",
            (),
        )
    )

    if len(authored) != len(
        set(authored)
    ):
        raise RuntimeError(
            "oak.__all__ contains duplicate names"
        )

    actual = tuple(
        sorted(authored)
    )

    if actual != _EXPECTED_ROOT_EXPORTS:
        missing = sorted(
            set(_EXPECTED_ROOT_EXPORTS)
            - set(actual)
        )
        unknown = sorted(
            set(actual)
            - set(_EXPECTED_ROOT_EXPORTS)
        )
        raise RuntimeError(
            "root exports differ; "
            f"missing={missing} unknown={unknown}"
        )


def _validate_obsolete_paths() -> None:
    present = [
        path
        for path in _OBSOLETE_MODULE_PATHS
        if (
            ROOT / path
        ).exists()
    ]

    if present:
        raise RuntimeError(
            "obsolete monolithic modules remain: "
            + ", ".join(present)
        )

    if (
        ROOT / "tests"
    ).exists():
        raise RuntimeError(
            "the refactor created a tests directory"
        )


def _validate_no_pytest_dependency() -> None:
    for path in _python_files(
        ROOT / "build" / "checks"
    ):
        if any(
            module == "pytest"
            or module.startswith(
                "pytest."
            )
            for module in _imported_modules(path)
        ):
            relative = path.relative_to(
                ROOT
            ).as_posix()
            raise RuntimeError(
                f"{relative} requires pytest"
            )


def validate_architecture() -> None:
    """Verify dependency direction, public exports, and removed modules."""
    _validate_dependency_direction()
    _validate_fragment_imports()
    _validate_root_exports()
    _validate_obsolete_paths()
    _validate_no_pytest_dependency()


__all__ = [
    "validate_architecture",
    "validate_outputs",
]
