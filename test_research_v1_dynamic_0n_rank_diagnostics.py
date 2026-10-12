"""Synthetic non-leakage checks for Dynamic 0-N outcome-independent ranks."""
from __future__ import annotations
import copy
import unittest

import pandas as pd

from research_v1_dynamic_0n_rank_diagnostics import rank_diagnostics


def samples():
    return pd.DataFrame([
        {"decision_date": "2026-02-02", "symbol": "AAAAAA", "netev_low": .9,
         "fh_label_available": False, "fh_net_return": None},
        {"decision_date": "2026-02-02", "symbol": "BBBBBB", "netev_low": .8,
         "fh_label_available": True, "fh_net_return": .1},
        {"decision_date": "2026-02-02", "symbol": "CCCCCC", "netev_low": .7,
         "fh_label_available": True, "fh_net_return": -.05},
        {"decision_date": "2026-02-02", "symbol": "DDDDDD", "netev_low": .6,
         "fh_label_available": False, "fh_net_return": None},
        {"decision_date": "2026-02-02", "symbol": "EEEEEE", "netev_low": .5,
         "fh_label_available": True, "fh_net_return": .2},
        {"decision_date": "2026-02-03", "symbol": "AAAAAA", "netev_low": .4,
         "fh_label_available": True, "fh_net_return": .3},
        {"decision_date": "2026-02-03", "symbol": "BBBBBB", "netev_low": -.1,
         "fh_label_available": False, "fh_net_return": None},
    ])


class DiagnosticRankLeakageTests(unittest.TestCase):
    def test_rank_before_label_observability_with_missing_rank1(self):
        out = rank_diagnostics(samples())
        self.assertFalse(out["ranking_uses_future_labels"])
        self.assertEqual(out["r1_3"]["ranked_rows"], 5)
        self.assertEqual(out["r1_3"]["missing_outcome_rows"], 2)
        self.assertEqual(out["r1_3"]["rows"], 3)
        self.assertAlmostEqual(out["r1_3"]["mean_net_return"], (.1-.05+.3)/3)
        # The rank-5 outcome may not be relabeled rank 3 by dropping
        # rank 1 and rank 4 merely because their future labels are absent.
        self.assertEqual(out["r4_5"]["ranked_rows"], 2)
        self.assertEqual(out["r4_5"]["rows"], 1)
        self.assertAlmostEqual(out["r4_5"]["mean_net_return"], .2)
        self.assertEqual(out["r4_5"]["missing_outcome_rows"], 1)
        self.assertEqual(out["positive_candidate_count_by_day"]["max"], 5)
        self.assertEqual(out["positive_candidate_count_by_day"]["days_gt3"], 1)
        self.assertEqual(out["positive_candidate_count_by_day"]["days_with_any"], 2)

    def test_missing_future_labels_cannot_move_ranks_or_positive_counts(self):
        frame = samples()
        a = rank_diagnostics(frame)
        b = frame.copy()
        b.loc[b.symbol=="AAAAAA", "fh_label_available"] = False
        b.loc[b.symbol=="AAAAAA", "fh_net_return"] = None
        changed = rank_diagnostics(b)
        for band in ("r1_3", "r4_5", "r6_10", "r11_plus"):
            self.assertEqual(a[band]["ranked_rows"], changed[band]["ranked_rows"])
        self.assertEqual(a["positive_candidate_count_by_day"],
                         changed["positive_candidate_count_by_day"])

    def test_score_tie_decided_by_symbol_not_future_outcome_or_input_order(self):
        f = samples()
        f.loc[f.symbol=="CCCCCC", "netev_low"] = .8
        a = rank_diagnostics(f)
        b = rank_diagnostics(f.iloc[::-1].reset_index(drop=True))
        self.assertEqual(a, b)

    def test_unknown_outcomes_do_not_become_zero_returns(self):
        f = samples()
        f["fh_label_available"] = False
        out = rank_diagnostics(f)
        self.assertEqual(out["r1_3"]["rows"], 0)
        self.assertIsNone(out["r1_3"]["mean_net_return"])
        self.assertEqual(out["positive_candidate_count_by_day"]["max"], 5)

    def test_duplicate_decision_symbol_rejected_instead_of_double_rank(self):
        f = samples()
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS"):
            rank_diagnostics(pd.concat([f, f.iloc[[0]]],ignore_index=True))

    def test_empty_frame_cannot_be_misreported_as_zero_profitability(self):
        x = samples().iloc[:0].copy()
        out = rank_diagnostics(x)
        self.assertIsNone(out["r1_3"]["mean_net_return"])
        self.assertEqual(out["r1_3"]["rows"], 0)
        self.assertFalse(out["ranking_uses_future_labels"])


if __name__=="__main__":
    unittest.main()
