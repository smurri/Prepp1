"""In-memory, thread-safe reference store.

Maps ``question_id -> {reference_id: Trace}``. Reference ids are monotonic
integers, unique across the whole store, assigned under a lock. This is the
single source of truth; the engine reads snapshots from it and never mutates a
stored :class:`Trace` (traces are frozen anyway).
"""

from __future__ import annotations

import threading
from itertools import count

from .models import Trace


class ReferenceStore:
    """Holds reference paths grouped by question id."""

    def __init__(self) -> None:
        self._data: dict[str, dict[int, Trace]] = {}
        self._ids = count(1)
        self._lock = threading.Lock()

    def add(self, question_id: str, trace: Trace) -> int:
        """Store ``trace`` under ``question_id`` and return its new id."""
        with self._lock:
            ref_id = next(self._ids)
            self._data.setdefault(question_id, {})[ref_id] = trace
            return ref_id

    def has_question(self, question_id: str) -> bool:
        with self._lock:
            return question_id in self._data

    def snapshot(self, question_id: str) -> list[tuple[int, Trace]]:
        """Return a stable ``(id, trace)`` list for scoring (empty if unknown)."""
        with self._lock:
            return list(self._data.get(question_id, {}).items())

    def traces(self, question_id: str) -> list[Trace]:
        with self._lock:
            return list(self._data.get(question_id, {}).values())

    def remove(self, question_id: str, reference_id: int) -> bool:
        """Remove one reference; return ``True`` if it existed."""
        with self._lock:
            refs = self._data.get(question_id)
            if refs is None or reference_id not in refs:
                return False
            del refs[reference_id]
            if not refs:
                del self._data[question_id]
            return True

    def clear(self, question_id: str | None = None) -> None:
        """Clear one question's references, or the entire store."""
        with self._lock:
            if question_id is None:
                self._data.clear()
            else:
                self._data.pop(question_id, None)
