"""Offline synthetic CSV parser: source row facts must equal provided claims."""
import hashlib
import unittest
from research_v1_krx_calendar_csv_source_validator import (
    extract_and_reconcile_csv as verify,
)
from research_v1_krx_official_calendar_input_preflight import SOURCE_PAGE

ORIGINAL = "일자,요일,비고\n2026-06-03,수,선거일\n2026-07-17,금,휴장\n".encode("utf-8-sig")


def claim(raw=ORIGINAL, dates=None):
    return {
        "source_kind": "KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE",
        "source_page_url": SOURCE_PAGE,
        "source_document_sha256": hashlib.sha256(raw).hexdigest(),
        "market": "KOSPI_CASH_EQUITIES",
        "year": 2026,
        "downloaded_at_utc": "2026-10-14T00:00:00Z",
        "calendar_closed_days": dates if dates is not None else ["2026-06-03","2026-07-17"],
    }


class StrictOriginalRowBinding(unittest.TestCase):
    def test_dates_read_from_original_bytes(self):
        a=verify(ORIGINAL,claim(),2026)
        self.assertEqual(a["status"],"SOURCE_CSV_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT")
        self.assertTrue(a["source_table_rows_verified_against_claim"])
        self.assertEqual(a["parsed_source_weekday_closures"],2)
        self.assertEqual(a["dates"],["2026-06-03","2026-07-17"])
        self.assertFalse(a["original_source_independently_authenticated"])
        self.assertFalse(a["actual_krx_trading_calendar_pit_admitted"])
        self.assertFalse(a["real_orders_authorized"])

    def test_forged_sidecar_same_hash_cannot_substitute_date(self):
        a=verify(ORIGINAL,claim(dates=["2026-06-03","2026-08-17"]),2026)
        self.assertEqual(a["status"],"FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_byte_change_refuses_before_any_table_mismatch(self):
        mutated=ORIGINAL.replace(b"2026-07-17",b"2026-07-16")
        a=verify(mutated,claim(),2026)
        self.assertEqual(a["status"],"FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_unsupported_xls_and_xlsx_and_html_cannot_be_claim_attested(self):
        for blob in (b"\xd0\xcf\x11\xe0" + b"x"*100,
                     b"PK\x03\x04" + b"x"*100,
                     b"<html>" + b"x"*100):
            with self.subTest(blob=blob[:4]):
                a=verify(blob,claim(blob),2026)
                self.assertEqual(a["status"],"FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_cp949_encoding(self):
        blob=ORIGINAL.decode("utf-8-sig").encode("cp949")
        a=verify(blob,claim(blob),2026)
        self.assertEqual(a["status"],"SOURCE_CSV_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT")

    def test_incorrect_weekday_refused(self):
        blob=ORIGINAL.decode("utf-8-sig").replace("2026-07-17,금","2026-07-17,목").encode()
        self.assertEqual(verify(blob,claim(blob),2026)["status"],
                         "FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_duplicate_day_rejected(self):
        blob=ORIGINAL + "2026-06-03,수,중복\n".encode()
        self.assertEqual(verify(blob,claim(blob),2026)["status"],
                         "FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_wrong_column_order_and_extra_column(self):
        for csvstr in (
            "요일,일자,비고\n수,2026-06-03,선거\n금,2026-07-17,휴장\n",
            "일자,요일,비고,시장\n2026-06-03,수,선거,KRX\n2026-07-17,금,휴장,KRX\n",
        ):
            blob=csvstr.encode()
            self.assertEqual(verify(blob,claim(blob),2026)["status"],
                             "FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_weekend_rows_are_not_day_traded(self):
        blob=ORIGINAL + "2026-06-06,토,토요일\n".encode()
        a=verify(blob,claim(blob),2026)
        self.assertEqual(a["status"],"SOURCE_CSV_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT")
        self.assertEqual(a["parsed_source_total_rows"],3)
        self.assertEqual(a["parsed_source_weekday_closures"],2)

    def test_false_source_claim_or_wrong_year_refused(self):
        c=claim();c["source_page_url"]="https://example.com"
        self.assertEqual(verify(ORIGINAL,c,2026)["status"],"FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")
        self.assertEqual(verify(ORIGINAL,claim(),2025)["status"],"FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_empty_and_malformed_date_refused(self):
        blob="일자,요일,비고\n2026-02-30,월,무효\n".encode()
        self.assertEqual(verify(blob,claim(blob,["2026-02-30"]),2026)["status"],
                         "FAIL_CLOSED_UNPARSED_OR_UNMATCHED_SOURCE_ROWS")

    def test_no_network_storage_trading_or_profit_authorization(self):
        a=verify(ORIGINAL,claim(),2026)
        self.assertEqual(a["source_openapi_requests"],0)
        self.assertEqual(a["ordering"],"DISABLED")
        self.assertFalse(a["performance_run_authorized"])
