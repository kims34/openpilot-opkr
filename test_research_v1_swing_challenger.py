import unittest

from research_v1_swing_challenger import (
    ALLOWED_SWING_HORIZONS,
    CAL_DAYS,
    TEST_DAYS,
    TOP_K,
    TRAIN_DAYS,
    _robustness_flags,
)


class SwingChallengerProtocolTest(unittest.TestCase):
    def test_preregistered_horizons(self):
        self.assertEqual(ALLOWED_SWING_HORIZONS, (10, 20))
        self.assertEqual(TOP_K, 3)
        self.assertEqual(TRAIN_DAYS, 504)
        self.assertEqual(CAL_DAYS, 126)
        self.assertEqual(TEST_DAYS, 126)

    def test_robustness_flags_require_every_gate(self):
        candidate = {
            "market_eligibility_overlay": {
                "metrics": {
                    "mean_net_return": 0.01,
                    "profit_factor": 1.2,
                    "cluster_bootstrap_95_low": 0.001,
                },
                "extreme_day_dependency": {
                    "remove_best_days": {
                        "5": {"metrics": {"mean_net_return": 0.002}}
                    }
                },
                "cost_stress": {
                    "2.0": {"mean_net_return": 0.001}
                },
            }
        }
        flags = _robustness_flags(candidate)
        self.assertTrue(flags["all_developmental_robustness_checks_pass"])
        candidate["market_eligibility_overlay"]["metrics"]["cluster_bootstrap_95_low"] = -0.001
        flags = _robustness_flags(candidate)
        self.assertFalse(flags["all_developmental_robustness_checks_pass"])


if __name__ == "__main__":
    unittest.main()
