import unittest

import pandas as pd

from research_v1_swing_cpcv import (
    aggregate_cpcv_views,
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


if __name__ == "__main__":
    unittest.main()

