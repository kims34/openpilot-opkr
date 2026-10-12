"""Offline synthetic 2022/2023 six-issuer original Q3 quarterly earnings tests."""
from __future__ import annotations
import io
import json
import os
import zipfile
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import (
    YEARS,FROZEN_SLOTS,MAX_CALLS_PER_SLOT,
    original_first_receipt,original_quarter_fact,compare_pair,run,
    HistoricalOriginalGap,
)
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT,_window
from test_research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    corporation_zip,filing as filing_index,
)
from test_research_v1_opendart_m20_q3_original_numeric_compat import filing as original_xml
from test_research_v1_opendart_original_xbrl_pilot import FakeResponse,zipp

SYNTHETIC_KEY="SYNTHETIC_ONLY_NO_REAL_SECRET"
R22="20221114000001"
R23="20231114000001"


class SyntheticOfficialSession:
    def __init__(self,*,report23=None,report22=None,registry_missing=None,
                 bad_initial_year=None,wrong_zip_year=None):
        self.calls=[]
        self.report22=original_xml(2022,amount="-123456") if report22 is None else report22
        self.report23=original_xml(2023,amount="345678") if report23 is None else report23
        self.registry_missing=registry_missing
        self.bad_initial_year=bad_initial_year
        self.wrong_zip_year=wrong_zip_year
    def get(self,url,*,params,timeout,allow_redirects,stream=False):
        assert url.startswith("https://opendart.fss.or.kr/api/")
        assert params["crtfc_key"]==SYNTHETIC_KEY
        assert allow_redirects is False
        service=url.rsplit("/",1)[-1]
        self.calls.append(service)
        if service=="corpCode.xml":
            assert timeout==20 and not stream
            return FakeResponse(corporation_zip(tuple(
                c for c in COHORT if c!=self.registry_missing)))
        if service=="list.json":
            assert timeout==20 and not stream
            assert params["pblntf_ty"]=="A" and params["page_count"]=="100"
            year=int(params["bgn_de"][:4])
            assert year in YEARS
            assert (params["bgn_de"],params["end_de"])==_window(year)
            assert params["corp_code"].isdigit() and len(params["corp_code"])==8
            response=filing_index(year,no_original=year==self.bad_initial_year)
            return FakeResponse(parsed=response)
        if service=="fnlttXbrl.xml":
            assert timeout==30 and stream
            assert params["reprt_code"]=="11014"
            rid=params["rcept_no"]
            assert rid in (R22,R23)
            archive=self.report22 if rid==R22 else self.report23
            if self.wrong_zip_year==int(rid[:4]):
                archive=b"corrupt archive raw secret 987654321"
            return FakeResponse(archive)
        raise AssertionError("UNAPPROVED_OFFICIAL_ENDPOINT")


class OlderQ3OriginalSafetyTests(unittest.TestCase):
    def test_exact_frozen_six_issuers_and_two_older_years(self):
        self.assertEqual(YEARS,(2022,2023))
        self.assertEqual(FROZEN_SLOTS,(0,1,2,3,4,5))
        self.assertEqual(MAX_CALLS_PER_SLOT,5)
    def test_no_key_means_no_network(self):
        spy=SyntheticOfficialSession()
        with patch.dict(os.environ,{},clear=True):
            report=run(0,spy)
        self.assertEqual(report["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(spy.calls,[])
        self.assertFalse(report["m20_signal_pit_admitted"])
    def test_actual_original_q3_source_shapes_for_every_issuer_synthetically(self):
        for slot in FROZEN_SLOTS:
            with self.subTest(slot=slot):
                spy=SyntheticOfficialSession()
                with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
                    report=run(slot,spy)
                self.assertEqual(report["source_status"],
                                 "ORIGINAL_2022_2023_Q3_NUMERIC_PAIR_SHAPE_ONLY_NOT_PIT")
                self.assertEqual(spy.calls,["corpCode.xml","list.json","list.json",
                                            "fnlttXbrl.xml","fnlttXbrl.xml"])
                self.assertTrue(report["two_original_q3_numeric_representations_consistent"])
                self.assertTrue(report["same_original_filing_reporter_context"])
                self.assertEqual(report["original_first_submission_Q3_archives_examined"],2)
                for flag in ("historical_issuer_security_mapping_verified",
                             "original_statement_table_binding_verified",
                             "intraday_publication_time_verified",
                             "historical_filing_pit_verified",
                             "revision_chain_completed",
                             "complete_original_quarterly_history_verified",
                             "all_historical_issuers_verified",
                             "historical_mcap_and_tradability_verified",
                             "m20_signal_pit_admitted",
                             "m20_performance_run_authorized",
                             "independent_holdout_authorized",
                             "champion_change_authorized",
                             "real_orders_authorized",
                             "funds_movement_authorized",
                             "permissions_change_authorized",
                             "financial_amounts_or_issuer_ids_saved",
                             "amounts_delta_and_sign_retained"):
                    self.assertIs(report[flag],False,flag)
                self.assertEqual(report["ordering"],"DISABLED")
                blob=json.dumps(report)
                for private in COHORT+(R22,R23,"-123456","345678",
                                       "SYNTHETIC_CORP",SYNTHETIC_KEY):
                    self.assertNotIn(private,blob)
    def test_2022_2023_source_receipt_selection_by_original_year(self):
        self.assertEqual(original_first_receipt(filing_index(2022),2022),R22)
        self.assertEqual(original_first_receipt(filing_index(2023),2023),R23)
    def test_same_day_correction_not_ordered_as_original(self):
        p=filing_index(2023,revised=True,same_day=True)
        with self.assertRaises(HistoricalOriginalGap):
            original_first_receipt(p,2023)
    def test_first_version_correction_only_is_not_original(self):
        spy=SyntheticOfficialSession(bad_initial_year=2022)
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            out=run(0,spy)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_code"],"INITIAL_FILING_AMBIGUOUS_OR_MISSING")
        self.assertEqual(spy.calls,["corpCode.xml","list.json"])
        self.assertFalse(out["real_orders_authorized"])
    def test_missing_current_company_registry_not_historic_pit_substitute(self):
        spy=SyntheticOfficialSession(registry_missing=COHORT[0])
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            out=run(0,spy)
        self.assertEqual(out["failure_code"],"FIXED_ISSUER_ABSENT_FROM_REGISTRY")
        self.assertEqual(spy.calls,["corpCode.xml"])
    def test_bad_original_xml_archive_stops_and_redacts(self):
        spy=SyntheticOfficialSession(wrong_zip_year=2022)
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            out=run(0,spy)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn("987654321",json.dumps(out))
        self.assertFalse(out["m20_performance_run_authorized"])
    def test_two_years_qname_change_is_not_treated_as_same_concept(self):
        report=compare_pair(original_xml(2022),
                            original_xml(2023,
                                concept="ifrs-full:ProfitLossFromOperatingActivities"))
        self.assertFalse(report["same_exact_qname"])
        self.assertFalse(report["two_original_q3_numeric_representations_consistent"])
    def test_reporter_or_accuracy_change_not_silently_backfilled(self):
        for kwargs,name in (({"entity":"OTHER_SYNTHETIC_CORP"},
                             "same_original_filing_reporter_context"),
                            ({"decimals":"-3"},"same_declared_decimals")):
            with self.subTest(name=name):
                report=compare_pair(original_xml(2022),original_xml(2023,**kwargs))
                self.assertFalse(report[name])
                self.assertFalse(report["two_original_q3_numeric_representations_consistent"])
    def test_different_cfs_axis_or_ytd_not_a_quarter_fact(self):
        for kwargs in ({"member":"SeparateMember"},{"quarters":False}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(HistoricalOriginalGap):
                    original_quarter_fact(original_xml(2022,**kwargs),2022)
    def test_wrong_currency_or_duplicate_context_fact_fail_closed(self):
        with self.assertRaises(HistoricalOriginalGap):
            original_quarter_fact(original_xml(2022,duplicate=True),2022)
        with zipfile.ZipFile(io.BytesIO(original_xml(2022))) as source:
            xml=source.read("statement.xbrl")
        bad=zipp({"statement.xbrl":xml.replace(b"iso4217:KRW",b"iso4217:USD")})
        with self.assertRaises(HistoricalOriginalGap):
            original_quarter_fact(bad,2022)
    def test_unverifiable_precision_and_numeric_amount_rejected(self):
        for kwargs in ({"decimals":None},{"decimals":"incorrect"},
                       {"amount":"NaN"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(HistoricalOriginalGap):
                    original_quarter_fact(original_xml(2022,**kwargs),2022)
    def test_in_scope_only(self):
        for bad in (-1,6,"0",None):
            with self.subTest(value=bad):
                spy=SyntheticOfficialSession()
                out=run(bad,spy)
                self.assertEqual(out["source_status"],"FAIL_CLOSED_FROZEN_SLOT_INVALID")
                self.assertEqual(spy.calls,[])
        with self.assertRaises(HistoricalOriginalGap):
            original_quarter_fact(original_xml(2024),2024)
        with self.assertRaises(HistoricalOriginalGap):
            original_first_receipt(filing_index(2024),2024)


if __name__=="__main__":
    unittest.main()
