import typing as ty
from reef_cli.candidates.candidate import CandidateNode


class CandidateFilter(ty.Protocol):
    """Protocol for filters that are applied to candidates."""
    def __call__(self, candidate: CandidateNode) -> bool:
        ...

class PassThroughFilter(CandidateFilter):
    """Filter that doesn't remove any candidates."""
    def __call__(self, candidate: CandidateNode) -> bool:
        return True
