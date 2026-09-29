import unittest
from datetime import date

import pandas as pd

from research_v1_core import DecisionRecord
from research_v1_exit_policy_compare import build_ca_safe_barrier_record_map


class ExitPolicyCompareTest(unittest.TestCase):
    def _legacy(self, decision_day, entry_day, cost=0.003):
        return DecisionRecord(
            decision_day=decision_day,
            entry_day=entry_day,
            symbol="AAA",
            score=0.0,
            entry_price=100.0,
            horizon=3,
            target_return=0.04,
            stop_return=-0.025,
            cost_return=cost,
            outcome="TIME",
            gross_return=0.0,
            net_return=-cost,
            exit_day=date(2026, 1, 6),
            exit_price=100.0,
        )

    def test_split_does_not_create_fake_stop(self):
        # Day 2 is a mechanical 2-for-1 price-scale change: raw 100 -> 50 but
        # KRX adjusted-base return is 0%.  Economic OHLC must remain continuous.
        raw = pd.DataFrame([
            {"decision_date": "2026-01-02", "symbol": "AAA", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-03", "symbol": "AAA", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-04", "symbol": "AAA", "open": 50.0, "high": 50.5, "low": 49.5, "close": 50.0, "volume": 2.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-05", "symbol": "AAA", "open": 50.0, "high": 50.5, "low": 49.5, "close": 50.0, "volume": 2.0, "value": 100.0, "krx_change_return": 0.0},
        ])
        raw["decision_date"] = pd.to_datetime(raw["decision_date"])
        base = self._legacy(date(2026, 1, 2), date(2026, 1, 3))
        result, diag = build_ca_safe_barrier_record_map(
            raw,
            {(base.decision_day, base.symbol): base},
            horizon=3,
            target_return=0.04,
            stop_return=-0.025,
        )
        rec = result[(base.decision_day, base.symbol)]
        self.assertEqual(rec.outcome, "TIME")
        self.assertAlmostEqual(rec.gross_return, 0.0, places=10)
        self.assertEqual(diag["built_records"], 1)

    def test_post_entry_gap_through_stop_fills_at_economic_open(self):
        raw = pd.DataFrame([
            {"decision_date": "2026-01-02", "symbol": "AAA", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-03", "symbol": "AAA", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            # Mechanical split, economically flat.
            {"decision_date": "2026-01-04", "symbol": "AAA", "open": 50.0, "high": 50.5, "low": 49.5, "close": 50.0, "volume": 2.0, "value": 100.0, "krx_change_return": 0.0},
            # True -6% overnight gap after the split.  Stop must fill at -6%,
            # not the planned -2.5% level.
            {"decision_date": "2026-01-05", "symbol": "AAA", "open": 47.0, "high": 47.0, "low": 47.0, "close": 47.0, "volume": 2.0, "value": 94.0, "krx_change_return": -0.06},
        ])
        raw["decision_date"] = pd.to_datetime(raw["decision_date"])
        base = self._legacy(date(2026, 1, 2), date(2026, 1, 3), cost=0.003)
        result, _ = build_ca_safe_barrier_record_map(
            raw,
            {(base.decision_day, base.symbol): base},
            horizon=3,
            target_return=0.04,
            stop_return=-0.025,
        )
        rec = result[(base.decision_day, base.symbol)]
        self.assertEqual(rec.outcome, "STOP")
        self.assertEqual(rec.exit_day, date(2026, 1, 5))
        self.assertAlmostEqual(rec.gross_return, -0.06, places=10)
        self.assertAlmostEqual(rec.net_return, -0.063, places=10)

    def test_same_bar_double_hit_is_stop_first(self):
        raw = pd.DataFrame([
            {"decision_date": "2026-01-02", "symbol": "AAA", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-03", "symbol": "AAA", "open": 100.0, "high": 105.0, "low": 97.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-04", "symbol": "AAA", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
            {"decision_date": "2026-01-05", "symbol": "AAA", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0, "value": 100.0, "krx_change_return": 0.0},
        ])
        raw["decision_date"] = pd.to_datetime(raw["decision_date"])
        base = self._legacy(date(2026, 1, 2), date(2026, 1, 3), cost=0.0)
        result, diag = build_ca_safe_barrier_record_map(
            raw,
            {(base.decision_day, base.symbol): base},
            horizon=3,
            target_return=0.04,
            stop_return=-0.025,
            ambiguity_policy="stop_first",
        )
        rec = result[(base.decision_day, base.symbol)]
        self.assertEqual(rec.outcome, "STOP")
        self.assertAlmostEqual(rec.gross_return, -0.025, places=10)
        self.assertEqual(diag["ambiguous_same_bar_stop_first"], 1)


if __name__ == "__main__":
    unittest.main()
