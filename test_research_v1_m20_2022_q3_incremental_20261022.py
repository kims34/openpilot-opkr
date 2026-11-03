"""Synthetic no-network Oct22 OpenDART full-day issuance census tests."""
import os
import unittest
from datetime import date
from unittest.mock import patch

import research_v1_m20_2022_q3_incremental_20261022 as p

CORP = "00001234"


def record(title="사업보고서 (2025.12)", day="20261022", serial="000001",
           company=CORP):
    return {"rcept_no": day + serial, "rcept_dt": day,
            "corp_code": company, "report_nm": title}


def listing(rows):
    return {"status":"000","total_count":str(len(rows)), "total_page":"1",
            "page_no":"1", "list":rows}


class OneDaySourceTests(unittest.TestCase):
    def test_contiguous_coverage_and_elapsed_kst_day(self):
        p.scope()
        self.assertEqual(p.VERIFIED_PRIOR_END, "20261021")
        self.assertEqual(p.START, "20261022")
        self.assertEqual(p.END, "20261022")

    def test_valid_status_013_has_no_rows(self):
        x = p.inspect({"status":"013"}, expected_company=CORP)
        self.assertEqual(x["source_status"],"OFFICIAL_INDEX_013_NO_PERIODIC_ROWS_OCT22")
        self.assertEqual(x["scoped_periodic_rows_checked"],0)
        self.assertEqual(x["new_q3_2022_correction_rows"],0)
        self.assertFalse(x["target_report_new_vintage_found_quarantine"])

    def test_013_with_hidden_financial_records_fails_closed(self):
        with self.assertRaisesRegex(p.Oct22SourceGap,
                                    "NO_RESULTS_STATUS_CONTAINS_ROWS"):
            p.inspect({"status":"013","list":[record()]},expected_company=CORP)

    def test_000_unrelated_periodic_filing_does_not_imply_amendment(self):
        x = p.inspect(listing([record()]),expected_company=CORP)
        self.assertEqual(x["source_status"],"OFFICIAL_INDEX_000_NO_TARGET_Q3_EDITION_OCT22")
        self.assertEqual(x["scoped_periodic_rows_checked"],1)
        self.assertEqual(x["new_q3_2022_correction_rows"],0)

    def test_known_correction_in_new_window_forces_quarantine(self):
        x = p.inspect(listing([record("[기재정정]분기보고서 (2022.09)")]),
                      expected_company=CORP)
        self.assertEqual(x["source_status"],"NEW_FIRST_SOURCE_VINTAGE_QUARANTINED")
        self.assertEqual(x["new_q3_2022_correction_rows"],1)
        self.assertTrue(x["target_report_new_vintage_found_quarantine"])

    def test_new_attachment_addition_forces_quarantine(self):
        x = p.inspect(listing([record("[첨부추가]분기보고서 (2022.09)")]),
                      expected_company=CORP)
        self.assertTrue(x["target_report_new_vintage_found_quarantine"])
        self.assertEqual(x["new_q3_2022_attachment_rows"],1)

    def test_new_unclassified_revision_never_ignored(self):
        with self.assertRaisesRegex(p.Oct22SourceGap,
                                    "NEW_TARGET_REPORT_EDITION_UNCLASSIFIED"):
            p.inspect(listing([record("[예기치않은정정]분기보고서 (2022.09)")]),
                      expected_company=CORP)

    def test_truncated_pages_never_accepted(self):
        bad=listing([record()])
        bad["total_page"]="2"
        with self.assertRaisesRegex(p.Oct22SourceGap,"OFFICIAL_PAGE_NOT_EXHAUSTIVE"):
            p.inspect(bad,expected_company=CORP)

    def test_duplicate_receipts_never_accepted(self):
        with self.assertRaisesRegex(p.Oct22SourceGap,"OFFICIAL_ROW_ISSUER_OR_RECEIPT_INVALID"):
            p.inspect(listing([record(),record()]),expected_company=CORP)

    def test_wrong_issuer_never_accepted(self):
        with self.assertRaisesRegex(p.Oct22SourceGap,"OFFICIAL_ROW_ISSUER_OR_RECEIPT_INVALID"):
            p.inspect(listing([record(company="12345678")]),expected_company=CORP)

    def test_not_the_elapsed_day_even_if_valid_day_rejected(self):
        with self.assertRaisesRegex(p.Oct22SourceGap,"OFFICIAL_ROW_OUTSIDE_OCT22_WINDOW"):
            p.inspect(listing([record(day="20261021")]),expected_company=CORP)

    def test_disclosure_number_day_must_match_receipt_day(self):
        r=record()
        r["rcept_no"]="20261021000001"
        with self.assertRaisesRegex(p.Oct22SourceGap,"OFFICIAL_ROW_OUTSIDE_OCT22_WINDOW"):
            p.inspect(listing([r]),expected_company=CORP)

    def test_official_provider_status_014_not_equivalent_to_zero_rows(self):
        with self.assertRaisesRegex(p.Oct22SourceGap,"OFFICIAL_INDEX_PROVIDER_STATUS_NOT_APPROVED"):
            p.inspect({"status":"014"},expected_company=CORP)

    def test_2_and_only_2_authenticated_api_requests(self):
        seen=[]
        def official(session, endpoint, params, zip_response=False):
            seen.append((endpoint,params.copy(),zip_response))
            if endpoint=="corpCode.xml":
                return b"stub"
            if endpoint=="list.json":
                return {"status":"013"}
            raise AssertionError("unapproved route")
        with patch.object(p,"_official_get",side_effect=official), \
             patch.object(p,"_registry",return_value={p.COHORT[p.SLOT]:CORP}):
            x=p.execute(object(),"fake-credential")
        self.assertEqual(len(seen),2)
        self.assertEqual([entry[0] for entry in seen],["corpCode.xml","list.json"])
        self.assertEqual(seen[-1][1]["bgn_de"],"20261022")
        self.assertEqual(seen[-1][1]["end_de"],"20261022")
        self.assertEqual(seen[-1][1]["last_reprt_at"],"N")
        self.assertNotIn("fake-credential",str(x))

    def test_no_key_has_no_api_side_effects(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), \
             patch.object(p,"_official_get") as transport:
            x=p.run(object())
        transport.assert_not_called()
        self.assertEqual(x["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(x["m20_feature_pit_admitted"])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_secret_provider_failure_never_logged_and_no_trading(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"PRIVATE_KEY"}), \
             patch.object(p,"_official_get",side_effect=ValueError(
                "PRIVATE_KEY company 20261022 amount 1,234,567")):
            x=p.run(object())
        self.assertEqual(x["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn("PRIVATE_KEY",str(x))
        self.assertNotIn("1,234,567",str(x))
        self.assertFalse(x["real_orders_authorized"])
        self.assertFalse(x["m20_performance_run_authorized"])
        self.assertFalse(x["first_2022_cfs_three_month_operating_profit_verified"])


if __name__ == "__main__":
    unittest.main()
