"""The public facade: :class:`EvalEngine`.

Register reference paths per question, then score new candidate paths against
them. The comparator (how two paths are compared) and the aggregation (how
per-reference scores combine) are injected here and may be overridden per call.
"""

from __future__ import annotations

from collections.abc import Iterable

from . import aggregation as _agg
from .aggregation import Aggregation
from .comparators import PathComparator, SequenceComparator
from .errors import InvalidTraceError, NoReferencesError, UnknownQuestionError
from .models import Trace
from .results import ReferenceScore, ScoreResult
from .store import ReferenceStore


class EvalEngine:
    """Scores agent execution paths against stored reference paths.

    Args:
        comparator: How to compare two paths. Defaults to
            :class:`~agent_eval.comparators.SequenceComparator` (normalized edit
            distance, order-sensitive).
        aggregation: How to collapse per-reference scores. Defaults to ``MAX``.
    """

    def __init__(
        self,
        comparator: PathComparator | None = None,
        aggregation: Aggregation | None = None,
    ) -> None:
        self._comparator: PathComparator = comparator or SequenceComparator()
        self._aggregation: Aggregation = aggregation or _agg.MAX
        self._store = ReferenceStore()

    # --- registration ------------------------------------------------------

    def add_reference(self, question_id: str, trace: Trace) -> int:
        """Register one known-good path for ``question_id``; returns its id."""
        self._require_question_id(question_id)
        self._require_trace(trace)
        return self._store.add(question_id, trace)

    def add_references(self, question_id: str, traces: Iterable[Trace]) -> list[int]:
        """Register several reference paths at once; returns their ids in order."""
        self._require_question_id(question_id)
        materialized = list(traces)
        for t in materialized:
            self._require_trace(t)
        return [self._store.add(question_id, t) for t in materialized]

    # --- inspection / lifecycle -------------------------------------------

    def references(self, question_id: str) -> list[Trace]:
        """Return the stored reference paths for a question (empty if none)."""
        return self._store.traces(question_id)

    def reference_items(self, question_id: str) -> list[tuple[int, Trace]]:
        """Return ``(reference_id, trace)`` pairs so callers can map ids back to
        :attr:`ScoreResult.breakdown` entries or to :meth:`remove_reference`."""
        return self._store.snapshot(question_id)

    def remove_reference(self, question_id: str, reference_id: int) -> bool:
        """Remove one reference; ``True`` if it existed, else ``False``."""
        return self._store.remove(question_id, reference_id)

    def clear(self, question_id: str | None = None) -> None:
        """Clear references for one question, or everything if ``None``."""
        self._store.clear(question_id)

    # --- scoring -----------------------------------------------------------

    def score(
        self,
        question_id: str,
        candidate: Trace,
        *,
        comparator: PathComparator | None = None,
        aggregation: Aggregation | None = None,
    ) -> ScoreResult:
        """Score ``candidate`` against the references for ``question_id``.

        Args:
            question_id: Must have at least one registered reference.
            candidate: The agent path to score.
            comparator: Optional per-call override of the comparator.
            aggregation: Optional per-call override of the aggregation.

        Returns:
            A :class:`ScoreResult` with the aggregated score and a per-reference
            breakdown sorted best-first.

        Raises:
            UnknownQuestionError: if ``question_id`` was never registered.
            NoReferencesError: if the question exists but has no references.
            InvalidTraceError: if ``candidate`` is not a :class:`Trace`.
        """
        self._require_question_id(question_id)
        self._require_trace(candidate)
        if not self._store.has_question(question_id):
            raise UnknownQuestionError(question_id)

        cmp = comparator or self._comparator
        agg = aggregation or self._aggregation

        refs = self._store.snapshot(question_id)
        if not refs:  # defensive: question existed but was emptied concurrently
            raise NoReferencesError(question_id)

        scored = [
            ReferenceScore(
                reference_id=ref_id,
                similarity=cmp.compare(candidate, ref_trace),
                reference_steps=len(ref_trace),
            )
            for ref_id, ref_trace in refs
        ]
        scored.sort(key=lambda r: r.similarity, reverse=True)

        final = agg([r.similarity for r in scored])
        return ScoreResult(
            score=final,
            question_id=question_id,
            comparator=cmp.name,
            aggregation=agg.name,
            candidate_steps=len(candidate),
            breakdown=tuple(scored),
        )

    # --- validation helpers ------------------------------------------------

    @staticmethod
    def _require_question_id(question_id: str) -> None:
        if not isinstance(question_id, str) or not question_id:
            raise InvalidTraceError("question_id must be a non-empty string")

    @staticmethod
    def _require_trace(trace: Trace) -> None:
        if not isinstance(trace, Trace):
            raise InvalidTraceError(f"expected a Trace, got {type(trace).__name__}")
