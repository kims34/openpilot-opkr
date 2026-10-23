"""No-credential, no-amount M20 normalized 2022 quarterly-source gate tests."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_normalized_quarter_source_gate as p

CORP = "00000001"
FIRST = "20221114000001"
AMENDED = "20230401000001"


def make_row(account="dart_OperatingIncomeLoss", receipt=AMENDED,
             current="10,000", prior="-9,000", **updates):
    return {
        "corp_code": CORP, "bsns_year": "2022", "reprt_code": "11014",
        "sj_div": "IS", "account_id": account, "account_nm": "영업이익",
        "currency": "KRW", "rcept_no": receipt,
        "thstrm_amount": current, "frmtrm_q_amount": prior,
        "thstrm_add_amount": "123456789012345",
        **updates,
    }


class NormalizedQuarterSchemaTests(unittest.TestCase):
    def test_one_2022_quarter_cfs_operating_row_reports_only_shapes(self):
        payload = {"status": "000", "list": [
            {"corp_code": CORP, "bsns_year": "2022", "reprt_code": "11014",
             "sj_div": "BS", "account_nm": "영업이익"},
            make_row(),
        ]}
        result = p.inspect_normalized(payload, CORP, FIRST, AMENDED)
        self.assertTrue(result["current_api_2022_q3_3month_amount_shape_present"])
        self.assertTrue(result["current_api_2021_q3_3month_comparative_shape_present"])
        self.assertEqual(result["recognized_unique_operating_account_id_count"], 1)
        self.assertEqual(result["current_api_reported_receipt_classification"],
                         "SAME_ID_AS_LATER_CORRECTION_NOT_VINTAGE_PROOF")
        self.assertFalse(result["current_api_has_as_of_original_version_parameter"])
        for raw in ("10,000", "-9,000", "123456789012345", CORP, AMENDED):
            self.assertNotIn(raw, str(result))

    def test_different_report_receipt_is_not_first_published_evidence(self):
        result = p.inspect_normalized({"status": "000", "list": [
            make_row(receipt=FIRST)
        ]}, CORP, FIRST, AMENDED)
        self.assertEqual(result["current_api_reported_receipt_classification"],
                         "SAME_ID_AS_FIRST_FILING_NOT_VINTAGE_PROOF")
        self.assertFalse(result["current_api_reported_receipt_is_first_published_version_verified"])

    def test_later_unknown_edition_is_not_vintage_proof(self):
        result = p.inspect_normalized({"status": "000", "list": [
            make_row(receipt="20250505000001")
        ]}, CORP, FIRST, AMENDED)
        self.assertEqual(result["current_api_reported_receipt_classification"],
                         "DIFFERENT_EDITION_NOT_VINTAGE_PROOF")

    def test_latest_api_cumulative_only_must_not_substitute(self):
        with self.assertRaisesRegex(
            p.NormalizedQuarterGap, "NORMALIZED_THREE_MONTH_AMOUNT_SHAPE_INVALID"
        ):
            p.inspect_normalized({"status": "000", "list": [
                make_row(prior="", current="")
            ]}, CORP, FIRST, AMENDED)

    def test_missing_numeric_q3_prior_comparator_fails_closed(self):
        for prior in (None, "", "not available", "1e12"):
            with self.subTest(prior=prior):
                with self.assertRaises(p.NormalizedQuarterGap):
                    p.inspect_normalized({"status": "000", "list": [
                        make_row(prior=prior)
                    ]}, CORP, FIRST, AMENDED)

    def test_competing_legacy_dart_accounts_cannot_be_silently_chosen(self):
        data = {"status": "000", "list": [
            make_row(account="dart_OperatingIncomeLoss"),
            make_row(account="ifrs-full_ProfitLossFromOperatingActivities"),
        ]}
        with self.assertRaisesRegex(p.NormalizedQuarterGap,
                                    "NORMALIZED_OPERATING_ACCOUNT_NOT_UNIQUE"):
            p.inspect_normalized(data, CORP, FIRST, AMENDED)

    def test_corp_or_report_code_mismatch_block(self):
        with self.assertRaisesRegex(p.NormalizedQuarterGap,
                                    "NORMALIZED_ROW_ISSUER_PERIOD_MISMATCH"):
            p.inspect_normalized({"status": "000", "list": [
                make_row(reprt_code="11013")
            ]}, CORP, FIRST, AMENDED)

    def test_unavailable_is_safe_gap_not_first_edition_proof(self):
        with self.assertRaisesRegex(p.NormalizedQuarterGap,
                                    "OFFICIAL_2022_NORMALIZED_FINANCIALS_ABSENT"):
            p.inspect_normalized({"status": "013"}, CORP, FIRST, AMENDED)

    def test_query_is_2022_q3_cfs_only_and_only_four_calls(self):
        seen = []
        orig = {"status": "000", "list": [{
            "rcept_no": FIRST, "rcept_dt": "20221114",
            "report_nm": "분기보고서 (2022.09)", "rm": "정",
        }]}
        amended = {"status": "000", "total_count": "1", "total_page": "1",
                   "page_no": "1", "list": [{
                       "rcept_no": AMENDED, "rcept_dt": "20230401",
                       "report_nm": "[기재정정]분기보고서 (2022.09)",
                   }]}
        def official(session, endpoint, params, zip_response=False):
            seen.append(endpoint)
            if endpoint == "corpCode.xml":
                self.assertTrue(zip_response)
                return b"stub"
            if endpoint == "list.json":
                return orig if params.get("bgn_de") == "20221001" else amended
            self.assertEqual(endpoint, "fnlttSinglAcntAll.json")
            self.assertEqual(params["bsns_year"], "2022")
            self.assertEqual(params["reprt_code"], "11014")
            self.assertEqual(params["fs_div"], "CFS")
            self.assertNotIn("rcept_no", params)
            return {"status": "000", "list": [make_row()]}
        with (
            patch.object(p, "_official_get", side_effect=official),
            patch.object(p, "_registry", return_value={p.COHORT[5]: CORP}),
            patch.object(p, "original_first_receipt", return_value=FIRST),
            patch.object(p, "_source_pair", return_value=AMENDED),
            patch.dict(os.environ, {"OPENDART_API_KEY": "SECRET_TEST_KEY"}),
        ):
            result = p.run(object())
        self.assertEqual(seen, ["corpCode.xml", "list.json", "list.json",
                               "fnlttSinglAcntAll.json"])
        self.assertEqual(result["max_official_requests"], 4)
        self.assertEqual(result["source_status"],
                         "CURRENT_API_NORMALIZED_CFS_2022_Q3_AMOUNT_SHAPE_ONLY_NOT_PIT")
        for name in ("api_financial_cells_original_pit_admitted",
                     "m20_feature_pit_admitted", "m20_performance_run_authorized",
                     "independent_holdout_authorized", "real_orders_authorized"):
            self.assertFalse(result[name])
        self.assertEqual(result["ordering"], "DISABLED")
        self.assertNotIn("SECRET_TEST_KEY", str(result))

    def test_api_exception_cannot_leak_secrets_or_financial_amounts(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "SECRET_TEST_KEY"}),
            patch.object(p, "_official_get",
                         side_effect=ValueError("SECRET_TEST_KEY 123,456 20230401000001")),
        ):
            result = p.run(object())
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["source_gap_reason"], "OFFICIAL_NORMALIZED_SOURCE_UNVERIFIED")
        self.assertNotIn("SECRET_TEST_KEY", str(result))
        self.assertNotIn("123,456", str(result))
        self.assertNotIn(AMENDED, str(result))

    def test_missing_key_makes_no_request(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": ""}),
            patch.object(p, "_official_get") as transport,
        ):
            result = p.run(object())
        transport.assert_not_called()
        self.assertFalse(result["m20_performance_run_authorized"])


if __name__ == "__main__":
    unittest.main()
