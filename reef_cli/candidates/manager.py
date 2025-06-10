import random
from reef_cli.candidates.candidate import CandidateNode

from reef_cli.candidates.filters import CandidateFilter, PassThroughFilter
from reef_cli.candidates.scorers import CandidateScorer, AllScorer


class CandidateManager:
    def __init__(self, candidates: list[CandidateNode], filters: list[CandidateFilter], scorers: list[CandidateScorer]) -> None:
        self.candidates = candidates
        self.scorers = scorers
        self.filters = filters
        self.scored: list[tuple["CandidateNode", int]] = []
        self.normalised: list[tuple["CandidateNode", float]] = []

    def filter(self) -> "CandidateManager":
        for f in self.filters:
            self.candidates = filter(f, self.candidates)
        return self

    def _score_one(self, candidate: CandidateNode) -> int:
        return 1 + sum(scorer(candidate) for scorer in self.scorers)

    def score(self) -> "CandidateManager":
        self.scored = [(cand, self._score_one(cand)) for cand in self.candidates]
        return self

    def normalise(self) -> "CandidateManager":
        total = sum(score for _, score in self.scored)
        self.normalised = [(cand, score / total) for cand, score in self.scored]
        return self

    def sample_one(self) -> "CandidateManager":
        weights = [weight for _, weight in self.normalised]
        candidates = [cand for cand, _ in self.normalised]
        return random.choices(candidates, weights=weights, k=1)[0]

    @classmethod
    def from_nothing(cls, candidates: list[CandidateNode]) -> "CandidateManager":
        """Dummy function to allow me to link code together."""
        return cls(
            candidates=candidates,
            filters=[PassThroughFilter()],
            scorers=[AllScorer(weight=1)]
        )
