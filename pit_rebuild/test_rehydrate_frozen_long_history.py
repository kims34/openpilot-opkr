"""Network-free tests for frozen long-history source rehydration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from rehydrate_frozen_long_history import (
    EXPECTED_SOURCE_FINGERPRINT,
    FROZEN_BUILDER_GIT_BLOB_SHA1,
    FrozenLongHistoryError,
    git_blob_sha1,
    require_exact_fingerprint,
    source_fingerprint,
    validate_builder,
    validate_verification,
)


ROOT = Path(__file__).resolve().parent


class FrozenLongHistoryRehydrationTest(unittest.TestCase):
    def test_current_pit_builder_is_exact_frozen_git_blob(self):
        builder = ROOT / "research_v1_marcap.py"
        self.assertEqual(
            validate_builder(builder),
            FROZEN_BUILDER_GIT_BLOB_SHA1,
        )

    def test_git_blob_sha_matches_git_object_formula(self):
        raw = b"abc\n"
        expected = hashlib.sha1(b"blob 4\0abc\n").hexdigest()
        self.assertEqual(git_blob_sha1(raw), expected)

    def test_source_fingerprint_semantics_are_order_sensitive_only_to_rows_not_index(self):
        frame = pd.DataFrame([
            {
                "decision_date": "2026-01-02", "symbol": "000002",
                "open": 2.0, "high": 2.2, "low": 1.8, "close": 2.1,
                "volume": 20.0, "value": 42.0, "krx_change_return": 0.01,
            },
            {
                "decision_date": "2026-01-02", "symbol": "000001",
                "open": 1.0, "high": 1.2, "low": 0.8, "close": 1.1,
                "volume": 10.0, "value": 11.0, "krx_change_return": 0.02,
            },
        ])
        a = source_fingerprint(frame)
        b = source_fingerprint(frame.reset_index(drop=True))
        self.assertEqual(a, b)
        self.assertEqual(a["rows"], 2)
        self.assertEqual(a["symbols"], 2)
        self.assertEqual(
            a["columns"],
            EXPECTED_SOURCE_FINGERPRINT["columns"],
        )

    def test_exact_reference_match_is_required(self):
        require_exact_fingerprint(dict(EXPECTED_SOURCE_FINGERPRINT))
        changed = dict(EXPECTED_SOURCE_FINGERPRINT)
        changed["rows"] += 1
        with self.assertRaisesRegex(FrozenLongHistoryError, "fingerprint mismatch"):
            require_exact_fingerprint(changed)

    def test_verification_cannot_grant_model_or_live_authority(self):
        body = {
            "classification": "FROZEN_LONG_HISTORY_SOURCE_REHYDRATION_VERIFIED",
            "frozen_action_id": 36643183157,
            "frozen_artifact_id": 11067383547,
            "frozen_artifact_digest": "sha256:c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f",
            "frozen_run_head_sha": "4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d",
            "frozen_builder_git_blob_sha1": FROZEN_BUILDER_GIT_BLOB_SHA1,
            "frozen_start": "2015-06-15",
            "frozen_end": "2026-09-23",
            "runtime_versions": {
                "python": "3.12.14", "pandas": "2.3.3",
                "numpy": "2.5.3", "pyarrow": "21.0.0",
            },
            "source_fingerprint": dict(EXPECTED_SOURCE_FINGERPRINT),
            "fingerprint_exact_match": True,
            "existing_2018_pit_tree_overwritten": False,
            "consumed_v1_holdout_read": False,
            "performance_evaluation_executed": False,
            "model_fit_executed": False,
            "historical_backfill_decisions_created": False,
            "fresh_alpha_observation_admitted": False,
            "promotion_authority": False,
            "live_order_authorized": False,
        }
        payload = json.dumps(
            body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        record = {
            **body,
            "verification_sha256": hashlib.sha256(payload).hexdigest(),
        }
        self.assertTrue(validate_verification(record)["valid"])
        changed = dict(record)
        changed["live_order_authorized"] = True
        with self.assertRaises(FrozenLongHistoryError):
            validate_verification(changed)


if __name__ == "__main__":
    unittest.main()
