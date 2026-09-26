import math
import unittest

import one_month_probability as model


class OneMonthProbabilityTest(unittest.TestCase):
    @staticmethod
    def rows(count, daily_return):
        price = 100.0
        out = []
        for i in range(count):
            out.append((f"d{i:04d}", price))
            price *= 1.0 + daily_return
        return out

    def test_uses_only_fully_completed_21_session_windows(self):
        rows = self.rows(900, 0.001)
        result = model.estimate(rows)
        expected = 900 - model.HORIZON - model.MIN_FEATURE_INDEX
        self.assertEqual(result["baseline_sample_size"], expected)
        self.assertEqual(result["horizon_sessions"], 21)
        self.assertEqual(result["threshold_percent"], 10)
        self.assertEqual(result["price_basis"], "daily_close")

    def test_rising_series_prefers_up_touch(self):
        result = model.estimate(self.rows(900, 0.006))
        self.assertGreater(result["up_10_probability"], result["down_10_probability"])
        self.assertGreater(result["up_10_probability"], 90.0)
        self.assertLess(result["down_10_probability"], 10.0)

    def test_falling_series_prefers_down_touch(self):
        result = model.estimate(self.rows(900, -0.006))
        self.assertGreater(result["down_10_probability"], result["up_10_probability"])
        self.assertGreater(result["down_10_probability"], 90.0)
        self.assertLess(result["up_10_probability"], 10.0)

    def test_probabilities_and_validation_are_bounded(self):
        price = 100.0
        rows = []
        for i in range(1200):
            rows.append((f"d{i:04d}", price))
            r = 0.018 * math.sin(i / 3.0) + 0.006 * math.sin(i / 29.0) + 0.0003
            price *= max(0.8, 1.0 + r)
        result = model.estimate(rows)
        for key in ("up_10_probability", "down_10_probability", "baseline_up_10_probability", "baseline_down_10_probability"):
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 100.0)
        self.assertGreater(result["sample_size"], 0)
        self.assertIn(result["selection_up"], ("analog", "baseline"))
        self.assertIn(result["selection_down"], ("analog", "baseline"))
        self.assertEqual(result["method"], model.METHOD)
        self.assertIn("features", result)

    def test_intraday_high_low_counts_barrier_touch(self):
        rows = self.rows(900, 0.0)
        ohlc = [(d, p, p, p) for d, p in rows]
        # Create recurring intraday +10% touches without changing closes.
        for anchor in range(model.MIN_FEATURE_INDEX, 860, 40):
            d, _, _, p = ohlc[anchor + 1]
            ohlc[anchor + 1] = (d, p * 1.11, p, p)
        result = model.estimate(rows, ohlc)
        self.assertEqual(result["price_basis"], "daily_high_low")
        self.assertGreater(result["baseline_up_10_probability"], 0.0)

    def test_rejects_short_history(self):
        with self.assertRaises(ValueError):
            model.estimate(self.rows(300, 0.001))


if __name__ == "__main__":
    unittest.main()
