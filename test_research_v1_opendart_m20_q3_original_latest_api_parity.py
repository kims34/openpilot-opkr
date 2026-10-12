"""Offline tests: current consolidated Q3 API vs original 2024/2025 XBRL."""
import json
import os
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_q3_original_latest_api_parity import (
    latest_consolidated_q3_operating_line, check_original_latest_parity,
    OriginalAPIParityError, run,
)
from test_research_v1_opendart_m20_q3_original_numeric_compat import filing
from test_research_v1_opendart_original_xbrl_pilot import (
    FakeSession, FakeResponse, R24, R25, CORP,
)


def latest(*, current="234", previous="123", receipt=R25,
           rows=None, current_ytd="9999", previous_ytd="8888"):
    item={
        "corp_code":CORP,"bsns_year":"2025","reprt_code":"11014",
        "sj_div":"IS", "account_id":"dart_OperatingIncomeLoss",
        "account_nm":"영업이익", "currency":"KRW",
        "rcept_no":receipt,
        "thstrm_amount":current, "frmtrm_q_amount":previous,
        "thstrm_add_amount":current_ytd,
        "frmtrm_add_amount":previous_ytd,
    }
    return {"status":"000","list":[item] if rows is None else rows}


class Session(FakeSession):
    def __init__(self, payload=None):
        super().__init__(
            response24=FakeResponse(filing(2024,amount="123")),
            response25=FakeResponse(filing(2025,amount="234")))
        self.latest = latest() if payload is None else payload
    def get(self,url,*,params,timeout,allow_redirects,stream=False):
        if url.endswith("fnlttSinglAcntAll.json"):
            assert timeout==20
            assert stream is False
            assert allow_redirects is False
            assert params=={
                "crtfc_key":"synthetic-only-key","corp_code":CORP,
                "bsns_year":"2025","reprt_code":"11014","fs_div":"CFS"}
            self.calls.append("fnlttSinglAcntAll.json")
            return FakeResponse(parsed=self.latest)
        return super().get(
            url,params=params,timeout=timeout,
            allow_redirects=allow_redirects,stream=stream)


class OpenDARTOriginalLatestParityTest(unittest.TestCase):
    def test_matching_original_quarters_and_later_api_conservative_only(self):
        out=check_original_latest_parity(
            original24=filing(2024,amount="123"),
            original25=filing(2025,amount="234"),
            latest_api=latest(),corp_code=CORP,first_2025_receipt=R25)
        self.assertTrue(out["original_and_latest_api_three_month_parity_observed"])
        self.assertTrue(out["latest_api_2025_three_month_matches_first_filing"])
        self.assertTrue(out["latest_api_2024_comparative_three_month_matches_first_filing"])
        self.assertEqual(out["latest_api_2025_q3_cfs_line_count"],1)
        self.assertFalse(out["historical_restatement_completeness_verified"])
        self.assertFalse(out["historical_publication_pit_verified"])
        self.assertFalse(out["m20_performance_run_authorized"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
        for secret in ("123","234",CORP,R24,R25,"9999","8888"):
            self.assertNotIn(secret,json.dumps(out))

    def test_current_later_api_revision_is_flag_not_overwritten(self):
        out=check_original_latest_parity(
            original24=filing(2024,amount="123"),
            original25=filing(2025,amount="234"),
            latest_api=latest(current="235"),corp_code=CORP,first_2025_receipt=R25)
        self.assertFalse(out["latest_api_2025_three_month_matches_first_filing"])
        self.assertTrue(out["latest_api_2024_comparative_three_month_matches_first_filing"])
        self.assertFalse(out["original_and_latest_api_three_month_parity_observed"])
        self.assertFalse(out["m20_signal_pit_admitted"])

    def test_prior_year_comparative_revision_not_a_2024_original(self):
        out=check_original_latest_parity(
            original24=filing(2024,amount="123"),
            original25=filing(2025,amount="234"),
            latest_api=latest(previous="124"),corp_code=CORP,first_2025_receipt=R25)
        self.assertFalse(out["latest_api_2024_comparative_three_month_matches_first_filing"])
        self.assertFalse(out["original_and_latest_api_three_month_parity_observed"])

    def test_correct_quarter_fields_used_ytd_ignored(self):
        out=check_original_latest_parity(
            original24=filing(2024,amount="123"),
            original25=filing(2025,amount="234"),
            latest_api=latest(current_ytd="-99999999",previous_ytd="500000000"),
            corp_code=CORP,first_2025_receipt=R25)
        self.assertTrue(out["original_and_latest_api_three_month_parity_observed"])
        self.assertFalse(out["historical_restatement_completeness_verified"])

    def test_later_api_receipt_not_claimed_first_filing(self):
        out=check_original_latest_parity(
            original24=filing(2024,amount="123"),
            original25=filing(2025,amount="234"),
            latest_api=latest(receipt="20251201000001"),corp_code=CORP,
            first_2025_receipt=R25)
        self.assertFalse(out["latest_api_receipt_is_first_filed_2025_q3"])
        self.assertFalse(out["original_and_latest_api_three_month_parity_observed"])

    def test_missing_previous_three_months_cannot_use_prior_ytd(self):
        with self.assertRaisesRegex(OriginalAPIParityError,"SOURCE_CFS_QUARTER_AMOUNT_INVALID"):
            latest_consolidated_q3_operating_line(
                latest(previous=None),corp_code=CORP,original_receipt=R25)

    def test_missing_current_three_months_cannot_use_current_ytd(self):
        with self.assertRaisesRegex(OriginalAPIParityError,"SOURCE_CFS_QUARTER_AMOUNT_INVALID"):
            latest_consolidated_q3_operating_line(
                latest(current=None),corp_code=CORP,original_receipt=R25)

    def test_ambiguous_current_api_line_never_picked(self):
        obj=latest()["list"][0]
        with self.assertRaisesRegex(OriginalAPIParityError,"CURRENT_CFS_OPERATING_ACCOUNT_NOT_UNIQUE"):
            latest_consolidated_q3_operating_line(
                latest(rows=[obj,obj.copy()]),corp_code=CORP,original_receipt=R25)

    def test_wrong_current_api_account_currency_rejected(self):
        for k,v in (("currency","USD"),("account_nm","투자수익"),
                    ("rcept_no","BAD"),("account_id","ifrs-full_ProfitLossFromOperatingActivities")):
            row=latest()["list"][0]
            row[k]=v
            with self.subTest(k=k),self.assertRaises(OriginalAPIParityError):
                latest_consolidated_q3_operating_line(
                    latest(rows=[row]),corp_code=CORP,original_receipt=R25)

    def test_representations_must_match_no_silent_conversion(self):
        with self.assertRaises(OriginalAPIParityError):
            check_original_latest_parity(
                original24=filing(2024,amount="123",decimals="0"),
                original25=filing(2025,amount="234",decimals="-3"),
                latest_api=latest(),corp_code=CORP,first_2025_receipt=R25)

    def test_api_request_route_and_fixed_original_files_only(self):
        session=Session()
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            result=run(session)
        self.assertEqual(result["source_status"],
                         "THREE_MONTH_ORIGINAL_VS_LATEST_API_PARITY_DIAGNOSTIC_ONLY")
        self.assertTrue(result["original_and_latest_api_three_month_parity_observed"])
        self.assertEqual(result["original_q3_reports_examined"],2)
        self.assertEqual(session.calls,["corpCode.xml","list.json","fnlttXbrl.xml",
                                        "fnlttXbrl.xml","fnlttSinglAcntAll.json"])
        self.assertFalse(result["historical_publication_pit_verified"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertFalse(result["real_orders_authorized"])
        for value in ("synthetic-only-key",CORP,R24,R25,"123","234"):
            self.assertNotIn(value,json.dumps(result))

    def test_missing_key_causes_zero_api_calls(self):
        session=Session()
        with patch.dict(os.environ,{},clear=True):
            out=run(session)
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(session.calls,[])

    def test_bad_later_api_fails_closed_without_values(self):
        session=Session(payload={"status":"013","message":"bad key SECRET_NAME"})
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(session)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_reason_code"],"CURRENT_CFS_API_NOT_AVAILABLE")
        self.assertFalse(out["m20_signal_pit_admitted"])
        self.assertNotIn("SECRET_NAME",json.dumps(out))


if __name__=="__main__":
    unittest.main()
