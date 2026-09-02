"""Typed target paths used by process values and steps."""

from typing import Annotated

from pydantic import AfterValidator

from oak.vocabulary import TargetPath
from oak.vocabulary.text.target_path import local_target, typed_target

ConstantTarget = Annotated[
    TargetPath,
    AfterValidator(lambda value: typed_target(value, "constant")),
]
StateTarget = Annotated[
    TargetPath,
    AfterValidator(lambda value: local_target(value, "state")),
]
InterfaceTarget = Annotated[
    TargetPath,
    AfterValidator(lambda value: local_target(value, "interface")),
]
ProcessTarget = Annotated[
    TargetPath,
    AfterValidator(lambda value: typed_target(value, "process")),
]

__all__ = [
    "ConstantTarget",
    "InterfaceTarget",
    "ProcessTarget",
    "StateTarget",
]
