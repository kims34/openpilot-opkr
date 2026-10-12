"""Synthetic source-only tests; absolutely no real OpenDART or KRX network."""
import io
import json
import os
import unittest
from unittest.mock import patch
import zipfile

from research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    COHORT,YEARS,MAX_CALLS,_registry,_window,_index_state,_execute,run,
    CoverageError,
)


def corporation_zip(codes=COHORT,*,duplicate=None):
    rows=[]
    for i,code in enumerate(codes):
        rows.append(f"<list><stock_code>{code}</stock_code><corp_code>{i+1:08d}</corp_code></list>")
    if duplicate is not None:
        rows.append("<list><stock_code>"+duplicate+"</stock_code><corp_code>90000001</corp_code></list>")
    document=("<result>"+"".join(rows)+"</result>").encode("utf-8")
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("CORPCODE.xml",document)
    return stream.getvalue()


def filing(year,*,revised=False,same_day=False,no_original=False):
    day=f"{year}1114"
    receipt=day+"000001"
    rows=[{
        "rcept_no":receipt,"rcept_dt":day,
        "report_nm":f"분기보고서 ({year}.09)" if not no_original else f"[기재정정]분기보고서 ({year}.09)",
    }]
    if revised:
        when=day if same_day else f"{year}1202"
        rows.append({
            "rcept_no":when+"000002","rcept_dt":when,
            "report_nm":f"[기재정정]분기보고서 ({year}.09)",
        })
    return {
        "status":"000","total_count":str(len(rows)),
        "total_page":"1","page_no":"1","list":rows,
    }


class Response:
    status_code=200
    def __init__(self,raw=None,data=None):
        self.content=b"{}" if raw is None else raw
        self._data=data
    def json(self):
        return self._data


class FakeOpenDART:
    def __init__(self,*,bad=None,cohort=COHORT):
        self.calls=[]
        self.bad=bad
        self.cohort=cohort
    def get(self,url,*,params,timeout,allow_redirects):
        assert url.startswith("https://opendart.fss.or.kr/api/")
        assert allow_redirects is False and timeout==20
        assert params["crtfc_key"]=="TEST_ONLY_NOT_AN_ACTUAL_KEY"
        endpoint=url.rsplit("/",1)[1]
        assert endpoint in ("corpCode.xml","list.json")
        self.calls.append((endpoint,dict(params)))
        if endpoint=="corpCode.xml":
            return Response(raw=corporation_zip(self.cohort))
        assert set(params)=={"crtfc_key","corp_code","bgn_de","end_de","pblntf_ty","page_count"}
        assert params["pblntf_ty"]=="A" and params["page_count"]=="100"
        year=int(params["bgn_de"][:4])
        assert params["bgn_de"]==f"{year}1001"
        assert params["end_de"]==f"{year+1}0228"
        if self.bad==(year,params["corp_code"]):
            return Response(data={"status":"901","message":"LEAK:567890"})
        return Response(data=filing(year))


class OriginalMultiIssuerCoverageTests(unittest.TestCase):
    def test_frozen_cohort_quarters_not_return_selected(self):
        self.assertEqual(len(COHORT),6)
        self.assertEqual(YEARS,(2022,2023,2024,2025))
        self.assertEqual(MAX_CALLS,25)
        self.assertEqual(_window(2025),("20251001","20260228"))
    def test_default_no_secret_has_zero_calls(self):
        f=FakeOpenDART()
        with patch.dict(os.environ,{},clear=True):
            r=run(f)
        self.assertEqual(r["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(f.calls,[])
        self.assertFalse(r["m20_performance_run_authorized"])
        self.assertFalse(r["real_orders_authorized"])
    def test_frozen_6x4_all_initial_date_coverage_only(self):
        f=FakeOpenDART()
        with patch.dict(os.environ,{"OPENDART_API_KEY":"TEST_ONLY_NOT_AN_ACTUAL_KEY"},clear=True),\
             patch("research_v1_opendart_m20_six_issuer_q3_filing_coverage.time.sleep",return_value=None):
            r=run(f)
        self.assertEqual(r["source_status"],"FIXED_COHORT_ORIGINAL_Q3_DATE_COVERAGE_NOT_PIT")
        self.assertEqual(r["official_api_requests"],25)
        self.assertEqual(len(f.calls),25)
        self.assertEqual(r["date_identified_original_report_cells"],24)
        self.assertEqual(r["currently_mapped_issuer_count"],6)
        self.assertEqual(r["year_coverage_aggregates"]["2025"]["unambiguous_original_q3_date_count"],6)
        for field in ("historical_kospi_membership_verified",
                      "historical_corp_to_security_mapping_verified",
                      "historical_publication_instant_verified",
                      "historical_publication_pit_verified",
                      "original_quarterly_operating_profit_verified",
                      "full_cross_section_and_quarter_history_covered",
                      "m20_signal_pit_admitted","m20_performance_run_authorized",
                      "independent_holdout_authorized",
                      "champion_change_authorized","real_orders_authorized",
                      "funds_movement_authorized","permissions_change_authorized",
                      "raw_provider_values_or_identifiers_saved"):
            self.assertIs(r[field],False,field)
        self.assertEqual(r["ordering"],"DISABLED")
        packed=json.dumps(r)
        for secret in COHORT+("TEST_ONLY_NOT_AN_ACTUAL_KEY","20251114000001",
                              "2025-11-14","00000001","LEAK:567890"):
            self.assertNotIn(secret,packed)
    def test_registry_exact_current_identifiers_but_not_historical(self):
        a=_registry(corporation_zip())
        self.assertEqual(len(a),6)
        self.assertEqual(a["005930"],"00000003")
        self.assertEqual(_registry(corporation_zip(COHORT[:2])),{
            COHORT[0]:"00000001",COHORT[1]:"00000002",
        })
    def test_registry_duplicate_fails_before_filing(self):
        with self.assertRaisesRegex(CoverageError,"CORPORATION_MAPPING_NOT_UNIQUE"):
            _registry(corporation_zip(duplicate=COHORT[0]))
    def test_registry_invalid_non_zip_and_xml_entity(self):
        for raw in (b"not zip",b"PK\x03\x04",corporation_zip(())):
            with self.subTest(size=len(raw)):
                if len(raw)<10:
                    with self.assertRaises(CoverageError):
                        _registry(raw)
                else:
                    self.assertEqual(_registry(raw),{})
    def test_later_correction_does_not_rewrite_initial_day(self):
        start,end=_window(2025)
        got=_index_state(filing(2025,revised=True),2025,start,end)
        self.assertEqual(got,"ORIGINAL_FIRST_FILING_DATE_ONLY_NOT_PIT")
    def test_same_day_version_is_ambiguous(self):
        start,end=_window(2025)
        state=_index_state(filing(2025,revised=True,same_day=True),2025,start,end)
        self.assertEqual(state,"INITIAL_FILING_DATE_MULTIPLE_VERSIONS")
    def test_initial_version_lacks_original(self):
        start,end=_window(2025)
        state=_index_state(filing(2025,no_original=True),2025,start,end)
        self.assertEqual(state,"INITIAL_VERSION_NOT_ORIGINAL")
    def test_no_data_not_imputed(self):
        start,end=_window(2025)
        self.assertEqual(_index_state({"status":"013"},2025,start,end),"NO_FILINGS_IN_WINDOW")
        self.assertEqual(_index_state({
            "status":"000","total_page":"1","page_no":"1","total_count":"0","list":[],
        },2025,start,end),"Q3_ORIGINAL_NOT_FOUND")
    def test_bad_receipt_chronology_fails_closed(self):
        p=filing(2025)
        p["list"][0]["rcept_no"]="20251113000001"
        with self.assertRaisesRegex(CoverageError,"FILING_INDEX_CHRONOLOGY_INVALID"):
            _index_state(p,2025,*_window(2025))
    def test_unverified_multiple_pages_fails_closed(self):
        p=filing(2025)
        p["total_page"]="2"
        with self.assertRaisesRegex(CoverageError,"FILING_INDEX_PAGES_UNVERIFIED"):
            _index_state(p,2025,*_window(2025))
    def test_bad_provider_response_redacted(self):
        f=FakeOpenDART(bad=(2024,"00000001"))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"TEST_ONLY_NOT_AN_ACTUAL_KEY"},clear=True),\
             patch("research_v1_opendart_m20_six_issuer_q3_filing_coverage.time.sleep",return_value=None):
            res=run(f)
        self.assertEqual(res["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(res["failure_reason_code"],"FILING_INDEX_OFFICIAL_STATUS_FAILED")
        self.assertNotIn("LEAK:567890",json.dumps(res))
    def test_missing_current_registry_no_index_replacement(self):
        f=FakeOpenDART(cohort=COHORT[:3])
        with patch.dict(os.environ,{"OPENDART_API_KEY":"TEST_ONLY_NOT_AN_ACTUAL_KEY"},clear=True),\
             patch("research_v1_opendart_m20_six_issuer_q3_filing_coverage.time.sleep",return_value=None):
            res=run(f)
        self.assertEqual(res["source_status"],"FIXED_COHORT_ORIGINAL_Q3_DATE_COVERAGE_NOT_PIT")
        self.assertEqual(res["official_api_requests"],13)
        self.assertEqual(res["date_identified_original_report_cells"],12)
        self.assertEqual(res["year_coverage_aggregates"]["2022"]["missing_registry_mapping_count"],3)
    def test_year_cannot_expand_approved_scope(self):
        for y in (2021,2026,"2025",None):
            with self.subTest(y=y),self.assertRaises(CoverageError):
                _window(y)

if __name__=="__main__":
    unittest.main()
