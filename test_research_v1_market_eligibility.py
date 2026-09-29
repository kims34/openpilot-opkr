import pandas as pd
import pytest

from research_v1_market_eligibility import (
    EXCEPTIONAL_THRESHOLD,
    tag_normal_market_eligibility,
    veto_frozen_topk_nonstandard_market,
)


def test_normal_price_limit_gate_is_pit_and_fail_closed():
    x = pd.DataFrame([
        {"decision_date": "2026-01-02", "symbol": "A", "ret1": 0.3000, "score": 3.0},
        {"decision_date": "2026-01-02", "symbol": "B", "ret1": -0.9495, "score": 2.0},
        {"decision_date": "2026-01-02", "symbol": "C", "ret1": None, "score": 1.0},
    ])
    tagged = tag_normal_market_eligibility(x).set_index("symbol")
    assert bool(tagged.loc["A", "normal_market_eligible"])
    assert not bool(tagged.loc["B", "normal_market_eligible"])
    assert not bool(tagged.loc["C", "normal_market_eligible"])
    assert EXCEPTIONAL_THRESHOLD == 0.305


def test_post_rank_veto_never_promotes_fourth_name():
    # Input is already frozen original Top3. B is vetoed; only A/C remain.
    frozen = pd.DataFrame([
        {"decision_date": "2026-01-02", "symbol": "A", "ret1": 0.01, "score": 0.9},
        {"decision_date": "2026-01-02", "symbol": "B", "ret1": -0.95, "score": 0.8},
        {"decision_date": "2026-01-02", "symbol": "C", "ret1": -0.03, "score": 0.7},
    ])
    kept, vetoed, diag = veto_frozen_topk_nonstandard_market(frozen)
    assert kept["symbol"].tolist() == ["A", "C"]
    assert vetoed["symbol"].tolist() == ["B"]
    assert diag["rows_before"] == 3
    assert diag["rows_after"] == 2
    assert diag["backfill_allowed"] is False


def test_gate_refuses_pre_30pct_regime():
    x = pd.DataFrame([
        {"decision_date": "2015-06-12", "symbol": "A", "ret1": 0.1}
    ])
    with pytest.raises(ValueError):
        tag_normal_market_eligibility(x)
