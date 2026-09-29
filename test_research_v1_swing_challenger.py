import unittest
from datetime import date

from research_v1_core import DecisionRecord
from research_v1_distributional_netev import _metric
from research_v1_swing_challenger import (
    ALLOWED_SWING_HORIZONS,
    CAL_DAYS,
    TEST_DAYS,
    TOP_K,
    TRAIN_DAYS,
    _comparison_view,
    _robustness_flags,
)


class SwingChallengerProtocolTest(unittest.TestCase):
    def test_preregistered_horizons(self):
        self.assertEqual(ALLOWED_SWING_HORIZONS, (10,))
        self.assertEqual(TOP_K, 3)
        self.assertEqual(TRAIN_DAYS, 504)
        self.assertEqual(CAL_DAYS, 126)
        self.assertEqual(TEST_DAYS, 126)

    @staticmethod
    def _robust_candidate():
        return {
            "market_eligibility_overlay": {
                "metrics": {
                    "mean_net_return": 0.01,
                    "profit_factor": 1.2,
                    "cluster_bootstrap_95_low": 0.001,
                },
                "extreme_day_dependency": {
                    "remove_best_days": {
                        "5": {"metrics": {
                            "mean_net_return": 0.002,
                            "profit_factor": 1.1,
                            "cluster_bootstrap_95_low": 0.0002,
                        }}
                    }
                },
                "cost_stress": {
                    "2.0": {"mean_net_return": 0.001, "profit_factor": 1.05}
                },
            }
        }

    def test_robustness_flags_require_every_frozen_gate(self):
        candidate = self._robust_candidate()
        flags = _robustness_flags(candidate)
        self.assertTrue(flags["all_developmental_robustness_checks_pass"])

        candidate["market_eligibility_overlay"]["metrics"]["cluster_bootstrap_95_low"] = -0.001
        self.assertFalse(_robustness_flags(candidate)["all_developmental_robustness_checks_pass"])

    def test_best5_requires_mean_pf_and_cluster_lcb(self):
        candidate = self._robust_candidate()
        best5 = candidate["market_eligibility_overlay"]["extreme_day_dependency"]["remove_best_days"]["5"]["metrics"]
        best5["cluster_bootstrap_95_low"] = -0.0001
        flags = _robustness_flags(candidate)
        self.assertFalse(flags["positive_after_remove_best_5_days"])
        self.assertFalse(flags["all_developmental_robustness_checks_pass"])

        candidate = self._robust_candidate()
        candidate["market_eligibility_overlay"]["extreme_day_dependency"]["remove_best_days"]["5"]["metrics"]["profit_factor"] = 1.0
        flags = _robustness_flags(candidate)
        self.assertFalse(flags["positive_after_remove_best_5_days"])

    def test_2x_cost_requires_mean_and_pf(self):
        candidate = self._robust_candidate()
        candidate["market_eligibility_overlay"]["cost_stress"]["2.0"]["profit_factor"] = 1.0
        flags = _robustness_flags(candidate)
        self.assertFalse(flags["positive_at_2x_cost"])
        self.assertFalse(flags["all_developmental_robustness_checks_pass"])

    def test_trade_metrics_still_report_both_tail_levels(self):
        def rec(day, net):
            return DecisionRecord(
                decision_day=day,
                entry_day=day,
                symbol=str(net),
                score=1.0,
                entry_price=100.0,
                horizon=10,
                target_return=0.04,
                stop_return=-0.025,
                cost_return=0.002,
                outcome="TIME",
                gross_return=net + 0.002,
                net_return=net,
                exit_day=day,
                exit_price=100.0 * (1.0 + net + 0.002),
            )

        metrics = _metric([
            rec(date(2026, 1, 2), 0.03),
            rec(date(2026, 1, 3), -0.01),
            rec(date(2026, 1, 4), -0.05),
        ])
        self.assertAlmostEqual(metrics["precision_at_selected"], 1.0 / 3.0)
        self.assertAlmostEqual(metrics["trade_expected_shortfall_95"], -0.05)
        self.assertAlmostEqual(metrics["trade_expected_shortfall_99"], -0.05)

    def test_comparison_view_uses_daily_portfolio_es_for_dominance(self):
        candidate = {
            "market_eligibility_overlay": {
                "selected_records": 2,
                "trade_days": 1,
                "trade_day_coverage": 0.1,
                "metrics": {
                    "precision_at_selected": 0.5,
                    "mean_net_return": 0.01,
                    "profit_factor": 1.1,
                    "trade_expected_shortfall_95": -0.20,
                    "trade_expected_shortfall_99": -0.30,
                    "cluster_bootstrap_95_low": -0.01,
                },
                "portfolio": {
                    "max_drawdown": -0.04,
                    "daily_expected_shortfall_95": -0.02,
                    "daily_expected_shortfall_99": -0.03,
                },
            }
        }
        view = _comparison_view(candidate)
        self.assertEqual(view["selected_records"], 2)
        self.assertEqual(view["fixed_participation_cost_proxy_mean_net_return"], 0.01)
        self.assertEqual(view["es95"], -0.02)
        self.assertEqual(view["es99"], -0.03)
        self.assertEqual(view["daily_portfolio_es95"], -0.02)
        self.assertEqual(view["daily_portfolio_es99"], -0.03)
        self.assertEqual(view["trade_es95"], -0.20)
        self.assertEqual(view["trade_es99"], -0.30)
        self.assertFalse(view["cost_model"]["capacity_curve_available"])


if __name__ == "__main__":
    unittest.main()
