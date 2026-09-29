import unittest

import pandas as pd

from research_v1_cross_asset_regime import (
    add_cross_asset_features,
    build_available_cross_asset,
)


class CrossAssetAvailabilityTest(unittest.TestCase):
    def setUp(self):
        us_dates = pd.to_datetime([
            "2026-09-21", "2026-09-22", "2026-09-23",
            "2026-09-24", "2026-09-25", "2026-09-28",
        ])
        self.nasdaq = pd.DataFrame({
            "observation_date": us_dates,
            "value": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
        })
        self.vix = pd.DataFrame({
            "observation_date": us_dates,
            "value": [20.0, 19.0, 18.0, 17.0, 18.0, 19.0],
        })

    def test_monday_observation_not_eligible_until_wednesday(self):
        available = build_available_cross_asset(self.nasdaq, self.vix)
        monday = available[available["source_observation_date"] == pd.Timestamp("2026-09-21")].iloc[0]
        self.assertEqual(monday["available_date"], pd.Timestamp("2026-09-23"))

        sup = pd.DataFrame({
            "decision_date": pd.to_datetime(["2026-09-22", "2026-09-23"]),
            "symbol": ["A", "A"],
        })
        out = add_cross_asset_features(sup, available)
        self.assertTrue(pd.isna(out.iloc[0]["source_observation_date"]))
        self.assertEqual(out.iloc[1]["source_observation_date"], pd.Timestamp("2026-09-21"))

    def test_friday_observation_waits_through_weekend_and_next_us_session(self):
        available = build_available_cross_asset(self.nasdaq, self.vix)
        friday = available[available["source_observation_date"] == pd.Timestamp("2026-09-25")].iloc[0]
        # Next U.S. observation is Monday Sep 28, then one more calendar day.
        self.assertEqual(friday["available_date"], pd.Timestamp("2026-09-29"))

    def test_no_same_or_future_source_observation_reaches_decision(self):
        available = build_available_cross_asset(self.nasdaq, self.vix)
        sup = pd.DataFrame({
            "decision_date": pd.to_datetime([
                "2026-09-23", "2026-09-24", "2026-09-25", "2026-09-28", "2026-09-29"
            ]),
            "symbol": ["A"] * 5,
        })
        out = add_cross_asset_features(sup, available)
        valid = out[out["source_observation_date"].notna()]
        self.assertTrue((valid["source_observation_date"] < valid["decision_date"]).all())
        self.assertTrue((valid["cross_asset_source_lag_days"] >= 2).all())


if __name__ == "__main__":
    unittest.main()
