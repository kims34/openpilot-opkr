import unittest

import pandas as pd

from research_v1_short_swing_compare import (
    BLOCK_LENGTH,
    RECENT_COMMON_OOS_SESSIONS,
    compare_common_oos_paths,
    frozen_short_swing_dominance_audit,
    paired_moving_block_bootstrap_lcb,
)


class ShortSwingComparisonTest(unittest.TestCase):
    def test_only_shared_oos_span_is_compared(self):
        idx = pd.date_range("2026-01-01", periods=25, freq="B")
        h5 = pd.Series(0.01, index=idx[:20])
        h10 = pd.Series(0.02, index=idx[5:])
        out = compare_common_oos_paths(h5, h10)
        self.assertEqual(out["n_days"], 15)
        self.assertEqual(out["common_start"], str(idx[5]))
        self.assertEqual(out["common_end"], str(idx[19]))
        self.assertEqual(out["block_length"], BLOCK_LENGTH)
        self.assertAlmostEqual(out["mean_difference"], 0.01)

    def test_internal_missing_session_is_cash_zero(self):
        idx = pd.date_range("2026-01-01", periods=15, freq="B")
        h5 = pd.Series(0.01, index=idx)
        h10 = pd.Series(0.02, index=idx.delete(7))
        out = compare_common_oos_paths(h5, h10)
        expected = ((14 * 0.01) + (-0.01)) / 15
        self.assertEqual(out["n_days"], 15)
        self.assertAlmostEqual(out["mean_difference"], expected)

    def test_short_series_uses_full_length_blocks_without_short_resamples(self):
        out = paired_moving_block_bootstrap_lcb([0.01, -0.02, 0.03], block_length=10, samples=50)
        self.assertEqual(out["n_days"], 3)
        self.assertEqual(out["block_length"], 3)
        self.assertAlmostEqual(out["mean_difference"], (0.01 - 0.02 + 0.03) / 3)

    def test_empty_path_is_safe(self):
        out = paired_moving_block_bootstrap_lcb([])
        self.assertEqual(out["n_days"], 0)
        self.assertEqual(out["lcb95"], 0.0)

    @staticmethod
    def _dominance_inputs():
        idx = pd.date_range("2020-01-01", periods=600, freq="B")
        h5 = pd.Series(0.0, index=idx)
        h10 = pd.Series(0.001, index=idx)
        h5_view = {
            "mdd": -0.10,
            "daily_portfolio_es95": -0.03,
            "daily_portfolio_es99": -0.05,
        }
        h10_view = {
            "fixed_participation_cost_proxy_mean_net_return": 0.01,
            "profit_factor": 1.5,
            "date_cluster_lcb95": 0.001,
            "mdd": -0.08,
            "daily_portfolio_es95": -0.02,
            "daily_portfolio_es99": -0.04,
        }
        best5 = {
            "mean_net_return": 0.002,
            "profit_factor": 1.1,
            "cluster_bootstrap_95_low": 0.0001,
        }
        cost2 = {"mean_net_return": 0.001, "profit_factor": 1.05}
        recent = {
            "sessions": RECENT_COMMON_OOS_SESSIONS,
            "selected_records": 12,
            "cluster_bootstrap_95_low": 0.0001,
        }
        return h5, h10, h5_view, h10_view, best5, cost2, recent

    def test_full_frozen_dominance_contract_can_pass_only_with_all_evidence(self):
        h5, h10, h5v, h10v, best5, cost2, recent = self._dominance_inputs()
        out = frozen_short_swing_dominance_audit(
            h5,
            h10,
            h5_view=h5v,
            h10_view=h10v,
            h10_best5=best5,
            h10_cost2=cost2,
            h10_recent=recent,
        )
        self.assertTrue(out["all_frozen_dominance_checks_pass"])
        self.assertFalse(out["promotion_allowed"])
        self.assertFalse(out["sealed_holdout_burned"])

    def test_recent_no_admissions_fails_contract(self):
        h5, h10, h5v, h10v, best5, cost2, recent = self._dominance_inputs()
        recent["selected_records"] = 0
        out = frozen_short_swing_dominance_audit(
            h5, h10,
            h5_view=h5v, h10_view=h10v,
            h10_best5=best5, h10_cost2=cost2, h10_recent=recent,
        )
        self.assertFalse(out["all_frozen_dominance_checks_pass"])
        self.assertIn("latest_504_has_admissions", out["failed_checks"])

    def test_worse_daily_es_or_missing_tail_evidence_fails_contract(self):
        h5, h10, h5v, h10v, best5, cost2, recent = self._dominance_inputs()
        h10v["daily_portfolio_es99"] = -0.06
        out = frozen_short_swing_dominance_audit(
            h5, h10,
            h5_view=h5v, h10_view=h10v,
            h10_best5=best5, h10_cost2=cost2, h10_recent=recent,
        )
        self.assertIn("h10_daily_es99_not_worse_than_h5", out["failed_checks"])

        h10v.pop("daily_portfolio_es95")
        out = frozen_short_swing_dominance_audit(
            h5, h10,
            h5_view=h5v, h10_view=h10v,
            h10_best5=best5, h10_cost2=cost2, h10_recent=recent,
        )
        self.assertIn("h10_daily_es95_not_worse_than_h5", out["failed_checks"])


if __name__ == "__main__":
    unittest.main()
