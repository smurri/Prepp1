"""Mock **NoSQL** backend: an in-memory, MongoDB-style document store.

Same seed data as the SQL mock, stored as denormalized JSON documents in
"collections" and queried with a tiny ``find()``. Demonstrates that the engine
is storage-agnostic: swap SQL for a document DB behind the same interface.
"""

from __future__ import annotations

import copy
from typing import Any

from .backend import CandidateRun, Question, ReferencePath, doc_to_path
from .seed import QUESTIONS


class _Collection:
    """A minimal document collection with a MongoDB-ish ``find``/``insert``."""

    def __init__(self) -> None:
        self._docs: list[dict[str, Any]] = []

    def insert(self, doc: dict[str, Any]) -> None:
        self._docs.append(copy.deepcopy(doc))

    def find(self, **query: Any) -> list[dict[str, Any]]:
        return [
            copy.deepcopy(d)
            for d in self._docs
            if all(d.get(k) == v for k, v in query.items())
        ]


class NoSqlBackend:
    """In-memory document-store reference backend implementing ``ReferenceBackend``."""

    name = "NoSQL (in-memory document store)"

    def __init__(self) -> None:
        self.questions_col = _Collection()
        self.references_col = _Collection()
        self.candidates_col = _Collection()
        self._load_seed()

    def _load_seed(self) -> None:
        for q in QUESTIONS:
            self.questions_col.insert(
                {"question_id": q["question_id"], "text": q["text"], "domain": q["domain"]}
            )
            for ref in q["references"]:
                self.references_col.insert(
                    {"question_id": q["question_id"], "author": ref["author"],
                     "quality": ref["quality"], "path": ref["path"]}
                )
            for cand in q["candidates"]:
                self.candidates_col.insert(
                    {"question_id": q["question_id"], "label": cand["label"],
                     "note": cand["note"], "path": cand["path"]}
                )

    def questions(self) -> list[Question]:
        docs = sorted(self.questions_col.find(), key=lambda d: d["question_id"])
        return [Question(d["question_id"], d["text"], d["domain"]) for d in docs]

    def reference_paths(self, question_id: str) -> list[ReferencePath]:
        docs = self.references_col.find(question_id=question_id)
        return [ReferencePath(d["author"], d["quality"], doc_to_path(d["path"])) for d in docs]

    def candidates(self, question_id: str) -> list[CandidateRun]:
        docs = self.candidates_col.find(question_id=question_id)
        return [CandidateRun(d["label"], d["note"], doc_to_path(d["path"])) for d in docs]
