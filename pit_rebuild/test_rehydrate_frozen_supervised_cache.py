"""Network-free contract tests for frozen supervised rehydration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import inspect
import tempfile
import unittest

import pandas as pd

from rehydrate_frozen_supervised_cache import (
    FROZEN_MODULE_BLOBS,
    _attach_record_columns_low_memory,
    FrozenSupervisedRehydrationError,
    load_reference,
    require_exact_meta,
    supervised_logical_fingerprint,
    validate_frozen_modules,
    validate_supervised_verification,
)


ROOT = Path(__file__).resolve().parent


class FrozenSupervisedRehydrationTest(unittest.TestCase):
    def test_vendored_modules_are_exact_frozen_git_blobs(self):
        self.assertEqual(validate_frozen_modules(ROOT), FROZEN_MODULE_BLOBS)

    def test_reference_is_exact_recovered_action_supervised_contract(self):
        reference, digest = load_reference(ROOT)
        self.assertEqual(reference["rows"], 2486909)
        self.assertEqual(reference["records"], 2484241)
        self.assertEqual(reference["diagnostics"]["ambiguous_same_bar"], 55604)
        self.assertEqual(reference["diagnostics"]["entry_no_fill"], 2668)
        self.assertEqual(
            reference["diagnostics"]["post_entry_missing_future_bar_conservative_stop"],
            7274,
        )
        self.assertEqual(
            reference["diagnostics"]["insufficient_global_future_horizon"],
            4561,
        )
        self.assertEqual(len(digest), 64)

    def test_reference_comparison_is_exact_not_threshold_based(self):
        reference, _ = load_reference(ROOT)
        require_exact_meta(reference, reference)
        changed = json.loads(json.dumps(reference))
        changed["diagnostics"]["entry_no_fill"] += 1
        with self.assertRaisesRegex(
            FrozenSupervisedRehydrationError, "metadata mismatch"
        ):
            require_exact_meta(changed, reference)

    def test_logical_fingerprint_is_stable_under_row_reordering(self):
        frame = pd.DataFrame([
            {
                "decision_date": "2026-01-02", "symbol": "000002",
                "x": 2.0, "rec_outcome": None,
            },
            {
                "decision_date": "2026-01-02", "symbol": "000001",
                "x": 1.0, "rec_outcome": "time",
            },
        ])
        a = supervised_logical_fingerprint(frame)
        b = supervised_logical_fingerprint(frame.iloc[::-1].reset_index(drop=True))
        self.assertEqual(a, b)
        self.assertEqual(a["record_rows"], 1)

    def test_low_memory_record_attachment_matches_frozen_merge_semantics(self):
        frozen_dir = ROOT / "frozen_supervised_v1"
        import sys
        sys.path.insert(0, str(frozen_dir))
        try:
            from research_v1_core import DecisionRecord
        finally:
            sys.path.pop(0)

        frame = pd.DataFrame([
            {
                "decision_date": pd.Timestamp("2026-01-02"),
                "symbol": "000001",
                "x": 1.0,
            },
            {
                "decision_date": pd.Timestamp("2026-01-02"),
                "symbol": "000002",
                "x": 2.0,
            },
        ])
        rec = DecisionRecord(
            decision_day=pd.Timestamp("2026-01-02").date(),
            entry_day=pd.Timestamp("2026-01-05").date(),
            symbol="000001",
            score=0.0,
            entry_price=100.0,
            horizon=5,
            target_return=0.04,
            stop_return=-0.025,
            cost_return=0.003,
            outcome="TIME",
            gross_return=0.01,
            net_return=0.007,
            exit_day=pd.Timestamp("2026-01-09").date(),
            exit_price=101.0,
        )
        out = _attach_record_columns_low_memory(
            frame.copy(), {(rec.decision_day, rec.symbol): rec}
        )
        self.assertEqual(out.loc[0, "rec_outcome"], "TIME")
        self.assertEqual(float(out.loc[0, "rec_horizon"]), 5.0)
        self.assertEqual(float(out.loc[0, "rec_net_return"]), 0.007)
        self.assertTrue(pd.isna(out.loc[1, "rec_outcome"]))
        self.assertTrue(pd.isna(out.loc[1, "rec_entry_price"]))
        self.assertTrue(pd.isna(out.loc[1, "rec_entry_day"]))

    def test_low_memory_writer_does_not_reintroduce_frozen_rec_rows_list(self):
        source = inspect.getsource(
            __import__("rehydrate_frozen_supervised_cache")
            ._build_cache_low_memory
        )
        self.assertNotIn("rec_rows = []", source)
        self.assertNotIn("rec_df =", source)
        self.assertNotIn(".merge(rec_df", source)

    def test_verification_never_grants_model_alpha_or_live_authority(self):
        body = {
            "classification": "FROZEN_SUPERVISED_CACHE_REHYDRATION_VERIFIED",
            "frozen_action_id": 36643183157,
            "frozen_artifact_id": 11067383547,
            "frozen_artifact_digest": "sha256:c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f",
            "frozen_run_head_sha": "4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d",
            "long_history_verification_sha256": "1" * 64,
            "reference_sha256": "2" * 64,
            "frozen_module_git_blobs": dict(FROZEN_MODULE_BLOBS),
            "runtime_versions": {
                "python": "3.12.14", "pandas": "2.3.3",
                "numpy": "2.5.3", "pyarrow": "21.0.0",
            },
            "supervised_logical_fingerprint": {
                "rows": 2486909, "columns": ["a"], "dtypes": ["float64"],
                "date_min": "2015-06-15", "date_max": "2026-09-23",
                "symbols": 1089, "record_rows": 2484241,
                "hash_xor_u64": "1", "hash_sum_u64": "2",
            },
            "supervised_parquet_sha256": "3" * 64,
            "meta_sha256": "4" * 64,
            "exact_reference_meta_match": True,
            "consumed_holdout_artifact_read": False,
            "performance_evaluation_executed": False,
            "model_fit_executed": False,
            "historical_decision_backfill_created": False,
            "fresh_alpha_observation_admitted": False,
            "promotion_authority": False,
            "live_order_authorized": False,
        }
        record = {
            **body,
            "verification_sha256": hashlib.sha256(
                json.dumps(
                    body, ensure_ascii=False, sort_keys=True,
                    separators=(",", ":"), allow_nan=False,
                ).encode("utf-8")
            ).hexdigest(),
        }
        self.assertTrue(validate_supervised_verification(record)["valid"])
        changed = dict(record)
        changed["model_fit_executed"] = True
        with self.assertRaises(FrozenSupervisedRehydrationError):
            validate_supervised_verification(changed)


if __name__ == "__main__":
    unittest.main()
