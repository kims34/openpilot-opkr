"""Network-free safety tests for the read-only prospective runtime."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from research_v1_prospective_frozen_producer import bind_prebuilt_model_for_target
from research_v1_krx_openapi_prospective_source import KRXProspectiveOpenAPISourceError
from research_v1_prospective_runtime import (
    EXPECTED_CALENDAR_COUNT,
    EXPECTED_CALENDAR_END,
    EXPECTED_CALENDAR_ORIGIN,
    EXPECTED_MODEL_SHA256,
    NETWORK_AUTH_VALUE,
    ProspectiveRuntimeError,
    _fetch_official_session_source,
    _fetch_official_source_with_failure_date,
    _load_verified_history,
    _store_rejected_openapi_source,
    _weekday_dates,
    load_calendar_prefix,
    load_pinned_model_bundle,
    require_read_only_runtime_authority,
    resolve_target_session,
)


ROOT = Path(__file__).resolve().parent


class ProspectiveRuntimeTest(unittest.TestCase):
    def test_pinned_calendar_prefix_and_model_are_exact_and_compatible(self):
        calendar = load_calendar_prefix(ROOT)
        self.assertEqual(len(calendar), EXPECTED_CALENDAR_COUNT)
        self.assertEqual(calendar[0], EXPECTED_CALENDAR_ORIGIN)
        self.assertEqual(calendar[-1], EXPECTED_CALENDAR_END)
        bundle = load_pinned_model_bundle(ROOT)
        self.assertEqual(bundle["model_bundle_sha256"], EXPECTED_MODEL_SHA256)
        rebound = bind_prebuilt_model_for_target(
            bundle,
            session_calendar=calendar,
            target_session=calendar[-1],
        )
        self.assertEqual(
            rebound["model_bundle"]["model_bundle_sha256"],
            EXPECTED_MODEL_SHA256,
        )
        self.assertFalse(
            rebound["producer_binding"]["independent_model_admission_verified"]
        )
        self.assertFalse(rebound["producer_binding"]["live_order_authorized"])

    def test_runtime_authority_requires_read_only_krx_and_rejects_trading_flags(self):
        base = {
            "INDEXALERT_PROSPECTIVE_NETWORK_AUTHORIZED": NETWORK_AUTH_VALUE,
            "KRX_AUTH_KEY": "secret-not-logged",
            "ORDERING": "DISABLED",
            "REAL_ORDERS_AUTHORIZED": "false",
            "FUNDS_MOVEMENT_AUTHORIZED": "false",
            "PERMISSION_CHANGE_AUTHORIZED": "false",
        }
        self.assertEqual(
            require_read_only_runtime_authority(base), "secret-not-logged"
        )
        for field in (
            "REAL_ORDERS_AUTHORIZED",
            "FUNDS_MOVEMENT_AUTHORIZED",
            "PERMISSION_CHANGE_AUTHORIZED",
        ):
            changed = dict(base)
            changed[field] = "true"
            with self.subTest(field=field):
                with self.assertRaises(ProspectiveRuntimeError):
                    require_read_only_runtime_authority(changed)
        changed = dict(base)
        changed["ORDERING"] = "ENABLED"
        with self.assertRaises(ProspectiveRuntimeError):
            require_read_only_runtime_authority(changed)

    def test_runtime_never_runs_before_finality_buffer(self):
        early = pd.Timestamp("2026-10-08T18:29:59+09:00")
        with self.assertRaisesRegex(ProspectiveRuntimeError, "18:30"):
            resolve_target_session(early)
        self.assertEqual(
            resolve_target_session(pd.Timestamp("2026-10-08T18:30:00+09:00")),
            "2026-10-08",
        )


    def test_source_failure_date_is_attached_without_suppressing_failure(self):
        failure = KRXProspectiveOpenAPISourceError(
            "common-stock current-session OHLC contains nonpositive value; redacted"
        )
        with patch(
            "research_v1_prospective_runtime._fetch_official_session_source",
            side_effect=failure,
        ) as fetch:
            with self.assertRaises(KRXProspectiveOpenAPISourceError) as caught:
                _fetch_official_source_with_failure_date(
                    pd.Timestamp("2026-09-25"), auth_key="not-revealed", evidence={}
                )
        self.assertIs(caught.exception, failure)
        self.assertEqual(getattr(failure, "source_failure_session"), "2026-09-25")
        fetch.assert_called_once()

    def test_gap_session_uses_same_session_security_master(self):
        day = pd.Timestamp("2026-10-08")
        daily = SimpleNamespace(
            response_frame=pd.DataFrame([{"x": 1}]),
            raw_bytes=b"daily",
            retrieved_at="2026-10-08T09:00:00+00:00",
        )
        master = SimpleNamespace(
            response_frame=pd.DataFrame([{"y": 1}]),
            raw_bytes=b"master",
            retrieved_at="2026-10-08T09:01:00+00:00",
        )
        built = {
            "session": "2026-10-08",
            "observed_available_by": "2026-10-08T09:01:00+00:00",
            "panel": pd.DataFrame(),
        }
        with patch(
            "research_v1_prospective_runtime._fetch_daily",
            return_value=daily,
        ) as daily_fetch, patch(
            "research_v1_prospective_runtime._fetch_master",
            return_value=master,
        ) as master_fetch, patch(
            "research_v1_prospective_runtime.build_current_session_openapi_source",
            return_value=built,
        ) as builder:
            out = _fetch_official_session_source(
                day,
                auth_key="redacted",
                evidence={"test": True},
            )
        self.assertIsNotNone(out)
        daily_fetch.assert_called_once_with(day, auth_key="redacted")
        master_fetch.assert_called_once_with(day, auth_key="redacted")
        self.assertEqual(
            builder.call_args.kwargs["expected_session"], "2026-10-08"
        )
        self.assertEqual(builder.call_args.kwargs["daily_raw"], b"daily")
        self.assertEqual(builder.call_args.kwargs["master_raw"], b"master")

    def test_rejected_source_retains_actual_bytes_and_failure_without_extra_fetch(self):
        daily = SimpleNamespace(
            response_frame=pd.DataFrame([{"x": 1}]), raw_bytes=b"private-daily-issue",
            retrieved_at="2026-10-08T09:00:00+00:00",
        )
        master = SimpleNamespace(
            raw_bytes=b"private-master-issue", retrieved_at="2026-10-08T09:01:00+00:00",
        )
        failure = KRXProspectiveOpenAPISourceError("rejected source; private text")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "private"
            git = Path(folder) / "git"
            with patch("research_v1_prospective_runtime._fetch_daily", return_value=daily) as df, patch(
                "research_v1_prospective_runtime._fetch_master", return_value=master
            ) as mf, patch(
                "research_v1_prospective_runtime.build_current_session_openapi_source",
                side_effect=failure,
            ):
                with self.assertRaises(KRXProspectiveOpenAPISourceError) as caught:
                    _fetch_official_source_with_failure_date(
                        pd.Timestamp("2026-09-28"), auth_key="secret-never-recorded",
                        evidence={}, private_root=root, git_worktree=git,
                    )
            self.assertIs(caught.exception, failure)
            self.assertEqual(failure.source_failure_session, "2026-09-28")
            self.assertIs(failure.private_rejected_source_receipt_saved, True)
            df.assert_called_once()
            mf.assert_called_once()
            receipts = list(root.rglob("rejected-*.json"))
            self.assertEqual(len(receipts), 1)
            receipt = json.loads(receipts[0].read_text())
            self.assertEqual(receipt["requested_source_session"], "2026-09-28")
            self.assertEqual(receipt["daily_retrieved_at"], daily.retrieved_at)
            self.assertFalse(receipt["decision_recorded"])
            self.assertFalse(receipt["independent_source_admission_verified"])
            self.assertFalse(receipt["fresh_alpha_observation_admitted"])
            self.assertFalse(receipt["live_order_authorized"])
            for item, field in ((daily, "daily_raw_sha256"), (master, "master_raw_sha256")):
                digest = hashlib.sha256(item.raw_bytes).hexdigest()
                self.assertEqual(receipt[field], digest)
                obj = root / "rejected-openapi" / "objects" / "sha256" / digest[:2] / (digest + ".bin")
                self.assertEqual(obj.read_bytes(), item.raw_bytes)
                self.assertEqual(obj.stat().st_mode & 0o777, 0o600)
            self.assertEqual(receipts[0].stat().st_mode & 0o777, 0o600)
            self.assertNotIn("secret-never-recorded", receipts[0].read_text())
            self.assertNotIn("private text", receipts[0].read_text())
            self.assertFalse(list(root.glob("session-*.json")))
            self.assertFalse(list(root.glob("anchor-payload-*.json")))
            _store_rejected_openapi_source(
                pd.Timestamp("2026-09-28"), daily=daily, master=master,
                private_root=root, git_worktree=git,
            )
            self.assertEqual(len(list(root.rglob("rejected-*.json"))), 1)
            daily.retrieved_at = "2026-10-08T09:15:00+00:00"
            _store_rejected_openapi_source(
                pd.Timestamp("2026-09-28"), daily=daily, master=master,
                private_root=root, git_worktree=git,
            )
            self.assertEqual(len(list(root.rglob("rejected-*.json"))), 2)
            self.assertEqual(json.loads(receipts[0].read_text())["daily_retrieved_at"], "2026-10-08T09:00:00+00:00")

    def test_rejected_source_storage_cannot_write_inside_git_or_publish_partial_receipt(self):
        from research_v1_krx_private_store import KRXPrivateStoreError
        daily = SimpleNamespace(raw_bytes=b"daily", retrieved_at="2026-10-08T09:00:00+00:00")
        master = SimpleNamespace(raw_bytes=b"master", retrieved_at="2026-10-08T09:01:00+00:00")
        with tempfile.TemporaryDirectory() as folder:
            git = Path(folder) / "git"
            with self.assertRaises(KRXPrivateStoreError):
                _store_rejected_openapi_source(
                    pd.Timestamp("2026-09-28"), daily=daily, master=master,
                    private_root=git / "private", git_worktree=git,
                )
            root = Path(folder) / "private"
            with patch("research_v1_prospective_runtime.write_raw_object", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    _store_rejected_openapi_source(
                        pd.Timestamp("2026-09-28"), daily=daily, master=master,
                        private_root=root, git_worktree=git,
                    )
            self.assertFalse(list(root.rglob("rejected-*.json")))
            self.assertFalse(hasattr(daily, "private_rejected_source_receipt_saved"))
            daily.retrieved_at = "2026-10-08T09:00:00"
            with self.assertRaises(ProspectiveRuntimeError):
                _store_rejected_openapi_source(
                    pd.Timestamp("2026-09-28"), daily=daily, master=master,
                    private_root=root, git_worktree=git,
                )

    def test_verified_warmup_preserves_frozen_contemporaneous_universe(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = []
            for session in ("2026-09-22", "2026-09-23"):
                for symbol in ("000001", "000002"):
                    rows.append({
                        "decision_date": pd.Timestamp(session),
                        "symbol": symbol,
                        "open": 10.0,
                        "high": 11.0,
                        "low": 9.0,
                        "close": 10.5,
                        "volume": 100.0,
                        "value": 1050.0,
                        "krx_change_return": 0.01,
                    })
            pd.DataFrame(rows).to_parquet(
                root / "kospi-pit-2026.parquet", index=False
            )
            frame, sessions = _load_verified_history(
                root,
                target=pd.Timestamp("2026-10-08"),
                availability_at="2026-10-08T09:30:00+00:00",
            )
        self.assertEqual(set(frame["symbol"]), {"000001", "000002"})
        self.assertEqual(sessions, ["2026-09-22", "2026-09-23"])

    def test_weekday_probe_never_attempts_weekends(self):
        days = _weekday_dates(
            pd.Timestamp("2026-10-01"),
            pd.Timestamp("2026-10-12"),
        )
        self.assertTrue(days)
        self.assertTrue(all(day.weekday() < 5 for day in days))
        self.assertEqual(days[0].strftime("%Y-%m-%d"), "2026-10-01")
        self.assertEqual(days[-1].strftime("%Y-%m-%d"), "2026-10-12")


if __name__ == "__main__":
    unittest.main()
