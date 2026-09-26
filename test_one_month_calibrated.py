import math
import unittest

import one_month_calibrated as model


class CalibratedOneMonthTest(unittest.TestCase):
    @staticmethod
    def rows(count=1000):
        price = 100.0
        out = []
        for i in range(count):
            out.append((f"d{i:04d}", price))
            # Deterministic but non-trivial regime changes.
            r = 0.007 * math.sin(i / 11.0) + 0.003 * math.sin(i / 37.0) + 0.00015
            price *= max(0.90, 1.0 + r)
        return out

    def test_blend_is_convex(self):
        self.assertAlmostEqual(model._blend(0.2, 0.8, 0.0), 0.2)
        self.assertAlmostEqual(model._blend(0.2, 0.8, 0.5), 0.5)
        self.assertAlmostEqual(model._blend(0.2, 0.8, 1.0), 0.8)

    def test_barrier_output_is_bounded_and_guarded(self):
        result = model.estimate_probability(self.rows())
        self.assertIn(result["blend_weight_up"], model.BLEND_WEIGHTS)
        self.assertIn(result["blend_weight_down"], model.BLEND_WEIGHTS)
        self.assertIn(result["selection_up"], ("baseline", "analog"))
        self.assertIn(result["selection_down"], ("baseline", "analog"))
        self.assertGreaterEqual(result["up_10_probability"], 0.0)
        self.assertLessEqual(result["up_10_probability"], 100.0)
        self.assertGreaterEqual(result["down_10_probability"], 0.0)
        self.assertLessEqual(result["down_10_probability"], 100.0)
        if result["blend_weight_up"] > 0:
            self.assertGreater((result["validation_up"] or {}).get("skill", 0.0), 0.0)
            self.assertGreater((result["validation_up_first_half"] or {}).get("skill", 0.0), 0.0)
            self.assertGreater((result["validation_up_second_half"] or {}).get("skill", 0.0), 0.0)
        if result["blend_weight_down"] > 0:
            self.assertGreater((result["validation_down"] or {}).get("skill", 0.0), 0.0)
            self.assertGreater((result["validation_down_first_half"] or {}).get("skill", 0.0), 0.0)
            self.assertGreater((result["validation_down_second_half"] or {}).get("skill", 0.0), 0.0)

    def test_six_bins_sum_to_100_and_use_guardrail(self):
        result = model.estimate_distribution(self.rows(1100))
        bins = result["terminal_return_six_bins"]
        self.assertEqual(len(bins), 6)
        self.assertAlmostEqual(sum(x["probability"] for x in bins), 100.0, places=7)
        self.assertIn(result["terminal_return_six_blend_weight"], model.BLEND_WEIGHTS)
        self.assertIn(result["terminal_return_six_selection"], ("baseline", "analog"))
        if result["terminal_return_six_blend_weight"] > 0:
            self.assertGreater((result["terminal_return_six_validation"] or {}).get("skill", 0.0), 0.0)
            self.assertGreater((result["terminal_return_six_validation_first_half"] or {}).get("skill", 0.0), 0.0)
            self.assertGreater((result["terminal_return_six_validation_second_half"] or {}).get("skill", 0.0), 0.0)

    def test_short_history_rejected(self):
        with self.assertRaises(ValueError):
            model.estimate_probability(self.rows(300))
        with self.assertRaises(ValueError):
            model.estimate_distribution(self.rows(300))


if __name__ == "__main__":
    unittest.main()
