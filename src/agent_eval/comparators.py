"""Path comparators: strategies for scoring one path against one reference.

Every comparator returns a similarity in ``[0, 1]`` where ``1.0`` means
"identical path". Comparators are pluggable via the :class:`PathComparator`
protocol so callers can swap or blend strategies without touching the engine.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol, runtime_checkable

from .models import Step, Trace, to_hashable

# --- step-level similarity -------------------------------------------------

#: A function comparing two steps, returning a similarity in ``[0, 1]``.
StepSimilarity = Callable[[Step, Step], float]


def _clamp(x: float) -> float:
    """Clamp to [0,1], absorbing floating-point drift and NaN (NaN -> 0.0)."""
    if x != x:  # NaN
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def tool_match(a: Step, b: Step) -> float:
    """Default step similarity: ``1.0`` if tool names match, else ``0.0``."""
    return 1.0 if a.tool == b.tool else 0.0


def tool_and_args(tool_weight: float = 0.5):
    """Step similarity that also credits overlapping ``args``.

    Score = ``tool_weight`` * (tool match) + (1 - tool_weight) * (arg overlap),
    where arg overlap is the Jaccard index of ``(key, value)`` pairs. Returns a
    callable suitable for :class:`SequenceComparator`.
    """
    if not 0.0 <= tool_weight <= 1.0:
        raise ValueError("tool_weight must be in [0, 1]")

    def _sim(a: Step, b: Step) -> float:
        tool = 1.0 if a.tool == b.tool else 0.0
        # to_hashable() makes this robust to nested/unhashable arg values (F1).
        ka = set(to_hashable(a.args))
        kb = set(to_hashable(b.args))
        if not ka and not kb:
            args = 1.0
        else:
            union = ka | kb
            args = len(ka & kb) / len(union) if union else 1.0
        return _clamp(tool_weight * tool + (1.0 - tool_weight) * args)

    return _sim


# --- protocol --------------------------------------------------------------


@runtime_checkable
class PathComparator(Protocol):
    """Compare a candidate path to a reference path → similarity in [0, 1]."""

    name: str

    def compare(self, candidate: Trace, reference: Trace) -> float: ...


# --- implementations -------------------------------------------------------


class SequenceComparator:
    """Normalized weighted edit (Levenshtein) distance over steps (the default).

    ``similarity = 1 - edit_distance / max(len_candidate, len_reference)``.
    Order-sensitive; charges insertions, deletions, and (partial) substitutions.
    Substitution cost is ``1 - step_similarity(a, b)``.
    """

    name = "sequence_edit"

    def __init__(self, step_similarity: StepSimilarity = tool_match) -> None:
        self._sim = step_similarity

    def compare(self, candidate: Trace, reference: Trace) -> float:
        a: Sequence[Step] = candidate.steps
        b: Sequence[Step] = reference.steps
        m, n = len(a), len(b)
        if m == 0 and n == 0:
            return 1.0
        if m == 0 or n == 0:
            return 0.0
        prev = list(range(n + 1))
        for i in range(1, m + 1):
            cur = [i] + [0] * n
            ai = a[i - 1]
            for j in range(1, n + 1):
                sub_cost = 1.0 - _clamp(self._sim(ai, b[j - 1]))
                cur[j] = min(prev[j] + 1.0, cur[j - 1] + 1.0, prev[j - 1] + sub_cost)
            prev = cur
        return _clamp(1.0 - prev[n] / max(m, n))


class JaccardComparator:
    """Order-insensitive overlap of the *set* of tool names (Jaccard index)."""

    name = "jaccard"

    def compare(self, candidate: Trace, reference: Trace) -> float:
        a = set(candidate.tool_names)
        b = set(reference.tool_names)
        if not a and not b:
            return 1.0
        union = a | b
        return _clamp(len(a & b) / len(union)) if union else 1.0


class LCSComparator:
    """Longest-common-subsequence ratio over tool names (order-sensitive, gap-tolerant)."""

    name = "lcs"

    def compare(self, candidate: Trace, reference: Trace) -> float:
        a = candidate.tool_names
        b = reference.tool_names
        m, n = len(a), len(b)
        if m == 0 and n == 0:
            return 1.0
        if m == 0 or n == 0:
            return 0.0
        prev = [0] * (n + 1)
        for i in range(1, m + 1):
            cur = [0] * (n + 1)
            for j in range(1, n + 1):
                cur[j] = prev[j - 1] + 1 if a[i - 1] == b[j - 1] else max(prev[j], cur[j - 1])
            prev = cur
        return _clamp(prev[n] / max(m, n))


class CompositeComparator:
    """Weighted blend of several comparators (weights need not sum to 1)."""

    name = "composite"

    def __init__(self, parts: Sequence[tuple[PathComparator, float]]) -> None:
        if not parts:
            raise ValueError("CompositeComparator needs at least one (comparator, weight)")
        if any(w < 0 for _, w in parts):
            raise ValueError("weights must be non-negative")
        if sum(w for _, w in parts) <= 0:
            raise ValueError("at least one weight must be positive")
        self._parts = tuple(parts)

    def compare(self, candidate: Trace, reference: Trace) -> float:
        total = sum(w for _, w in self._parts)
        blended = sum(c.compare(candidate, reference) * w for c, w in self._parts) / total
        return _clamp(blended)
