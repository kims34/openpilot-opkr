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
        rows = self.rows(100, 0.001)
        result = model.estimate(rows)
        # Eligible historical as-of indices are 20..78 inclusive. The final
        # 21 sessions are not used as incomplete forward labels.
        self.assertEqual(result["baseline_sample_size"], 59)
        self.assertEqual(result["horizon_sessions"], 21)
        self.assertEqual(result["threshold_percent"], 10)
        self.assertEqual(result["price_basis"], "daily_close")

    def test_rising_series_prefers_up_touch(self):
        result = model.estimate(self.rows(180, 0.006))
        self.assertGreater(result["up_10_probability"], result["down_10_probability"])
        self.assertGreater(result["up_10_probability"], 90.0)
        self.assertLess(result["down_10_probability"], 10.0)

    def test_falling_series_prefers_down_touch(self):
        result = model.estimate(self.rows(180, -0.006))
        self.assertGreater(result["down_10_probability"], result["up_10_probability"])
        self.assertGreater(result["down_10_probability"], 90.0)
        self.assertLess(result["up_10_probability"], 10.0)

    def test_probabilities_are_bounded_on_mixed_regime(self):
        price = 100.0
        rows = []
        for i in range(260):
            rows.append((f"d{i:04d}", price))
            r = 0.018 * math.sin(i / 3.0) + 0.001
            price *= max(0.8, 1.0 + r)
        result = model.estimate(rows)
        self.assertGreaterEqual(result["up_10_probability"], 0.0)
        self.assertLessEqual(result["up_10_probability"], 100.0)
        self.assertGreaterEqual(result["down_10_probability"], 0.0)
        self.assertLessEqual(result["down_10_probability"], 100.0)
        self.assertGreater(result["sample_size"], 0)
        self.assertEqual(result["method"], model.METHOD)

    def test_rejects_short_history(self):
        with self.assertRaises(ValueError):
            model.estimate(self.rows(60, 0.001))


if __name__ == "__main__":
    unittest.main()
