"""Regression tests for issues raised in the independent design/code review."""

import pytest

from agent_eval import (
    AgentEvalError,
    EvalEngine,
    InvalidTraceError,
    SequenceComparator,
    Step,
    Trace,
    UnknownQuestionError,
    tool_and_args,
)

T = Trace.from_tools


# --- F1: unhashable / nested arg values ------------------------------------

def test_step_with_nested_unhashable_args_is_hashable():
    s = Step("search", {"filters": ["a", "b"], "opts": {"k": 1}})
    assert isinstance(hash(s), int)  # must not raise
    assert hash(s) == hash(Step("search", {"filters": ["a", "b"], "opts": {"k": 1}}))


def test_identity_holds_with_unhashable_args_under_tool_and_args():
    cmp = SequenceComparator(step_similarity=tool_and_args(0.5))
    t = Trace(steps=(Step("search", {"tags": ["x", "y"]}),))
    assert cmp.compare(t, t) == 1.0  # previously raised TypeError


def test_tool_and_args_credits_nested_arg_overlap():
    cmp = SequenceComparator(step_similarity=tool_and_args(0.5))
    a = Trace(steps=(Step("s", {"tags": ["x", "y"]}),))
    b = Trace(steps=(Step("s", {"tags": ["x", "y"]}),))
    assert cmp.compare(a, b) == 1.0  # tool + full arg overlap


# --- F2: score() validates question_id -------------------------------------

@pytest.mark.parametrize("bad", ["", None, 123, ["x"]])
def test_score_rejects_bad_question_id(bad):
    e = EvalEngine()
    e.add_reference("q", T(["a"]))
    with pytest.raises(InvalidTraceError):
        e.score(bad, T(["a"]))  # type: ignore[arg-type]


# --- error hierarchy contract (review: untested) ---------------------------

def test_error_subclass_contract():
    e = EvalEngine()
    e.add_reference("q", T(["a"]))
    with pytest.raises(KeyError):            # UnknownQuestionError is-a KeyError
        e.score("nope", T(["a"]))
    with pytest.raises(AgentEvalError):      # …and is-a AgentEvalError
        e.score("nope", T(["a"]))
    with pytest.raises(ValueError):          # InvalidTraceError is-a ValueError
        Step("")
    assert issubclass(UnknownQuestionError, AgentEvalError)


# --- score() is a pure read (review HIGH: untested NFR) ---------------------

def test_score_does_not_mutate_store_or_inputs():
    e = EvalEngine()
    e.add_reference("q", T(["search", "lookup"]))
    before = e.reference_items("q")
    candidate = T(["search", "calc"])
    r1 = e.score("q", candidate)
    r2 = e.score("q", candidate)
    after = e.reference_items("q")
    assert before == after                       # store unchanged by value
    assert [id(t) for _, t in before] == [id(t) for _, t in after]  # …and identity
    assert candidate.tool_names == ("search", "calc")  # candidate untouched
    assert r1.score == r2.score                  # deterministic


# --- default comparator ignores args (review: untested) --------------------

def test_default_comparator_ignores_args():
    cmp = SequenceComparator()  # default step similarity = tool name only
    a = Trace(steps=(Step("search", {"q": "a"}),))
    b = Trace(steps=(Step("search", {"q": "b"}),))
    assert cmp.compare(a, b) == 1.0


# --- duplicate references (review: untested edge case) ----------------------

def test_duplicate_reference_does_not_change_max_score():
    e = EvalEngine()
    e.add_reference("q", T(["search", "lookup"]))
    before = e.score("q", T(["search", "lookup"])).score
    e.add_reference("q", T(["search", "lookup"]))  # exact duplicate
    after = e.score("q", T(["search", "lookup"]))
    assert after.score == before == 1.0
    assert len(after.breakdown) == 2  # both stored with distinct ids


def test_reference_items_maps_ids_to_breakdown():
    e = EvalEngine()
    rid = e.add_reference("q", T(["search", "lookup"]))
    items = e.reference_items("q")
    assert items == [(rid, T(["search", "lookup"]))]
    result = e.score("q", T(["search", "lookup"]))
    assert result.best.reference_id == rid
    assert result.best.reference_steps == 2
