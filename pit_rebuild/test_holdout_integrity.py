"""Synthetic-only tests: no private data, network, metrics or orders."""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import research_kospi_clean_v2 as v2
import evaluate_sealed_holdout as evaluator
import validation_stage_gate as gate
from holdout_training_boundary import training_rows

def synthetic(future_return=0.001):
    dates = pd.bdate_range("2026-01-01", periods=100)
    cutoff = dates[79]
    r = np.full(100, 0.001)
    r[80:] = future_return
    close = 100 * np.cumprod(1+r)
    data = pd.DataFrame({"date":dates, "day_idx":np.arange(100), "code":"123450", "name":"Synthetic", "open":close/(1+r), "close":close, "amount":1000000., "r1":r})
    return v2.engineer(data), data[["day_idx","date"]], cutoff

class BoundaryTests(unittest.TestCase):
    def test_reproduce_original_future_label_leakage(self):
        a, cal, cutoff = synthetic(0.001)
        b, _, _ = synthetic(-0.02)
        original_a = a[a.date <= cutoff].set_index("decision_idx")
        original_b = b[b.date <= cutoff].set_index("decision_idx")
        pd.testing.assert_frame_equal(original_a[v2.FEATURES], original_b[v2.FEATURES])
        self.assertNotEqual(original_a.loc[79, "ret1"], original_b.loc[79, "ret1"])
        self.assertNotEqual(original_a.loc[78, "ret5"], original_b.loc[78, "ret5"])

    def test_fixed_training_is_invariant_to_fresh_outcomes(self):
        a, cal, cutoff = synthetic(0.001)
        b, _, _ = synthetic(-0.02)
        for h in v2.HORIZONS:
            with self.subTest(horizon=h):
                safe_a = training_rows(a, cal, cutoff, h, v2.TRAIN_DAYS, v2.PURGE_DAYS)
                safe_b = training_rows(b, cal, cutoff, h, v2.TRAIN_DAYS, v2.PURGE_DAYS)
                pd.testing.assert_frame_equal(safe_a[v2.FEATURES+[f"ret{h}"]], safe_b[v2.FEATURES+[f"ret{h}"]])
                self.assertLess(int(safe_a.decision_idx.max()), 75)

    def test_original_training_length_is_preserved(self):
        obs, cal, cutoff = synthetic()
        safe = training_rows(obs, cal, cutoff, 1, 10, v2.PURGE_DAYS)
        self.assertEqual(safe.decision_idx.tolist(), list(range(65,75)))

    def test_insufficient_purge_is_rejected(self):
        obs, cal, cutoff = synthetic()
        with self.assertRaises(ValueError): training_rows(obs,cal,cutoff,5,1260,4)

    def test_calendar_gap_is_rejected(self):
        obs, cal, cutoff = synthetic()
        with self.assertRaises(ValueError): training_rows(obs,cal.drop(index=40),cutoff,1,1260,5)

    def test_duplicate_date_is_rejected(self):
        obs, cal, cutoff = synthetic()
        cal.loc[40,"date"] = cal.loc[39,"date"]
        with self.assertRaises(ValueError): training_rows(obs,cal,cutoff,1,1260,5)

    def test_forged_decision_binding_is_rejected(self):
        obs, cal, cutoff = synthetic()
        obs.loc[obs.decision_idx==60,"date"] = pd.Timestamp("2099-01-01")
        with self.assertRaises(ValueError): training_rows(obs,cal,cutoff,1,1260,5)

    def test_retired_evaluator_cannot_read_or_fit(self):
        with patch.object(evaluator.pd,"read_parquet",side_effect=AssertionError("private data access")) as read, patch.object(evaluator.v3,"model",side_effect=AssertionError("model execution")) as model:
            with self.assertRaisesRegex(SystemExit,"EVAL_RETIRED"):
                evaluator.main()
            read.assert_not_called()
            model.assert_not_called()

    def test_consumed_gate_blocks_even_if_manifest_claims_sealed(self):
        with tempfile.TemporaryDirectory() as root:
            baseline = Path(root)/"baseline"
            result = Path(root)/"result.json"
            baseline.touch()
            result.write_text('{"passed":false}')
            with patch.object(gate,"BASELINE",baseline), patch.object(gate,"SEALED_RESULT",result), patch.object(gate,"load_json",side_effect=AssertionError("manifest access after consumed result")):
                with self.assertRaisesRegex(SystemExit,"window is consumed"):
                    gate.check("sealed_holdout")

if __name__ == "__main__": unittest.main()
