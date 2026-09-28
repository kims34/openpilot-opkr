from datetime import date

import pandas as pd
import pytest

from research_v1_core import Bar, economic_outcome
from research_v1_portfolio import simulate_portfolio


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
    _, summary = simulate_portfolio(panel, [rec1, rec2], horizon=5)
    assert summary.entries_executed == 1
    assert summary.duplicate_entries_suppressed == 1
