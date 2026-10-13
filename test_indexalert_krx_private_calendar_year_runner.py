"""Offline fail-closed behavior: cannot run private calendar audit on CI."""
import hashlib
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from research_v1_krx_private_calendar_year_runner import run_year

HASH = hashlib.sha256(b"synthetic").hexdigest()


class TestPrivateCalendarYearRunner(unittest.TestCase):
    def test_defaults_to_dry_run_without_any_file_reads(self):
        x=run_year(year=2025,document=Path("/data/nonexistent.xls"),
                   claim=Path("/data/nonexistent.json"),
                   expected_document_sha256=HASH)
        self.assertEqual(x["status"],"DRY_RUN_NO_PRIVATE_FILES_READ")
        self.assertIsNone(x["source_comparison"])

    def test_requires_dedicated_worker_even_with_fake_private_paths(self):
        with patch.dict("os.environ",{"RAILWAY_SERVICE_NAME":"untrusted-worker",
                                       "KRX_PRIVATE_RAW_DIR":"/data"},clear=True):
            x=run_year(year=2025,document=Path("/data/a.xls"),
                claim=Path("/data/b.json"),expected_document_sha256=HASH,execute=True)
        self.assertEqual(x["status"],"FAIL_CLOSED_NO_AUTHORIZED_SOURCE")
        self.assertFalse(x["live_orders_authorized"])

    def test_no_private_volume_in_ci_even_if_worker_name_spoofed(self):
        with patch.dict("os.environ",{"RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
                                       "KRX_PRIVATE_RAW_DIR":"/tmp"},clear=True):
            x=run_year(year=2025,document=Path("/data/a.xls"),
                claim=Path("/data/b.json"),expected_document_sha256=HASH,execute=True)
        self.assertEqual(x["status"],"FAIL_CLOSED_NO_AUTHORIZED_SOURCE")
        self.assertIsNone(x["original_document_sha256"])

    def test_year_and_hash_format_refusal(self):
        with patch.dict("os.environ",{"RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
                                       "KRX_PRIVATE_RAW_DIR":"/data"},clear=True):
            for bad_year,bad_hash in ((2027,HASH),(2015,"not-a-sha"),(True,HASH)):
                with self.subTest(bad_year=bad_year,bad_hash=bad_hash):
                    x=run_year(year=bad_year,document=Path("/data/a.xls"),
                        claim=Path("/data/b.json"),expected_document_sha256=bad_hash,execute=True)
                    self.assertEqual(x["status"],"FAIL_CLOSED_NO_AUTHORIZED_SOURCE")

    def test_never_report_original_days_or_prices(self):
        x=run_year(year=2026,document=Path("/data/a.xls"),claim=Path("/data/b.json"),
                   expected_document_sha256=HASH)
        self.assertEqual(x["ordering"],"DISABLED")
        self.assertFalse(x["performance_authorized"])
        self.assertFalse(x["source_admitted_for_pit"])
        self.assertFalse(x["official_session_schedule_attested"])
        self.assertFalse(x["27_quarantined_securities_released"])
        self.assertFalse(x["original_market_rows_emitted"])
        self.assertFalse(x["network_requests_attempted"])


    def test_source_rows_validate_before_private_comparison(self):
        source="일자,요일,비고\n2026-06-03,수,선거\n2026-07-17,금,휴장\n".encode("utf-8-sig")
        data={
            "source_kind":"KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE",
            "source_page_url":"https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp",
            "source_document_sha256":hashlib.sha256(source).hexdigest(),
            "market":"KOSPI_CASH_EQUITIES",
            "year":2026,
            "downloaded_at_utc":"2026-10-14T00:00:00Z",
            "calendar_closed_days":["2026-06-03","2026-07-17"],
        }
        with tempfile.TemporaryDirectory() as folder:
            doc=Path(folder)/"export.csv"
            claim=Path(folder)/"claim.json"
            doc.write_bytes(source)
            claim.write_text(json.dumps(data),encoding="utf-8")
            env={"RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
                 "KRX_PRIVATE_RAW_DIR":"/data"}
            simulated={"status":"EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT",
                       "verified_original_pairs":201,
                       "original_empty_day_count":14,
                       "reference_closed_day_count":2}
            with (patch.dict("os.environ",env,clear=True),
                  patch("research_v1_krx_private_calendar_year_runner._in_private_mount",
                        return_value=True),
                  patch("pathlib.Path.exists",return_value=True),
                  patch("pathlib.Path.is_symlink",return_value=False),
                  patch("research_v1_krx_private_calendar_year_runner.audit_private_scope",
                        return_value=simulated) as mock):
                result=run_year(
                    year=2026,document=doc,claim=claim,
                    expected_document_sha256=hashlib.sha256(source).hexdigest(),
                    execute=True)
                self.assertEqual(result["status"],"EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT")
                self.assertFalse(result["source_admitted_for_pit"])
                mock.assert_called_once()
                data["calendar_closed_days"]=["2026-06-03","2026-07-16"]
                claim.write_text(json.dumps(data),encoding="utf-8")
                second=run_year(
                    year=2026,document=doc,claim=claim,
                    expected_document_sha256=hashlib.sha256(source).hexdigest(),
                    execute=True)
                self.assertEqual(second["status"],"FAIL_CLOSED_NO_AUTHORIZED_SOURCE")
                self.assertEqual(mock.call_count,1)

    def test_unsupported_original_binary_sheet_never_calls_private_audit(self):
        blob=b"\xd0\xcf\x11\xe0" + b"x"*80
        data={
            "source_kind":"KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE",
            "source_page_url":"https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp",
            "source_document_sha256":hashlib.sha256(blob).hexdigest(),
            "market":"KOSPI_CASH_EQUITIES",
            "year":2026,
            "downloaded_at_utc":"2026-10-14T00:00:00Z",
            "calendar_closed_days":["2026-06-03"],
        }
        with tempfile.TemporaryDirectory() as folder:
            doc=Path(folder)/"original.xls"
            claim=Path(folder)/"claim.json"
            doc.write_bytes(blob)
            claim.write_text(json.dumps(data),encoding="utf-8")
            env={"RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
                 "KRX_PRIVATE_RAW_DIR":"/data"}
            with (patch.dict("os.environ",env,clear=True),
                  patch("research_v1_krx_private_calendar_year_runner._in_private_mount",
                        return_value=True),
                  patch("pathlib.Path.exists",return_value=True),
                  patch("pathlib.Path.is_symlink",return_value=False),
                  patch("research_v1_krx_private_calendar_year_runner.audit_private_scope"
                        ) as mock):
                result=run_year(
                    year=2026,document=doc,claim=claim,
                    expected_document_sha256=hashlib.sha256(blob).hexdigest(),
                    execute=True)
                self.assertEqual(result["status"],"FAIL_CLOSED_NO_AUTHORIZED_SOURCE")
                mock.assert_not_called()

if __name__=="__main__":
    unittest.main()
