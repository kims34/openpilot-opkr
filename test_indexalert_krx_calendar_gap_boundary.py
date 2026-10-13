"""Synthetic-only offline fail-closed tests for KRX calendar/source evidence."""
import unittest

from research_v1_krx_calendar_gap_boundary import reconcile_candidates

GOOD = "a" * 64
SOURCE = "b" * 64


def obs(d, s="EMPTY"):
    return {"date": d, "response_state": s, "raw_receipt_sha256": GOOD}


def cal(d, s="CLOSED"):
    return {
        "date": d, "session_state": s,
        "source_kind": "KRX_OFFICIAL_EXCHANGE_CALENDAR",
        "source_document_sha256": SOURCE,
    }


class TestKRXCalendarBoundary(unittest.TestCase):
    def test_empty_on_claimed_closure_still_never_admitted(self):
        r = reconcile_candidates([obs("2026-01-01")], [cal("2026-01-01")])
        self.assertEqual(r["status"], "CANDIDATES_RECORDED_SOURCE_ADMISSION_BLOCKED")
        self.assertEqual(r["closure_candidates_only"], 1)
        self.assertEqual(r["official_calendar_matches_attested"], 0)
        self.assertEqual(r["source_admitted_dates"], [])
        self.assertFalse(r["official_calendar_independently_attested"])
        self.assertFalse(r["source_admitted_for_backtest"])

    def test_open_empty_is_not_automatically_holiday(self):
        r = reconcile_candidates([obs("2026-01-02")], [cal("2026-01-02", "OPEN")])
        self.assertEqual(r["possible_open_day_source_gaps"], 1)
        self.assertEqual(r["closure_candidates_only"], 0)
        self.assertEqual(r["status"], "OPEN_DISCREPANCIES_SOURCE_ADMISSION_BLOCKED")

    def test_closed_but_has_rows_is_contradiction(self):
        r = reconcile_candidates([obs("2026-01-05", "NONEMPTY")], [cal("2026-01-05")])
        self.assertEqual(r["closed_day_response_contradictions"], 1)
        self.assertFalse(r["m20_performance_testing_authorized"])

    def test_unproven_official_origin_is_not_a_calendar(self):
        c = cal("2026-01-06")
        c["source_kind"] = "SECONDARY_BLOG"
        r = reconcile_candidates([obs("2026-01-06")], [c])
        self.assertEqual(r["unmatched_or_untrusted_calendar_dates"], 1)

    def test_missing_calendar_does_not_fill_with_guessed_holiday(self):
        r = reconcile_candidates([obs("2026-01-07")], [])
        self.assertEqual(r["unmatched_or_untrusted_calendar_dates"], 1)
        self.assertEqual(r["source_admitted_dates"], [])

    def test_duplicate_observation_rejected(self):
        r = reconcile_candidates([obs("2026-01-08"), obs("2026-01-08")], [cal("2026-01-08")])
        self.assertEqual(r["status"], "FAIL_CLOSED_INVALID_OR_INCOMPLETE_INPUT")
        self.assertEqual(r["observed_weekday_receipts"], 0)

    def test_duplicate_calendar_rejected(self):
        r = reconcile_candidates([obs("2026-01-08")], [cal("2026-01-08"), cal("2026-01-08")])
        self.assertEqual(r["status"], "FAIL_CLOSED_INVALID_OR_INCOMPLETE_INPUT")

    def test_weekend_or_impossible_date_rejected(self):
        for day in ("2026-01-03", "2026-02-30", "20260105", "2030-13-05"):
            with self.subTest(day=day):
                self.assertEqual(reconcile_candidates([obs(day)], [])["status"],
                                 "FAIL_CLOSED_INVALID_OR_INCOMPLETE_INPUT")

    def test_no_pricing_positions_credentials_or_live_flags(self):
        r = reconcile_candidates([obs("2026-01-09", "NONEMPTY")], [cal("2026-01-09", "OPEN")])
        self.assertEqual(r["open_response_consistent_candidates_only"], 1)
        self.assertFalse(r["real_orders_authorized"])
        self.assertFalse(r["independent_holdout_authorized"])
        self.assertFalse(r["network_requests_attempted"])
        self.assertFalse(r["private_storage_mutated"])
        self.assertFalse(r["raw_rows_emitted"])
        self.assertEqual(r["ordering"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
