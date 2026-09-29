import unittest

import numpy as np
import pandas as pd

from research_v1_selected_calibration import _cluster_bootstrap_q25_diagnostic

from research_v1_swing_cpcv import (
    aggregate_cpcv_views,
    calibration_sensitivity,
    cpcv_assignments,
)


class SwingCpcvProtocolTest(unittest.TestCase):
    def test_assignments_are_disjoint_and_purged(self):
        dates = list(pd.date_range("2015-01-01", periods=1800, freq="B"))
        assignments = cpcv_assignments(dates, horizon=10)
        self.assertEqual(len(assignments), 60)
        positions = {pd.Timestamp(d): i for i, d in enumerate(dates)}
        for split in assignments:
            train = set(split["train_dates"])
            cal = set(split["cal_dates"])
            test = set(split["test_dates"])
            self.assertFalse(train & cal)
            self.assertFalse(train & test)
            self.assertFalse(cal & test)
            protected_positions = {positions[d] for d in cal | test}
            for d in train:
                self.assertTrue(all(
                    abs(positions[d] - p) > 10 for p in protected_positions
                ))

    def test_only_short_h5_and_swing_h10_are_allowed(self):
        dates = list(pd.date_range("2015-01-01", periods=1800, freq="B"))
        cpcv_assignments(dates, horizon=5)
        cpcv_assignments(dates, horizon=10)
        with self.assertRaises(ValueError):
            cpcv_assignments(dates, horizon=20)

    def test_aggregate_uses_fold_distribution_not_pooled_duplicate_rows(self):
        base = {
            "precision_at_selected": 0.5,
            "fixed_participation_cost_proxy_mean_net_return": 0.01,
            "profit_factor": 1.2,
            "mdd": -0.1,
            "es95": -0.05,
            "es99": -0.08,
            "date_cluster_lcb95": 0.001,
        }
        weak = dict(base)
        weak["fixed_participation_cost_proxy_mean_net_return"] = -0.02
        weak["profit_factor"] = 0.8
        weak["date_cluster_lcb95"] = -0.01
        out = aggregate_cpcv_views([base, weak])
        self.assertEqual(out["splits_evaluated"], 2)
        self.assertEqual(out["fraction_positive_net_ev"], 0.5)
        self.assertEqual(out["fraction_pf_gt_1"], 0.5)
        self.assertEqual(out["fraction_positive_cluster_lcb"], 0.5)


    def test_calibration_sensitivity_detects_sign_flip_and_abstention(self):
        def row(cal, net, trades):
            return {
                "split": {"test_group_ids": [0, 1], "cal_group_id": cal},
                "comparison_view": {
                    "fixed_participation_cost_proxy_mean_net_return": net,
                    "selected_records": trades,
                },
            }
        out = calibration_sensitivity([
            row(2, 0.01, 4),
            row(3, -0.02, 0),
            row(4, 0.03, 8),
            row(5, -0.01, 2),
        ])
        self.assertEqual(out["test_combinations"], 1)
        self.assertEqual(out["fraction_net_ev_sign_flip"], 1.0)
        self.assertEqual(out["fraction_some_calibration_all_abstain"], 1.0)
        self.assertAlmostEqual(out["median_net_ev_range"], 0.05)
        self.assertEqual(out["median_trade_count_range"], 8.0)

    def test_each_test_combination_has_all_four_calibration_groups(self):
        dates = list(pd.date_range("2015-01-01", periods=1800, freq="B"))
        assignments = cpcv_assignments(dates, horizon=10)
        grouped = {}
        for split in assignments:
            grouped.setdefault(tuple(split["test_group_ids"]), set()).add(split["cal_group_id"])
        self.assertEqual(len(grouped), 15)
        for test_groups, cal_groups in grouped.items():
            self.assertEqual(len(cal_groups), 4)
            self.assertEqual(cal_groups, set(range(6)) - set(test_groups))


    def test_q25_uncertainty_diagnostic_is_deterministic_and_clustered(self):
        rows = []
        for day, base in zip(pd.date_range("2026-01-01", periods=20, freq="B"), np.linspace(-0.03, 0.03, 20)):
            for j in range(3):
                rows.append({"decision_date": day, "residual": float(base + j * 0.001)})
        frame = pd.DataFrame(rows)
        a = _cluster_bootstrap_q25_diagnostic(frame, reps=100)
        b = _cluster_bootstrap_q25_diagnostic(frame, reps=100)
        self.assertEqual(a, b)
        self.assertEqual(a["rows"], 60)
        self.assertEqual(a["days"], 20)
        self.assertGreaterEqual(a["bootstrap_p95"], a["bootstrap_p05"])
        self.assertTrue(a["diagnostic_only"])


if __name__ == "__main__":
    unittest.main()
