"""Text shapes, one module each."""

from oak.vocabulary.text.dotted_path import DottedPath
from oak.vocabulary.text.non_blank_line import NonBlankLine
from oak.vocabulary.text.placeholder import Placeholder
from oak.vocabulary.text.process_name import ProcessName
from oak.vocabulary.text.regex_pattern import RegexPattern
from oak.vocabulary.text.slug_id import SlugId
from oak.vocabulary.text.target_path import TargetPath
from oak.vocabulary.text.value_reference import ValueReference

__all__ = [
    "DottedPath",
    "NonBlankLine",
    "Placeholder",
    "ProcessName",
    "RegexPattern",
    "SlugId",
    "TargetPath",
    "ValueReference",
]
