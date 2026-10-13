"""Zero-network synthetic tests for SHA-verified source result adapter."""
import unittest

from research_v1_krx_calendar_receipt_adapter import (
    normalize_preverified_source_days as norm,
    NONEMPTY, EMPTY_WITH_MASTER, BOTH_EMPTY,
)
from research_v1_krx_calendar_gap_boundary import reconcile_candidates

PAIR = "a" * 64


def row(day="2026-01-02", state=EMPTY_WITH_MASTER, daily=0, common=0):
    return {
        "day": day, "source_day_class": state,
        "pair_sha256": PAIR, "daily_rows": daily, "common_rows": common,
    }


class TestKRXSourceDayAdapter(unittest.TestCase):
    def test_official_private_empty_source_class_is_unknown_not_holiday(self):
        x = norm([row()])
        self.assertEqual(x["status"], "DECLARED_SOURCE_METADATA_NORMALIZED_NOT_PIT")
        self.assertEqual(x["observations"][0]["response_state"], "EMPTY")
        self.assertFalse(x["original_source_bytes_verified_by_this_adapter"])
        self.assertFalse(x["calendar_attested"])

    def test_both_empty_is_unverified(self):
        x = norm([row(state=BOTH_EMPTY)])
        self.assertEqual(x["observations"][0]["response_state"], "EMPTY")
        self.assertFalse(x["PIT_admitted"])

    def test_nonempty_still_not_tradeable(self):
        x = norm([row(state=NONEMPTY, daily=700, common=500)])
        self.assertEqual(x["observations"][0]["response_state"], "NONEMPTY")
        self.assertFalse(x["security_status_attested"])
        self.assertFalse(x["real_orders_authorized"])

    def test_fail_closed_if_empty_class_has_nonempty_daily_rows(self):
        self.assertTrue(norm([row(daily=1)])["status"].startswith("FAIL_CLOSED"))

    def test_fail_closed_if_nonempty_class_has_no_common_stocks(self):
        self.assertTrue(norm([row(state=NONEMPTY, daily=2, common=0)])["status"].startswith("FAIL_CLOSED"))

    def test_fail_closed_if_invalid_hash_or_unsupported_class(self):
        invalid = row()
        invalid["pair_sha256"] = "bad"
        self.assertTrue(norm([invalid])["status"].startswith("FAIL_CLOSED"))
        invalid = row()
        invalid["source_day_class"] = "PROVEN_TRADING_DAY"
        self.assertTrue(norm([invalid])["status"].startswith("FAIL_CLOSED"))

    def test_fail_closed_on_duplicates_or_weekends(self):
        self.assertTrue(norm([row(), row()])["status"].startswith("FAIL_CLOSED"))
        self.assertTrue(norm([row(day="2026-01-03")])["status"].startswith("FAIL_CLOSED"))

    def test_metadata_adapter_and_calendar_candidate_never_promote(self):
        normalized = norm([row(day="2026-01-05")])
        evidence = {
            "date": "2026-01-05", "session_state": "CLOSED",
            "source_kind": "KRX_OFFICIAL_EXCHANGE_CALENDAR",
            "source_document_sha256": "b" * 64,
        }
        candidate = reconcile_candidates(normalized["observations"], [evidence])
        self.assertEqual(candidate["closure_candidates_only"], 1)
        self.assertFalse(candidate["official_calendar_independently_attested"])
        self.assertFalse(candidate["source_admitted_for_backtest"])
        self.assertEqual(candidate["source_admitted_dates"], [])

    def test_empty_input_and_boolean_int_counts_rejected(self):
        self.assertTrue(norm([])["status"].startswith("FAIL_CLOSED"))
        self.assertTrue(norm([row(daily=False)])["status"].startswith("FAIL_CLOSED"))

    def test_sorting_preserves_date_without_market_rows(self):
        x = norm([row(day="2026-01-06"), row(day="2026-01-05")])
        self.assertEqual([y["date"] for y in x["observations"]], ["2026-01-05", "2026-01-06"])
        self.assertNotIn("price", str(x))
        self.assertFalse(x["network_requests_attempted"])


if __name__ == "__main__":
    unittest.main()
