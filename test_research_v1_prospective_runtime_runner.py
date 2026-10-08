"""Network-free tests for the Tiny-Live prospective capture runtime."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from research_v1_prospective_runtime_runner import (
    KST,
    PINNED_MODEL_SHA256,
    ProspectiveRuntimeError,
    _capture_time_allowed,
    _frame_sha256,
    _load_cached_panel,
    _panel_path,
    _public_anchor_manifest,
    _safe_status,
    _store_panel,
    _write_status,
)


class ProspectiveRuntimeRunnerTest(unittest.TestCase):
    def test_post_close_guard_is_explicit_and_kst_based(self):
        before = datetime(2026, 10, 8, 9, 59, tzinfo=timezone.utc)  # 18:59 KST
        after = datetime(2026, 10, 8, 10, 0, tzinfo=timezone.utc)   # 19:00 KST
        self.assertFalse(_capture_time_allowed(before))
        self.assertTrue(_capture_time_allowed(after))
        self.assertEqual(after.astimezone(KST).hour, 19)

    def test_warmup_cache_uses_one_explicit_root_without_double_nesting(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder) / "warmup"
            session = "2026-10-07"
            panel = pd.DataFrame([{
                "decision_date": pd.Timestamp(session),
                "symbol": "005930",
                "standard_code": "KR7005930003",
                "open": 70000.0,
                "high": 71000.0,
                "low": 69000.0,
                "close": 70500.0,
                "volume": 1000.0,
                "value": 70500000.0,
                "krx_change_return": 0.01,
                "available_at": "2026-10-07T09:10:00+00:00",
                "source_route": "KRX_OPENAPI_APPROVED_SERVICE",
                "source_dataset": "stk_bydd_trd",
                "availability_semantics": "OBSERVED_AVAILABLE_BY_RETRIEVAL_TIME_NOT_OFFICIAL_PUBLICATION_TIME",
            }])
            _store_panel(cache, session, panel)
            receipt = {
                "session": session,
                "normalized_panel_sha256": _frame_sha256(panel),
                "daily_raw_sha256": "1" * 64,
                "master_raw_sha256": "2" * 64,
            }
            _write_status(cache.parent, status="TEST_ONLY")
            receipt_path = cache / f"source-{session}.json"
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with patch(
                "research_v1_prospective_runtime_runner.validate_source_receipt",
                return_value={"valid": True},
            ), patch(
                "research_v1_prospective_runtime_runner.verify_raw_object",
                return_value={"verified": True},
            ):
                loaded = _load_cached_panel(cache, session)
            self.assertIsNotNone(loaded)
            self.assertEqual(_frame_sha256(loaded), _frame_sha256(panel))
            self.assertEqual(_panel_path(cache, session), cache / f"panel-{session}.parquet")
            self.assertFalse((cache / "warmup").exists())

    def test_cached_panel_fails_closed_when_raw_evidence_is_not_verified(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder)
            session = "2026-10-07"
            panel = pd.DataFrame([{
                "decision_date": pd.Timestamp(session),
                "symbol": "005930",
                "standard_code": "KR7005930003",
                "open": 70000.0, "high": 71000.0, "low": 69000.0,
                "close": 70500.0, "volume": 1000.0, "value": 70500000.0,
                "krx_change_return": 0.01,
                "available_at": "2026-10-07T09:10:00+00:00",
                "source_route": "KRX_OPENAPI_APPROVED_SERVICE",
                "source_dataset": "stk_bydd_trd",
                "availability_semantics": "OBSERVED_AVAILABLE_BY_RETRIEVAL_TIME_NOT_OFFICIAL_PUBLICATION_TIME",
            }])
            _store_panel(cache, session, panel)
            (cache / f"source-{session}.json").write_text(
                json.dumps({
                    "session": session,
                    "normalized_panel_sha256": _frame_sha256(panel),
                    "daily_raw_sha256": "1" * 64,
                    "master_raw_sha256": "2" * 64,
                }),
                encoding="utf-8",
            )
            with patch(
                "research_v1_prospective_runtime_runner.validate_source_receipt",
                return_value={"valid": True},
            ), patch(
                "research_v1_prospective_runtime_runner.verify_raw_object",
                side_effect=ValueError("tampered"),
            ):
                with self.assertRaisesRegex(
                    ProspectiveRuntimeError, "raw-object integrity"
                ):
                    _load_cached_panel(cache, session)

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
