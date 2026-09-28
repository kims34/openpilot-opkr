import unittest
from datetime import date

import pandas as pd

from research_v1_core import DecisionRecord
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_pit_features import add_pit_features


class CorporateActionSafeReturnTest(unittest.TestCase):
    def test_feature_return_uses_krx_base_adjusted_change_not_raw_close_jump(self):
        raw = pd.DataFrame({
            "decision_date": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "symbol": ["000001", "000001"],
            "open": [100.0, 50.0],
            "high": [101.0, 52.0],
            "low": [99.0, 49.0],
            "close": [100.0, 51.0],
            "volume": [1000.0, 2000.0],
            "value": [100000.0, 102000.0],
            "krx_change_return": [0.0, 0.02],
        })
        x = add_pit_features(raw)
        second = x.iloc[1]
        self.assertAlmostEqual(float(second["raw_close_ret1"]), -0.49, places=8)
        self.assertAlmostEqual(float(second["ret1"]), 0.02, places=8)
        self.assertGreater(abs(float(second["corporate_action_return_gap"])), 0.50)

    def test_fixed_horizon_economic_return_survives_split(self):
        raw = pd.DataFrame({
            "decision_date": pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"]),
            "symbol": ["000001"] * 3,
            "open": [100.0, 100.0, 50.0],
            "high": [101.0, 101.0, 52.0],
            "low": [99.0, 99.0, 49.0],
            "close": [100.0, 100.0, 51.0],
            "volume": [1000.0, 1000.0, 2000.0],
            "value": [100000.0, 100000.0, 102000.0],
            "krx_change_return": [0.0, 0.0, 0.02],
        })
        frame = pd.DataFrame({
            "decision_date": pd.to_datetime(["2026-01-02"]),
            "symbol": ["000001"],
        })
        rec = DecisionRecord(
            decision_day=date(2026, 1, 2),
            entry_day=date(2026, 1, 5),
            symbol="000001",
            score=0.0,
            entry_price=100.0,
            horizon=2,
            target_return=0.0,
            stop_return=0.0,
            cost_return=0.0,
            outcome="TIME",
            gross_return=0.0,
            net_return=0.0,
            exit_day=date(2026, 1, 6),
            exit_price=51.0,
        )
        z = add_fixed_horizon_target(
            raw, frame, {(date(2026, 1, 2), "000001"): rec}, horizon=2
        )
        row = z.iloc[0]
        self.assertAlmostEqual(float(row["fh_raw_price_ratio_return"]), -0.49, places=8)
        self.assertAlmostEqual(float(row["fh_gross_return"]), 0.02, places=8)
        self.assertAlmostEqual(float(row["fh_net_return"]), 0.02, places=8)


if __name__ == "__main__":
    unittest.main()
