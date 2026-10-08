"""Network-free contract tests for frozen block16 model reconstruction."""
from __future__ import annotations

import inspect
import json
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

from rehydrate_frozen_block16_model import (
    BLOCK_INDEX,
    BLOCK_TEST_START,
    CAL_END,
    CAL_START,
    CALIBRATION_SOURCE_ID,
    CONTEXT_FEATURES,
    FROZEN_SOURCE_FINGERPRINT,
    REFERENCE_FILE,
    TRAIN_END,
    _build_model_bundle,
    _hash_rows,
    _pipe,
)


ROOT = Path(__file__).resolve().parent


class FrozenBlock16ModelRehydrationTest(unittest.TestCase):
    def test_reference_is_exact_adopted_action_block16(self):
        ref = json.loads((ROOT / REFERENCE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(ref["block_index"], BLOCK_INDEX)
        self.assertEqual(ref["test_start"], BLOCK_TEST_START)
        self.assertEqual(ref["train_end"], TRAIN_END)
        self.assertEqual(ref["cal_start"], CAL_START)
        self.assertEqual(ref["cal_end"], CAL_END)
        self.assertEqual(
            ref["policy_aligned_residual_quantiles"]["__global__"]["low"],
            -0.10747415305238285,
        )
        self.assertEqual(
            ref["policy_aligned_residual_quantiles"]["__global__"]["n"], 371
        )
        self.assertEqual(
            ref["policy_aligned_residual_quantiles"]["__global__"]["source"],
            CALIBRATION_SOURCE_ID,
        )
        self.assertEqual(ref["calibration_policy_diagnostics"]["rows_before"], 378)
        self.assertEqual(ref["calibration_policy_diagnostics"]["rows_after"], 371)
        self.assertEqual(ref["calibration_policy_diagnostics"]["vetoed_rows"], 7)
        self.assertFalse(
            ref["calibration_policy_diagnostics"]["backfill_allowed"]
        )

    def test_source_identity_is_exact_frozen_action_source(self):
        self.assertEqual(FROZEN_SOURCE_FINGERPRINT["rows"], 2512128)
        self.assertEqual(FROZEN_SOURCE_FINGERPRINT["symbols"], 1089)
        self.assertEqual(
            FROZEN_SOURCE_FINGERPRINT["hash_xor_u64"],
            "17836462952802001740",
        )
        self.assertEqual(
            FROZEN_SOURCE_FINGERPRINT["hash_sum_u64"],
            "17879387804724068608",
        )

    def test_block16_bundle_is_compatible_with_canonical_model_validator(self):
        rng = np.random.default_rng(17)
        x = pd.DataFrame(
            rng.normal(size=(80, len(CONTEXT_FEATURES))),
            columns=CONTEXT_FEATURES,
        )
        y = pd.Series(rng.normal(scale=0.01, size=len(x)))
        model = _pipe()
        model.fit(x, y)
        q = {
            "__global__": {
                "low": -0.1, "med": 0.0, "high": 0.1, "n": 40,
                "source": CALIBRATION_SOURCE_ID,
            },
            "low": {
                "low": -0.1, "med": 0.0, "high": 0.1, "n": 40,
                "source": CALIBRATION_SOURCE_ID,
                "fallback_global": True, "bucket_n": 5,
            },
            "mid": {
                "low": -0.1, "med": 0.0, "high": 0.1, "n": 40,
                "source": CALIBRATION_SOURCE_ID,
                "fallback_global": True, "bucket_n": 8,
            },
            "high": {
                "low": -0.09, "med": 0.01, "high": 0.11, "n": 32,
                "source": CALIBRATION_SOURCE_ID,
                "fallback_global": False,
            },
        }
        bundle = _build_model_bundle(
            model, q,
            training_input_sha256="a" * 64,
            calibration_input_sha256="b" * 64,
        )
        repo_root = ROOT.parent
        sys.path.insert(0, str(repo_root))
        try:
            from research_v1_prospective_model_bundle import validate_model_bundle
            self.assertTrue(validate_model_bundle(bundle)["valid"])
        finally:
            sys.path.pop(0)
        self.assertFalse(bundle["independent_model_admission_verified"])
        self.assertFalse(bundle["signal_generation_complete"])
        self.assertFalse(bundle["live_order_authorized"])

    def test_model_input_hash_is_deterministic_and_order_independent(self):
        rng = np.random.default_rng(9)
        frame = pd.DataFrame(
            rng.normal(size=(12, len(CONTEXT_FEATURES))),
            columns=CONTEXT_FEATURES,
        )
        frame.insert(0, "symbol", [f"{i:06d}" for i in range(len(frame))])
        frame.insert(
            0, "decision_date",
            [pd.Timestamp("2026-01-02")] * len(frame),
        )
        frame["fh_net_return"] = rng.normal(size=len(frame))
        a = _hash_rows(frame)
        b = _hash_rows(frame.sample(frac=1.0, random_state=11))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)

    def test_script_has_no_test_performance_or_holdout_path(self):
        import rehydrate_frozen_block16_model as module
        source = inspect.getsource(module.rehydrate)
        self.assertIn('"test_rows_consumed_for_fit": False', source)
        self.assertIn('"test_outcomes_consumed_for_fit": False', source)
        self.assertIn('"consumed_v1_holdout_artifact_read": False', source)
        self.assertIn('"performance_evaluation_executed": False', source)
        self.assertIn("os.rename(attempt, out_dir)", source)


if __name__ == "__main__":
    unittest.main()
