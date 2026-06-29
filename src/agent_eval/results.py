"""Explainable result objects returned by :meth:`EvalEngine.score`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceScore:
    """How the candidate scored against one specific reference."""

    reference_id: int
    similarity: float
    reference_steps: int


@dataclass(frozen=True)
class ScoreResult:
    """The outcome of scoring a candidate path against a question's references.

    ``score`` is the aggregated similarity in ``[0, 1]``. ``breakdown`` lists the
    per-reference similarities sorted best-first, so callers can explain *why*.
    """

    score: float
    question_id: str
    comparator: str
    aggregation: str
    candidate_steps: int
    breakdown: tuple[ReferenceScore, ...]

    @property
    def best(self) -> ReferenceScore | None:
        """The single most similar reference, or ``None`` if there were none."""
        return self.breakdown[0] if self.breakdown else None

    def __float__(self) -> float:
        return self.score
