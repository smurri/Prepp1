from agent_eval import Trace, align, alignment_summary
from agent_eval.explain import EXTRA, MATCH, MISSING, SUBSTITUTE

T = Trace.from_tools


def test_identical_paths_are_all_matches():
    ops = align(T(["search", "lookup", "summarize"]), T(["search", "lookup", "summarize"]))
    assert [o.op for o in ops] == [MATCH, MATCH, MATCH]
    assert alignment_summary(ops) == {MATCH: 3, SUBSTITUTE: 0, EXTRA: 0, MISSING: 0}


def test_extra_candidate_step_is_flagged_extra():
    # candidate has a redundant 'search' the reference lacks
    ops = align(T(["search", "geocode", "forecast"]), T(["geocode", "forecast"]))
    summary = alignment_summary(ops)
    assert summary[EXTRA] == 1
    assert summary[MATCH] == 2
    extra = next(o for o in ops if o.op == EXTRA)
    assert extra.candidate == "search" and extra.reference is None


def test_missing_reference_step_is_flagged_missing():
    # candidate skipped 'check_policy' that the reference has
    ops = align(T(["lookup", "refund"]), T(["lookup", "check_policy", "refund"]))
    summary = alignment_summary(ops)
    assert summary[MISSING] == 1
    assert summary[MATCH] == 2
    missing = next(o for o in ops if o.op == MISSING)
    assert missing.reference == "check_policy" and missing.candidate is None


def test_substitution_is_flagged():
    ops = align(T(["search", "calculate"]), T(["search", "summarize"]))
    summary = alignment_summary(ops)
    assert summary[SUBSTITUTE] == 1
    assert summary[MATCH] == 1
    sub = next(o for o in ops if o.op == SUBSTITUTE)
    assert sub.candidate == "calculate" and sub.reference == "summarize"


def test_alignment_cost_matches_sequence_comparator():
    # The number of non-match ops / max(len) should equal 1 - sequence similarity.
    from agent_eval import SequenceComparator

    a, b = T(["a", "b", "c", "d"]), T(["a", "x", "c"])
    ops = align(a, b)
    edits = sum(1 for o in ops if o.op != MATCH)
    sim = SequenceComparator().compare(a, b)
    assert edits / max(len(a), len(b)) == 1.0 - sim


def test_empty_paths():
    assert align(Trace(), Trace()) == []
    ops = align(Trace(), T(["search"]))
    assert alignment_summary(ops)[MISSING] == 1
