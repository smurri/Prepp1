"""Property-based invariants (hypothesis) + a concurrency smoke test.

These encode the spec's guarantees, not the implementation's current output:
scores live in [0,1], identity is 1.0, comparators are symmetric, and max
aggregation is monotonic under added references.
"""

import threading

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agent_eval import (
    EvalEngine,
    JaccardComparator,
    LCSComparator,
    SequenceComparator,
    Trace,
)

T = Trace.from_tools

tools = st.lists(st.sampled_from(["search", "lookup", "calc", "summarize", "fetch"]), max_size=8)
COMPARATORS = [SequenceComparator(), JaccardComparator(), LCSComparator()]


@pytest.mark.parametrize("cmp", COMPARATORS)
@given(a=tools, b=tools)
def test_score_in_unit_interval(cmp, a, b):
    assert 0.0 <= cmp.compare(T(a), T(b)) <= 1.0


@pytest.mark.parametrize("cmp", COMPARATORS)
@given(a=tools)
def test_identity_is_one(cmp, a):
    assert cmp.compare(T(a), T(a)) == 1.0


@pytest.mark.parametrize("cmp", COMPARATORS)
@given(a=tools, b=tools)
def test_symmetry(cmp, a, b):
    assert cmp.compare(T(a), T(b)) == pytest.approx(cmp.compare(T(b), T(a)))


@given(cand=tools, refs=st.lists(tools, min_size=1, max_size=5), extra=tools)
def test_max_aggregation_is_monotonic(cand, refs, extra):
    engine = EvalEngine()  # default comparator + MAX aggregation
    engine.add_references("q", [T(r) for r in refs])
    before = engine.score("q", T(cand)).score
    engine.add_reference("q", T(extra))
    after = engine.score("q", T(cand)).score
    assert after >= before - 1e-9


def test_concurrent_add_and_score_is_safe():
    engine = EvalEngine()
    engine.add_reference("q", T(["search", "lookup"]))

    errors: list[Exception] = []

    def worker(i: int) -> None:
        try:
            for _ in range(50):
                engine.add_reference("q", T(["search", f"tool{i}"]))
                engine.score("q", T(["search", "lookup"]))
        except Exception as exc:  # noqa: BLE001 - record any thread failure
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    # 1 seed + 8 workers * 50 adds = 401 references, all with unique ids.
    assert len(engine.references("q")) == 401
