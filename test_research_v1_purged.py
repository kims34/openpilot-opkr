import pandas as pd

from research_v1_ml import FEATURES
from research_v1_pit_labels import kospi_statutory_sell_tax_bps
from research_v1_pit_run_purged import _walk_forward_pit


def _synthetic_frame(n_dates=30, symbols=("000001", "000002")):
    dates = pd.bdate_range("2026-01-02", periods=n_dates)
    rows = []
    for i, d in enumerate(dates):
        for j, symbol in enumerate(symbols):
            row = {
                "decision_date": d,
                "symbol": symbol,
                "label_positive_net": int((i + j) % 2 == 0),
                "net_return": 0.01 if (i + j) % 2 == 0 else -0.01,
                "label_available": True,
                "entry_fillable": True,
                "ambiguous_same_bar": False,
                "post_entry_missing_future": False,
            }
            for k, feature in enumerate(FEATURES):
                row[feature] = float(i + 1) / 100.0 + float(j + k) / 1000.0
            rows.append(row)
    return pd.DataFrame(rows), list(dates)


def test_walk_forward_purges_full_horizon_before_first_test_block():
    frame, dates = _synthetic_frame()
    pred = _walk_forward_pit(
        frame,
        "logistic_l2",
        train_days=10,
        test_days=5,
        context=False,
        purge_days=3,
    )

    assert not pred.empty
    first = pred.iloc[0]
    # 10 complete training dates, then 3 embargo dates, then test begins.
    assert pd.Timestamp(first["decision_date"]) == dates[13]
    assert pd.Timestamp(first["train_end"]) == dates[9]
    assert pd.Timestamp(first["embargo_start"]) == dates[10]
    assert pd.Timestamp(first["embargo_end"]) == dates[12]
    assert int(first["purge_days"]) == 3


def test_each_fold_keeps_label_horizon_out_of_test_boundary():
    frame, dates = _synthetic_frame(n_dates=36)
    purge = 5
    pred = _walk_forward_pit(
        frame,
        "logistic_l2",
        train_days=10,
        test_days=4,
        context=False,
        purge_days=purge,
    )

    # For every test row, its fold train_end must be at least `purge` complete
    # decision sessions behind that fold's first test decision date.
    date_pos = {pd.Timestamp(d): i for i, d in enumerate(dates)}
    for _, fold in pred.groupby(["train_end", "embargo_start", "embargo_end"], dropna=False):
        test_start = pd.Timestamp(fold["decision_date"].min())
        train_end = pd.Timestamp(fold["train_end"].iloc[0])
        assert date_pos[test_start] - date_pos[train_end] == purge + 1


def test_kospi_statutory_tax_schedule_matches_research_years():
    assert kospi_statutory_sell_tax_bps("2022-06-01") == 23.0
    assert kospi_statutory_sell_tax_bps("2023-06-01") == 20.0
    assert kospi_statutory_sell_tax_bps("2024-06-01") == 18.0
    assert kospi_statutory_sell_tax_bps("2025-06-01") == 15.0
    assert kospi_statutory_sell_tax_bps("2026-06-01") == 20.0
