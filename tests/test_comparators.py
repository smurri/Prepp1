import pytest

from agent_eval import (
    CompositeComparator,
    JaccardComparator,
    LCSComparator,
    SequenceComparator,
    Step,
    Trace,
    tool_and_args,
)

T = Trace.from_tools

ALL_COMPARATORS = [SequenceComparator(), JaccardComparator(), LCSComparator()]


@pytest.mark.parametrize("cmp", ALL_COMPARATORS)
def test_identity_is_one(cmp):
    t = T(["search", "lookup", "summarize"])
    assert cmp.compare(t, t) == 1.0


@pytest.mark.parametrize("cmp", ALL_COMPARATORS)
def test_both_empty_is_one(cmp):
    assert cmp.compare(Trace(), Trace()) == 1.0


@pytest.mark.parametrize("cmp", ALL_COMPARATORS)
def test_empty_vs_nonempty_is_zero(cmp):
    assert cmp.compare(Trace(), T(["search"])) == 0.0
    assert cmp.compare(T(["search"]), Trace()) == 0.0


@pytest.mark.parametrize("cmp", ALL_COMPARATORS)
def test_disjoint_paths_score_zero(cmp):
    assert cmp.compare(T(["a", "b"]), T(["c", "d"])) == 0.0


@pytest.mark.parametrize("cmp", ALL_COMPARATORS)
def test_range_is_unit_interval(cmp):
    val = cmp.compare(T(["search", "lookup", "calc"]), T(["search", "summarize"]))
    assert 0.0 <= val <= 1.0


def test_sequence_one_substitution():
    # 3-step paths differing in one step → edit distance 1 of 3 → 2/3.
    val = SequenceComparator().compare(T(["search", "lookup", "calc"]),
                                       T(["search", "lookup", "summarize"]))
    assert val == pytest.approx(2 / 3)


def test_sequence_is_order_sensitive_but_jaccard_is_not():
    a, b = T(["search", "lookup"]), T(["lookup", "search"])
    assert JaccardComparator().compare(a, b) == 1.0      # same set
    assert SequenceComparator().compare(a, b) < 1.0       # different order


def test_lcs_rewards_subsequence_with_gap():
    # "search,summarize" is a subsequence of the reference → LCS 2 of 3.
    val = LCSComparator().compare(T(["search", "summarize"]),
                                  T(["search", "lookup", "summarize"]))
    assert val == pytest.approx(2 / 3)


def test_jaccard_partial_overlap():
    # sets {a,b,c} vs {b,c,d}: |∩|=2, |∪|=4 → 0.5
    assert JaccardComparator().compare(T(["a", "b", "c"]), T(["b", "c", "d"])) == 0.5


def test_tool_and_args_gives_partial_credit_for_args():
    sim = tool_and_args(tool_weight=0.5)
    cmp = SequenceComparator(step_similarity=sim)
    same_tool_diff_args = cmp.compare(
        Trace(steps=(Step("search", {"q": "a"}),)),
        Trace(steps=(Step("search", {"q": "b"}),)),
    )
    # tool matches (0.5) + no arg overlap (0.0) → step sim 0.5 → path sim 0.5
    assert same_tool_diff_args == pytest.approx(0.5)


def test_composite_blends_components():
    a, b = T(["search", "lookup"]), T(["lookup", "search"])
    comp = CompositeComparator([(SequenceComparator(), 1.0), (JaccardComparator(), 1.0)])
    seq = SequenceComparator().compare(a, b)
    jac = JaccardComparator().compare(a, b)
    assert comp.compare(a, b) == pytest.approx((seq + jac) / 2)


def test_composite_rejects_bad_weights():
    with pytest.raises(ValueError):
        CompositeComparator([])
    with pytest.raises(ValueError):
        CompositeComparator([(SequenceComparator(), 0.0)])
    with pytest.raises(ValueError):
        CompositeComparator([(SequenceComparator(), -1.0)])
