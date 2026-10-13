"""Offline fail-closed behavior: cannot run private calendar audit on CI."""
import hashlib
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


if __name__=="__main__":
    unittest.main()
