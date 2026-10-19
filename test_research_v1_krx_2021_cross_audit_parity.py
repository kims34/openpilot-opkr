"""KRX 2021 independent original-day checker parity (synthetic; NEVER PIT).

Two separately developed 261-day date-set validators must never disagree
about the KRX initial 10 / later 3 market closures or the pinned original
annual SHA. Every receipt in these tests is invented; no Railway mounts,
official KRX queries, broker network, amounts or securities are accessed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_krx_2021_private_calendar_day_reconciliation as a
import research_v1_krx_2021_private_calendar_reconcile as b

DAY_CLASS_EMPTY = "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
DAY_CLASS_OPEN = "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"


def synthetic_receipts(empty_days):
    days = a._bounds("2021-01-01", "2021-12-31")
    rows = [{
        "day": day,
        "pair_sha256": hashlib.sha256(("invented/" + day).encode()).hexdigest(),
        "daily_rows": 0 if day in empty_days else 19,
        "source_day_class": DAY_CLASS_EMPTY if day in empty_days else DAY_CLASS_OPEN,
    } for day in days]
    sha = hashlib.sha256(json.dumps(
        [{"day": x["day"], "pair_sha256": x["pair_sha256"]} for x in rows],
        sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return rows, sha


def both_results(rows, sha, *, pinned_sha=None):
    if pinned_sha is None:
        pinned_sha = sha
    with patch.object(a, "SOURCE_SNAPSHOT_SHA256", pinned_sha):
        original = a._source_rows_match_expected_calendar(rows)
    by_day = {x["day"]: x for x in rows}
    with (patch.object(b, "EXISTING_2021_PANEL_SHA256", pinned_sha),
          patch.object(b, "_trusted_private_root", return_value=Path("/data/mock")),
          patch.object(b, "_check_one", side_effect=lambda root, day: by_day[day])):
        alternate = b.review_private_2021(execute=True, environment={
            "RAILWAY_SERVICE_NAME": b.WORKER,
            "KRX_PRIVATE_RAW_DIR": "/data",
        })
    return original, alternate


class CrossAuditParityTest(unittest.TestCase):
    def test_public_2021_original_10_and_added_3_sets_exactly_equal(self):
        self.assertEqual(a.KRX_INITIAL_2021_CLOSED, b.INITIAL_2021)
        self.assertEqual(a.KRX_REVISED_2021_CLOSED, b.ADDED_2021)
        self.assertEqual(a.EXPECTED_CLOSED, b.OFFICIAL_FINAL_2021)
        self.assertEqual(len(a.EXPECTED_CLOSED), 13)
        self.assertEqual(a.EXPECTED_WEEKDAYS, b.EXPECTED_WEEKDAY_PAIRS)
        self.assertEqual(a.EXPECTED_WEEKDAYS, 261)

    def test_private_snapshot_pin_is_the_same_in_both_independent_checkers(self):
        self.assertEqual(a.SOURCE_SNAPSHOT_SHA256, b.EXISTING_2021_PANEL_SHA256)
        self.assertEqual(
            a.SOURCE_SNAPSHOT_SHA256,
            "362716e7bb5e025a9dcd39207b1ee095d97c633b8ca907722c766edf799ec2a1",
        )

    def test_both_synthetic_exact_date_sets_match_but_never_admit_pit(self):
        rows, sha = synthetic_receipts(a.EXPECTED_CLOSED)
        x, y = both_results(rows, sha)
        self.assertTrue(x["source_date_by_date_retrospective_calendar_match"])
        self.assertEqual(y["status"], "PRIVATE_2021_DATE_SET_SHAPE_MATCH_NOT_PIT")
        self.assertEqual(x["private_original_2021_weekday_pairs_verified"], 261)
        self.assertEqual(y["original_pairs_reverified"], 261)
        self.assertFalse(x["2021_exchange_calendar_pit_admitted"])
        self.assertFalse(y["private_2021_original_date_set_independently_reconciled"])
        self.assertFalse(y["official_exchange_date_source_cryptographically_attested"])
        self.assertFalse(y["original_publication_pit_verified"])
        self.assertFalse(x["m20_performance_run_authorized"])
        self.assertFalse(y["m20_performance_run_authorized"])
        self.assertFalse(x["real_orders_authorized"])
        self.assertFalse(y["live_orders_authorized"])
        self.assertEqual(x["ordering"], "DISABLED")
        self.assertEqual(y["ordering"], "DISABLED")

    def test_equal_13_count_with_one_displaced_date_rejected_by_both(self):
        empty = (a.EXPECTED_CLOSED - {"20210816"}) | {"20210817"}
        self.assertEqual(len(empty), 13)
        x, y = both_results(*synthetic_receipts(empty))
        self.assertEqual(x["status"], "FAIL_CLOSED_2021_DAY_BY_DAY_CALENDAR_MISMATCH")
        self.assertEqual(y["status"], "PRIVATE_2021_DATE_SET_DISCREPANCY_NOT_PIT")
        self.assertEqual(x["original_source_empty_days_count"], 13)
        self.assertEqual(y["empty_daily_original_pairs_total"], 13)
        self.assertEqual(x["unexpected_source_empty_days_count"], 1)
        self.assertEqual(y["empty_daily_original_pairs_on_other_weekdays"], 1)
        self.assertFalse(x["source_date_by_date_retrospective_calendar_match"])
        self.assertFalse(y["private_2021_original_date_set_independently_reconciled"])

    def test_fourteenth_source_empty_day_rejected_by_both(self):
        rows, sha = synthetic_receipts(a.EXPECTED_CLOSED | {"20210817"})
        x, y = both_results(rows, sha)
        self.assertEqual(x["status"], "FAIL_CLOSED_2021_DAY_BY_DAY_CALENDAR_MISMATCH")
        self.assertEqual(y["status"], "PRIVATE_2021_DATE_SET_DISCREPANCY_NOT_PIT")
        self.assertEqual(x["original_source_empty_days_count"], 14)
        self.assertEqual(y["empty_daily_original_pairs_total"], 14)

    def test_both_block_a_fabricated_annual_snapshot_sha(self):
        rows, sha = synthetic_receipts(a.EXPECTED_CLOSED)
        self.assertNotEqual(sha, "0" * 64)
        x, y = both_results(rows, sha, pinned_sha="0" * 64)
        self.assertEqual(x["status"], "FAIL_CLOSED_2021_IMMUTABLE_SOURCE_FINGERPRINT_DRIFT")
        self.assertEqual(y["status"], "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED")
        self.assertFalse(x["original_pair_fingerprint_matched"])
        self.assertFalse(y["original_panel_sha256_matches_prior_audit"])
        self.assertFalse(x["source_date_by_date_retrospective_calendar_match"])
        self.assertFalse(y["live_orders_authorized"])

    def test_2021_notice_vintage_is_distinct_from_retrospective_calendar(self):
        self.assertEqual(a._base()["2021_later_announcement_publication_date"], b.HOLIDAY_NOTICE_ASOF)
        before = a.strict_krx_2021_calendar_preopen_reference("2021-08-04")
        after = a.strict_krx_2021_calendar_preopen_reference("2021-08-05")
        self.assertEqual(before["reference_market_closure_count"], 10)
        self.assertEqual(after["reference_market_closure_count"], 13)
        self.assertFalse(before["official_asof_market_calendar_source_admitted"])
        self.assertFalse(after["official_asof_market_calendar_source_admitted"])
        self.assertFalse(before["historical_source_publication_pit_verified"])


if __name__ == "__main__":
    unittest.main()
