"""Safety tests for the prospective HTTP/scheduler wrapper."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from research_v1_prospective_http_runtime import (
    _latest_anchor,
    _read_status,
    _safe_status,
    validate_anchor_payload,
)
from research_v1_prospective_runtime import _canonical


class ProspectiveHTTPRuntimeTest(unittest.TestCase):
    def _anchor(self):
        body = {
            "classification": "PROSPECTIVE_ANCHOR_PAYLOAD_NOT_ADMISSION",
            "session": "2026-10-08",
            "decision_at": "2026-10-08T09:40:00+00:00",
            "source_receipt_sha256": "1" * 64,
            "input_snapshot_sha256": "2" * 64,
            "producer_binding_sha256": "3" * 64,
            "model_bundle_sha256": "4" * 64,
            "decision_capture_sha256": "5" * 64,
            "session_manifest_sha256": "6" * 64,
            "independent_chronology_admission_verified": False,
            "fresh_alpha_observation_admitted": False,
            "live_order_authorized": False,
        }
        body["anchor_payload_sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
        return body

    def test_anchor_payload_is_hash_only_and_non_authorizing(self):
        anchor = self._anchor()
        checked = validate_anchor_payload(anchor)
        self.assertTrue(checked["valid"])
        self.assertFalse(checked["live_order_authorized"])
        encoded = str(anchor).lower()
        for forbidden in ("token", "password", "secret", "account", "order_id"):
            self.assertNotIn(forbidden, encoded)

    def test_anchor_tamper_fails_closed(self):
        anchor = self._anchor()
        anchor["source_receipt_sha256"] = "a" * 64
        with self.assertRaisesRegex(Exception, "fingerprint mismatch"):
            validate_anchor_payload(anchor)

    def test_latest_anchor_uses_latest_canonical_session_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            older = self._anchor()
            older["session"] = "2026-10-07"
            older["decision_at"] = "2026-10-07T09:40:00+00:00"
            older["anchor_payload_sha256"] = hashlib.sha256(
                _canonical({k: v for k, v in older.items() if k != "anchor_payload_sha256"})
            ).hexdigest()
            (root / "anchor-payload-2026-10-07.json").write_bytes(
                _canonical(older) + b"\n"
            )
            newest = self._anchor()
            (root / "anchor-payload-2026-10-08.json").write_bytes(
                _canonical(newest) + b"\n"
            )
            self.assertEqual(_latest_anchor(root)["session"], "2026-10-08")

    def test_public_status_never_grants_trading_authority(self):
        status = _safe_status(
            {
                "status": "STRUCTURAL_SESSION_COMMITTED",
                "session": "2026-10-08",
                "session_manifest_sha256": "a" * 64,
                "chronology_anchor_pending": True,
            }
        )
        self.assertEqual(status["ordering"], "DISABLED")
        self.assertFalse(status["real_orders_authorized"])
        self.assertFalse(status["funds_movement_authorized"])
        self.assertFalse(status["permission_change_authorized"])
        self.assertFalse(status["fresh_alpha_observation_admitted"])
        self.assertFalse(status["live_order_authorized"])

    def test_missing_status_defaults_to_waiting_and_disabled(self):
        with tempfile.TemporaryDirectory() as folder:
            status = _read_status(Path(folder))
            self.assertEqual(status["status"], "WAITING")
            self.assertEqual(status["ordering"], "DISABLED")
            self.assertFalse(status["real_orders_authorized"])


if __name__ == "__main__":
    unittest.main()
