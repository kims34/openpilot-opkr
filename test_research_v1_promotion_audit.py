import unittest
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from research_v1_promotion_audit import promotion_evidence_audit


class PromotionAuditRegressionTest(unittest.TestCase):
    def test_best5_requires_positive_cluster_lcb_not_only_mean_and_pf(self):
        start = date(2026, 1, 1)
        records = [
            SimpleNamespace(decision_day=start + timedelta(days=i), net_return=0.01)
            for i in range(6)
        ]
        pred = pd.DataFrame({
            "decision_date": pd.to_datetime([start + timedelta(days=i) for i in range(6)])
        })

        robust = {
            "mean_net_return": 0.01,
            "profit_factor": 1.5,
            "cluster_bootstrap_95_low": 0.001,
        }
        best5_lcb_failure = {
            "mean_net_return": 0.02,
            "profit_factor": 1.8,
            "cluster_bootstrap_95_low": -0.001,
        }
        # _metric call order: overall, recent, remove-best-1, remove-best-3,
        # remove-best-5. Keep everything robust except the frozen best-5 LCB.
        with patch(
            "research_v1_promotion_audit._metric",
            side_effect=[robust, robust, robust, robust, best5_lcb_failure],
        ):
            out = promotion_evidence_audit(
                records,
                pred,
                recent_test_sessions=6,
                cost_stress={"2.0": {"mean_net_return": 0.001, "profit_factor": 1.1}},
            )

        self.assertFalse(out["evidence_flags"]["jackpot_independent_after_best5_days"])
        self.assertIn(
            "BEST_5_DECISION_DAY_ROBUSTNESS_FAILS_MEAN_PF_OR_CLUSTER_LCB",
            out["blockers"],
        )
        self.assertEqual(out["classification"], "DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE")


if __name__ == "__main__":
    unittest.main()
