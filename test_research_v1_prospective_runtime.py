"""Network-free safety tests for the read-only prospective runtime."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from research_v1_prospective_frozen_producer import bind_prebuilt_model_for_target
from research_v1_prospective_runtime import (
    EXPECTED_CALENDAR_COUNT,
    EXPECTED_CALENDAR_END,
    EXPECTED_CALENDAR_ORIGIN,
    EXPECTED_MODEL_SHA256,
    NETWORK_AUTH_VALUE,
    ProspectiveRuntimeError,
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
