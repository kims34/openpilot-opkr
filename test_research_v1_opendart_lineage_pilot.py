"""Offline safety tests for the OpenDART M20 lineage pilot.

Synthetic identifiers/amounts only. No network, broker, KRX or credentials.
"""
import io
import os
import unittest
import zipfile
from unittest.mock import patch

from research_v1_opendart_lineage_pilot import (
    BUSINESS_YEAR, REPORT_CODE, STOCK_CODE, ACCOUNT_ID, LEGACY_ACCOUNT_ID,
    corp_from_official_zip, filing_receipts, financial_shape, operating_taxonomy_shape, run,
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
        "account_nm": "영업이익",
        "currency": "KRW",
        "rcept_no": RECEIPT,
        "thstrm_amount": "1,234",
        "frmtrm_q_amount": "1,200",
    }]}


def taxonomy_payload():
    return {"status": "000", "list": [{
        "sj_div": "IS1", "account_id": ACCOUNT_ID,
        "label_kor": "영업이익(손실)", "data_tp": "X",
    }]}


class FakeResponse:
    def __init__(self, content=b"", obj=None, code=200):
        self.content = content
        self._obj = obj
        self.status_code = code

    def json(self):
        return self._obj


class FakeSession:
    def __init__(self, rows=None, files=None, money=None, taxonomy=None):
        self.rows = rows if rows is not None else [(CORP, STOCK_CODE)]
        self.files = files if files is not None else filing_payload()
        self.money = money if money is not None else financial_payload()
        self.taxonomy = taxonomy if taxonomy is not None else taxonomy_payload()
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
        if url.endswith("xbrlTaxonomy.json"):
            assert params["sj_div"] == "IS1"
            return FakeResponse(content=b"{}", obj=self.taxonomy)
        if url.endswith("fnlttSinglAcntAll.json"):
            return FakeResponse(content=b"{}", obj=self.money)
        raise ValueError("unexpected endpoint")


class OpenDartLineagePilotTests(unittest.TestCase):
    def test_missing_and_duplicate_lines_are_distinguished_without_admission(self):
        for count, reason in ((0, "missing"), (2, "multiple")):
            with self.subTest(count=count):
                payload = financial_payload()
                row = payload["list"][0]
                payload["list"] = [dict(row) for _ in range(count)]
                # Unrelated issuer/year/statement rows must not affect counts.
                payload["list"].extend([
                    dict(row, account_id="dart_OperatingIncomeLoss", corp_code="87654321"),
                    dict(row, account_id="dart_OperatingIncomeLoss", bsns_year="2024"),
                    dict(row, account_id="dart_OperatingIncomeLoss", sj_div="CF"),
                ])
                session = FakeSession(money=payload)
                with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-not-real"}, clear=True):
                    out = run(session)
                self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
                self.assertEqual(out["failure_reason_code"], reason + " standardized operating-profit line" + ("s" if count else ""))
                self.assertEqual(out["expected_account_id_match_count"], count)
                self.assertEqual(out["dart_operating_income_candidate_count"], count)
                self.assertFalse(out["alternative_account_semantics_verified"])
                for flag in ("pit_source_admitted", "performance_run_authorized", "live_order_authorized"):
                    self.assertIs(out[flag], False)
                self.assertEqual(len(session.calls), 4)
                for private in (CORP, RECEIPT, "1,234", "synthetic-not-real"):
                    self.assertNotIn(private, str(out))

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
        out = financial_shape(financial_payload(), CORP, {RECEIPT}, taxonomy_payload())
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
                financial_shape(payload, CORP, {RECEIPT}, taxonomy_payload())

    def test_never_promotes_or_authorizes_performance_even_with_valid_data(self):
        session = FakeSession()
        with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-not-real"}, clear=True):
            out = run(session)
        self.assertEqual(session.calls,
                         ["corpCode.xml", "list.json", "xbrlTaxonomy.json", "fnlttSinglAcntAll.json"])
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
        self.assertTrue(out["current_official_operating_taxonomy_verified"])
        self.assertFalse(out["historical_taxonomy_version_verified"])
        self.assertFalse(out["quarter_comparability_and_restatement_verified"])

    def test_taxonomy_must_be_exact_unique_and_monetary(self):
        for field, value in (("sj_div", "IS2"), ("label_kor", "당기순이익"),
                             ("account_id", LEGACY_ACCOUNT_ID), ("data_tp", "Text")):
            p = taxonomy_payload()
            p["list"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                operating_taxonomy_shape(p)
        p = taxonomy_payload()
        p["list"] *= 2
        for malformed in (p, None, {"status": "000", "list": []}, {"status": "013"}):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                financial_shape(financial_payload(), CORP, {RECEIPT}, malformed)

    def test_bad_taxonomy_stops_before_financial_fetch(self):
        session = FakeSession(taxonomy={"status": "013"})
        with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-not-real"}, clear=True):
            out = run(session)
        self.assertEqual(out["failure_stage"], "OPERATING_TAXONOMY")
        self.assertEqual(len(session.calls), 3)
        self.assertNotIn("fnlttSinglAcntAll.json", session.calls)
        self.assertFalse(out["performance_run_authorized"])

    def test_statement_currency_labels_and_amounts_cannot_be_guessed(self):
        for field, value in (("currency", "USD"), ("currency", None),
                             ("account_nm", "당기순이익"),
                             ("thstrm_amount", "1,2,34"),
                             ("frmtrm_q_amount", "1,200,")):
            p = financial_payload()
            p["list"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                financial_shape(p, CORP, {RECEIPT}, taxonomy_payload())
        p = financial_payload()
        p["list"].append(dict(p["list"][0], account_id=LEGACY_ACCOUNT_ID))
        with self.assertRaisesRegex(ValueError, "competing"):
            financial_shape(p, CORP, {RECEIPT}, taxonomy_payload())

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

