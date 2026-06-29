"""Aggregation strategies: collapse per-reference similarities into one score.

A question may have many reference paths. After comparing the candidate against
each, we aggregate the per-reference similarities into a single score in
``[0, 1]``. ``MAX`` (the default) answers "did it resemble *a* good path?".
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Aggregation(Protocol):
    """Collapse a non-empty sequence of similarities into one score in [0, 1]."""

    name: str

    def __call__(self, scores: Sequence[float]) -> float: ...


class _Max:
    name = "max"

    def __call__(self, scores: Sequence[float]) -> float:
        return max(scores)


class _Mean:
    name = "mean"

    def __call__(self, scores: Sequence[float]) -> float:
        return sum(scores) / len(scores)


class TopKMean:
    """Mean of the ``k`` highest similarities (robust to weak references).

    If ``k`` exceeds the number of references, all are used.
    """

    def __init__(self, k: int) -> None:
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k = k
        self.name = f"top{k}_mean"

    def __call__(self, scores: Sequence[float]) -> float:
        top = sorted(scores, reverse=True)[: self.k]
        return sum(top) / len(top)


#: Best-reference match (default). Monotonic: adding references never lowers it.
MAX: Aggregation = _Max()
#: Average similarity across all references.
MEAN: Aggregation = _Mean()
