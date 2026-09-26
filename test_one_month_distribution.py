import math
import unittest

import one_month_distribution as model


class OneMonthDistributionTest(unittest.TestCase):
    @staticmethod
    def rows(count, daily_return):
        price = 100.0
        out = []
        for i in range(count):
            out.append((f"d{i:04d}", price))
            price *= 1.0 + daily_return
        return out

    def test_uses_only_completed_21_session_terminal_returns(self):
        result = model.estimate(self.rows(900, 0.0))
        expected = 900 - model.HORIZON - model.MIN_FEATURE_INDEX
        self.assertEqual(result["terminal_return_baseline_sample_size"], expected)
        self.assertEqual(result["terminal_return_bin_width_percent"], 2)

    def test_flat_series_mode_is_near_zero(self):
        result = model.estimate(self.rows(900, 0.0))
        self.assertEqual(result["terminal_return_mode_label"], "+0% ~ +2%")
        self.assertGreater(result["terminal_return_mode_probability"], 90.0)
        self.assertEqual(result["terminal_return_mode_direction"], "up")

    def test_rising_series_mode_is_positive(self):
        result = model.estimate(self.rows(900, 0.001))
        self.assertGreater(result["terminal_return_mode_midpoint"], 0.0)
        self.assertIn("+", result["terminal_return_mode_label"])

    def test_falling_series_mode_is_negative(self):
        result = model.estimate(self.rows(900, -0.001))
        self.assertLess(result["terminal_return_mode_midpoint"], 0.0)
        self.assertEqual(result["terminal_return_mode_direction"], "down")

    def test_probability_is_bounded_and_selection_is_valid(self):
        price = 100.0
        rows = []
        for i in range(1200):
            rows.append((f"d{i:04d}", price))
            r = 0.012 * math.sin(i / 5.0) + 0.004 * math.sin(i / 31.0) + 0.0002
            price *= max(0.85, 1.0 + r)
        result = model.estimate(rows)
        self.assertGreaterEqual(result["terminal_return_mode_probability"], 0.0)
        self.assertLessEqual(result["terminal_return_mode_probability"], 100.0)
        self.assertIn(result["terminal_return_selection"], ("analog", "baseline"))
        self.assertEqual(result["terminal_return_method"], model.METHOD)
        self.assertEqual(len(result["terminal_return_top3"]), 3)

    def test_rejects_short_history(self):
        with self.assertRaises(ValueError):
            model.estimate(self.rows(300, 0.001))


if __name__ == "__main__":
    unittest.main()
