"""No-network synthetic regression for new 5 frozen issuer original Q3 pairs."""
from __future__ import annotations
import json
import os
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_extra_original_q3_pairs import (
    FROZEN_SLOTS,MAX_CALLS_PER_SLOT,
    check_original_pair_slot,run,
)
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT
from test_research_v1_opendart_m20_six_issuer_q3_filing_coverage import corporation_zip
from test_research_v1_opendart_m20_q3_original_numeric_compat import filing
from test_research_v1_opendart_original_xbrl_pilot import (
    FakeResponse,R24,R25,index
)

KEY="SYNTHETIC_ONLY_DONT_USE"


class Session:
    def __init__(self,*,bad_zip=False,missing_code=None,concept_change=False):
        self.calls=[]
        self.bad_zip=bad_zip
        self.missing_code=missing_code
        self.concept_change=concept_change
    def get(self,url,*,params,timeout,allow_redirects,stream=False):
        assert url.startswith("https://opendart.fss.or.kr/api/")
        assert params["crtfc_key"]==KEY
        assert allow_redirects is False
        endpoint=url.rsplit("/",1)[1]
        self.calls.append(endpoint)
        if endpoint=="corpCode.xml":
            assert timeout==20 and stream is False
            codes=tuple(c for c in COHORT if c!=self.missing_code)
            return FakeResponse(corporation_zip(codes))
        if endpoint=="list.json":
            assert timeout==20 and stream is False
            assert params["bgn_de"]=="20241001" and params["end_de"]=="20261012"
            assert params["page_count"]=="100" and params["pblntf_ty"]=="A"
            return FakeResponse(b"{}",index())
        if endpoint=="fnlttXbrl.xml":
            assert timeout==30 and stream is True
            assert params["reprt_code"]=="11014"
            rid=params["rcept_no"]
            assert rid in (R24,R25)
            if rid==R24:
                blob=filing(2024,amount="123456")
            else:
                blob=filing(2025,amount="234567",
                            concept=(
                                "ifrs-full:ProfitLossFromOperatingActivities"
                                if self.concept_change else "dart:OperatingIncomeLoss"))
            return FakeResponse(b"NOT_ZIP" if self.bad_zip else blob)
        raise AssertionError("UNAPPROVED_ROUTE")


class AdditionalIssuerOriginalPairTests(unittest.TestCase):
    def test_five_exact_extra_frozen_slots_exclude_already_proven_firm(self):
        self.assertEqual(FROZEN_SLOTS,(0,1,3,4,5))
        self.assertEqual(MAX_CALLS_PER_SLOT,4)
        self.assertEqual(len(COHORT),6)
    def test_no_secret_makes_zero_network_calls_for_every_slot(self):
        for slot in FROZEN_SLOTS:
            with self.subTest(slot=slot):
                spy=Session()
                with patch.dict(os.environ,{},clear=True):
                    out=run(slot,spy)
                self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
                self.assertEqual(spy.calls,[])
                self.assertFalse(out["m20_performance_run_authorized"])
                self.assertFalse(out["real_orders_authorized"])
    def test_all_five_synthetic_original_pairs_and_no_risky_authority(self):
        for slot in FROZEN_SLOTS:
            with self.subTest(slot=slot):
                spy=Session()
                with patch.dict(os.environ,{"OPENDART_API_KEY":KEY},clear=True):
                    out=run(slot,spy)
                self.assertEqual(out["source_status"],
                    "ONE_NEW_ISSUER_ORIGINAL_Q3_NUMERIC_REPRESENTATION_SHAPE_ONLY")
                self.assertEqual(out["actual_official_api_calls"],4)
                self.assertEqual(out["original_xbrl_reports_fetched"],2)
                self.assertEqual(spy.calls,["corpCode.xml","list.json",
                                           "fnlttXbrl.xml","fnlttXbrl.xml"])
                self.assertTrue(out["minimal_original_pair_numeric_representation_consistent"])
                for name in ("historical_issuer_mapping_verified",
                             "original_statement_table_binding_verified",
                             "original_filing_historical_publication_pit_verified",
                             "historical_earnings_restatement_lineage_verified",
                             "complete_quarter_history_and_universe_verified",
                             "decision_time_mcap_and_security_status_verified",
                             "m20_signal_pit_admitted","m20_performance_run_authorized",
                             "independent_holdout_authorized",
                             "champion_change_authorized","real_orders_authorized",
                             "funds_movement_authorized","permissions_change_authorized",
                             "raw_earnings_filing_or_issuer_ids_saved",
                             "historical_profit_amounts_saved"):
                    self.assertIs(out[name],False,name)
                self.assertEqual(out["ordering"],"DISABLED")
                txt=json.dumps(out)
                for secret in COHORT+(R24,R25,"123456","234567",KEY,"SYNTHETIC_CORP"):
                    self.assertNotIn(secret,txt)
    def test_source_concept_mismatch_must_not_be_rescued(self):
        session=Session(concept_change=True)
        with patch.dict(os.environ,{"OPENDART_API_KEY":KEY},clear=True):
            out=run(FROZEN_SLOTS[0],session)
        self.assertEqual(out["source_status"],
                         "ONE_NEW_ISSUER_ORIGINAL_Q3_NUMERIC_REPRESENTATION_SHAPE_ONLY")
        self.assertFalse(out["minimal_original_pair_numeric_representation_consistent"])
        self.assertFalse(out["same_exact_taxonomy_qname"])
        self.assertFalse(out["m20_signal_pit_admitted"])
    def test_invalid_slot_not_first_issuer_or_new_unapproved(self):
        for slot in (-1,2,6,"0",None):
            with self.subTest(slot=slot):
                spy=Session()
                with patch.dict(os.environ,{"OPENDART_API_KEY":KEY},clear=True):
                    out=run(slot,spy)
                self.assertEqual(out["source_status"],"FAIL_CLOSED_SCOPE_INVALID")
                self.assertEqual(spy.calls,[])
                self.assertFalse(out["real_orders_authorized"])
    def test_missing_current_corp_code_is_not_backfilled(self):
        spy=Session(missing_code=COHORT[0])
        with patch.dict(os.environ,{"OPENDART_API_KEY":KEY},clear=True):
            out=run(FROZEN_SLOTS[0],spy)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_reason_code"],"EXISTING_REGISTRY_ISSUER_NOT_FOUND")
        self.assertEqual(spy.calls,["corpCode.xml"])
    def test_official_archive_corruption_is_fail_closed(self):
        spy=Session(bad_zip=True)
        with patch.dict(os.environ,{"OPENDART_API_KEY":KEY},clear=True):
            out=run(FROZEN_SLOTS[0],spy)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertFalse(out["m20_signal_pit_admitted"])
        self.assertEqual(spy.calls,["corpCode.xml","list.json",
                                    "fnlttXbrl.xml","fnlttXbrl.xml"])
    def test_malformed_scope_cannot_execute_market_or_order_routes(self):
        bad=Session()
        with self.assertRaises(Exception):
            check_original_pair_slot(2,bad,KEY)
        self.assertEqual(bad.calls,[])
        with self.assertRaises(Exception):
            check_original_pair_slot(0,bad,"")
        self.assertEqual(bad.calls,[])


if __name__=="__main__":
    unittest.main()
