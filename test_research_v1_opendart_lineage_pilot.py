"""Offline safety tests for the OpenDART M20 lineage pilot.

Synthetic identifiers/amounts only. No network, broker, KRX or credentials.
"""
import io
import os
import unittest
import zipfile
from unittest.mock import patch

from research_v1_opendart_lineage_pilot import (
    BUSINESS_YEAR, REPORT_CODE, STOCK_CODE, ACCOUNT_ID,
    corp_from_official_zip, filing_receipts, financial_shape, run,
)

CORP = "12345678"
RECEIPT = "20251114000001"


def fake_zip(rows):
    xml = "<result>" + "".join(
        f"<list><corp_code>{corp}</corp_code><stock_code>{stock}</stock_code></list>"
        for corp, stock in rows
    ) + "</result>"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as out:
        out.writestr("CORPCODE.xml", xml)
    return buf.getvalue()


def filing_payload():
    return {"status": "000", "total_page": 1, "list": [
        {"report_nm": "분기보고서 (2025.09)", "rcept_no": RECEIPT},
    ]}


def financial_payload():
    return {"status": "000", "list": [{
        "corp_code": CORP,
        "bsns_year": BUSINESS_YEAR,
        "reprt_code": REPORT_CODE,
        "sj_div": "IS",
        "account_id": ACCOUNT_ID,
        "rcept_no": RECEIPT,
        "thstrm_amount": "1,234",
        "frmtrm_q_amount": "1,200",
    }]}


class FakeResponse:
    def __init__(self, content=b"", obj=None, code=200):
        self.content = content
        self._obj = obj
        self.status_code = code

    def json(self):
        return self._obj


class FakeSession:
    def __init__(self, rows=None, files=None, money=None):
        self.rows = rows if rows is not None else [(CORP, STOCK_CODE)]
        self.files = files if files is not None else filing_payload()
        self.money = money if money is not None else financial_payload()
        self.calls = []

    def get(self, url, *, params, timeout, allow_redirects):
        assert allow_redirects is False
        assert timeout == 20
        assert url.startswith("https://opendart.fss.or.kr/api/")
        self.calls.append(url.split("/")[-1])
        if url.endswith("corpCode.xml"):
            return FakeResponse(content=fake_zip(self.rows))
        if url.endswith("list.json"):
            return FakeResponse(content=b"{}", obj=self.files)
        if url.endswith("fnlttSinglAcntAll.json"):
            return FakeResponse(content=b"{}", obj=self.money)
        raise ValueError("unexpected endpoint")


class OpenDartLineagePilotTests(unittest.TestCase):
    def test_current_corp_mapping_exactly_one(self):
        self.assertEqual(corp_from_official_zip(fake_zip([(CORP, STOCK_CODE)])), CORP)
        for rows in ([], [(CORP, STOCK_CODE), ("87654321", STOCK_CODE)],
                     [("bad", STOCK_CODE)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                corp_from_official_zip(fake_zip(rows))

    def test_unofficial_archive_fails_closed(self):
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            corp_from_official_zip(b"not a zip")

    def test_filing_receipts_exact_and_complete_page(self):
        self.assertEqual(filing_receipts(filing_payload()), {RECEIPT})
        for changed in ({"status": "013", "total_page": 1, "list": []},
                        {"status": "000", "total_page": 2, "list": filing_payload()["list"]},
                        {"status": "000", "total_page": 1, "list": []}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                filing_receipts(changed)

    def test_financial_line_filing_and_quarter_amounts_must_match(self):
        out = financial_shape(financial_payload(), CORP, {RECEIPT})
        self.assertTrue(out["official_filing_receipt_linked"])
        self.assertTrue(out["standardized_operating_profit_quarter_shape_found"])
        for mutation in ("wrong_id", "bad_prior", "wrong_receipt", "wrong_period"):
            payload = financial_payload()
            row = payload["list"][0]
            if mutation == "wrong_id":
                row["account_id"] = "-표준계정코드 미사용-"
            elif mutation == "bad_prior":
                row["frmtrm_q_amount"] = ""
            elif mutation == "wrong_receipt":
                row["rcept_no"] = "20251114000002"
            else:
                row["reprt_code"] = "11011"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                financial_shape(payload, CORP, {RECEIPT})

    def test_never_promotes_or_authorizes_performance_even_with_valid_data(self):
        session = FakeSession()
        with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-not-real"}, clear=True):
            out = run(session)
        self.assertEqual(session.calls,
                         ["corpCode.xml", "list.json", "fnlttSinglAcntAll.json"])
        self.assertEqual(out["source_status"], "PILOT_SOURCE_SHAPE_PRESENT_NOT_PIT_ADMITTED")
        for key in ("pit_source_admitted", "performance_run_authorized",
                    "holdout_authorized", "champion_change_allowed",
                    "live_order_authorized", "krx_status_verified",
                    "historical_filing_version_pit_verified",
                    "exact_publication_time_verified", "quarterly_amounts_saved"):
            self.assertIs(out[key], False, key)
        self.assertEqual(out["ordering"], "DISABLED")
        self.assertNotIn("synthetic-not-real", str(out))
        self.assertNotIn(CORP, str(out))
        self.assertNotIn(RECEIPT, str(out))

    def test_absent_key_does_not_connect(self):
        with patch.dict(os.environ, {}, clear=True):
            out = run(FakeSession())
        self.assertEqual(out["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertFalse(out["pit_source_admitted"])

    def test_official_data_gap_is_fail_closed_without_leaks(self):
        session = FakeSession(money={"status": "013"})
        with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-not-real"}, clear=True):
            out = run(session)
        self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_stage"], "FINANCIAL_LINE")
        self.assertEqual(out["failure_reason_code"], "official financial endpoint not admitted")
        self.assertFalse(out["performance_run_authorized"])
        self.assertNotIn("synthetic-not-real", str(out))


if __name__ == "__main__":
    unittest.main()
