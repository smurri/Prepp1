"""Backend abstraction shared by the SQL and NoSQL mocks.

Both mock stores expose the same :class:`ReferenceBackend` interface so the UI
(and tests) can swap them freely. This file also holds the value objects and the
(de)serialization between a stored "path document" and a :class:`Trace`.

NOTE: these backends are *mocks for the demo/UI*. The core ``agent_eval`` library
remains pure and in-memory — it never imports a backend.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from ..models import Step, Trace


@dataclass(frozen=True)
class Question:
    question_id: str
    text: str
    domain: str


@dataclass(frozen=True)
class ReferencePath:
    author: str
    quality: str  # "gold" | "acceptable" | ...
    trace: Trace


@dataclass(frozen=True)
class CandidateRun:
    label: str
    note: str
    trace: Trace


# --- (de)serialization -----------------------------------------------------

def path_to_doc(trace: Trace) -> list[dict[str, Any]]:
    """Serialize a Trace into a JSON-friendly list of ``{tool, args}`` dicts."""
    return [{"tool": s.tool, "args": dict(s.args)} for s in trace.steps]


def doc_to_path(doc: Sequence[dict[str, Any]]) -> Trace:
    """Rebuild a Trace from a stored path document."""
    return Trace(steps=tuple(Step(tool=s["tool"], args=s.get("args", {})) for s in doc))


# --- backend protocol ------------------------------------------------------

@runtime_checkable
class ReferenceBackend(Protocol):
    """A read interface over stored questions, references, and candidate runs."""

    name: str

    def questions(self) -> list[Question]: ...
    def reference_paths(self, question_id: str) -> list[ReferencePath]: ...
    def candidates(self, question_id: str) -> list[CandidateRun]: ...


def hydrate(engine: Any, backend: ReferenceBackend) -> dict[str, list[int]]:
    """Load every reference from ``backend`` into an :class:`EvalEngine`.

    Returns ``{question_id: [reference_id, ...]}`` for the registered references.
    Typed as ``Any`` for the engine to avoid a circular import.
    """
    registered: dict[str, list[int]] = {}
    for q in backend.questions():
        ids = [engine.add_reference(q.question_id, ref.trace)
               for ref in backend.reference_paths(q.question_id)]
        registered[q.question_id] = ids
    return registered
