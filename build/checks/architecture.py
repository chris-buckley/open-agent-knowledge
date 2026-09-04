"""Static verification of repository architecture and refactor cleanup."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_ARCHITECTURE_PATH = Path(__file__).resolve()

_EXPECTED_ROOT_EXPORTS = (
    "InterpreterContext",
    "InterpreterHandler",
    "build_interpreter_context",
    "task_context",
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
    "InterfaceFlow",
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

_FORBIDDEN_CLEANUP_TOKENS = (
    "oak.parse._",
    "if False:",
    "_json_equal",
    "_OPERATOR_PHRASES",
    "_reverse_operator",
    "_invert_operator",
)

_SYMBOL_LOCATIONS = {
    "PART_ORDER": frozenset(
        {
            "oak/node/index.py",
            "oak/node/structure.py",
            "oak/parse/document.py",
            "oak/parse/grouping.py",
            "oak/render/json_ld/document.py",
            "oak/render/oak/arrangement.py",
        }
    ),
    "BUILT_IN_INSTRUCTIONS": frozenset(
        {
            "oak/node/interpretation.py",
            "oak/parse/data.py",
        }
    ),
}

_SYMBOL_OWNERS = {
    "PART_ORDER": "oak/node/structure.py",
    "BUILT_IN_INSTRUCTIONS": "oak/node/interpretation.py",
}

ImportReference = tuple[
    str,
    tuple[str, ...],
    int,
]


def validate_architecture() -> None:
    """Verify dependency direction, exports, and obsolete implementation."""
    _validate_guard_independence()
    _validate_dependency_direction()
    _validate_leaf_imports()
    _validate_private_parser_imports()
    _validate_explicit_exports()
    _validate_initializer_purity()
    _validate_obsolete_paths_and_imports()
    _validate_cleanup_tokens()
    _validate_shared_symbol_ownership()
    _validate_no_pytest_dependency()


def _python_files(
    directory: Path,
) -> Iterator[Path]:
    if not directory.exists():
        return

    yield from sorted(
        directory.rglob("*.py")
    )


def _repository_python_files() -> Iterator[Path]:
    for name in (
        "oak",
        "build",
        "examples",
    ):
        yield from _python_files(
            ROOT / name
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


def _relative_path(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def _module_name(
    path: Path,
) -> str:
    parts = list(
        path.relative_to(
            ROOT
        ).with_suffix("").parts
    )

    if parts[-1] == "__init__":
        parts.pop()

    return ".".join(parts)


def _package_name(
    path: Path,
) -> str:
    module = _module_name(path)

    if path.name == "__init__.py":
        return module

    return module.rpartition(".")[0]


def _resolve_from_module(
    path: Path,
    node: ast.ImportFrom,
) -> str:
    if node.level == 0:
        return node.module or ""

    package = _package_name(path)
    package_parts = (
        package.split(".")
        if package
        else []
    )
    parent_count = node.level - 1

    if parent_count > len(package_parts):
        raise RuntimeError(
            f"{_relative_path(path)}:{node.lineno} "
            "has a relative import above the repository package"
        )

    base = package_parts[
        : len(package_parts) - parent_count
    ]

    if node.module is not None:
        base.extend(
            node.module.split(".")
        )

    return ".".join(base)


def _import_references(
    path: Path,
) -> Iterator[ImportReference]:
    for node in ast.walk(
        _syntax_tree(path)
    ):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield (
                    alias.name,
                    (),
                    node.lineno,
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            yield (
                _resolve_from_module(
                    path,
                    node,
                ),
                tuple(
                    alias.name
                    for alias in node.names
                ),
                node.lineno,
            )


def _import_targets(
    module: str,
    names: tuple[str, ...],
) -> Iterator[str]:
    if module:
        yield module

    for name in names:
        if name == "*":
            continue

        yield (
            f"{module}.{name}"
            if module
            else name
        )


def _matches_prefix(
    module: str,
    prefix: str,
) -> bool:
    return (
        module == prefix
        or module.startswith(
            prefix + "."
        )
    )


def _matching_target(
    module: str,
    names: tuple[str, ...],
    prefixes: Iterable[str],
) -> str | None:
    for target in _import_targets(
        module,
        names,
    ):
        for prefix in prefixes:
            if _matches_prefix(
                target,
                prefix,
            ):
                return target

    return None


def _reject_dependencies(
    paths: Iterable[Path],
    prefixes: tuple[str, ...],
    relationship: str,
) -> None:
    for path in paths:
        for (
            module,
            names,
            line,
        ) in _import_references(path):
            matched = _matching_target(
                module,
                names,
                prefixes,
            )

            if matched is None:
                continue

            raise RuntimeError(
                f"{_relative_path(path)}:{line} "
                f"violates {relationship}: {matched}"
            )


def _node_model_files() -> Iterator[Path]:
    validation = (
        ROOT
        / "oak"
        / "node"
        / "validation"
    )

    for path in _python_files(
        ROOT / "oak" / "node"
    ):
        if (
            path == validation
            or validation in path.parents
        ):
            continue

        yield path


def _validate_dependency_direction() -> None:
    _reject_dependencies(
        _python_files(
            ROOT / "oak" / "vocabulary"
        ),
        ("oak.node",),
        "oak.vocabulary must not import oak.node",
    )
    _reject_dependencies(
        _node_model_files(),
        (
            "oak.parse",
            "oak.render",
            "oak.resolve",
            "oak.execute",
        ),
        (
            "node model modules must not import "
            "parsing, rendering, resolution, or execution"
        ),
    )
    _reject_dependencies(
        _python_files(
            ROOT
            / "oak"
            / "node"
            / "validation"
        ),
        (
            "oak.parse",
            "oak.render",
            "oak.resolve",
            "oak.execute",
        ),
        (
            "node validation must not import "
            "parsing, rendering, resolution, or execution"
        ),
    )
    _reject_dependencies(
        _python_files(
            ROOT / "oak" / "parse"
        ),
        ("oak.render",),
        "parsing must not import an OAK renderer",
    )
    _reject_dependencies(
        _python_files(
            ROOT / "oak" / "render"
        ),
        ("oak.parse",),
        "OAK and JSON-LD rendering must not import the parser",
    )
    _reject_dependencies(
        _python_files(
            ROOT / "oak" / "resolve"
        ),
        ("oak.execute",),
        "resolution must not import execution",
    )


def _is_package(
    module: str,
) -> bool:
    return (
        ROOT.joinpath(
            *module.split(".")
        )
        / "__init__.py"
    ).is_file()


def _is_submodule(
    module: str,
    name: str,
) -> bool:
    package = ROOT.joinpath(
        *module.split(".")
    )
    entries = {
        entry.name
        for entry in package.iterdir()
    }

    return f"{name}.py" in entries or (
        name in entries
        and (
            package / name / "__init__.py"
        ).is_file()
    )


def _imports_barrel(
    module: str,
    names: tuple[str, ...],
) -> bool:
    if module == "oak":
        return True

    if not _matches_prefix(
        module,
        "oak",
    ) or not _is_package(module):
        return False

    return not names or any(
        not _is_submodule(
            module,
            name,
        )
        for name in names
    )


def _validate_leaf_imports() -> None:
    root_init = (
        ROOT
        / "oak"
        / "__init__.py"
    )

    for path in _python_files(
        ROOT / "oak"
    ):
        if path == root_init:
            continue

        for (
            module,
            names,
            line,
        ) in _import_references(path):
            if not _imports_barrel(
                module,
                names,
            ):
                continue

            raise RuntimeError(
                f"{_relative_path(path)}:{line} "
                f"imports through the package barrel {module}"
            )


def _validate_private_parser_imports() -> None:
    paths = (
        *tuple(
            _python_files(
                ROOT / "oak" / "execute"
            )
        ),
        *tuple(
            _python_files(
                ROOT / "build" / "checks"
            )
        ),
    )

    for path in paths:
        for (
            module,
            names,
            line,
        ) in _import_references(path):
            if not _matches_prefix(
                module,
                "oak.parse",
            ):
                continue

            module_suffix = module.split(".")[2:]
            private = [
                name
                for name in names
                if name.startswith("_")
            ]
            private.extend(
                part
                for part in module_suffix
                if part.startswith("_")
            )

            if not private:
                continue

            raise RuntimeError(
                f"{_relative_path(path)}:{line} "
                "imports private parser names: "
                + ", ".join(private)
            )


def _export_value(
    statement: ast.stmt,
) -> ast.expr | None:
    if isinstance(
        statement,
        ast.Assign,
    ):
        targets = tuple(
            statement.targets
        )
        value = statement.value

    elif isinstance(
        statement,
        ast.AnnAssign,
    ):
        targets = (
            statement.target,
        )
        value = statement.value

    else:
        return None

    if any(
        isinstance(target, ast.Name)
        and target.id == "__all__"
        for target in targets
    ):
        return value

    return None


def _all_assignments(
    tree: ast.Module,
) -> tuple[ast.expr, ...]:
    values: list[ast.expr] = []

    for statement in tree.body:
        if (
            isinstance(
                statement,
                ast.AugAssign,
            )
            and isinstance(
                statement.target,
                ast.Name,
            )
            and statement.target.id
            == "__all__"
        ):
            raise RuntimeError(
                "__all__ must not use augmented assignment"
            )

        value = _export_value(
            statement
        )

        if value is not None:
            values.append(value)

    return tuple(values)


def _literal_exports(
    path: Path,
    *,
    required: bool,
) -> tuple[str, ...] | None:
    assignments = _all_assignments(
        _syntax_tree(path)
    )

    if not assignments:
        if required:
            raise RuntimeError(
                f"{_relative_path(path)} "
                "does not define explicit __all__"
            )

        return None

    if len(assignments) != 1:
        raise RuntimeError(
            f"{_relative_path(path)} "
            "defines __all__ more than once"
        )

    try:
        value = ast.literal_eval(
            assignments[0]
        )
    except (
        ValueError,
        TypeError,
    ) as error:
        raise RuntimeError(
            f"{_relative_path(path)} "
            "computes __all__ instead of using one literal"
        ) from error

    if (
        not isinstance(
            value,
            (
                tuple,
                list,
            ),
        )
        or not all(
            isinstance(name, str)
            for name in value
        )
    ):
        raise RuntimeError(
            f"{_relative_path(path)} "
            "__all__ must be one literal sequence of strings"
        )

    exports = tuple(value)

    if len(exports) != len(
        set(exports)
    ):
        raise RuntimeError(
            f"{_relative_path(path)} "
            "__all__ contains duplicate names"
        )

    return exports


def _validate_explicit_exports() -> None:
    for path in _python_files(
        ROOT / "oak"
    ):
        _literal_exports(
            path,
            required=path.name == "__init__.py",
        )

        for node in ast.walk(
            _syntax_tree(path)
        ):
            if not isinstance(
                node,
                ast.ImportFrom,
            ):
                continue

            if any(
                alias.name == "*"
                for alias in node.names
            ):
                raise RuntimeError(
                    f"{_relative_path(path)}:{node.lineno} "
                    "uses a wildcard import"
                )

    root_exports = _literal_exports(
        ROOT / "oak" / "__init__.py",
        required=True,
    )

    if root_exports is None:
        raise RuntimeError(
            "oak/__init__.py has no explicit exports"
        )

    actual = tuple(
        sorted(root_exports)
    )
    expected = tuple(
        sorted(_EXPECTED_ROOT_EXPORTS)
    )

    if actual != expected:
        missing = sorted(
            set(expected)
            - set(actual)
        )
        unknown = sorted(
            set(actual)
            - set(expected)
        )
        raise RuntimeError(
            "root exports differ; "
            f"missing={missing} unknown={unknown}"
        )


def _validate_initializer_purity() -> None:
    for path in _python_files(
        ROOT / "oak"
    ):
        if path.name != "__init__.py":
            continue

        for index, statement in enumerate(
            _syntax_tree(path).body
        ):
            if isinstance(
                statement,
                (
                    ast.Import,
                    ast.ImportFrom,
                ),
            ):
                continue

            if (
                index == 0
                and isinstance(
                    statement,
                    ast.Expr,
                )
                and isinstance(
                    statement.value,
                    ast.Constant,
                )
                and isinstance(
                    statement.value.value,
                    str,
                )
            ):
                continue

            if _export_value(statement) is not None:
                continue

            raise RuntimeError(
                f"{_relative_path(path)}:{statement.lineno} "
                "holds logic in a package initializer"
            )


def _validate_guard_independence() -> None:
    for (
        module,
        names,
        line,
    ) in _import_references(
        _ARCHITECTURE_PATH
    ):
        matched = _matching_target(
            module,
            names,
            (
                "oak",
                "build",
            ),
        )

        if matched is None:
            continue

        raise RuntimeError(
            "build/checks/architecture.py:"
            f"{line} imports product module {matched}"
        )


def _validate_obsolete_paths_and_imports() -> None:
    present = [
        relative
        for relative in _OBSOLETE_MODULE_PATHS
        if (
            ROOT / relative
        ).exists()
    ]

    if present:
        raise RuntimeError(
            "obsolete monolithic modules remain: "
            + ", ".join(present)
        )

    for path in _repository_python_files():
        if path == _ARCHITECTURE_PATH:
            continue

        source = path.read_text(
            encoding="utf-8"
        )

        for relative in _OBSOLETE_MODULE_PATHS:
            if relative in source:
                raise RuntimeError(
                    f"{_relative_path(path)} "
                    f"contains obsolete path {relative}"
                )

        for (
            module,
            names,
            line,
        ) in _import_references(path):
            matched = _matching_target(
                module,
                names,
                _OBSOLETE_IMPORTS,
            )

            if matched is None:
                continue

            raise RuntimeError(
                f"{_relative_path(path)}:{line} "
                f"imports obsolete module {matched}"
            )


def _validate_cleanup_tokens() -> None:
    for path in _repository_python_files():
        if path == _ARCHITECTURE_PATH:
            continue

        source = path.read_text(
            encoding="utf-8"
        )

        for token in _FORBIDDEN_CLEANUP_TOKENS:
            if token not in source:
                continue

            raise RuntimeError(
                f"{_relative_path(path)} "
                f"contains obsolete refactor token {token!r}"
            )


def _assigned_names(
    path: Path,
) -> set[str]:
    names: set[str] = set()

    for statement in _syntax_tree(path).body:
        targets: tuple[ast.expr, ...] = ()

        if isinstance(
            statement,
            ast.Assign,
        ):
            targets = tuple(
                statement.targets
            )

        elif isinstance(
            statement,
            ast.AnnAssign,
        ):
            targets = (
                statement.target,
            )

        for target in targets:
            if isinstance(
                target,
                ast.Name,
            ):
                names.add(
                    target.id
                )

    return names


def _validate_shared_symbol_ownership() -> None:
    oak_files = tuple(
        _python_files(
            ROOT / "oak"
        )
    )

    for (
        symbol,
        expected_locations,
    ) in _SYMBOL_LOCATIONS.items():
        actual_locations = frozenset(
            _relative_path(path)
            for path in oak_files
            if symbol in path.read_text(
                encoding="utf-8"
            )
        )

        if actual_locations != expected_locations:
            raise RuntimeError(
                f"{symbol} locations differ; "
                f"expected={sorted(expected_locations)} "
                f"actual={sorted(actual_locations)}"
            )

        owners = [
            _relative_path(path)
            for path in oak_files
            if symbol in _assigned_names(path)
        ]
        expected_owner = _SYMBOL_OWNERS[
            symbol
        ]

        if owners != [
            expected_owner
        ]:
            raise RuntimeError(
                f"{symbol} owners differ; "
                f"expected={[expected_owner]} "
                f"actual={owners}"
            )


def _validate_no_pytest_dependency() -> None:
    for path in _python_files(
        ROOT / "build" / "checks"
    ):
        for (
            module,
            names,
            line,
        ) in _import_references(path):
            matched = _matching_target(
                module,
                names,
                ("pytest",),
            )

            if matched is None:
                continue

            raise RuntimeError(
                f"{_relative_path(path)}:{line} "
                f"requires pytest through {matched}"
            )

    if (
        ROOT / "tests"
    ).exists():
        raise RuntimeError(
            "the refactor created a tests directory"
        )



__all__ = [
    "validate_architecture",
]
