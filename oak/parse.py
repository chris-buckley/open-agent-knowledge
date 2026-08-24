"""Parse one OAK text document into checked models."""

from __future__ import annotations

import csv
import html
import io
import json
import re
from dataclasses import dataclass
from typing import Literal

import yaml
from pydantic import ConfigDict, JsonValue, TypeAdapter, ValidationError

from oak.node.model import Root
from oak.render.oak.arrangement import PART_ORDER
from oak.render.oak.instructions import BUILT_IN_INSTRUCTIONS

GroupingName = Literal["xml", "markdown"]
_JSON = TypeAdapter(
    JsonValue,
    config=ConfigDict(strict=True, regex_engine="rust-regex"),
)
_SLUG = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
_PLACEHOLDER = r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*"
_ENTRY = re.compile(rf"^({_SLUG}): (.*)$")
_BLOCK = re.compile(rf"^({_SLUG}): (TEXT|JSON|CSV|YAML)<<$")
_WHERE = re.compile(rf"^- <({_PLACEHOLDER})> (.*)\.$")
_CHILD = re.compile(r"^(~{5,})node$")
_XML_ATTR = re.compile(r"\s+([A-Za-z][A-Za-z0-9_-]*)=(['\"])(.*?)\2")
_DECODER = json.JSONDecoder()


@dataclass(frozen=True, slots=True)
class ParseFailure:
    """One stable OAK parse failure."""

    code: str
    path: str
    message: str
    line: int | None = None

    def __str__(self) -> str:
        location = self.path + (
            f":{self.line}"
            if self.line is not None
            else ""
        )
        return f"[{self.code}] {location}: {self.message}"


class OakParseError(ValueError):
    """Every failure from one OAK parse."""

    code = "oak_parse_invalid"

    def __init__(self, failures: list[ParseFailure]) -> None:
        self.failures = tuple(failures)
        super().__init__("\n".join(map(str, failures)))


class _Parser:
    def __init__(
        self,
        source: str | bytes,
        grouping: GroupingName | None,
    ) -> None:
        self.failures: list[ParseFailure] = []
        self.text = (
            self._decode(source)
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .strip("\n")
        )
        self.grouping = self._grouping(grouping)

    def fail(
        self,
        code: str,
        path: str,
        message: str,
        line: int | None = None,
    ) -> None:
        self.failures.append(
            ParseFailure(
                code,
                path,
                message,
                line,
            )
        )

    def _decode(self, source: str | bytes) -> str:
        if isinstance(source, str):
            return source

        if not isinstance(source, bytes):
            self.fail(
                "invalid_source_type",
                "document",
                "source must be UTF-8 bytes or text",
            )
            return ""

        try:
            return source.decode("utf-8")
        except UnicodeDecodeError as error:
            self.fail(
                "invalid_utf8",
                "document",
                str(error),
            )
            return ""

    def _grouping(
        self,
        selected: GroupingName | None,
    ) -> GroupingName:
        if selected in ("xml", "markdown"):
            return selected

        if selected is not None:
            self.fail(
                "unknown_grouping",
                "document",
                f"unknown OAK grouping {selected}",
            )
            return "xml"

        first = self.text.lstrip().split("\n", 1)[0]
        if first == "<instructions>":
            return "xml"
        if first == "~~~~instructions":
            return "markdown"

        self.fail(
            "unknown_grouping",
            "document",
            "the first part delimiter is not xml or markdown",
            1,
        )
        return "xml"

    @staticmethod
    def _blank(
        lines: list[str],
        index: int,
    ) -> int:
        while index < len(lines) and not lines[index]:
            index += 1
        return index

    def parse(self) -> Root:
        data = (
            self._xml_node(
                self.text,
                1,
                "root",
            )
            if self.grouping == "xml"
            else self._markdown_node(
                self.text,
                1,
                "root",
            )
        )
        self._assign_ids(data)

        try:
            root = Root.model_validate(data)
        except ValidationError as error:
            root = None
            for detail in error.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ):
                path = (
                    ".".join(
                        map(
                            str,
                            detail["loc"],
                        )
                    )
                    or "root"
                )
                self.fail(
                    str(detail["type"]),
                    path,
                    detail["msg"],
                )

        if self.failures:
            raise OakParseError(self.failures)

        if root is None:
            raise RuntimeError(
                "root validation failed without an error"
            )

        return root

    def _xml_node(
        self,
        text: str,
        base: int,
        path: str,
    ) -> dict[str, object]:
        lines = text.split("\n") if text else []
        parts: dict[str, tuple[str, int]] = {}
        index = 0

        for part in PART_ORDER:
            index = self._blank(
                lines,
                index,
            )
            opening = f"<{part}>"
            closing = f"</{part}>"

            if (
                index >= len(lines)
                or lines[index] != opening
            ):
                self.fail(
                    "missing_part",
                    f"{path}.{part}",
                    f"expected {opening}",
                    base + index,
                )
                found = next(
                    (
                        item
                        for item in range(
                            index,
                            len(lines),
                        )
                        if lines[item] == opening
                    ),
                    None,
                )
                if found is None:
                    parts[part] = (
                        "",
                        base + index,
                    )
                    continue
                index = found

            end = next(
                (
                    item
                    for item in range(
                        index + 1,
                        len(lines),
                    )
                    if lines[item] == closing
                ),
                None,
            )
            if end is None:
                self.fail(
                    "unclosed_part",
                    f"{path}.{part}",
                    f"missing {closing}",
                    base + index,
                )
                end = len(lines)

            parts[part] = (
                "\n".join(
                    lines[index + 1 : end]
                ),
                base + index + 1,
            )
            index = end + 1

        children: list[dict[str, object]] = []
        index = self._blank(
            lines,
            index,
        )

        while index < len(lines):
            child_path = (
                f"{path}.children.{len(children)}"
            )

            if lines[index] != "<node>":
                self.fail(
                    "unexpected_document_text",
                    path,
                    f"unexpected line {lines[index]!r}",
                    base + index,
                )
                index += 1
                continue

            depth = 1
            end = index + 1
            while end < len(lines) and depth:
                depth += lines[end] == "<node>"
                depth -= lines[end] == "</node>"
                end += 1

            body_end = (
                end - 1
                if not depth
                else len(lines)
            )
            if depth:
                self.fail(
                    "unclosed_node",
                    child_path,
                    "missing </node>",
                    base + index,
                )

            children.append(
                self._xml_node(
                    "\n".join(
                        lines[index + 1 : body_end]
                    ),
                    base + index + 1,
                    child_path,
                )
            )
            index = self._blank(
                lines,
                end,
            )

        return self._parts(
            parts,
            children,
            path,
        )

    def _markdown_node(
        self,
        text: str,
        base: int,
        path: str,
    ) -> dict[str, object]:
        lines = text.split("\n") if text else []
        parts: dict[str, tuple[str, int]] = {}
        index = 0

        for part in PART_ORDER:
            index = self._blank(
                lines,
                index,
            )
            opening = f"~~~~{part}"

            if (
                index >= len(lines)
                or lines[index] != opening
            ):
                self.fail(
                    "missing_part",
                    f"{path}.{part}",
                    f"expected {opening}",
                    base + index,
                )
                found = next(
                    (
                        item
                        for item in range(
                            index,
                            len(lines),
                        )
                        if lines[item] == opening
                    ),
                    None,
                )
                if found is None:
                    parts[part] = (
                        "",
                        base + index,
                    )
                    continue
                index = found

            end = next(
                (
                    item
                    for item in range(
                        index + 1,
                        len(lines),
                    )
                    if lines[item] == "~~~~"
                ),
                None,
            )
            if end is None:
                self.fail(
                    "unclosed_part",
                    f"{path}.{part}",
                    "missing ~~~~",
                    base + index,
                )
                end = len(lines)

            parts[part] = (
                "\n".join(
                    lines[index + 1 : end]
                ),
                base + index + 1,
            )
            index = end + 1

        children: list[dict[str, object]] = []
        index = self._blank(
            lines,
            index,
        )

        while index < len(lines):
            child_path = (
                f"{path}.children.{len(children)}"
            )
            match = _CHILD.fullmatch(
                lines[index]
            )

            if match is None:
                self.fail(
                    "unexpected_document_text",
                    path,
                    f"unexpected line {lines[index]!r}",
                    base + index,
                )
                index += 1
                continue

            fence = match.group(1)
            end = next(
                (
                    item
                    for item in range(
                        index + 1,
                        len(lines),
                    )
                    if lines[item] == fence
                ),
                None,
            )
            if end is None:
                self.fail(
                    "unclosed_node",
                    child_path,
                    f"missing {fence}",
                    base + index,
                )
                end = len(lines)

            children.append(
                self._markdown_node(
                    "\n".join(
                        lines[index + 1 : end]
                    ),
                    base + index + 1,
                    child_path,
                )
            )
            index = self._blank(
                lines,
                end + 1,
            )

        return self._parts(
            parts,
            children,
            path,
        )

    def _xml_attrs(
        self,
        line: str,
        tag: str,
        path: str,
        number: int,
        *,
        self_closing: bool = False,
    ) -> dict[str, str]:
        prefix = f"<{tag}"
        suffix = (
            " />"
            if self_closing
            else ">"
        )

        if (
            not line.startswith(prefix)
            or not line.endswith(suffix)
        ):
            self.fail(
                "invalid_entry_delimiter",
                path,
                f"invalid {tag} delimiter",
                number,
            )
            return {}

        source = line[
            len(prefix) : -len(suffix)
        ]
        result: dict[str, str] = {}
        index = 0

        while index < len(source):
            match = _XML_ATTR.match(
                source,
                index,
            )
            if match is None:
                self.fail(
                    "invalid_attribute",
                    path,
                    (
                        "invalid attribute text "
                        f"{source[index:]!r}"
                    ),
                    number,
                )
                break

            key = match.group(1)
            if key in result:
                self.fail(
                    "duplicate_attribute",
                    path,
                    (
                        f"attribute {key} occurs "
                        "more than once"
                    ),
                    number,
                )

            result[key] = html.unescape(
                match.group(3)
            )
            index = match.end()

        return result

    def _markdown_attrs(
        self,
        line: str,
        tag: str,
        path: str,
        number: int,
    ) -> dict[str, str]:
        prefix = f"~~~{tag}"

        if not line.startswith(prefix):
            self.fail(
                "invalid_entry_delimiter",
                path,
                f"invalid {tag} delimiter",
                number,
            )
            return {}

        source = line[len(prefix) :]
        index = 0
        result: dict[str, str] = {}

        while index < len(source):
            if source[index] != ";":
                self.fail(
                    "invalid_attribute",
                    path,
                    (
                        "expected ; before "
                        f"{source[index:]!r}"
                    ),
                    number,
                )
                break

            equal = source.find(
                "=",
                index + 1,
            )
            if equal < 0:
                self.fail(
                    "invalid_attribute",
                    path,
                    "attribute has no =",
                    number,
                )
                break

            key = source[index + 1 : equal]
            if not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_-]*",
                key,
            ):
                self.fail(
                    "invalid_attribute",
                    path,
                    (
                        "invalid attribute name "
                        f"{key!r}"
                    ),
                    number,
                )
                break

            try:
                value, used = (
                    _DECODER.raw_decode(
                        source[equal + 1 :]
                    )
                )
            except json.JSONDecodeError as error:
                self.fail(
                    "invalid_attribute_value",
                    path,
                    str(error),
                    number,
                )
                break

            if not isinstance(value, str):
                self.fail(
                    "invalid_attribute_value",
                    path,
                    (
                        f"attribute {key} must be "
                        "a JSON string"
                    ),
                    number,
                )
                break

            if key in result:
                self.fail(
                    "duplicate_attribute",
                    path,
                    (
                        f"attribute {key} occurs "
                        "more than once"
                    ),
                    number,
                )

            result[key] = value
            index = equal + 1 + used

        return result

    def _attrs(
        self,
        line: str,
        tag: str,
        path: str,
        number: int,
        *,
        self_closing: bool = False,
    ) -> dict[str, str]:
        if self.grouping == "xml":
            return self._xml_attrs(
                line,
                tag,
                path,
                number,
                self_closing=self_closing,
            )

        return self._markdown_attrs(
            line,
            tag,
            path,
            number,
        )

    def _body_entries(
        self,
        text: str,
        start: int,
        tag: str,
        path: str,
    ) -> list[
        tuple[
            dict[str, str],
            str,
            int,
        ]
    ]:
        lines = text.split("\n") if text else []
        entries: list[
            tuple[
                dict[str, str],
                str,
                int,
            ]
        ] = []
        index = 0
        closing = (
            f"</{tag}>"
            if self.grouping == "xml"
            else "~~~"
        )

        while index < len(lines):
            if not lines[index]:
                index += 1
                continue

            entry_path = (
                f"{path}.{len(entries)}"
            )
            attrs = self._attrs(
                lines[index],
                tag,
                entry_path,
                start + index,
            )
            end = next(
                (
                    item
                    for item in range(
                        index + 1,
                        len(lines),
                    )
                    if lines[item] == closing
                ),
                None,
            )

            if end is None:
                self.fail(
                    "unclosed_entry",
                    entry_path,
                    f"missing {closing}",
                    start + index,
                )
                end = len(lines)

            entries.append(
                (
                    attrs,
                    "\n".join(
                        lines[index + 1 : end]
                    ),
                    start + index,
                )
            )
            index = end + 1

        return entries

    def _trigger_entries(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[
        tuple[
            dict[str, str],
            int,
        ]
    ]:
        entries = []

        for offset, line in enumerate(
            text.split("\n")
            if text
            else []
        ):
            if line:
                entry_path = (
                    f"{path}.{len(entries)}"
                )
                entries.append(
                    (
                        self._attrs(
                            line,
                            "trigger",
                            entry_path,
                            start + offset,
                            self_closing=True,
                        ),
                        start + offset,
                    )
                )

        return entries

    def _required(
        self,
        attrs: dict[str, str],
        name: str,
        path: str,
        line: int,
    ) -> str:
        if name in attrs:
            return attrs[name]

        self.fail(
            "missing_attribute",
            path,
            f"missing attribute {name}",
            line,
        )
        return "missing"

    def _json(
        self,
        source: str,
        path: str,
        line: int,
    ) -> JsonValue:
        try:
            return _JSON.validate_python(
                json.loads(source)
            )
        except (
            json.JSONDecodeError,
            ValidationError,
        ) as error:
            self.fail(
                "invalid_json_value",
                path,
                str(error),
                line,
            )
            return None

    def _instructions(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        result = []

        for offset, line in enumerate(
            text.split("\n")
            if text
            else []
        ):
            if not line:
                self.fail(
                    "blank_instruction",
                    path,
                    "an instruction line is blank",
                    start + offset,
                )
            elif line not in BUILT_IN_INSTRUCTIONS:
                result.append(
                    {
                        "part": "instructions",
                        "id": None,
                        "body": line,
                    }
                )

        return result

    def _csv_cell(
        self,
        source: str,
        path: str,
        line: int,
    ) -> JsonValue:
        try:
            value = json.loads(source)
        except json.JSONDecodeError:
            return source

        if isinstance(
            value,
            (
                list,
                dict,
            ),
        ):
            self.fail(
                "invalid_csv_cell",
                path,
                "a CSV cell must be a JSON scalar",
                line,
            )
            return source

        return value

    def _csv(
        self,
        source: str,
        path: str,
        line: int,
    ) -> JsonValue:
        try:
            rows = list(
                csv.reader(
                    io.StringIO(source)
                )
            )
        except csv.Error as error:
            self.fail(
                "invalid_csv",
                path,
                str(error),
                line,
            )
            return []

        if len(rows) < 2:
            self.fail(
                "invalid_csv",
                path,
                (
                    "CSV needs one header and "
                    "one or more data rows"
                ),
                line,
            )
            return []

        header = rows[0]
        if (
            not header
            or any(
                not name
                for name in header
            )
        ):
            self.fail(
                "invalid_csv_header",
                path,
                "CSV header names must be non-empty",
                line,
            )

        if len(set(header)) != len(header):
            self.fail(
                "duplicate_csv_column",
                path,
                "CSV header names must be unique",
                line,
            )

        result = []
        for offset, row in enumerate(
            rows[1:],
            1,
        ):
            if len(row) != len(header):
                self.fail(
                    "csv_column_mismatch",
                    (
                        f"{path}."
                        f"{offset - 1}"
                    ),
                    (
                        f"row has {len(row)} cells; "
                        f"expected {len(header)}"
                    ),
                    line + offset,
                )
                continue

            result.append(
                {
                    name: self._csv_cell(
                        cell,
                        (
                            f"{path}."
                            f"{offset - 1}."
                            f"{name}"
                        ),
                        line + offset,
                    )
                    for name, cell in zip(
                        header,
                        row,
                        strict=True,
                    )
                }
            )

        return result

    def _constants(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        lines = text.split("\n") if text else []
        result = []
        index = 0

        while index < len(lines):
            if not lines[index]:
                index += 1
                continue

            entry_path = (
                f"{path}.{len(result)}"
            )
            block = _BLOCK.fullmatch(
                lines[index]
            )

            if block:
                identifier, token = (
                    block.groups()
                )
                end = next(
                    (
                        item
                        for item in range(
                            index + 1,
                            len(lines),
                        )
                        if lines[item] == ">>"
                    ),
                    None,
                )

                if end is None:
                    self.fail(
                        "unclosed_constant_block",
                        entry_path,
                        "missing >>",
                        start + index,
                    )
                    end = len(lines)

                body = "\n".join(
                    lines[index + 1 : end]
                )
                form = token.lower()

                if form == "text":
                    value: JsonValue = body
                elif form == "json":
                    value = self._json(
                        body,
                        f"{entry_path}.value",
                        start + index + 1,
                    )
                elif form == "csv":
                    value = self._csv(
                        body,
                        f"{entry_path}.value",
                        start + index + 1,
                    )
                else:
                    try:
                        value = (
                            _JSON.validate_python(
                                yaml.safe_load(body)
                            )
                        )
                    except (
                        yaml.YAMLError,
                        ValidationError,
                    ) as error:
                        self.fail(
                            "invalid_yaml_value",
                            f"{entry_path}.value",
                            str(error),
                            start + index + 1,
                        )
                        value = None

                result.append(
                    {
                        "part": "constants",
                        "id": identifier,
                        "form": form,
                        "value": value,
                    }
                )
                index = end + 1
                continue

            inline = _ENTRY.fullmatch(
                lines[index]
            )
            if inline is None:
                self.fail(
                    "invalid_constant",
                    entry_path,
                    (
                        "invalid constant line "
                        f"{lines[index]!r}"
                    ),
                    start + index,
                )
            else:
                identifier, source = (
                    inline.groups()
                )
                result.append(
                    {
                        "part": "constants",
                        "id": identifier,
                        "value": self._json(
                            source,
                            f"{entry_path}.value",
                            start + index,
                        ),
                    }
                )

            index += 1

        return result

    def _state(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        result = []

        for offset, line in enumerate(
            text.split("\n")
            if text
            else []
        ):
            if not line:
                continue

            entry_path = (
                f"{path}.{len(result)}"
            )
            match = _ENTRY.fullmatch(line)

            if match is None:
                self.fail(
                    "invalid_state",
                    entry_path,
                    (
                        "invalid state line "
                        f"{line!r}"
                    ),
                    start + offset,
                )
                continue

            identifier, source = match.groups()
            result.append(
                {
                    "part": "state",
                    "id": identifier,
                    "value": self._json(
                        source,
                        f"{entry_path}.value",
                        start + offset,
                    ),
                }
            )

        return result

    @staticmethod
    def _details(source: str) -> list[str]:
        result = []
        index = 0
        start = 0
        tick = False

        while index < len(source):
            if source[index] == "`":
                tick = not tick
            elif (
                not tick
                and source.startswith(
                    "; ",
                    index,
                )
            ):
                result.append(
                    source[start:index]
                )
                index += 2
                start = index
                continue

            index += 1

        return [
            *result,
            source[start:],
        ]

    def _scalars(
        self,
        source: str,
        path: str,
        line: int,
    ) -> list[object]:
        values = re.findall(
            r"`([^`]*)`",
            source,
        )

        if not values:
            self.fail(
                "invalid_scalar_list",
                path,
                (
                    "expected one or more "
                    "backtick values"
                ),
                line,
            )

        result = []
        for value in values:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value

            result.append(
                value
                if isinstance(
                    parsed,
                    (
                        list,
                        dict,
                        type(None),
                    ),
                )
                else parsed
            )

        return result

    def _bound(
        self,
        source: str,
        path: str,
        line: int,
    ) -> object:
        match = re.fullmatch(
            rf"<({_PLACEHOLDER})>",
            source,
        )

        if match:
            return match.group(1)

        try:
            value = json.loads(source)
        except json.JSONDecodeError as error:
            self.fail(
                "invalid_bound",
                path,
                str(error),
                line,
            )
            return 0

        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                (
                    int,
                    float,
                ),
            )
        ):
            self.fail(
                "invalid_bound",
                path,
                (
                    "a bound must be a number "
                    "or placeholder"
                ),
                line,
            )
            return 0

        return value

    def _constraint(
        self,
        source: str,
        path: str,
        line: int,
    ) -> dict[str, object] | None:
        if source == "is non-empty":
            return {
                "kind": "non_empty",
            }

        if source == "is one line":
            return {
                "kind": "lines",
                "min": 1,
                "max": 1,
            }

        match = re.fullmatch(
            (
                "is "
                "(string|integer|number|boolean|"
                "quantity|datetime|uri|path)"
            ),
            source,
        )
        if match:
            return {
                "kind": "type",
                "of": match.group(1),
            }

        if source.startswith("is one of "):
            return {
                "kind": "one_of",
                "values": self._scalars(
                    source[10:],
                    path,
                    line,
                ),
            }

        match = re.fullmatch(
            r"matches `([^`]*)`",
            source,
        )
        if match:
            return {
                "kind": "regex",
                "pattern": match.group(1),
            }

        match = re.fullmatch(
            r"is at most ([0-9]+) characters",
            source,
        )
        if match:
            return {
                "kind": "max_chars",
                "n": int(match.group(1)),
            }

        match = re.fullmatch(
            r"has ([0-9]+) lines",
            source,
        )
        if match:
            value = int(match.group(1))
            return {
                "kind": "lines",
                "min": value,
                "max": value,
            }

        match = re.fullmatch(
            (
                r"has ([0-9]+) to "
                r"([0-9]+) lines"
            ),
            source,
        )
        if match:
            return {
                "kind": "lines",
                "min": int(match.group(1)),
                "max": int(match.group(2)),
            }

        match = re.fullmatch(
            r"has at most ([0-9]+) lines",
            source,
        )
        if match:
            return {
                "kind": "lines",
                "max": int(match.group(1)),
            }

        match = re.fullmatch(
            r"has at least ([0-9]+) lines",
            source,
        )
        if match:
            return {
                "kind": "lines",
                "min": int(match.group(1)),
            }

        match = re.fullmatch(
            (
                "is a list of "
                "(string|integer|number|boolean|"
                "quantity|datetime|uri|path) "
                r"joined by `([^`]*)`"
            ),
            source,
        )
        if match:
            return {
                "kind": "list_of",
                "item": match.group(1),
                "separator": match.group(2),
            }

        for prefix, kind in (
            (
                "is at least ",
                "at_least",
            ),
            (
                "is at most ",
                "at_most",
            ),
        ):
            if source.startswith(prefix):
                return {
                    "kind": kind,
                    "value": self._bound(
                        source[len(prefix) :],
                        path,
                        line,
                    ),
                }

        return None

    def _where(
        self,
        source: str,
        path: str,
        line: int,
    ) -> dict[str, object] | None:
        match = _WHERE.fullmatch(source)

        if match is None:
            self.fail(
                "invalid_where",
                path,
                (
                    "invalid WHERE line "
                    f"{source!r}"
                ),
                line,
            )
            return None

        placeholder, details = match.groups()
        constraints = []
        examples = []
        description = None
        segments = self._details(details)

        for index, segment in enumerate(
            segments
        ):
            example = re.fullmatch(
                r"(.*) \(e\.g\. (.*)\)",
                segment,
            )
            constraint_source = (
                example.group(1)
                if example
                else segment
            )

            if example:
                examples = self._scalars(
                    example.group(2),
                    f"{path}.examples",
                    line,
                )

            constraint = self._constraint(
                constraint_source,
                (
                    f"{path}.constraints."
                    f"{len(constraints)}"
                ),
                line,
            )

            if (
                constraint is not None
                and description is None
            ):
                constraints.append(constraint)
            else:
                description = "; ".join(
                    segments[index:]
                )
                break

        if not constraints:
            self.fail(
                "missing_where_constraint",
                path,
                (
                    "a WHERE line needs at "
                    "least one constraint"
                ),
                line,
            )

        result: dict[str, object] = {
            "placeholder": placeholder,
            "constraints": constraints,
        }
        if examples:
            result["examples"] = examples
        if description is not None:
            result["description"] = description

        return result

    def _schema_body(
        self,
        body: str,
        path: str,
        line: int,
    ) -> tuple[
        str,
        list[dict[str, object]],
    ]:
        marker = body.rfind("\n\nWHERE:")

        if marker < 0:
            self.fail(
                "missing_where_heading",
                path,
                (
                    "schema body needs a "
                    "WHERE heading"
                ),
                line,
            )
            return body, []

        source = body[marker + 8 :]
        if source.startswith("\n"):
            source = source[1:]

        where = []
        where_line = (
            line
            + body[:marker].count("\n")
            + 2
        )

        for offset, item in enumerate(
            source.split("\n")
            if source
            else []
        ):
            if item:
                parsed = self._where(
                    item,
                    (
                        f"{path}.where."
                        f"{len(where)}"
                    ),
                    where_line + offset,
                )
                if parsed is not None:
                    where.append(parsed)

        return body[:marker], where

    def _schemas(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        result = []

        for attrs, body, line in self._body_entries(
            text,
            start,
            "schema",
            path,
        ):
            entry_path = (
                f"{path}.{len(result)}"
            )
            template, where = self._schema_body(
                body,
                entry_path,
                line + 1,
            )
            schema: dict[str, object] = {
                "part": "schemas",
                "id": self._required(
                    attrs,
                    "id",
                    entry_path,
                    line,
                ),
                "template": template,
                "where": where,
            }

            for name in (
                "name",
                "purpose",
            ):
                if name in attrs:
                    schema[name] = attrs[name]

            result.append(schema)

        return result

    def _value(
        self,
        source: str,
        path: str,
        line: int,
    ) -> dict[str, object]:
        if source.startswith("$constant."):
            return {
                "source": "constant",
                "constant": source[10:],
            }

        if source.startswith("$state."):
            return {
                "source": "state",
                "state": source[7:],
            }

        if source.startswith("$interface."):
            parts = source[11:].split(".")
            if len(parts) == 2:
                return {
                    "source": "interface",
                    "interface": parts[0],
                    "placeholder": parts[1],
                }

            self.fail(
                "invalid_value_reference",
                path,
                (
                    "invalid interface reference "
                    f"{source!r}"
                ),
                line,
            )
            return {
                "source": "interface",
                "interface": "missing",
                "placeholder": "MISSING",
            }

        if source.startswith("$"):
            return {
                "source": "binding",
                "binding": source[1:],
            }

        return {
            "source": "literal",
            "value": self._json(
                source,
                f"{path}.value",
                line,
            ),
        }

    @staticmethod
    def _can_value(source: str) -> bool:
        if re.fullmatch(
            (
                rf"\$constant\.{_SLUG}|"
                rf"\$state\.{_SLUG}|"
                rf"\${_PLACEHOLDER}"
            ),
            source,
        ):
            return True

        if re.fullmatch(
            (
                rf"\$interface\.{_SLUG}\."
                rf"{_PLACEHOLDER}"
            ),
            source,
        ):
            return True

        try:
            json.loads(source)
            return True
        except json.JSONDecodeError:
            return False

    def _condition(
        self,
        source: str,
        path: str,
        line: int,
    ) -> dict[str, object]:
        candidates = []

        for separator, operator in (
            (
                " does not equal ",
                "not_equals",
            ),
            (
                " equals ",
                "equals",
            ),
        ):
            start = 0
            while (
                index := source.find(
                    separator,
                    start,
                )
            ) >= 0:
                left = source[:index]
                right = source[
                    index + len(separator) :
                ]

                if (
                    self._can_value(left)
                    and self._can_value(right)
                ):
                    candidates.append(
                        (
                            left,
                            operator,
                            right,
                        )
                    )

                start = index + 1

        if len(candidates) != 1:
            self.fail(
                "invalid_condition",
                path,
                (
                    "condition must contain one "
                    "unambiguous comparison"
                ),
                line,
            )
            return {
                "left": {
                    "source": "literal",
                    "value": None,
                },
                "operator": "equals",
                "right": {
                    "source": "literal",
                    "value": None,
                },
            }

        left, operator, right = candidates[0]
        return {
            "left": self._value(
                left,
                f"{path}.left",
                line,
            ),
            "operator": operator,
            "right": self._value(
                right,
                f"{path}.right",
                line,
            ),
        }

    def _indent(
        self,
        line: str,
        path: str,
        number: int,
    ) -> tuple[int, str]:
        leading = line[
            : len(line) - len(line.lstrip())
        ]
        if "\t" in leading:
            self.fail(
                "invalid_indent",
                path,
                "indentation must use spaces",
                number,
            )

        source = line.lstrip(" ")
        return (
            len(line) - len(source),
            source,
        )

    def _binding(
        self,
        source: str,
        path: str,
        line: int,
    ) -> dict[str, object]:
        if " = " not in source:
            self.fail(
                "invalid_binding",
                path,
                "binding must contain =",
                line,
            )
            return {
                "placeholder": "MISSING",
                "value": {
                    "source": "literal",
                    "value": None,
                },
            }

        placeholder, value = source.split(
            " = ",
            1,
        )
        return {
            "placeholder": placeholder,
            "value": self._value(
                value,
                f"{path}.value",
                line,
            ),
        }

    def _steps(
        self,
        lines: list[str],
        index: int,
        indent: int,
        path: str,
        start: int,
    ) -> tuple[
        list[dict[str, object]],
        int,
    ]:
        result: list[dict[str, object]] = []

        while index < len(lines):
            if not lines[index]:
                index += 1
                continue

            current, source = self._indent(
                lines[index],
                f"{path}.{len(result)}",
                start + index,
            )

            if (
                current < indent
                or (
                    current == indent
                    and source == "ELSE:"
                )
            ):
                break

            if current > indent:
                self.fail(
                    "unexpected_indent",
                    f"{path}.{len(result)}",
                    (
                        f"expected {indent} spaces; "
                        f"got {current}"
                    ),
                    start + index,
                )
                index += 1
                continue

            step_path = (
                f"{path}.{len(result)}"
            )
            number = start + index

            if source.startswith("ACT "):
                step: dict[str, object] = {
                    "kind": "act",
                    "instruction": source[4:],
                }
                index += 1
                inputs = []
                outputs = []

                if index < len(lines):
                    child_indent, child = (
                        self._indent(
                            lines[index],
                            step_path,
                            start + index,
                        )
                    )

                    if (
                        child_indent == indent + 2
                        and child == "INPUTS:"
                    ):
                        index += 1

                        while index < len(lines):
                            (
                                binding_indent,
                                binding,
                            ) = self._indent(
                                lines[index],
                                step_path,
                                start + index,
                            )

                            if (
                                binding_indent
                                != indent + 4
                            ):
                                break

                            inputs.append(
                                self._binding(
                                    binding,
                                    (
                                        f"{step_path}."
                                        "inputs."
                                        f"{len(inputs)}"
                                    ),
                                    start + index,
                                )
                            )
                            index += 1

                if index < len(lines):
                    child_indent, child = (
                        self._indent(
                            lines[index],
                            step_path,
                            start + index,
                        )
                    )

                    if (
                        child_indent == indent + 2
                        and child.startswith(
                            "OUTPUTS: "
                        )
                    ):
                        outputs = [
                            item.strip()
                            for item in child[9:].split(
                                ","
                            )
                            if item.strip()
                        ]
                        index += 1

                if inputs:
                    step["inputs"] = inputs
                if outputs:
                    step["outputs"] = outputs

                result.append(step)
                continue

            if (
                source.startswith("SET state.")
                and " = " in source
            ):
                target, value = source[10:].split(
                    " = ",
                    1,
                )
                result.append(
                    {
                        "kind": "set",
                        "state": target,
                        "value": self._value(
                            value,
                            f"{step_path}.value",
                            number,
                        ),
                    }
                )
                index += 1
                continue

            if (
                source.startswith(
                    "EMIT interface."
                )
                and source.endswith(":")
            ):
                interface = source[15:-1]
                bindings = []
                index += 1

                while index < len(lines):
                    (
                        binding_indent,
                        binding,
                    ) = self._indent(
                        lines[index],
                        step_path,
                        start + index,
                    )

                    if (
                        binding_indent
                        != indent + 2
                    ):
                        break

                    bindings.append(
                        self._binding(
                            binding,
                            (
                                f"{step_path}."
                                "bindings."
                                f"{len(bindings)}"
                            ),
                            start + index,
                        )
                    )
                    index += 1

                result.append(
                    {
                        "kind": "emit",
                        "interface": interface,
                        "bindings": bindings,
                    }
                )
                continue

            if (
                source.startswith("IF ")
                and source.endswith(":")
            ):
                condition = self._condition(
                    source[3:-1],
                    f"{step_path}.condition",
                    number,
                )
                then, index = self._steps(
                    lines,
                    index + 1,
                    indent + 2,
                    f"{step_path}.then",
                    start,
                )
                step = {
                    "kind": "if",
                    "condition": condition,
                    "then": then,
                }

                if index < len(lines):
                    (
                        else_indent,
                        else_source,
                    ) = self._indent(
                        lines[index],
                        step_path,
                        start + index,
                    )

                    if (
                        else_indent == indent
                        and else_source == "ELSE:"
                    ):
                        otherwise, index = (
                            self._steps(
                                lines,
                                index + 1,
                                indent + 2,
                                (
                                    f"{step_path}."
                                    "otherwise"
                                ),
                                start,
                            )
                        )
                        step["otherwise"] = (
                            otherwise
                        )

                result.append(step)
                continue

            if source.startswith("CALL process."):
                result.append(
                    {
                        "kind": "call",
                        "process": source[13:],
                    }
                )
                index += 1
                continue

            if source.startswith("FAIL "):
                result.append(
                    {
                        "kind": "fail",
                        "message": self._json(
                            source[5:],
                            (
                                f"{step_path}."
                                "message"
                            ),
                            number,
                        ),
                    }
                )
                index += 1
                continue

            self.fail(
                "unknown_process_step",
                step_path,
                (
                    "unknown process step "
                    f"{source!r}"
                ),
                number,
            )
            index += 1

        return result, index

    def _processes(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        result = []

        for attrs, body, line in self._body_entries(
            text,
            start,
            "process",
            path,
        ):
            entry_path = (
                f"{path}.{len(result)}"
            )
            lines = (
                body.split("\n")
                if body
                else []
            )
            steps, index = self._steps(
                lines,
                0,
                0,
                f"{entry_path}.steps",
                line + 1,
            )

            if index < len(lines):
                self.fail(
                    "unexpected_process_text",
                    entry_path,
                    (
                        "unexpected line "
                        f"{lines[index]!r}"
                    ),
                    line + index + 1,
                )

            result.append(
                {
                    "part": "processes",
                    "id": self._required(
                        attrs,
                        "id",
                        entry_path,
                        line,
                    ),
                    "name": self._required(
                        attrs,
                        "name",
                        entry_path,
                        line,
                    ),
                    "steps": steps,
                }
            )

        return result

    def _triggers(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        result = []

        for attrs, line in self._trigger_entries(
            text,
            start,
            path,
        ):
            entry_path = (
                f"{path}.{len(result)}"
            )
            trigger: dict[str, object] = {
                "part": "triggers",
                "id": self._required(
                    attrs,
                    "id",
                    entry_path,
                    line,
                ),
                "when": self._required(
                    attrs,
                    "when",
                    entry_path,
                    line,
                ),
                "process": self._required(
                    attrs,
                    "process",
                    entry_path,
                    line,
                ),
            }

            if "given" in attrs:
                trigger["given"] = (
                    self._condition(
                        attrs["given"],
                        f"{entry_path}.given",
                        line,
                    )
                )

            result.append(trigger)

        return result

    def _interfaces(
        self,
        text: str,
        start: int,
        path: str,
    ) -> list[dict[str, object]]:
        result = []

        for attrs, body, line in self._body_entries(
            text,
            start,
            "interface",
            path,
        ):
            entry_path = (
                f"{path}.{len(result)}"
            )
            interface: dict[str, object] = {
                "part": "interfaces",
                "id": self._required(
                    attrs,
                    "id",
                    entry_path,
                    line,
                ),
                "direction": self._required(
                    attrs,
                    "direction",
                    entry_path,
                    line,
                ),
                "schema": self._required(
                    attrs,
                    "schema",
                    entry_path,
                    line,
                ),
            }

            if body:
                if "\n" in body:
                    self.fail(
                        "invalid_interface_body",
                        entry_path,
                        (
                            "an interface description "
                            "must be one line"
                        ),
                        line + 1,
                    )
                interface["description"] = body

            result.append(interface)

        return result

    def _parts(
        self,
        parts: dict[str, tuple[str, int]],
        children: list[dict[str, object]],
        path: str,
    ) -> dict[str, object]:
        def get(
            name: str,
        ) -> tuple[str, int]:
            return parts.get(
                name,
                (
                    "",
                    1,
                ),
            )

        instructions, instructions_line = (
            get("instructions")
        )
        constants, constants_line = get(
            "constants"
        )
        schemas, schemas_line = get("schemas")
        state, state_line = get("state")
        triggers, triggers_line = get(
            "triggers"
        )
        processes, processes_line = get(
            "processes"
        )
        interfaces, interfaces_line = get(
            "interfaces"
        )

        return {
            "id": None,
            "instructions": self._instructions(
                instructions,
                instructions_line,
                f"{path}.instructions",
            ),
            "constants": self._constants(
                constants,
                constants_line,
                f"{path}.constants",
            ),
            "schemas": self._schemas(
                schemas,
                schemas_line,
                f"{path}.schemas",
            ),
            "state": self._state(
                state,
                state_line,
                f"{path}.state",
            ),
            "triggers": self._triggers(
                triggers,
                triggers_line,
                f"{path}.triggers",
            ),
            "processes": self._processes(
                processes,
                processes_line,
                f"{path}.processes",
            ),
            "interfaces": self._interfaces(
                interfaces,
                interfaces_line,
                f"{path}.interfaces",
            ),
            "children": children,
        }

    @staticmethod
    def _nodes(
        data: dict[str, object],
    ):
        yield data

        for child in data.get(
            "children",
            [],
        ):
            if isinstance(child, dict):
                yield from _Parser._nodes(
                    child
                )

    def _assign_ids(
        self,
        data: dict[str, object],
    ) -> None:
        used = {
            entry["id"]
            for node in self._nodes(data)
            for part in PART_ORDER
            for entry in node.get(part, [])
            if (
                isinstance(entry, dict)
                and isinstance(
                    entry.get("id"),
                    str,
                )
            )
        }
        counters = {
            "root": 0,
            "node": 0,
            "instruction": 0,
        }

        def allocate(prefix: str) -> str:
            while True:
                counters[prefix] += 1
                candidate = (
                    "root"
                    if (
                        prefix == "root"
                        and counters[prefix] == 1
                    )
                    else (
                        f"{prefix}-"
                        f"{counters[prefix]}"
                    )
                )

                if candidate not in used:
                    used.add(candidate)
                    return candidate

        for index, node in enumerate(
            self._nodes(data)
        ):
            node["id"] = allocate(
                "root"
                if index == 0
                else "node"
            )

            for instruction in node.get(
                "instructions",
                [],
            ):
                instruction["id"] = allocate(
                    "instruction"
                )


def parse_oak(
    source: str | bytes,
    *,
    grouping: GroupingName | None = None,
) -> Root:
    """Parse one OAK document and run every model and graph check."""
    return _Parser(
        source,
        grouping,
    ).parse()


def parse(
    source: str | bytes,
    *,
    grouping: GroupingName | None = None,
) -> Root:
    """Parse one OAK document."""
    return parse_oak(
        source,
        grouping=grouping,
    )


__all__ = [
    "OakParseError",
    "ParseFailure",
    "parse",
    "parse_oak",
]
