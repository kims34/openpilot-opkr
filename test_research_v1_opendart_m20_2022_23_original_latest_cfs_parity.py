"""Synthetic original 2022/2023 vs 2023 CFS 3-month API comparisons."""
from __future__ import annotations
import json
import os
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_2022_23_original_latest_cfs_parity import (
    latest_q3_2023_cfs_pair,inspect_original_vs_latest,run,OriginalComparativeGap,
)
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT
from test_research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import (
    SyntheticOfficialSession,SYNTHETIC_KEY,R22,R23,
)
from test_research_v1_opendart_m20_q3_original_numeric_compat import filing
from test_research_v1_opendart_original_xbrl_pilot import FakeResponse

CORP="00000001"


def latest(*,current="345678",prior="-123456",receipt=R23,
           current_ytd="999999",prior_ytd="888888",rows=None,
           account_id="dart_OperatingIncomeLoss"):
    row={
        "corp_code":CORP,"bsns_year":"2023","reprt_code":"11014",
        "sj_div":"IS","account_id":account_id,
        "account_nm":"영업이익","currency":"KRW",
        "rcept_no":receipt,"thstrm_amount":current,
        "frmtrm_q_amount":prior,"thstrm_add_amount":current_ytd,
        "frmtrm_add_amount":prior_ytd,
    }
    return {"status":"000","list":[row] if rows is None else rows}


class ExtendedSession(SyntheticOfficialSession):
    def __init__(self,api=None,**kwargs):
        super().__init__(**kwargs)
        self.api=latest() if api is None else api
    def get(self,url,*,params,timeout,allow_redirects,stream=False):
        if url.endswith("fnlttSinglAcntAll.json"):
            assert timeout==20 and not stream and not allow_redirects
            assert set(params)=={
                "crtfc_key","corp_code","bsns_year","reprt_code","fs_div",
            }
            assert params["crtfc_key"]==SYNTHETIC_KEY
            assert params["corp_code"] in {
                f"{i+1:08d}" for i in range(6)
            }
            assert params["bsns_year"]=="2023"
            assert params["reprt_code"]=="11014"
            assert params["fs_div"]=="CFS"
            self.calls.append("fnlttSinglAcntAll.json")
            return FakeResponse(parsed=self.api)
        return super().get(
            url,params=params,timeout=timeout,
            allow_redirects=allow_redirects,stream=stream)


class HistoricalCFSReconciliationTests(unittest.TestCase):
    def test_2023_original_and_2022_original_match_3month_fields_only(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),
            filing(2023,amount="345678"),latest(),
            corp_code=CORP,receipt23=R23)
        self.assertTrue(out["api_2023_3month_equals_2023_first_original"])
        self.assertTrue(out["api_2022_comparative_3month_equals_2022_first_original"])
        self.assertTrue(out["origins_versus_current_2023_CFS_both_values_match"])
        self.assertTrue(out["initial_qnames_same"])
        self.assertFalse(out["historic_xbrl_qname_compatibility_admitted"])
        for value in ("-123456","345678",CORP,R22,R23):
            self.assertNotIn(value,json.dumps(out))
    def test_disagreeing_original_names_can_agree_in_amounts_but_are_not_pit(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),
            filing(2023,amount="345678",
                   concept="ifrs-full:ProfitLossFromOperatingActivities"),
            latest(),corp_code=CORP,receipt23=R23)
        self.assertFalse(out["initial_qnames_same"])
        self.assertFalse(out["initial_local_concept_name_same"])
        self.assertFalse(out["initial_source_namespace_same"])
        self.assertTrue(out["origins_versus_current_2023_CFS_both_values_match"])
        self.assertFalse(out["historic_xbrl_qname_compatibility_admitted"])
    def test_taxonomy_namespace_only_change_detected_separately(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),
            filing(2023,amount="345678",
                   concept="ifrs-full:OperatingIncomeLoss"),
            latest(),corp_code=CORP,receipt23=R23)
        self.assertFalse(out["initial_qnames_same"])
        self.assertTrue(out["initial_local_concept_name_same"])
        self.assertFalse(out["initial_source_namespace_same"])
        self.assertFalse(out["historic_xbrl_qname_compatibility_admitted"])
    def test_current_2023_3month_restatement_flag_not_auto_filled(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),filing(2023,amount="345678"),
            latest(current="345679"),corp_code=CORP,receipt23=R23)
        self.assertFalse(out["api_2023_3month_equals_2023_first_original"])
        self.assertFalse(out["origins_versus_current_2023_CFS_both_values_match"])
    def test_previous_year_comparative_differs_from_original(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),filing(2023,amount="345678"),
            latest(prior="-123457"),corp_code=CORP,receipt23=R23)
        self.assertFalse(out["api_2022_comparative_3month_equals_2022_first_original"])
        self.assertFalse(out["origins_versus_current_2023_CFS_both_values_match"])
    def test_explicitly_ignore_ytd_cumulative_values(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),filing(2023,amount="345678"),
            latest(current_ytd="10000000",prior_ytd="-20000000"),
            corp_code=CORP,receipt23=R23)
        self.assertTrue(out["origins_versus_current_2023_CFS_both_values_match"])
    def test_current_api_receipt_differs_after_correction(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),filing(2023,amount="345678"),
            latest(receipt="20231201000001"),corp_code=CORP,receipt23=R23)
        self.assertFalse(out["api_2023_receipt_is_first_submitted"])
        self.assertFalse(out["origins_versus_current_2023_CFS_both_values_match"])
    def test_cfs_account_cardinality_fail_closed(self):
        duplicate=latest()["list"][0]
        for payload in (
            latest(rows=[]),latest(rows=[duplicate,duplicate.copy()]),
            {"status":"013"}):
            with self.subTest(payload=payload.get("status")):
                with self.assertRaises(OriginalComparativeGap):
                    latest_q3_2023_cfs_pair(payload,corp_code=CORP,
                                           first_receipt=R23)
    def test_invalid_currency_account_name_or_wrong_unit(self):
        for key,value in (
            ("currency","USD"),("account_nm","상품매출"),
            ("rcept_no","bad"),("fs_div","OFS"),
            ("thstrm_amount",None),("frmtrm_q_amount",None),
        ):
            row=latest()["list"][0]
            row[key]=value
            with self.subTest(field=key),self.assertRaises(OriginalComparativeGap):
                latest_q3_2023_cfs_pair(latest(rows=[row]),
                                        corp_code=CORP,first_receipt=R23)
    def test_2023_cfs_api_legacy_account_name_allowed_not_source_admitted(self):
        out=inspect_original_vs_latest(
            filing(2022,amount="-123456"),filing(2023,amount="345678"),
            latest(account_id="ifrs-full_ProfitLossFromOperatingActivities"),
            corp_code=CORP,receipt23=R23)
        self.assertFalse(out["api_operating_account_uses_dart_namespace"])
        self.assertFalse(out["historic_xbrl_qname_compatibility_admitted"])
    def test_six_preselected_fixed_issuer_approved_calls(self):
        for slot in range(6):
            with self.subTest(slot=slot):
                s=ExtendedSession()
                # Synthetic DART registry associates slot with id slot+1.
                s.api["list"][0]["corp_code"]=f"{slot+1:08d}"
                with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
                    out=run(slot,s)
                self.assertEqual(out["source_status"],
                    "ORIGINAL_2022_2023_TO_CFS_3MONTH_PARITY_DIAGNOSTIC_ONLY")
                self.assertEqual(s.calls,[
                    "corpCode.xml","list.json","list.json",
                    "fnlttXbrl.xml","fnlttXbrl.xml","fnlttSinglAcntAll.json"])
                self.assertTrue(out["origins_versus_current_2023_CFS_both_values_match"])
                for k in ("historical_xbrl_qname_equivalence_verified",
                          "initial_xbrl_statement_table_binding_verified",
                          "historical_security_corp_mapping_verified",
                          "historical_intraday_publication_pit_verified",
                          "historical_correction_lineage_complete",
                          "market_status_and_true_cost_return_path_verified",
                          "full_universe_history_verified",
                          "m20_feature_pit_admitted","m20_performance_run_authorized",
                          "independent_holdout_authorized","champion_change_authorized",
                          "real_orders_authorized","funds_movement_authorized",
                          "permissions_change_authorized",
                          "data_values_issuer_ids_and_source_rows_saved"):
                    self.assertIs(out[k],False,k)
                self.assertEqual(out["ordering"],"DISABLED")
                pack=json.dumps(out)
                for token in (SYNTHETIC_KEY, "-123456","345678",R22,R23)+COHORT:
                    self.assertNotIn(token,pack)
    def test_no_secret_never_uses_api(self):
        session=ExtendedSession()
        with patch.dict(os.environ,{},clear=True):
            out=run(0,session)
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(session.calls,[])
        self.assertFalse(out["m20_performance_run_authorized"])
    def test_official_account_api_error_fail_closed_without_source_data(self):
        s=ExtendedSession(api={"status":"901","message":"SENSITIVE_API_KEY_12345"})
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            out=run(0,s)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_code"],"LATEST_CFS_API_NOT_AVAILABLE")
        self.assertEqual(out["failure_stage"],"EXACT_ORIGINAL_VS_LATEST_COMPARATIVE")
        self.assertNotIn("SENSITIVE_API_KEY_12345",json.dumps(out))
    def test_underlying_original_parser_gap_is_classified_without_pit(self):
        from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import HistoricalOriginalGap
        s=ExtendedSession()
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            with patch(
                "research_v1_opendart_m20_2022_23_original_latest_cfs_parity.original_quarter_fact",
                side_effect=HistoricalOriginalGap("EXACT_CONSOLIDATED_Q3_KRW_OPERATING_FACT_NOT_UNIQUE"),
            ):
                out=run(5,s)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_stage"],"ORIGINAL_2022_Q3_FACT_PARSE")
        self.assertEqual(out["failure_code"],"EXACT_CONSOLIDATED_Q3_KRW_OPERATING_FACT_NOT_UNIQUE")
        self.assertFalse(out["m20_performance_run_authorized"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
        self.assertFalse(out["two_initial_original_Q3_XBRL_financial_facts_found"])
        self.assertNotIn(SYNTHETIC_KEY,json.dumps(out))

    def test_xbrl_source_parser_gap_is_classified_and_not_admitted(self):
        from research_v1_opendart_original_xbrl_pilot import OriginalXbrlProbeError
        s=ExtendedSession()
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            with patch(
                "research_v1_opendart_m20_2022_23_original_latest_cfs_parity.original_quarter_fact",
                side_effect=OriginalXbrlProbeError("OFFICIAL_XBRL_ZIP_ABSENT"),
            ):
                out=run(5,s)
        self.assertEqual(out["failure_code"],"OFFICIAL_XBRL_ZIP_ABSENT")
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertFalse(out["historical_intraday_publication_pit_verified"])
        self.assertFalse(out["independent_holdout_authorized"])

    def test_2023_vintage_bad_zip_is_distinguished_with_no_fallback(self):
        from research_v1_opendart_original_xbrl_pilot import OriginalXbrlProbeError
        from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import (
            original_quarter_fact as real_original_quarter_fact,
        )
        session=ExtendedSession()
        def only_2023_fails(raw,year):
            if year==2023:
                raise OriginalXbrlProbeError("OFFICIAL_XBRL_ZIP_ABSENT")
            return real_original_quarter_fact(raw,year)
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            with patch(
                "research_v1_opendart_m20_2022_23_original_latest_cfs_parity.original_quarter_fact",
                side_effect=only_2023_fails,
            ):
                out=run(5,session)
        self.assertEqual(out["failure_stage"],"ORIGINAL_2023_Q3_FACT_PARSE")
        self.assertEqual(out["failure_code"],"OFFICIAL_XBRL_ZIP_ABSENT")
        self.assertEqual(session.calls,[
            "corpCode.xml","list.json","list.json",
            "fnlttXbrl.xml","fnlttXbrl.xml",
        ])
        self.assertFalse(out["two_initial_original_Q3_XBRL_financial_facts_found"])
        self.assertFalse(out["m20_feature_pit_admitted"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")

    def test_unknown_error_text_never_leaks_in_reason_code(self):
        s=ExtendedSession()
        private="SOURCE_SECRET_KEY_AND_RAW_PROVIDER_MESSAGE_778899"
        with patch.dict(os.environ,{"OPENDART_API_KEY":SYNTHETIC_KEY},clear=True):
            with patch(
                "research_v1_opendart_m20_2022_23_original_latest_cfs_parity.original_quarter_fact",
                side_effect=ValueError(private),
            ):
                out=run(5,s)
        self.assertEqual(out["failure_code"],"UNCLASSIFIED")
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn(private,json.dumps(out))
        self.assertFalse(out["funds_movement_authorized"])

    def test_bad_slot_never_network(self):
        for slot in (-1,6,"0",None):
            with self.subTest(slot=slot):
                s=ExtendedSession()
                out=run(slot,s)
                self.assertEqual(out["source_status"],"FAIL_CLOSED_FROZEN_SLOT_INVALID")
                self.assertEqual(s.calls,[])


if __name__=="__main__":
    unittest.main()
