"""Synthetic guards only; passing never means improved real-money accuracy."""
import copy
import unittest
from datetime import date, timedelta

import numpy as np
import research_monthly_touch_v1 as model


def fixture(n=970):
    rng = np.random.default_rng(1401)
    returns = rng.normal(0.0004, 0.012, n - 1)
    prices = 100.0 * np.exp(np.r_[0.0, np.cumsum(returns)])
    start = date(2021, 1, 1)
    dates = [(start + timedelta(days=i)).isoformat() for i in range(n)]
    close = list(zip(dates, prices.tolist()))
    ohlc = [(d, float(p) * 1.003, float(p) * 0.997, float(p)) for d, p in close]
    iv = {d: 20.0 + (8.0 if i % 60 < 20 else 0.0)
          for i, d in enumerate(dates)}
    return close, ohlc, iv


class MonthlyTouchResearchTests(unittest.TestCase):
    def test_strict_ohlc_alignment(self):
        close, ohlc, _ = fixture()
        a, p, h, l = model.validate_ohlc(close, ohlc)
        self.assertEqual(len(a), 970)
        self.assertTrue(np.all(h >= p))
        self.assertTrue(np.all(l <= p))

    def test_missing_ohlc_cannot_be_replaced_by_close(self):
        close, ohlc, _ = fixture()
        with self.assertRaises(model.SourceQualityError):
            model.validate_ohlc(close, ohlc[:-1])

    def test_duplicated_date_or_wrong_close_rejected(self):
        close, ohlc, _ = fixture()
        corrupt = ohlc.copy()
        corrupt[45] = (ohlc[44][0], *ohlc[45][1:])
        with self.assertRaises(model.SourceQualityError):
            model.validate_ohlc(close, corrupt)
        corrupt = ohlc.copy()
        d, high, low, price = corrupt[10]
        corrupt[10] = (d, high, low, price * 1.5)
        with self.assertRaises(model.SourceQualityError):
            model.validate_ohlc(close, corrupt)

    def test_invalid_high_low_or_nonfinite_rejected(self):
        close, ohlc, _ = fixture()
        bad = ohlc.copy()
        d, _, low, price = bad[1]
        bad[1] = (d, price * .9, low, price)
        with self.assertRaises(model.SourceQualityError):
            model.validate_ohlc(close, bad)
        bad = ohlc.copy()
        d, hi, lo, price = bad[2]
        bad[2] = (d, hi, float("nan"), price)
        with self.assertRaises(model.SourceQualityError):
            model.validate_ohlc(close, bad)

    def test_barrier_touch_is_intraday_and_independent(self):
        close, ohlc, _ = fixture()
        _, p, h, l = model.validate_ohlc(close, ohlc)
        p[:] = 100.
        h[:] = 100.
        l[:] = 100.
        h[11] = 111.
        l[12] = 89.
        self.assertEqual(model.touch_label(p, h, l, 10).tolist(), [1., 1.])
        self.assertEqual(model.touch_label(p, h, l, 12).tolist(), [0., 0.])

    def test_horizon_excludes_anchor_and_day22(self):
        p = np.ones(70) * 100
        h, l = p.copy(), p.copy()
        h[0] = 120
        l[22] = 75
        self.assertEqual(model.touch_label(p, h, l, 0).tolist(), [0., 0.])

    def test_monte_carlo_only_uses_known_past_prices(self):
        close, _, _ = fixture()
        p = np.array([x[1] for x in close])
        before = model.simulate_touch(p, 550, 22.0, 400, paths=128)
        p[551:] *= 100
        after = model.simulate_touch(p, 550, 22.0, 400, paths=128)
        np.testing.assert_array_equal(before, after)

    def test_monte_carlo_repeatable_and_probability_bounded(self):
        close, _, _ = fixture()
        p = np.array([x[1] for x in close])
        a = model.simulate_touch(p, 550, 21, 221, paths=128)
        b = model.simulate_touch(p, 550, 21, 221, paths=128)
        np.testing.assert_array_equal(a, b)
        self.assertTrue(np.all((a >= 0) & (a <= 1)))

    def test_matured_baseline_cannot_see_recent_unfinished_labels(self):
        close, ohlc, _ = fixture()
        _, p, h, l = model.validate_ohlc(close, ohlc)
        before = model.asof_baseline(p, h, l, 700)
        h[701:] *= 5.
        l[701:] *= .1
        after = model.asof_baseline(p, h, l, 700)
        np.testing.assert_array_equal(before, after)

    def test_missing_implied_daily_source_blocks_not_silent(self):
        close, ohlc, iv = fixture()
        del iv[close[-45][0]]
        with self.assertRaises(model.SourceQualityError):
            model.evaluate("QQQ", close, ohlc, iv, paths=64)

    def test_insufficient_history_and_unapproved_ticker(self):
        close, ohlc, iv = fixture()
        with self.assertRaises(model.SourceQualityError):
            model.evaluate("TQQQ", close, ohlc, iv, paths=64)
        with self.assertRaises(model.SourceQualityError):
            model.evaluate("SPY", close[:700], ohlc[:700], iv, paths=64)

    def test_synthetic_evaluation_never_changes_production(self):
        close, ohlc, iv = fixture()
        result = model.evaluate("SPY", close, ohlc, iv, paths=64)
        self.assertEqual(result["development_n"], 252)
        self.assertEqual(result["reserved_test_n"], 126)
        self.assertEqual(result["embargo_sessions"], 21)
        self.assertFalse(result["app_changed"])
        self.assertFalse(result["order_authorization"])
        self.assertEqual(result["production_admission"], "BLOCKED")
        self.assertEqual(result["source_quality"], "PUBLIC_BACKFILL_NO_PIT_PROOF")


if __name__ == "__main__":
    unittest.main()
