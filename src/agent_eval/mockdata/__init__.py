"""Mock data + mock backends for the demo and UI (not part of the core library).

Provides realistic seed data and two interchangeable mock backends — a SQL one
(in-memory SQLite) and a NoSQL one (in-memory document store) — behind the shared
:class:`ReferenceBackend` interface, plus :func:`hydrate` to load an engine.
"""

from __future__ import annotations

from .backend import (
    CandidateRun,
    Question,
    ReferenceBackend,
    ReferencePath,
    doc_to_path,
    hydrate,
    path_to_doc,
)
from .nosql_backend import NoSqlBackend
from .seed import QUESTIONS
from .sql_backend import SqlBackend

#: Convenient registry for the UI's backend picker.
BACKENDS: dict[str, type] = {
    "SQL (SQLite)": SqlBackend,
    "NoSQL (documents)": NoSqlBackend,
}

__all__ = [
    "BACKENDS",
    "CandidateRun",
    "NoSqlBackend",
    "Question",
    "QUESTIONS",
    "ReferenceBackend",
    "ReferencePath",
    "SqlBackend",
    "doc_to_path",
    "hydrate",
    "path_to_doc",
]
