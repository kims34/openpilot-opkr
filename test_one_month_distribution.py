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
        self.assertEqual(result["terminal_return_six_baseline_sample_size"], expected)

    def test_flat_series_mode_is_near_zero(self):
        result = model.estimate(self.rows(900, 0.0))
        self.assertEqual(result["terminal_return_mode_label"], "+0% ~ +2%")
        self.assertGreater(result["terminal_return_mode_probability"], 90.0)
        self.assertEqual(result["terminal_return_mode_direction"], "up")
        bins = result["terminal_return_six_bins"]
        self.assertGreater(bins[2]["probability"], 90.0)

    def test_rising_series_mode_is_positive(self):
        result = model.estimate(self.rows(900, 0.001))
        self.assertGreater(result["terminal_return_mode_midpoint"], 0.0)
        self.assertIn("+", result["terminal_return_mode_label"])
        self.assertGreater(result["terminal_return_six_bins"][2]["probability"], 90.0)

    def test_falling_series_mode_is_negative(self):
        result = model.estimate(self.rows(900, -0.001))
        self.assertLess(result["terminal_return_mode_midpoint"], 0.0)
        self.assertEqual(result["terminal_return_mode_direction"], "down")
        self.assertGreater(result["terminal_return_six_bins"][3]["probability"], 90.0)

    def test_six_bucket_boundaries_are_non_overlapping(self):
        # Every exact boundary belongs to one, and only one, defined bucket.
        self.assertEqual(model._six_class_index(0.1000), 0)
        self.assertEqual(model._six_class_index(0.0999), 1)
        self.assertEqual(model._six_class_index(0.0500), 1)
        self.assertEqual(model._six_class_index(0.0499), 2)
        self.assertEqual(model._six_class_index(0.0000), 2)
        self.assertEqual(model._six_class_index(-0.0001), 3)
        self.assertEqual(model._six_class_index(-0.0500), 3)
        self.assertEqual(model._six_class_index(-0.0501), 4)
        self.assertEqual(model._six_class_index(-0.1000), 4)
        self.assertEqual(model._six_class_index(-0.1001), 5)

    def test_six_bucket_order_and_rounded_total(self):
        price = 100.0
        rows = []
        for i in range(1200):
            rows.append((f"d{i:04d}", price))
            r = 0.012 * math.sin(i / 5.0) + 0.004 * math.sin(i / 31.0) + 0.0002
            price *= max(0.85, 1.0 + r)
        result = model.estimate(rows)
        bins = result["terminal_return_six_bins"]
        self.assertEqual(
            [x["label"] for x in bins],
            ["+10% 이상", "+5% ~ +10%", "0% ~ +5%", "0% ~ -5%", "-5% ~ -10%", "-10% 이하"],
        )
        self.assertEqual(len(bins), 6)
        self.assertAlmostEqual(sum(x["probability"] for x in bins), 100.0, places=7)
        self.assertEqual(result["terminal_return_six_total_probability"], 100.0)
        self.assertIn(result["terminal_return_six_selection"], ("analog", "baseline"))
        self.assertEqual(result["terminal_return_six_method"], model.SIX_METHOD)

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
        for item in result["terminal_return_six_bins"]:
            self.assertGreaterEqual(item["probability"], 0.0)
            self.assertLessEqual(item["probability"], 100.0)

    def test_rejects_short_history(self):
        with self.assertRaises(ValueError):
            model.estimate(self.rows(300, 0.001))


if __name__ == "__main__":
    unittest.main()
