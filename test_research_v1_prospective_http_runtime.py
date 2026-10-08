"""Safety tests for the prospective HTTP/scheduler wrapper."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from research_v1_prospective_http_runtime import (
    _failure_reason_code,
    _failure_source_session,
    _failure_ohlc_counts,
    _latest_anchor,
    _read_status,
    _safe_status,
    validate_anchor_payload,
)
from research_v1_prospective_runtime import _canonical
from research_v1_krx_openapi_prospective_source import KRXProspectiveOpenAPISourceError


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


    def test_public_source_diagnostic_uses_static_enum_not_provider_text(self):
        reason = _failure_reason_code(
            KRXProspectiveOpenAPISourceError(
                "daily-trade symbols missing from same-session security master"
                " secret=DO_NOT_LEAK account=DO_NOT_LEAK"
            )
        )
        self.assertEqual(reason, "MASTER_COVERAGE_GAP")
        self.assertNotIn("DO_NOT_LEAK", reason)
        self.assertEqual(
            _failure_reason_code(
                KRXProspectiveOpenAPISourceError("provider response secret=DO_NOT_LEAK")
            ),
            "KRX_SOURCE_OTHER",
        )
        self.assertEqual(
            _failure_reason_code(RuntimeError("private token=DO_NOT_LEAK")),
            "OTHER_FAILURE",
        )

    def test_public_status_accepts_only_known_safe_failure_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            status = _safe_status({"status": "FAIL_CLOSED", "session": "2026-10-08"})
            status["error_class"] = "KRXProspectiveOpenAPISourceError"
            status["error_reason_code"] = "MASTER_COVERAGE_GAP"
            (root / "runtime-status.json").write_bytes(_canonical(status) + b"\n")
            self.assertEqual(_read_status(root)["error_reason_code"], "MASTER_COVERAGE_GAP")
            status["error_reason_code"] = "MASTER_COVERAGE_GAP secret=DO_NOT_LEAK"
            (root / "runtime-status.json").write_bytes(_canonical(status) + b"\n")
            with self.assertRaisesRegex(Exception, "error reason is invalid"):
                _read_status(root)


    def test_failure_date_is_only_canonical_past_or_same_day(self):
        exc = KRXProspectiveOpenAPISourceError("private secret=DO_NOT_LEAK")
        exc.source_failure_session = "2026-09-25"
        self.assertEqual(_failure_source_session(exc), "2026-09-25")
        for bad in ("2026-09-25 token=DO_NOT_LEAK", "2026-02-30", "20260925", "", None):
            exc.source_failure_session = bad
            self.assertIsNone(_failure_source_session(exc))
        self.assertIsNone(_failure_source_session(RuntimeError("private")))

    def test_public_status_rejects_forged_failure_date(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            status = _safe_status({"status": "FAIL_CLOSED", "session": "2026-10-08"})
            status["error_class"] = "KRXProspectiveOpenAPISourceError"
            status["error_reason_code"] = "COMMON_OHLC_NONPOSITIVE"
            status["source_failure_session"] = "2026-09-25"
            path = root / "runtime-status.json"
            path.write_bytes(_canonical(status) + b"\n")
            self.assertEqual(_read_status(root)["source_failure_session"], "2026-09-25")
            for bad in ("2026-10-09", "2026-02-30", "2026-09-25 account=DO_NOT_LEAK", None, 0):
                status["source_failure_session"] = bad
                path.write_bytes(_canonical(status) + b"\n")
                with self.assertRaisesRegex(Exception, "source failure session is invalid"):
                    _read_status(root)


    def test_ohlc_counts_are_bounded_and_only_emitted_for_source_error(self):
        from research_v1_prospective_http_runtime import _validated_ohlc_counts
        sample = {
            "common_stock_rows": 970, "nonpositive_ohlc_rows": 2,
            "zero_volume_value_rows": 2, "other_activity_rows": 0,
            "all_zero_ohlc_rows": 1,
        }
        exc = KRXProspectiveOpenAPISourceError(
            "common-stock current-session OHLC contains nonpositive value; private"
        )
        exc.source_failure_session = "2026-09-28"
        exc.safe_ohlc_counts = sample
        self.assertEqual(_failure_ohlc_counts(exc), sample)
        self.assertIsNone(_failure_ohlc_counts(RuntimeError("secret")))
        for key, bad in (
            ("nonpositive_ohlc_rows", -1),
            ("nonpositive_ohlc_rows", True),
            ("zero_volume_value_rows", 3),
            ("common_stock_rows", 1000001),
            ("all_zero_ohlc_rows", "2 DO_NOT_LEAK"),
        ):
            tampered = dict(sample, **{key: bad})
            self.assertIsNone(_validated_ohlc_counts(tampered))
        exc.source_failure_session = "unsafe date token=DO_NOT_LEAK"
        self.assertIsNone(_failure_ohlc_counts(exc))

    def test_public_status_rejects_forged_ohlc_aggregate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            status = _safe_status({"status": "FAIL_CLOSED", "session": "2026-10-08"})
            status.update({
                "error_class": "KRXProspectiveOpenAPISourceError",
                "error_reason_code": "COMMON_OHLC_NONPOSITIVE",
                "source_failure_session": "2026-09-28",
                "ohlc_failure_counts": {
                    "common_stock_rows": 970, "nonpositive_ohlc_rows": 2,
                    "zero_volume_value_rows": 2, "other_activity_rows": 0,
                    "all_zero_ohlc_rows": 1,
                },
            })
            path = root / "runtime-status.json"
            path.write_bytes(_canonical(status) + b"\n")
            self.assertEqual(
                _read_status(root)["ohlc_failure_counts"]["nonpositive_ohlc_rows"], 2
            )
            cases = [
                dict(status, ohlc_failure_counts={"issue_code": "DO_NOT_LEAK"}),
                dict(status, error_reason_code="OTHER_FAILURE"),
                dict(status, source_failure_session=None),
            ]
            for altered in cases:
                path.write_bytes(_canonical(altered) + b"\n")
                with self.assertRaises(Exception):
                    _read_status(root)

    def test_missing_status_defaults_to_waiting_and_disabled(self):
        with tempfile.TemporaryDirectory() as folder:
            status = _read_status(Path(folder))
            self.assertEqual(status["status"], "WAITING")
            self.assertEqual(status["ordering"], "DISABLED")
            self.assertFalse(status["real_orders_authorized"])


if __name__ == "__main__":
    unittest.main()
