import typing as ty
from reef_cli.candidates.candidate import CandidateNode


class CandidateScorer(ty.Protocol):
    """Protocol for scorer that gives candidate integer
    increase to score based on condition."""
    def __call__(self, candidate: CandidateNode) -> bool:
        ...


class AllScorer(CandidateScorer):
    """Scorer that blindly assigns weight to score of all candidates."""
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def __call__(self, candidate: CandidateNode) -> int:
        return self.weight
