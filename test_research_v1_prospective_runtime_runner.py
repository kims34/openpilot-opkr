"""Network-free tests for the Tiny-Live prospective capture runtime."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from research_v1_prospective_runtime_runner import (
    KST,
    PINNED_MODEL_SHA256,
    ProspectiveRuntimeError,
    _capture_time_allowed,
    _public_anchor_manifest,
    _safe_status,
    _write_status,
)


class ProspectiveRuntimeRunnerTest(unittest.TestCase):
    def test_post_close_guard_is_explicit_and_kst_based(self):
        before = datetime(2026, 10, 8, 9, 59, tzinfo=timezone.utc)  # 18:59 KST
        after = datetime(2026, 10, 8, 10, 0, tzinfo=timezone.utc)   # 19:00 KST
        self.assertFalse(_capture_time_allowed(before))
        self.assertTrue(_capture_time_allowed(after))
        self.assertEqual(after.astimezone(KST).hour, 19)

    def test_public_anchor_manifest_is_hash_only_and_non_authorizing(self):
        hashes = {
            "session": "2026-10-08",
            "source_receipt_sha256": "1" * 64,
            "input_snapshot_sha256": "2" * 64,
            "producer_binding_sha256": "3" * 64,
            "model_bundle_sha256": PINNED_MODEL_SHA256,
            "decision_capture_sha256": "4" * 64,
            "session_manifest_sha256": "5" * 64,
            "structural_session_committed": True,
            "live_order_authorized": False,
        }
        out = _public_anchor_manifest(hashes, "2026-10-08T10:00:00+00:00")
        self.assertEqual(out["session"], "2026-10-08")
        self.assertFalse(out["independent_source_admission_verified"])
        self.assertFalse(out["independent_model_admission_verified"])
        self.assertFalse(out["independent_chronology_admission_verified"])
        self.assertFalse(out["fresh_alpha_observation_admitted"])
        self.assertFalse(out["live_order_authorized"])
        encoded = json.dumps(out).lower()
        for forbidden in ("token", "password", "secret", "account", "auth_key"):
            self.assertNotIn(forbidden, encoded)

    def test_status_file_never_grants_order_or_funds_authority(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            out = _write_status(
                root,
                status="STRUCTURAL_SESSION_COMMITTED_NOT_ADMITTED",
                target_session="2026-10-08",
            )
            self.assertEqual(out["ordering"], "DISABLED")
            self.assertFalse(out["real_orders_authorized"])
            self.assertFalse(out["funds_movement_authorized"])
            self.assertFalse(out["broker_permission_change_authorized"])
            self.assertFalse(out["fresh_alpha_observation_admitted"])
            loaded = _safe_status(root)
            self.assertEqual(loaded, out)

    def test_public_status_rejects_secret_like_field(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "public" / "status.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"token_value": "x"}), encoding="utf-8")
            with self.assertRaises(ProspectiveRuntimeError):
                _safe_status(root)


if __name__ == "__main__":
    unittest.main()
