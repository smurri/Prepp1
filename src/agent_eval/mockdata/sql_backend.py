"""Mock **SQL** backend backed by an in-memory SQLite database (stdlib only).

A real relational store: normalized tables, a unique index, foreign keys, and
JSON-encoded path columns. Demonstrates loading reference paths out of a SQL DB
into the eval engine — without any external dependency or real persistence.
"""

from __future__ import annotations

import json
import sqlite3

from .backend import CandidateRun, Question, ReferencePath, doc_to_path
from .seed import QUESTIONS

_SCHEMA = """
CREATE TABLE questions (
    question_id TEXT PRIMARY KEY,
    text        TEXT NOT NULL,
    domain      TEXT NOT NULL
);
CREATE TABLE reference_paths (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL REFERENCES questions(question_id),
    author      TEXT NOT NULL,
    quality     TEXT NOT NULL,
    path_json   TEXT NOT NULL
);
CREATE TABLE candidates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL REFERENCES questions(question_id),
    label       TEXT NOT NULL,
    note        TEXT NOT NULL,
    path_json   TEXT NOT NULL
);
CREATE INDEX idx_refs_q ON reference_paths(question_id);
CREATE INDEX idx_cand_q ON candidates(question_id);
"""


class SqlBackend:
    """In-memory SQLite-backed reference store implementing ``ReferenceBackend``."""

    name = "SQL (SQLite, in-memory)"

    def __init__(self) -> None:
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._load_seed()

    def _load_seed(self) -> None:
        cur = self._conn.cursor()
        for q in QUESTIONS:
            cur.execute(
                "INSERT INTO questions(question_id, text, domain) VALUES (?, ?, ?)",
                (q["question_id"], q["text"], q["domain"]),
            )
            for ref in q["references"]:
                cur.execute(
                    "INSERT INTO reference_paths(question_id, author, quality, path_json) "
                    "VALUES (?, ?, ?, ?)",
                    (q["question_id"], ref["author"], ref["quality"], json.dumps(ref["path"])),
                )
            for cand in q["candidates"]:
                cur.execute(
                    "INSERT INTO candidates(question_id, label, note, path_json) "
                    "VALUES (?, ?, ?, ?)",
                    (q["question_id"], cand["label"], cand["note"], json.dumps(cand["path"])),
                )
        self._conn.commit()

    def questions(self) -> list[Question]:
        rows = self._conn.execute(
            "SELECT question_id, text, domain FROM questions ORDER BY question_id"
        ).fetchall()
        return [Question(r["question_id"], r["text"], r["domain"]) for r in rows]

    def reference_paths(self, question_id: str) -> list[ReferencePath]:
        rows = self._conn.execute(
            "SELECT author, quality, path_json FROM reference_paths "
            "WHERE question_id = ? ORDER BY id",
            (question_id,),
        ).fetchall()
        return [
            ReferencePath(r["author"], r["quality"], doc_to_path(json.loads(r["path_json"])))
            for r in rows
        ]

    def candidates(self, question_id: str) -> list[CandidateRun]:
        rows = self._conn.execute(
            "SELECT label, note, path_json FROM candidates "
            "WHERE question_id = ? ORDER BY id",
            (question_id,),
        ).fetchall()
        return [
            CandidateRun(r["label"], r["note"], doc_to_path(json.loads(r["path_json"])))
            for r in rows
        ]
