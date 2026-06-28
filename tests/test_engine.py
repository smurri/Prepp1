import pytest

from agent_eval import (
    MEAN,
    EvalEngine,
    InvalidTraceError,
    JaccardComparator,
    NoReferencesError,
    Trace,
    UnknownQuestionError,
)

T = Trace.from_tools


def make_engine():
    e = EvalEngine()
    e.add_reference("q1", T(["search", "lookup", "summarize"]))
    return e


def test_exact_match_scores_one():
    e = make_engine()
    r = e.score("q1", T(["search", "lookup", "summarize"]))
    assert r.score == 1.0
    assert r.best is not None
    assert r.best.similarity == 1.0
    assert r.comparator == "sequence_edit"
    assert r.aggregation == "max"
    assert r.candidate_steps == 3


def test_partial_match_between_zero_and_one():
    e = make_engine()
    r = e.score("q1", T(["search", "calculate"]))
    assert 0.0 < r.score < 1.0


def test_unknown_question_raises():
    e = make_engine()
    with pytest.raises(UnknownQuestionError):
        e.score("does-not-exist", T(["search"]))


def test_score_requires_trace():
    e = make_engine()
    with pytest.raises(InvalidTraceError):
        e.score("q1", ["search", "lookup"])  # type: ignore[arg-type]


def test_add_reference_validates_inputs():
    e = EvalEngine()
    with pytest.raises(InvalidTraceError):
        e.add_reference("", T(["a"]))
    with pytest.raises(InvalidTraceError):
        e.add_reference("q1", "not a trace")  # type: ignore[arg-type]


def test_max_aggregation_picks_best_reference():
    e = EvalEngine()
    e.add_reference("q", T(["a", "b", "c", "d"]))   # poor match
    e.add_reference("q", T(["search", "lookup"]))   # exact match below
    r = e.score("q", T(["search", "lookup"]))
    assert r.score == 1.0
    assert len(r.breakdown) == 2
    # breakdown sorted best-first
    assert r.breakdown[0].similarity >= r.breakdown[1].similarity


def test_adding_reference_never_lowers_max_score():
    e = EvalEngine()
    e.add_reference("q", T(["x", "y", "z"]))
    before = e.score("q", T(["search", "lookup"])).score
    e.add_reference("q", T(["a", "b"]))
    after = e.score("q", T(["search", "lookup"])).score
    assert after >= before


def test_per_call_overrides():
    e = make_engine()
    r = e.score("q1", T(["summarize", "lookup", "search"]),
                comparator=JaccardComparator(), aggregation=MEAN)
    assert r.comparator == "jaccard"
    assert r.aggregation == "mean"
    assert r.score == 1.0  # same set, order-insensitive


def test_references_and_remove_and_clear():
    e = EvalEngine()
    rid = e.add_reference("q", T(["a"]))
    assert len(e.references("q")) == 1
    assert e.remove_reference("q", rid) is True
    assert e.remove_reference("q", rid) is False
    assert e.references("q") == []
    # question now gone → scoring raises
    with pytest.raises(UnknownQuestionError):
        e.score("q", T(["a"]))


def test_add_references_bulk_returns_ids():
    e = EvalEngine()
    ids = e.add_references("q", [T(["a"]), T(["b"]), T(["c"])])
    assert len(ids) == 3
    assert len(set(ids)) == 3
    assert len(e.references("q")) == 3


def test_clear_all():
    e = EvalEngine()
    e.add_reference("q1", T(["a"]))
    e.add_reference("q2", T(["b"]))
    e.clear()
    assert e.references("q1") == []
    assert e.references("q2") == []


def test_float_dunder_returns_score():
    e = make_engine()
    r = e.score("q1", T(["search", "lookup", "summarize"]))
    assert float(r) == 1.0


def test_no_references_error_is_defensive(monkeypatch):
    # Simulate a question that reports as existing but yields no snapshot.
    e = make_engine()
    monkeypatch.setattr(e._store, "snapshot", lambda q: [])
    with pytest.raises(NoReferencesError):
        e.score("q1", T(["search"]))
