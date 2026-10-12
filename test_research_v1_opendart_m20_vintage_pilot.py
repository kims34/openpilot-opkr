"""Offline only, synthetic OpenDART list.json receipts (no network or keys)."""
import io
import json
import os
import unittest
import zipfile
from unittest.mock import patch

from research_v1_opendart_m20_vintage_pilot import (
    VintageEvidenceError, validate_complete_q3_filing_index,
    conservative_earliest_date_allowed, run,
)


def fake_corp_archive():
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, "w") as z:
        z.writestr(
            "CORPCODE.xml",
            "<result><list><stock_code>005930</stock_code>"
            "<corp_code>12345678</corp_code></list></result>",
        )
    return buff.getvalue()


def data():
    rows = [
        {"rcept_no":"20241114000001",
         "report_nm":"분기보고서 (2024.09)", "rcept_dt":"20241114"},
        {"rcept_no":"20251114000001",
         "report_nm":"분기보고서 (2025.09)", "rcept_dt":"20251114"},
    ]
    return {"status":"000","total_count":"2","total_page":"1",
            "page_no":"1","list":rows}


class Response:
    def __init__(self, content=b"", obj=None, code=200):
        self.content = content
        self.obj = obj
        self.status_code = code

    def json(self):
        return self.obj


class Session:
    def __init__(self, payload=None):
        self.payload = data() if payload is None else payload
        self.paths=[]

    def get(self, path, *, params, timeout, allow_redirects):
        assert path.startswith("https://opendart.fss.or.kr/api/")
        assert allow_redirects is False
        assert timeout == 20
        endpoint=path.rsplit("/",1)[1]
        self.paths.append(endpoint)
        if endpoint=="corpCode.xml":
            return Response(content=fake_corp_archive())
        if endpoint=="list.json":
            assert params["pblntf_ty"]=="A"
            assert params["bgn_de"]=="20241001"
            assert params["end_de"]=="20261012"
            return Response(content=b"{}",obj=self.payload)
        raise ValueError("UNEXPECTED_ENDPOINT")


class M20VintageTests(unittest.TestCase):
    def test_two_original_q3_receipt_dates_are_ordered_but_not_pit(self):
        got=validate_complete_q3_filing_index(data())
        self.assertEqual(got["q_minus_4_initial_filing_date"],"2024-11-14")
        self.assertEqual(got["q_current_initial_filing_date"],"2025-11-14")
        self.assertEqual(got["q_minus_4_filing_versions_observed"],1)
        self.assertEqual(got["q_current_filing_versions_observed"],1)
        self.assertFalse(got["historical_publication_time_verified"])
        self.assertFalse(got["original_document_vintage_authenticated"])
        self.assertFalse(got["quarter_and_prior_year_amounts_comparable_verified"])
        self.assertTrue(got["receipt_date_only_no_intraday_publication_clock"])
        for sensitive in ("12345678","20241114000001","20251114000001"):
            self.assertNotIn(sensitive, json.dumps(got))

    def test_later_correction_does_not_rewrite_original_filing_date(self):
        p=data()
        p["list"].append({"rcept_no":"20251201000002",
                          "rcept_dt":"20251201",
                          "report_nm":"[기재정정]분기보고서 (2025.09)"})
        p["total_count"]="3"
        got=validate_complete_q3_filing_index(p)
        self.assertEqual(got["q_current_initial_filing_date"],"2025-11-14")
        self.assertEqual(got["q_current_filing_versions_observed"],2)
        self.assertFalse(got["historical_revision_lineage_independently_verified"])

    def test_same_day_multiple_versions_flagged_not_ordered_by_receipt(self):
        p=data()
        p["list"].append({"rcept_no":"20251114000002",
                          "rcept_dt":"20251114",
                          "report_nm":"[기재정정] 분기보고서 (2025.09)"})
        p["total_count"]="3"
        got=validate_complete_q3_filing_index(p)
        self.assertTrue(got["multiple_versions_on_initial_filing_date"])
        self.assertFalse(got["historical_publication_time_verified"])

    def test_no_same_day_or_unverified_future_admission(self):
        self.assertFalse(conservative_earliest_date_allowed(
            filing_date="2025-11-14",decision_date="2025-11-14",
            historical_available_at_verified=True))
        self.assertFalse(conservative_earliest_date_allowed(
            filing_date="2025-11-14",decision_date="2025-11-17",
            historical_available_at_verified=False))
        self.assertTrue(conservative_earliest_date_allowed(
            filing_date="2025-11-14",decision_date="2025-11-17",
            historical_available_at_verified=True))
        with self.assertRaisesRegex(VintageEvidenceError,"PIT_AUTHORITY_INVALID"):
            conservative_earliest_date_allowed(
                filing_date="2025-11-14",decision_date="2025-11-17",
                historical_available_at_verified="true")

    def test_incomplete_index_or_unpaged_data_rejected(self):
        for mutation in ("pages","count","page_number","oversize"):
            with self.subTest(mutation=mutation):
                p=data()
                if mutation=="pages":p["total_page"]="2"
                elif mutation=="count":p["total_count"]="30"
                elif mutation=="page_number":p["page_no"]="2"
                else:p["total_count"]="101"
                with self.assertRaises(VintageEvidenceError):
                    validate_complete_q3_filing_index(p)

    def test_missing_required_q3_2024_fails_closed(self):
        p=data()
        p["list"].pop(0)
        p["total_count"]="1"
        with self.assertRaisesRegex(VintageEvidenceError,"REQUIRED_Q3_REPORT_NOT_FOUND"):
            validate_complete_q3_filing_index(p)

    def test_duplicate_receipt_fails_closed(self):
        p=data()
        p["list"].append(dict(p["list"][0]))
        p["total_count"]="3"
        with self.assertRaisesRegex(VintageEvidenceError,"FILING_RECEIPT_DUPLICATED"):
            validate_complete_q3_filing_index(p)

    def test_receipt_date_drift_fails_closed(self):
        p=data()
        p["list"][0]["rcept_dt"]="20241115"
        with self.assertRaisesRegex(VintageEvidenceError,"FILING_INDEX_CHRONOLOGY_INVALID"):
            validate_complete_q3_filing_index(p)

    def test_official_source_error_keeps_all_authority_false(self):
        session=Session({"status":"013","list":[],"total_page":"0","total_count":"0"})
        with patch.dict(os.environ,{"OPENDART_API_KEY":"fake-secret"},clear=True):
            out=run(session)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_stage"],"HISTORICAL_FILING_INDEX")
        self.assertEqual(out["failure_reason"],"OFFICIAL_FILING_INDEX_NOT_ADMITTED")
        self.assertFalse(out["pit_source_admitted"])
        self.assertFalse(out["feature_performance_testing_authorized"])
        self.assertFalse(out["live_order_authorized"])
        self.assertNotIn("fake-secret",str(out))

    def test_valid_fake_source_remains_non_admitted(self):
        session=Session()
        with patch.dict(os.environ,{"OPENDART_API_KEY":"fake-secret"},clear=True):
            out=run(session)
        self.assertEqual(session.paths,["corpCode.xml","list.json"])
        self.assertEqual(out["source_status"],"DATE_LEVEL_REPORT_VINTAGE_PILOT_ONLY")
        for key in ("historical_revision_lineage_independently_verified",
                    "historical_publication_time_verified",
                    "original_document_vintage_authenticated",
                    "quarter_and_prior_year_amounts_comparable_verified",
                    "pit_source_admitted",
                    "feature_performance_testing_authorized",
                    "sealed_holdout_authorized","champion_change_authorized",
                    "live_order_authorized"):
            self.assertIs(out[key],False,key)
        self.assertEqual(out["ordering"],"DISABLED")
        for value in ("fake-secret","12345678","20251114000001"):
            self.assertNotIn(value,str(out))

    def test_missing_key_does_not_call_api(self):
        session=Session()
        with patch.dict(os.environ,{},clear=True):
            out=run(session)
        self.assertEqual(session.paths,[])
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(out["pit_source_admitted"])


if __name__ == "__main__":
    unittest.main()
