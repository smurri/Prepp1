import pytest

from agent_eval import MAX, MEAN, TopKMean


def test_max_picks_best():
    assert MAX([0.2, 0.9, 0.5]) == 0.9
    assert MAX.name == "max"


def test_mean_averages():
    assert MEAN([0.0, 1.0]) == 0.5
    assert MEAN.name == "mean"


def test_topk_mean_uses_top_k():
    agg = TopKMean(2)
    
    assert agg([0.1, 0.9, 0.8, 0.2]) == pytest.approx((0.9 + 0.8) / 2)
    assert agg.name == "top2_mean"


def test_topk_mean_with_k_larger_than_n_uses_all():
    agg = TopKMean(10)
    assert agg([0.4, 0.6]) == pytest.approx(0.5)


def test_topk_mean_rejects_bad_k():
    with pytest.raises(ValueError):
        TopKMean(0)
