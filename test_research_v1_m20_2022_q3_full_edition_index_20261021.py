"""Offline regression for one-pass fixed first-original and corrected index."""
import copy
import os
import unittest
from unittest.mock import patch

import research_v1_m20_2022_q3_full_edition_index_20261021 as p

ISSUER="00001234"
FIRST="20221114000001"
AMENDED="20240502000001"


def row(day, counter, title, *, issuer=ISSUER, marker=""):
    return {"rcept_no": day+f"{counter:06d}",
            "rcept_dt": day,"corp_code": issuer,
            "report_nm": title, "rm": marker}


def response(rows):
    return {"status":"000","total_count":str(len(rows)),
            "total_page":"1","page_no":"1","list":rows}


def originals():
    return response([row("20221114",1,"분기보고서 (2022.09)",marker="정")])


def later():
    rows=[row("20230302",i,"분기보고서 (2023.03)")
          for i in range(1,31)]
    rows.append(row("20240502",1,"[기재정정]분기보고서 (2022.09)"))
    return response(rows)


class FullContiguousEditionIndexTests(unittest.TestCase):
    def verified(self, first=None, after=None):
        return p.verify_source_indexes(
            originals() if first is None else first,
            later() if after is None else after,
            issuer=ISSUER,
        )

    def test_first_original_to_oct21_single_official_source_history_passes(self):
        result=self.verified()
        self.assertEqual(result["source_status"],
                         "FULL_CONTIGUOUS_OFFICIAL_INDEX_RANGE_VERIFIED_SOURCE_ONLY")
        self.assertEqual(result["later_periodic_index_rows"],31)
        self.assertEqual(result["later_verified_correction_rows"],1)
        self.assertEqual(result["later_verified_attachment_addition_rows"],0)
        self.assertEqual(result["observed_correction_index_coverage_end"],"20261021")
        self.assertTrue(result["initial_to_later_index_windows_adjacent"])
        self.assertFalse(result["original_to_corrected_data_semantics_bound"])
        self.assertNotIn(AMENDED,str(result))
        self.assertNotIn(FIRST,str(result))
        self.assertNotIn(ISSUER,str(result))

    def test_empty_or_013_later_index_is_not_a_complete_later_chain(self):
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CONTIGUOUS_OFFICIAL_INDEX_STATUS_UNVERIFIED"):
            self.verified(after={"status":"013"})

    def test_unverified_missing_or_extra_page_fails_closed(self):
        x=later()
        x["total_page"]="2"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CONTIGUOUS_INDEX_TRUNCATED_OR_MISSING"):
            self.verified(after=x)
        x=later()
        x["total_count"]="32"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CONTIGUOUS_INDEX_TRUNCATED_OR_MISSING"):
            self.verified(after=x)

    def test_census_row_baseline_drift_fails_even_unrelated_filing(self):
        x=later()
        x["list"].append(row("20260801",1,"사업보고서 (2025.12)"))
        x["total_count"]="32"
        with self.assertRaisesRegex(p.ContiguousGap,"LATER_INDEX_ROW_BASELINE_DRIFT"):
            self.verified(after=x)

    def test_cross_corporation_response_not_trusted(self):
        x=later()
        x["list"][4]["corp_code"]="12345678"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CONTIGUOUS_INDEX_ROW_OR_ISSUER_INVALID"):
            self.verified(after=x)

    def test_duplicate_receipt_in_later_window_rejected(self):
        x=later()
        x["list"][1]["rcept_no"]=x["list"][0]["rcept_no"]
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CONTIGUOUS_INDEX_ROW_OR_ISSUER_INVALID"):
            self.verified(after=x)

    def test_known_correction_must_stay_inside_prev_proven_scope(self):
        x=later()
        x["list"][-1]["rcept_dt"]="20261019"
        x["list"][-1]["rcept_no"]="20261019000001"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CORRECTION_OUTSIDE_PREVIOUSLY_PINNED_INDEX"):
            self.verified(after=x)

    def test_more_than_one_correction_invalid(self):
        x=later()
        x["list"][3]["report_nm"]="[첨부정정]분기보고서 (2022.09)"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "UNEXPECTED_CORRECTION_OR_ATTACHMENTS"):
            self.verified(after=x)

    def test_unknown_target_edition_label_cannot_be_ignored(self):
        x=later()
        x["list"][3]["report_nm"]="[차이발생]분기보고서 (2022.09)"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "UNRECOGNIZED_LATER_2022_Q3_EDITION"):
            self.verified(after=x)

    def test_attachment_addition_not_misread_as_no_correction(self):
        x=later()
        x["list"][3]["report_nm"]="[첨부추가]분기보고서 (2022.09)"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "UNEXPECTED_CORRECTION_OR_ATTACHMENTS"):
            self.verified(after=x)

    def test_original_without_correction_marker_is_not_cross_attested(self):
        x=originals()
        x["list"][0]["rm"]=""
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "FIRST_SUBMISSION_CORRECTION_HINT_DRIFT"):
            self.verified(first=x)

    def test_original_withdrawal_marker_never_accepted(self):
        x=originals()
        x["list"][0]["rm"]="철정"
        with self.assertRaises(Exception):
            self.verified(first=x)

    def test_filing_date_outside_window_rejected(self):
        x=later()
        x["list"][0]["rcept_dt"]="20230228"
        x["list"][0]["rcept_no"]="20230228000001"
        with self.assertRaisesRegex(p.ContiguousGap,
                                    "CONTIGUOUS_INDEX_DAY_OUTSIDE_WINDOW"):
            self.verified(after=x)

    def test_provider_invocation_exact_three_official_gets_read_only(self):
        calls=[]
        def fake(session,endpoint,params,zip_response=False):
            calls.append((endpoint,params.copy(),zip_response))
            if endpoint=="corpCode.xml":return b"fake-registry"
            if endpoint=="list.json":
                return originals() if params["bgn_de"]=="20221001" else later()
            raise AssertionError("unexpected endpoint")
        with patch.object(p,"_official_get",side_effect=fake), \
             patch.object(p,"_registry",return_value={p.COHORT[p.SLOT]:ISSUER}):
            result=p.execute(object(),"DONT_LOG")
        self.assertEqual(len(calls),3)
        self.assertEqual([x[0] for x in calls],["corpCode.xml","list.json","list.json"])
        self.assertEqual(calls[-1][1]["end_de"],"20261021")
        self.assertEqual(result["later_verified_correction_rows"],1)
        self.assertNotIn("DONT_LOG",str(result))

    def test_auth_missing_never_touches_network(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), \
             patch.object(p,"_official_get") as transport:
            x=p.run(object())
        transport.assert_not_called()
        self.assertEqual(x["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(x["ordering"],"DISABLED")
        self.assertFalse(x["m20_feature_pit_admitted"])

    def test_errors_redacted_and_all_orders_and_performance_denied(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"SECRET"}), \
             patch.object(p,"_official_get",
                          side_effect=ValueError("SECRET company123 99,999")):
            x=p.run(object())
        self.assertEqual(x["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for fragment in ("SECRET","99,999","company123"):
            self.assertNotIn(fragment,str(x))
        self.assertFalse(x["real_orders_authorized"])
        self.assertFalse(x["m20_performance_run_authorized"])
        self.assertFalse(x["original_2022_q3_cfs_standalone_operating_profit_verified"])
        self.assertEqual(x["ordering"],"DISABLED")


if __name__=="__main__":
    unittest.main()
