"""Offline fail-closed behavior: cannot run private calendar audit on CI."""
import hashlib
import json
import tempfile
from pathlib import Path
from datetime import date, timedelta
from contextlib import redirect_stdout
import io
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
                self.assertEqual(result["status"],"FAIL_CLOSED_INCOMPLETE_PRIVATE_SOURCE_COMPARISON_RECEIPT")
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

    def test_real_xlsx_rows_are_checked_before_private_source_verifier(self):
        import json
        import tempfile
        from test_indexalert_krx_calendar_xlsx_source_validator import make_book, claim as make_claim
        raw=make_book()
        data=make_claim(raw)
        with tempfile.TemporaryDirectory() as folder:
            doc=Path(folder)/"original.xlsx"
            note=Path(folder)/"claim.json"
            doc.write_bytes(raw)
            note.write_text(json.dumps(data),encoding="utf-8")
            env={"RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
                 "KRX_PRIVATE_RAW_DIR":"/data"}
            proof={"status":"EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT",
                   "verified_original_pairs":201,"original_empty_day_count":14}
            with (patch.dict("os.environ",env,clear=True),
                  patch("research_v1_krx_private_calendar_year_runner._in_private_mount",return_value=True),
                  patch("pathlib.Path.exists",return_value=True),
                  patch("pathlib.Path.is_symlink",return_value=False),
                  patch("research_v1_krx_private_calendar_year_runner.audit_private_scope",
                        return_value=proof) as private):
                out=run_year(year=2026,document=doc,claim=note,
                        expected_document_sha256=hashlib.sha256(raw).hexdigest(),execute=True)
                self.assertEqual(out["status"],"FAIL_CLOSED_INCOMPLETE_PRIVATE_SOURCE_COMPARISON_RECEIPT")
                private.assert_called_once()
                self.assertFalse(out["source_admitted_for_pit"])
                data["calendar_closed_days"]=["2026-06-03","2026-07-16"]
                note.write_text(json.dumps(data),encoding="utf-8")
                blocked=run_year(year=2026,document=doc,claim=note,
                        expected_document_sha256=hashlib.sha256(raw).hexdigest(),execute=True)
                self.assertEqual(blocked["status"],"FAIL_CLOSED_NO_AUTHORIZED_SOURCE")
                self.assertEqual(private.call_count,1)


    def test_full_year_original_manifest_sha_pinned_synthetic_receipt_can_reconcile(self):
        """A complete, mocked 2026 scope has to match the REAL manifest metadata.

        CSV rows/holidays and source receipts here are synthetic and never
        represent actual exchange observations or exchange source admission.
        """
        from research_v1_krx_private_calendar_year_runner import MANIFEST
        year = 2026
        july = [date(year, 1, 1) + timedelta(days=i) for i in range(31)]
        dates = [d for d in july if d.weekday() < 5][:14]
        lines = ["일자,요일,비고"] + [
            f"{d.isoformat()},{'월화수목금토일'[d.weekday()]},합성" for d in dates
        ]
        raw = ("\n".join(lines) + "\n").encode("utf-8-sig")
        digest = hashlib.sha256(raw).hexdigest()
        sidecar = {
            "source_kind": "KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE",
            "source_page_url": "https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp",
            "source_document_sha256": digest,
            "market": "KOSPI_CASH_EQUITIES",
            "year": year,
            "downloaded_at_utc": "2026-10-14T00:00:00Z",
            "calendar_closed_days": [d.isoformat() for d in dates],
        }
        inventory = json.loads(MANIFEST.read_text(encoding="utf-8"))
        record = next(x for x in inventory["offline_verification"]["per_year"]
                      if x["year"] == year)
        exact = {
            "status": "EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT",
            "weekday_scope_count": 201,
            "verified_original_pairs": 201,
            "original_empty_day_count": 14,
            "reference_closed_day_count": 14,
            "empty_on_reference_closed": 14,
            "empty_on_reference_open": 0,
            "nonempty_on_reference_closed": 0,
            "original_audit_compatible_snapshot_sha256": record["reported_metadata_snapshot_sha256"],
            "comparison_metadata_sha256": hashlib.sha256(b"synthetic-comparison").hexdigest(),
            "original_official_calendar_attested": False,
            "source_contract_gates_C_D_open": False,
            "real_orders_authorized": False,
        }
        with tempfile.TemporaryDirectory() as rootdir:
            doc = Path(rootdir) / "synthetic-original.csv"
            claim = Path(rootdir) / "synthetic-sidecar.json"
            doc.write_bytes(raw)
            claim.write_text(json.dumps(sidecar), encoding="utf-8")
            env = {
                "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
                # Intentionally NO KRX_PRIVATE_RAW_DIR: original audit defaults /data.
            }
            with (patch.dict("os.environ", env, clear=True),
                  patch("research_v1_krx_private_calendar_year_runner._in_private_mount",
                        return_value=True),
                  patch("pathlib.Path.exists", return_value=True),
                  patch("pathlib.Path.is_symlink", return_value=False),
                  patch("research_v1_krx_private_calendar_year_runner.audit_private_scope",
                        return_value=exact) as comparison):
                result = run_year(year=year, document=doc, claim=claim,
                                  expected_document_sha256=digest, execute=True)
                self.assertEqual(result["status"], "EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT")
                self.assertFalse(result["source_admitted_for_pit"])
                self.assertEqual(result["yearly_expected_weekday_pairs"], 201)
                self.assertEqual(result["yearly_expected_empty_responses"], 14)
                self.assertEqual(comparison.call_args.kwargs["private_root"],
                                 Path("/data/openapi_kospi_history_v1"))
                self.assertEqual(comparison.call_args.kwargs["expected_original_audit_snapshot_sha256"],
                                 record["reported_metadata_snapshot_sha256"])
                # A second original "audit" reply without its fingerprint MUST
                # not pass, even if it claims the matching status.
                missing = dict(exact)
                missing.pop("original_audit_compatible_snapshot_sha256")
                comparison.return_value = missing
                failed = run_year(year=year, document=doc, claim=claim,
                                  expected_document_sha256=digest, execute=True)
                self.assertEqual(failed["status"],
                                 "FAIL_CLOSED_INCOMPLETE_PRIVATE_SOURCE_COMPARISON_RECEIPT")
                self.assertFalse(failed["source_admitted_for_pit"])

                incorrect = dict(exact, original_empty_day_count=13)
                comparison.return_value = incorrect
                failed = run_year(year=year, document=doc, claim=claim,
                                  expected_document_sha256=digest, execute=True)
                self.assertEqual(failed["status"],
                                 "FAIL_CLOSED_INCOMPLETE_PRIVATE_SOURCE_COMPARISON_RECEIPT")
                comparison.return_value = dict(exact, empty_on_reference_open=1)
                failed = run_year(year=year, document=doc, claim=claim,
                                  expected_document_sha256=digest, execute=True)
                self.assertEqual(failed["status"],
                                 "FAIL_CLOSED_INCOMPLETE_PRIVATE_SOURCE_COMPARISON_RECEIPT")

                # Mismatch is preserved as diagnostic evidence, but never
                # treated as successful source admission.
                mismatch = dict(exact,
                    status="EXACT_DATE_SET_MISMATCH_SOURCE_ADMISSION_BLOCKED",
                    empty_on_reference_closed=13,
                    empty_on_reference_open=1,
                    nonempty_on_reference_closed=1)
                comparison.return_value = mismatch
                failed = run_year(year=year, document=doc, claim=claim,
                                  expected_document_sha256=digest, execute=True)
                self.assertEqual(failed["status"],
                                 "EXACT_DATE_SET_MISMATCH_SOURCE_ADMISSION_BLOCKED")
                self.assertFalse(failed["source_admitted_for_pit"])

    def test_cli_mismatch_is_failure_not_success(self):
        from research_v1_krx_private_calendar_year_runner import main
        fake_argv = ["runner", "--year", "2026", "--document", "/data/source.csv",
                     "--claim", "/data/sidecar.json",
                     "--expected-document-sha256", HASH, "--audit"]
        with (patch("sys.argv", fake_argv),
              patch("research_v1_krx_private_calendar_year_runner.run_year",
                    return_value={"status": "EXACT_DATE_SET_MISMATCH_SOURCE_ADMISSION_BLOCKED"}),
              redirect_stdout(io.StringIO())):
            with self.assertRaises(SystemExit) as ex:
                main()
            self.assertEqual(ex.exception.code, 1)

    def test_cli_dry_run_has_no_filesystem_io_and_no_error_exit(self):
        from research_v1_krx_private_calendar_year_runner import main
        fake_argv = ["runner", "--year", "2026", "--document", "/data/not-there",
                     "--claim", "/data/not-there", "--expected-document-sha256", HASH]
        capture = io.StringIO()
        with patch("sys.argv", fake_argv), redirect_stdout(capture):
            main()
        self.assertIn("DRY_RUN_NO_PRIVATE_FILES_READ", capture.getvalue())


if __name__=="__main__":
    unittest.main()
