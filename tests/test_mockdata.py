"""Tests for the mock backends: both must return identical content and hydrate
the engine to sensible scores."""

import pytest

from agent_eval import EvalEngine, Trace
from agent_eval.mockdata import (
    NoSqlBackend,
    SqlBackend,
    doc_to_path,
    hydrate,
    path_to_doc,
)

BACKENDS = [SqlBackend, NoSqlBackend]


@pytest.mark.parametrize("Backend", BACKENDS)
def test_backend_loads_questions_and_references(Backend):
    b = Backend()
    questions = b.questions()
    assert len(questions) >= 3
    for q in questions:
        refs = b.reference_paths(q.question_id)
        assert len(refs) >= 1
        assert all(isinstance(r.trace, Trace) and len(r.trace) > 0 for r in refs)
        assert all(r.quality for r in refs)


def test_sql_and_nosql_backends_return_identical_content():
    sql, nosql = SqlBackend(), NoSqlBackend()
    sql_q = {q.question_id: q for q in sql.questions()}
    nosql_q = {q.question_id: q for q in nosql.questions()}
    assert sql_q.keys() == nosql_q.keys()
    for qid in sql_q:
        assert sql_q[qid] == nosql_q[qid]
        sql_refs = [(r.author, r.quality, r.trace) for r in sql.reference_paths(qid)]
        nosql_refs = [(r.author, r.quality, r.trace) for r in nosql.reference_paths(qid)]
        assert sql_refs == nosql_refs
        sql_cands = [(c.label, c.trace) for c in sql.candidates(qid)]
        nosql_cands = [(c.label, c.trace) for c in nosql.candidates(qid)]
        assert sql_cands == nosql_cands


def test_serde_roundtrip_preserves_trace():
    b = SqlBackend()
    q = b.questions()[0]
    trace = b.reference_paths(q.question_id)[0].trace
    assert doc_to_path(path_to_doc(trace)) == trace


@pytest.mark.parametrize("Backend", BACKENDS)
def test_scoring_a_gold_reference_against_itself_is_perfect(Backend):
    b = Backend()
    engine = EvalEngine()
    hydrate(engine, b)
    for q in b.questions():
        gold = next(r for r in b.reference_paths(q.question_id) if r.quality == "gold")
        result = engine.score(q.question_id, gold.trace)
        assert result.score == 1.0  # a stored gold path matches itself exactly


@pytest.mark.parametrize("Backend", BACKENDS)
def test_off_track_candidate_scores_below_ideal(Backend):
    b = Backend()
    engine = EvalEngine()
    hydrate(engine, b)
    # weather-paris has both an 'ideal' and an 'off-track' candidate.
    cands = {c.label: c for c in b.candidates("weather-paris")}
    ideal = engine.score("weather-paris", cands["ideal"].trace).score
    off = engine.score("weather-paris", cands["off-track"].trace).score
    assert ideal == 1.0
    assert off < ideal
