import typing as ty
from dep_graph.nodes import CandidateNode


class CandidateFilter(ty.Protocol):
    """Protocol for filters that are applied to candidates."""
    def __call__(self, candidate: CandidateNode) -> bool:
        ...

class PassThroughFilter(ty.Protocol):
    """Filter that doesn't remove any candidates."""
    def __call__(self, candidate: CandidateNode) -> bool:
        return True
