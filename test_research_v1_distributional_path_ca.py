import unittest

import pandas as pd

from research_v1_distributional_path_ca import add_ca_safe_path_features


class CASafePathFeatureTest(unittest.TestCase):
    def test_split_day_gap_uses_krx_base_price_not_prior_raw_close(self):
        raw = pd.DataFrame(
            {
                "decision_date": pd.to_datetime(["2026-01-02", "2026-01-05"]),
                "symbol": ["000001", "000001"],
                "open": [100.0, 51.0],
                "high": [101.0, 52.0],
                "low": [99.0, 50.0],
                "close": [100.0, 51.0],
                "value": [1_000_000.0, 1_100_000.0],
                "krx_change_return": [0.0, 0.02],
            }
        )
        supervised = raw[["decision_date", "symbol"]].copy()
        out = add_ca_safe_path_features(raw, supervised)
        row = out.iloc[1]
        # KRX base price = 51/1.02 = 50, so the opening gap is +2%.
        self.assertAlmostEqual(float(row["gap1_ca"]), 0.02, places=10)
        # A raw previous-close gap would have been -49%, proving the distinction.
        raw_gap = 51.0 / 100.0 - 1.0
        self.assertLess(raw_gap, -0.40)

    def test_path_features_do_not_require_future_rows(self):
        dates = pd.bdate_range("2026-01-02", periods=25)
        raw = pd.DataFrame(
            {
                "decision_date": dates,
                "symbol": ["000001"] * len(dates),
                "open": [100.0] * len(dates),
                "high": [102.0] * len(dates),
                "low": [99.0] * len(dates),
                "close": [101.0] * len(dates),
                "value": [1_000_000.0 + i for i in range(len(dates))],
                "krx_change_return": [0.01] * len(dates),
            }
        )
        supervised = raw[["decision_date", "symbol"]].copy()
        full = add_ca_safe_path_features(raw, supervised)
        cut_raw = raw.iloc[:21].copy()
        cut_sup = supervised.iloc[:21].copy()
        cut = add_ca_safe_path_features(cut_raw, cut_sup)
        cols = ["gap1_ca", "intraday_ret1", "range1", "close_location1", "value_surprise20_log"]
        for col in cols:
            a = full.loc[20, col]
            b = cut.loc[20, col]
            if pd.isna(a) and pd.isna(b):
                continue
            self.assertAlmostEqual(float(a), float(b), places=12)


if __name__ == "__main__":
    unittest.main()
