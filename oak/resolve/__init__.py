"""Public resolution of reachable OAK document graphs."""

from oak.resolve.errors import ResolutionError, ResolutionFailure
from oak.resolve.graph import ResolvedGraph
from oak.resolve.resolver import (
    DocumentLoader,
    DocumentSource,
    resolve,
)

__all__ = [
    "DocumentLoader",
    "DocumentSource",
    "ResolvedGraph",
    "ResolutionError",
    "ResolutionFailure",
    "resolve",
]
