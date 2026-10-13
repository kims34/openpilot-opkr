"""Synthetic-only no-network preflight for KRX official calendar export."""
import hashlib
import unittest

from research_v1_krx_official_calendar_input_preflight import (
    normalize_calendar_export_claim as check, SOURCE_PAGE,
)

ORIGINAL = b"FAKE-SYNTHETIC-KRX-SHEET-v1" * 12


def claim(year=2026, dates=None, source=ORIGINAL):
    return {
        "source_kind": "KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE",
        "source_page_url": SOURCE_PAGE,
        "source_document_sha256": hashlib.sha256(source).hexdigest(),
        "market": "KOSPI_CASH_EQUITIES",
        "year": year,
        "downloaded_at_utc": "2026-10-14T01:00:00Z",
        "calendar_closed_days": dates or ["2026-06-03", "2026-07-17"],
    }


class OriginalHolidayExportPreflight(unittest.TestCase):
    def test_bound_bytes_not_original_source_admission(self):
        x=check(ORIGINAL,claim(),2026)
        self.assertEqual(x["closed_weekday_count"],2)
        self.assertEqual(x["status"],"SOURCE_BYTES_HASH_BOUND_CALENDAR_CLAIM_ONLY_NOT_PIT")
        self.assertFalse(x["normalization_against_source_table_attested"])
        self.assertFalse(x["official_exchange_calendar_admitted"])
        self.assertFalse(x["performance_run_authorized"])
        self.assertFalse(x["orders_authorized"])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_tampered_source_does_not_pass(self):
        x=check(ORIGINAL+b"x",claim(),2026)
        self.assertTrue(x["status"].startswith("FAIL_CLOSED"))

    def test_wrong_market_does_not_pass(self):
        c=claim();c["market"]="DERIVATIVES"
        self.assertTrue(check(ORIGINAL,c,2026)["status"].startswith("FAIL_CLOSED"))

    def test_third_party_source_claim_does_not_pass(self):
        c=claim();c["source_kind"]="XKRX_SECONDARY_PYTHON"
        self.assertTrue(check(ORIGINAL,c,2026)["status"].startswith("FAIL_CLOSED"))

    def test_duplicates_and_weekends_do_not_pass(self):
        for dates in (["2026-06-03","2026-06-03"],["2026-06-06"],
                      ["2025-07-17"],["2026-02-30"]):
            with self.subTest(dates=dates):
                self.assertTrue(check(ORIGINAL,claim(dates=dates),2026)["status"].startswith("FAIL_CLOSED"))

    def test_claim_must_match_year(self):
        self.assertTrue(check(ORIGINAL,claim(),2025)["status"].startswith("FAIL_CLOSED"))
        self.assertTrue(check(ORIGINAL,claim(year=True),True)["status"].startswith("FAIL_CLOSED"))

    def test_backdated_or_malformed_timestamp_rejected(self):
        for time in ("2014-01-01T01:00:00Z","2026-10-14T10:00:00+09:00","bad"):
            c=claim();c["downloaded_at_utc"]=time
            self.assertTrue(check(ORIGINAL,c,2026)["status"].startswith("FAIL_CLOSED"))

    def test_blob_size_and_encoding_rejected(self):
        self.assertTrue(check(b"",claim(),2026)["status"].startswith("FAIL_CLOSED"))
        self.assertTrue(check("pretend",claim(),2026)["status"].startswith("FAIL_CLOSED"))
        self.assertTrue(check(ORIGINAL,{**claim(),"calendar_closed_days":[]},2026)["status"].startswith("FAIL_CLOSED"))

    def test_unverified_metadata_must_not_release_quarantined_securities(self):
        x=check(ORIGINAL,claim(),2026)
        self.assertFalse(x["27_problem_securities_released"])
        self.assertFalse(x["original_security_status_pit_verified"])
        self.assertFalse(x["holdout_authorized"])
        self.assertFalse(x["network_requests_attempted"])
        self.assertFalse(x["private_data_mutated"])


if __name__=="__main__":
    unittest.main()
