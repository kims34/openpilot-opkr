"""Synthetic cross-auditor parity for the two KRX 2021 read-only reviewers.

Never reads the Railway private volume or requests provider data. Distinct
implementations must reject the same displaced holiday and source digest drift.
Passing these synthetic checks does NOT authenticate historical PIT or trading.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_krx_2021_private_calendar_day_reconciliation as strict
import research_v1_krx_2021_private_calendar_reconcile as alternate


def synthetic_source():
    days = strict._bounds("2021-01-01", "2021-12-31")
    rows = []
    for day in days:
        closed = day in strict.EXPECTED_CLOSED
        rows.append({
            "day": day,
            "pair_sha256": hashlib.sha256(("synthetic:" + day).encode()).hexdigest(),
            "daily_rows": 0 if closed else 100,
            "source_day_class": (
                "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
                if closed else strict.NONEMPTY
            ),
        })
    panel_digest = hashlib.sha256(json.dumps(
        [{"day": x["day"], "pair_sha256": x["pair_sha256"]} for x in rows],
        sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    return rows, panel_digest


def evaluate_both(rows, snapshot_sha):
    with patch.object(strict, "SOURCE_SNAPSHOT_SHA256", snapshot_sha):
        first = strict._source_rows_match_expected_calendar(rows)
    by_date = {r["day"]: r for r in rows}
    def mock_check(root, day):
        return by_date[day]
    with (
        patch.object(alternate, "EXISTING_2021_PANEL_SHA256", snapshot_sha),
        patch.object(alternate, "_trusted_private_root", return_value=Path("/data/mock")),
        patch.object(alternate, "_check_one", side_effect=mock_check),
    ):
        second = alternate.review_private_2021(
            execute=True, environment={
                "RAILWAY_SERVICE_NAME": alternate.WORKER,
                "KRX_PRIVATE_RAW_DIR": "/data",
            },
        )
    return first, second


class CalendarAuditorParity(unittest.TestCase):
    def test_identical_schedule_vintage_and_pin(self):
        self.assertEqual(strict.EXPECTED_CLOSED, alternate.OFFICIAL_FINAL_2021)
        self.assertEqual(strict.KRX_INITIAL_2021_CLOSED, alternate.INITIAL_2021)
        self.assertEqual(strict.KRX_REVISED_2021_CLOSED, alternate.ADDED_2021)
        self.assertEqual(strict.SOURCE_SNAPSHOT_SHA256,
                         alternate.EXISTING_2021_PANEL_SHA256)
        self.assertEqual(len(strict.EXPECTED_CLOSED), 13)
        self.assertEqual(len(strict._bounds("2021-01-01", "2021-12-31")), 261)

    def test_exact_synthetic_date_match_stays_non_pit_in_both(self):
        rows, sha = synthetic_source()
        first, second = evaluate_both(rows, sha)
        self.assertTrue(first["source_date_by_date_retrospective_calendar_match"])
        self.assertEqual(second["status"], "PRIVATE_2021_DATE_SET_SHAPE_MATCH_NOT_PIT")
        self.assertEqual(first["private_original_2021_weekday_pairs_verified"], 261)
        self.assertEqual(second["original_pairs_reverified"], 261)
        self.assertEqual(first["original_source_empty_days_count"],
                         second["empty_daily_original_pairs_total"])
        self.assertFalse(first["2021_exchange_calendar_pit_admitted"])
        self.assertFalse(second["original_publication_pit_verified"])

    def test_displaced_holiday_preserves_13_but_both_reject(self):
        rows, sha = synthetic_source()
        a = next(row for row in rows if row["day"] == "20210816")
        b = next(row for row in rows if row["day"] == "20210817")
        a.update(daily_rows=100, source_day_class=strict.NONEMPTY)
        b.update(daily_rows=0, source_day_class=
                 "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP")
        first, second = evaluate_both(rows, sha)
        self.assertEqual(first["original_source_empty_days_count"], 13)
        self.assertEqual(second["empty_daily_original_pairs_total"], 13)
        self.assertFalse(first["source_date_by_date_retrospective_calendar_match"])
        self.assertEqual(second["status"], "PRIVATE_2021_DATE_SET_DISCREPANCY_NOT_PIT")
        self.assertEqual(first["expected_closures_missing_from_source_empty_days_count"],
                         second["expected_holidays_with_nonempty_daily_rows"])
        self.assertEqual(first["unexpected_source_empty_days_count"],
                         second["empty_daily_original_pairs_on_other_weekdays"])

    def test_stale_annual_snapshot_blocks_both(self):
        rows, _ = synthetic_source()
        first, second = evaluate_both(rows, "f" * 64)
        self.assertEqual(first["status"],
                         "FAIL_CLOSED_2021_IMMUTABLE_SOURCE_FINGERPRINT_DRIFT")
        self.assertEqual(second["status"], "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED")
        self.assertFalse(first["original_pair_fingerprint_matched"])
        self.assertFalse(second["original_panel_sha256_matches_prior_audit"])

    def test_unsupported_2021_source_day_class_fails_closed_both(self):
        rows, sha = synthetic_source()
        rows[0]["source_day_class"] = "HOLIDAY_ALREADY_PIT_ADMITTED"
        first, second = evaluate_both(rows, sha)
        self.assertEqual(first["status"], "FAIL_CLOSED_2021_SOURCE_DAY_CLASS")
        self.assertEqual(second["status"], "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED")

    def test_all_results_leave_authorizations_false_and_emit_no_days(self):
        rows, sha = synthetic_source()
        first, second = evaluate_both(rows, sha)
        for a in (first, second):
            self.assertEqual(a["ordering"], "DISABLED")
            self.assertFalse(a["m20_performance_run_authorized"])
            self.assertFalse(a["funds_movement_authorized"])
            self.assertFalse(a["network_request_attempted"])
            self.assertFalse(a["storage_mutated"])
            self.assertFalse(a["champion_change_authorized"])
            for row in rows:
                self.assertNotIn(row["day"], str(a))
                self.assertNotIn(row["pair_sha256"], str(a))
        # These independent reviewers deliberately expose different names for
        # the same forbidden Holdout access right.
        self.assertIs(first["independent_holdout_authorized"], False)
        self.assertIs(second["holdout_access_authorized"], False)


if __name__ == "__main__":
    unittest.main()
