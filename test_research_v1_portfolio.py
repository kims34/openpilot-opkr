from datetime import date

import pandas as pd
import pytest

from research_v1_core import Bar, economic_outcome
from research_v1_portfolio import filter_executable_records, simulate_portfolio
from research_v1_distributional_netev import freeze_original_topk


def _panel():
    rows = []
    prices = {
        "A": [100, 101, 102, 103, 104, 105],
        "B": [100, 99, 98, 97, 96, 95],
    }
    days = pd.bdate_range("2026-01-02", periods=6)
    for sym, xs in prices.items():
        for d, px in zip(days, xs):
            rows.append({
                "decision_date": d,
                "symbol": sym,
                "open": px,
                "high": px * 1.005,
                "low": px * 0.995,
                "close": px,
                "volume": 1000,
                "value": px * 1000,
                "source": "test",
                "point_in_time_universe": False,
            })
    return pd.DataFrame(rows)


def _bar(day, px):
    return Bar(day, px, px * 1.005, px * 0.995, px, 1000, px * 1000)


def test_mtm_path_and_mdd_are_finite():
    panel = _panel()
    days = [d.date() for d in pd.bdate_range("2026-01-02", periods=6)]
    rec = economic_outcome(
        decision_day=days[0],
        symbol="A",
        score=1.0,
        entry_price=101,
        future_bars=[_bar(days[i], 100 + i) for i in range(1, 6)],
        target_return=0.20,
        stop_return=-0.20,
        round_trip_cost_return=0.002,
    )
    path, summary = simulate_portfolio(panel, [rec], horizon=5)
    assert not path.empty
    assert summary.entries_executed == 1
    assert summary.max_drawdown <= 0
    assert summary.end_equity > 0


def test_duplicate_symbol_is_not_pyramided_while_open():
    panel = _panel()
    days = [d.date() for d in pd.bdate_range("2026-01-02", periods=6)]
    rec1 = economic_outcome(
        decision_day=days[0], symbol="A", score=2.0, entry_price=101,
        future_bars=[_bar(days[i], 100 + i) for i in range(1, 6)],
        target_return=0.20, stop_return=-0.20, round_trip_cost_return=0.0,
    )
    rec2 = economic_outcome(
        decision_day=days[1], symbol="A", score=1.0, entry_price=102,
        future_bars=[_bar(days[i], 100 + i) for i in range(2, 6)],
        target_return=0.20, stop_return=-0.20, round_trip_cost_return=0.0,
    )
    kept, skipped = filter_executable_records([rec1, rec2], True)
    assert len(kept) == 1
    assert skipped == 1
    _, summary = simulate_portfolio(panel, [rec1, rec2], horizon=5)
    assert summary.entries_executed == 1
    assert summary.duplicate_entries_suppressed == 1


def test_cash_only_days_are_kept_in_evaluation_window():
    panel = _panel()
    days = [d.date() for d in pd.bdate_range("2026-01-02", periods=6)]
    rec = economic_outcome(
        decision_day=days[0], symbol="A", score=1.0, entry_price=101,
        future_bars=[_bar(days[1], 101)],
        target_return=0.20, stop_return=-0.20, round_trip_cost_return=0.0,
    )
    path, summary = simulate_portfolio(
        panel, [rec], horizon=5, evaluation_start=days[0], evaluation_end=days[-1]
    )
    assert summary.sessions == 6
    assert len(path) == 6
    assert path.iloc[-1]["positions"] == 0


def test_empty_strategy_can_represent_full_cash_window():
    panel = _panel()
    days = [d.date() for d in pd.bdate_range("2026-01-02", periods=6)]
    path, summary = simulate_portfolio(
        panel, [], horizon=5, evaluation_start=days[0], evaluation_end=days[-1]
    )
    assert len(path) == 6
    assert summary.total_return == pytest.approx(0.0)
    assert summary.average_cash_weight == pytest.approx(1.0)



def test_distributional_freezes_original_top3_without_backfill():
    day = pd.Timestamp("2026-01-02")
    eligible = pd.DataFrame({
        "decision_date": [day] * 5,
        "symbol": ["A", "B", "C", "D", "E"],
        "score": [5.0, 4.0, 3.0, 2.0, 1.0],
        "netev_low": [0.5, 0.4, 0.3, 0.2, 0.1],
    })
    frozen = freeze_original_topk(eligible, 3)
    assert frozen["symbol"].tolist() == ["A", "B", "C"]
    # D/E must not enter the candidate set later if A/B/C are blocked.
    assert set(frozen["symbol"]).isdisjoint({"D", "E"})
