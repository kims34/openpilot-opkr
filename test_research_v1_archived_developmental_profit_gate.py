"""Synthetic tests: costed historical upside must not masquerade as promoted alpha."""
from __future__ import annotations
import copy
import math
import unittest

from research_v1_archived_developmental_profit_gate import (
    ARCHIVED_DYNAMIC_EXPERIMENT, ARCHIVED_DYNAMIC_STAGE,
    ARCHIVED_RANKAWARE_EXPERIMENT, ARCHIVED_RANKAWARE_STAGE,
    POLICIES, DevelopmentalEvidenceError, adjudicate_archived_developmental_results,
)


def policy(*, mean=.016, lower=-.0007, after_best=-.007, max_n=719):
    return {
        "metrics": {
            "mean_net_return": mean, "profit_factor": 1.6, "trades": 100,
            "cluster_bootstrap_95_low": lower,
        },
        "portfolio": {
            "sessions": 2105, "cagr_252": .02, "max_drawdown": -.15,
            "daily_expected_shortfall_95": -.005,
            "daily_expected_shortfall_99": -.02,
            "max_concurrent_positions": 733,
        },
        "cost_stress": {
            "2.0": {"mean_net_return": .012, "profit_factor": 1.4}
        },
        "extreme_day_dependency": {
            "remove_best_days": {
                "5": {"metrics": {
                    "mean_net_return": after_best,
                    "profit_factor": .75,
                    "cluster_bootstrap_95_low": -.005,
                }}
            }
        },
        "selected_n_by_trade_day": {"max": max_n},
    }


def valid_reports():
    d = {
        "experiment": ARCHIVED_DYNAMIC_EXPERIMENT,
        "stage": ARCHIVED_DYNAMIC_STAGE,
        "frozen": {
            "horizon": 5, "train_days": 504, "cal_days": 126,
            "test_days": 126, "purge_days": 5, "sealed_holdout_touched": False,
        },
        "policies": {key: policy() for key in POLICIES},
    }
    r = {
        "experiment": ARCHIVED_RANKAWARE_EXPERIMENT,
        "stage": ARCHIVED_RANKAWARE_STAGE,
        "protocol": {"sealed_holdout_touched": False},
        "result": policy(mean=.018, lower=-.024, after_best=-.016, max_n=722),
        "selected_n": {"max": 722},
    }
    return d, r


class ArchivedDevelopmentalProfitGateTests(unittest.TestCase):
    def test_positive_trade_mean_cagr_and_double_cost_are_insufficient(self):
        d,r=valid_reports()
        out=adjudicate_archived_developmental_results(d,r)
        self.assertEqual(out["candidates_checked"],5)
        self.assertEqual(out["candidates_passing_all_observed_robustness"],0)
        self.assertTrue(all(c["mean_net_return_pct"]>0 for c in out["candidates"]))
        self.assertTrue(all(c["twice_cost_mean_net_return_pct"]>0 for c in out["candidates"]))
        self.assertTrue(all(not c["promotion_authorized"] for c in out["candidates"]))
        self.assertTrue(all(c["date_cluster_lcb95_pct"]<0 for c in out["candidates"]))
        self.assertEqual(out["ordering"],"DISABLED")
        self.assertFalse(out["independent_holdout_read"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertEqual(out["developmental_replays_performed"],0)

    def test_genuine_developmental_robustness_still_cannot_promote(self):
        d,r=valid_reports()
        for p in list(d["policies"].values())+[r["result"]]:
            p["metrics"]["cluster_bootstrap_95_low"] = .005
            q = p["extreme_day_dependency"]["remove_best_days"]["5"]["metrics"]
            q.update(mean_net_return=.01, profit_factor=1.2,
                     cluster_bootstrap_95_low=.003)
        out=adjudicate_archived_developmental_results(d,r)
        self.assertEqual(out["candidates_passing_all_observed_robustness"],5)
        self.assertFalse(out["independent_holdout_authorized"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertFalse(out["m20_performance_run_authorized"])

    def test_100k_capital_concurrent_count_not_a_tradability_claim(self):
        d,r=valid_reports()
        out=adjudicate_archived_developmental_results(d,r)
        a=out["candidates"][3];b=out["candidates"][4]
        self.assertEqual(a["max_concurrent_positions"],733)
        self.assertEqual(a["max_admitted_names_same_decision_day"],719)
        self.assertEqual(a["hypothetical_equal_cohort_krw_per_name_at_max_n"],27.82)
        self.assertEqual(b["max_admitted_names_same_decision_day"],722)
        self.assertEqual(b["hypothetical_equal_cohort_krw_per_name_at_max_n"],27.70)
        self.assertFalse(a["verified_krw_round_lot_capacity"])
        self.assertFalse(b["verified_krw_round_lot_capacity"])

    def test_missing_metrics_fail_closed_instead_of_zero_imputation(self):
        d,r=valid_reports()
        del d["policies"][POLICIES[0]]["metrics"]["cluster_bootstrap_95_low"]
        with self.assertRaises(DevelopmentalEvidenceError):
            adjudicate_archived_developmental_results(d,r)

    def test_nonfinite_return_or_pf_rejected(self):
        for value in [None, float("nan"), float("inf"), "1.0"]:
            d,r=valid_reports()
            d["policies"][POLICIES[0]]["metrics"]["mean_net_return"]=value
            with self.subTest(value=value),self.assertRaises(DevelopmentalEvidenceError):
                adjudicate_archived_developmental_results(d,r)

    def test_cross_cohort_or_holdout_protocol_change_rejected(self):
        for fn in [
            lambda d,r:d["frozen"].update(train_days=250),
            lambda d,r:d["frozen"].update(sealed_holdout_touched=True),
            lambda d,r:r["protocol"].update(sealed_holdout_touched=True),
            lambda d,r:d.update(experiment="FUTURE_POST_SELECTION"),
            lambda d,r:d["policies"].pop(POLICIES[-1]),
        ]:
            d,r=valid_reports();fn(d,r)
            with self.assertRaises(DevelopmentalEvidenceError):
                adjudicate_archived_developmental_results(d,r)


if __name__=="__main__":
    unittest.main()
