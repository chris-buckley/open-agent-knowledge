"""Public validation rules and compact authoring guidance."""

from oak.rules.guidance import AUTHORING_GUIDANCE
from oak.rules.model import AuthoringRule, GuidanceRule
from oak.rules.validation import RULES, RULES_BY_CODE, rule_error

__all__ = [
    "AUTHORING_GUIDANCE",
    "AuthoringRule",
    "GuidanceRule",
    "RULES",
    "RULES_BY_CODE",
    "rule_error",
]
