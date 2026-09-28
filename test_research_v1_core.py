from datetime import date

import pytest

from research_v1_core import (
    AmbiguousFirstHit,
    Bar,
    cost_model_return,
    date_cluster_bootstrap_mean,
    economic_outcome,
)


def b(day, o, h, l, c):
    return Bar(date.fromisoformat(day), o, h, l, c, 1000, c * 1000)


def test_same_bar_target_stop_is_ambiguous():
    future = [b("2026-01-02", 100, 105, 95, 101)]
    with pytest.raises(AmbiguousFirstHit):
        economic_outcome(date(2026, 1, 1), "TEST", 1.0, 100, future, 0.04, -0.03, 0.0)


def test_gap_through_stop_uses_open():
    future = [b("2026-01-02", 90, 95, 89, 92)]
    r = economic_outcome(date(2026, 1, 1), "TEST", 1.0, 100, future, 0.04, -0.03, 0.001)
    assert r.outcome == "STOP"
    assert r.exit_price == 90
    assert r.gross_return == pytest.approx(-0.10)
    assert r.net_return == pytest.approx(-0.101)


def test_gap_through_target_uses_open():
    future = [b("2026-01-02", 108, 109, 106, 107)]
    r = economic_outcome(date(2026, 1, 1), "TEST", 1.0, 100, future, 0.04, -0.03, 0.0)
    assert r.outcome == "TARGET"
    assert r.exit_price == 108
    assert r.gross_return == pytest.approx(0.08)


def test_time_exit_uses_last_close():
    future = [b("2026-01-02", 100, 102, 99, 101), b("2026-01-05", 101, 102, 100, 101.5)]
    r = economic_outcome(date(2026, 1, 1), "TEST", 1.0, 100, future, 0.05, -0.05, 0.0)
    assert r.outcome == "TIME"
    assert r.exit_price == pytest.approx(101.5)


def test_cost_increases_with_participation():
    c1 = cost_model_return(4, 23, 0.02, 0.0001)
    c2 = cost_model_return(4, 23, 0.02, 0.01)
    assert c2 > c1


def test_cluster_bootstrap_treats_same_day_as_cluster():
    rows = [
        economic_outcome(date(2026, 1, 1), "A", 1, 100, [b("2026-01-02", 101, 102, 100.5, 101)], 0.10, -0.10, 0),
        economic_outcome(date(2026, 1, 1), "B", 1, 100, [b("2026-01-02", 101, 102, 100.5, 101)], 0.10, -0.10, 0),
        economic_outcome(date(2026, 1, 2), "C", 1, 100, [b("2026-01-05", 99, 99.5, 98, 99)], 0.10, -0.10, 0),
    ]
    point, lo, hi = date_cluster_bootstrap_mean(rows, samples=500, seed=1)
    assert point == pytest.approx(0.0, abs=1e-12)
    assert lo <= point <= hi
