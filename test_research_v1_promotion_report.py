import pandas as pd

from research_v1_promotion_report import (
    _frozen_evidence_flags_and_blockers,
    _metrics,
)


def test_promotion_report_records_trade_es95_and_es99():
    returns = [-0.50, -0.40, -0.30, -0.20, -0.10] + [0.01] * 95
    df = pd.DataFrame({
        "decision_date": pd.date_range("2026-01-01", periods=100, freq="D").astype(str),
        "fh_net_return": returns,
    })
    out = _metrics(df, boot=50)
    assert out["trade_expected_shortfall_95"] == -0.30
    assert out["trade_expected_shortfall_99"] == -0.50


def _robust():
    return {
        "mean_net_return": 0.01,
        "profit_factor": 1.2,
        "cluster_bootstrap_95_low": 0.001,
    }


def test_best5_requires_positive_cluster_lcb_even_when_mean_and_pf_pass():
    overall = _robust()
    after5 = _robust()
    after5["cluster_bootstrap_95_low"] = -0.001
    recent = _robust()
    stress2 = {"mean_net_return": 0.001, "profit_factor": 1.1}
    flags, blockers = _frozen_evidence_flags_and_blockers(
        overall, after5, recent, stress2, recent_records=10
    )
    assert flags["jackpot_independent_after_best5_days"] is False
    assert "BEST_5_DECISION_DAY_ROBUSTNESS_FAILS_MEAN_PF_OR_CLUSTER_LCB" in blockers


def test_2x_cost_requires_profit_factor_above_one():
    flags, blockers = _frozen_evidence_flags_and_blockers(
        _robust(),
        _robust(),
        _robust(),
        {"mean_net_return": 0.001, "profit_factor": 1.0},
        recent_records=10,
    )
    assert flags["cost_2x_survives"] is False
    assert "FAILS_2X_COST_STRESS" in blockers


def test_no_recent_admissions_is_explicit_blocker():
    flags, blockers = _frozen_evidence_flags_and_blockers(
        _robust(), _robust(), _robust(),
        {"mean_net_return": 0.001, "profit_factor": 1.1},
        recent_records=0,
    )
    assert flags["recent_504_session_robust"] is False
    assert "NO_ADMISSIONS_IN_LATEST_504_TEST_SESSIONS" in blockers
