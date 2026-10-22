"""Offline-only scoped official OpenDART incremental amendment index safety tests."""
import os
import unittest
from unittest.mock import patch

import research_v1_m20_2022_q3_incremental_correction_census as p

COMPANY="00000001"


def report(receipt="20261015000001",title="분기보고서 (2026.09)",corp=COMPANY):
    return {"corp_code":corp,"rcept_no":receipt,
            "rcept_dt":receipt[:8],"report_nm":title}


def with_rows(rows):
    return {"status":"000","total_page":1,"page_no":1,
            "total_count":len(rows),"list":rows}


class ScopedIncrementalCorrectionTests(unittest.TestCase):
    def test_previous_census_end_and_new_begin_exactly_contiguous(self):
        with patch.object(p,"PRIOR_CENSUS_END","20261012"):
            with self.assertRaisesRegex(p.IncrementalGap,
                                        "CONTIGUOUS_PREVIOUS_INDEX_SCOPE_DRIFT"):
                p._scope()
        p._scope()

    def test_official_013_no_records_only_for_exact_scoped_window(self):
        x=p.inspect_index({"status":"013","message":"no records"},expected_company=COMPANY)
        self.assertTrue(x["official_013_no_query_results"])
        self.assertTrue(x["incremental_window_has_no_matching_target_report"])
        self.assertFalse(x["new_target_edition_found_stop"])
        self.assertEqual(x["bounded_index_rows_examined"],0)
        self.assertEqual(x["new_2022_q3_correction_rows_in_window"],0)

    def test_013_with_hidden_records_or_bad_pagination_is_not_absence(self):
        bad=({"status":"013","list":[report()]},
             {"status":"013","total_count":"1"},
             {"status":"013","total_page":"1"})
        for item in bad:
            with self.subTest(item=item),self.assertRaisesRegex(
                p.IncrementalGap,"NO_DATA_STATUS_WITH_ROWS_OR_PAGINATION"
            ):
                p.inspect_index(item,expected_company=COMPANY)

    def test_valid_unrelated_000_periodic_reports_do_not_implicate_2022(self):
        x=p.inspect_index(with_rows([report(),report("20261020000001")]),
                          expected_company=COMPANY)
        self.assertEqual(x["bounded_index_rows_examined"],2)
        self.assertTrue(x["incremental_window_has_no_matching_target_report"])
        self.assertEqual(x["source_status"],
                         "OFFICIAL_INDEX_000_NO_TARGET_EDITION_IN_INCREMENTAL_WINDOW")

    def test_actual_target_amendment_title_is_quarantined_not_accepted(self):
        q=report("20261019000001","[기재정정]"+p.REPORT)
        x=p.inspect_index(with_rows([q]),expected_company=COMPANY)
        self.assertEqual(x["new_2022_q3_correction_rows_in_window"],1)
        self.assertTrue(x["new_target_edition_found_stop"])
        self.assertFalse(x["incremental_window_has_no_matching_target_report"])
        self.assertEqual(x["source_status"],"ADDITIONAL_TARGET_EDITION_FOUND_QUARANTINE")
        self.assertNotIn("20261019",str(x))
        self.assertNotIn(COMPANY,str(x))

    def test_attachment_addition_is_also_new_edition_and_quarantined(self):
        x=p.inspect_index(with_rows([report(
            "20261020000001","[첨부추가]"+p.REPORT)]),expected_company=COMPANY)
        self.assertEqual(x["new_2022_q3_attachment_rows_in_window"],1)
        self.assertTrue(x["new_target_edition_found_stop"])

    def test_unknown_target_report_edit_keeps_failure_closed(self):
        with self.assertRaisesRegex(p.IncrementalGap,
                                    "TARGET_2022_Q3_UNRECOGNIZED_EDITION"):
            p.inspect_index(with_rows([report("20261018000001",
                          "[불명정정]"+p.REPORT)]),expected_company=COMPANY)

    def test_malformed_provider_status_cannot_silently_imply_no_data(self):
        for status in ("014","020","010","900",None):
            with self.subTest(status=status),self.assertRaisesRegex(
                p.IncrementalGap,"OFFICIAL_INDEX_UNVERIFIED_PROVIDER_STATUS"
            ):
                p.inspect_index({"status":status},expected_company=COMPANY)

    def test_truncated_or_multipage_success_does_not_count_as_complete(self):
        examples=({"status":"000","total_page":2,"page_no":1,
                   "total_count":101,"list":[report()]},
                  {"status":"000","total_page":1,"page_no":1,
                   "total_count":2,"list":[report()]})
        for data in examples:
            with self.subTest(data=data["total_count"]),self.assertRaisesRegex(
                p.IncrementalGap,"OFFICIAL_INDEX_PAGINATION_INCOMPLETE"
            ):
                p.inspect_index(data,expected_company=COMPANY)

    def test_outside_window_receipt_date_mismatch_and_company_not_accepted(self):
        for row in (report("20261013000001"),
                    report("20261022000001"),
                    report("20261015000001",corp="00000002"),
                    {"corp_code":COMPANY,"rcept_no":"20261015000001",
                     "rcept_dt":"20261016","report_nm":"분기보고서 (2026.09)"}):
            with self.subTest(row=row),self.assertRaises(p.IncrementalGap):
                p.inspect_index(with_rows([row]),expected_company=COMPANY)

    def test_duplicate_identifiers_are_fail_closed(self):
        same=report()
        with self.assertRaisesRegex(p.IncrementalGap,"OFFICIAL_ROW_IDENTITY_INVALID"):
            p.inspect_index(with_rows([same,same]),expected_company=COMPANY)

    def test_missing_or_non_string_company_mapping_is_rejected(self):
        with self.assertRaisesRegex(p.IncrementalGap,"COMPANY_MAPPING_SHAPE_INVALID"):
            p.inspect_index({"status":"013"},expected_company="wrong")

    def test_exactly_two_official_read_only_api_calls_when_authenticated(self):
        calls=[]
        def mocked(_sess,endpoint,args,zip_response=False):
            calls.append((endpoint,args,zip_response))
            if endpoint=="corpCode.xml":
                return b"fakezip"
            if endpoint=="list.json":
                return {"status":"013"}
            raise AssertionError("unexpected call")
        with (patch.dict(os.environ,{"OPENDART_API_KEY":"SECRET_TEST"}),
              patch.object(p,"_registry",return_value={p.COHORT[p.SLOT]:COMPANY}),
              patch.object(p,"_official_get",side_effect=mocked)):
            x=p.run(object())
        self.assertEqual([c[0] for c in calls],["corpCode.xml","list.json"])
        self.assertEqual(calls[1][1]["bgn_de"],"20261014")
        self.assertEqual(calls[1][1]["end_de"],"20261021")
        self.assertEqual(calls[1][1]["last_reprt_at"],"N")
        self.assertEqual(calls[1][1]["pblntf_ty"],"A")
        self.assertFalse(calls[1][2])
        self.assertEqual(x["source_status"],
                         "OFFICIAL_INDEX_013_NO_ROWS_IN_INCREMENTAL_WINDOW")
        self.assertFalse(x["m20_feature_pit_admitted"])
        self.assertFalse(x["real_orders_authorized"])
        self.assertEqual(x["ordering"],"DISABLED")
        self.assertNotIn("SECRET_TEST",str(x))
        self.assertNotIn(COMPANY,str(x))

    def test_no_secret_means_no_network_and_not_found_does_not_admit_pit(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":""}),
              patch.object(p,"_official_get") as fetch):
            x=p.run(object())
        fetch.assert_not_called()
        self.assertEqual(x["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(x["original_to_amended_profit_cell_binding_verified"])

    def test_untrusted_secret_or_provider_error_never_emitted(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":"TOP_SECRET"}),
              patch.object(p,"_official_get",side_effect=ValueError(
                  "TOP_SECRET receipt 20261015000001 account 99,999"))):
            x=p.run(object())
        self.assertEqual(x["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for private in ("TOP_SECRET","20261015000001","99,999"):
            self.assertNotIn(private,str(x))
        for k,v in p.STATIC.items():
            if isinstance(v,bool):
                self.assertFalse(x[k])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_fixed_window_ends_before_current_full_korea_local_day(self):
        with patch.object(p,"END","20261022"):
            with self.assertRaisesRegex(p.IncrementalGap,"BOUNDED_CENSUS_WINDOW_DRIFT"):
                p._scope()


if __name__=="__main__":
    unittest.main()
