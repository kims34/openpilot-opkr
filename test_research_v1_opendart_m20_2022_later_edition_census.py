"""Offline tests for bounded later-edition enumeration, without provider keys."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_later_edition_census as census

REGULAR = {
    "rcept_no": "20230302000001",
    "rcept_dt": "20230302",
    "report_nm": "사업보고서 (2022.12)",
}
CORRECTION = {
    "rcept_no": "20230303000001",
    "rcept_dt": "20230303",
    "report_nm": "[기재정정]분기보고서 (2022.09)",
}
ATTACHMENT = {
    "rcept_no": "20230304000001",
    "rcept_dt": "20230304",
    "report_nm": "[첨부추가]분기보고서 (2022.09)",
}


def page(rows, *, total=None, number=1, pages=1):
    return {
        "status": "000", "total_count": str(total if total is not None else len(rows)),
        "total_page": str(pages), "page_no": str(number),
        "list": rows,
    }


class LaterEditionCensusTests(unittest.TestCase):
    def test_distinguishes_later_corrections_and_attachments(self):
        result = census.assess_pages([page([REGULAR, CORRECTION, ATTACHMENT])])
        self.assertEqual(result["2022_q3_late_confirmed_corrections"], 1)
        self.assertEqual(result["2022_q3_late_attachment_additions"], 1)
        self.assertTrue(result["2022_q3_correction_flag_reconciled_to_late_index"])
        self.assertFalse(result["initial_and_later_edition_lineage_semantically_linked"])
        self.assertFalse(result["all_revisions_ever_identified"])

    def test_zero_late_2022_matches_does_not_override_original_rm_hint(self):
        result = census.assess_pages([page([REGULAR])])
        self.assertEqual(result["2022_q3_late_confirmed_corrections"], 0)
        self.assertFalse(result["2022_q3_correction_flag_reconciled_to_late_index"])
        self.assertTrue(result["initial_original_rm_correction_hint_from_prior_official_evidence"])

    def test_unknown_edition_title_fails_closed(self):
        unknown = dict(CORRECTION, report_nm="[기타]분기보고서 (2022.09)")
        with self.assertRaisesRegex(census.LaterEditionGap, "UNKNOWN_2022_Q3_EDITION_NAME"):
            census.assess_pages([page([unknown])])

    def test_duplicate_or_misdated_receipt_fails_closed(self):
        for rows in (
            [REGULAR, REGULAR],
            [dict(REGULAR, rcept_dt="20230303")],
            [dict(REGULAR, rcept_dt="20221231", rcept_no="20221231000001")],
        ):
            with self.subTest(rows=rows):
                with self.assertRaises(census.LaterEditionGap):
                    census.assess_pages([page(rows)])

    def test_missing_page_or_inconsistent_count_fails_closed(self):
        rows = [
            {
                "rcept_no": f"20230302{i:06d}",
                "rcept_dt": "20230302",
                "report_nm": "사업보고서 (2022.12)",
            }
            for i in range(100)
        ]
        first = page(rows, total=101, pages=2)
        second = page([CORRECTION], total=101, number=2, pages=2)
        self.assertEqual(
            census.assess_pages([first, second])["late_index_all_periodic_rows_validated"],
            101,
        )
        for attempted in ([first], [first, dict(second, total_count="102")],
                          [first, dict(second, page_no="1")]):
            with self.subTest(attempted=attempted[-1].get("page_no")):
                with self.assertRaises(census.LaterEditionGap):
                    census.assess_pages(attempted)

    def test_bounded_official_calls_and_secret_redaction(self):
        calls = []
        def official(session, endpoint, params, zip_response=False):
            calls.append((endpoint, params))
            if endpoint == "corpCode.xml":
                return b"mock-registry"
            self.assertEqual(params["last_reprt_at"], "N")
            self.assertEqual(params["bgn_de"], census.LATER_BEGIN)
            self.assertEqual(params["end_de"], census.AS_OF)
            self.assertEqual(params["page_no"], "1")
            return page([CORRECTION, ATTACHMENT])
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKE_SECRET_KEY"}),
            patch.object(census, "_official_get", side_effect=official),
            patch.object(census, "_registry", return_value={census.COHORT[5]: "00000001"}),
        ):
            result = census.run(object())
        self.assertEqual(result["source_status"], "POST_WINDOW_SOURCE_EDITION_COUNTS_ONLY_NOT_PIT")
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["2022_q3_late_confirmed_corrections"], 1)
        self.assertNotIn("FAKE_SECRET_KEY", str(result))
        self.assertNotIn("00000001", str(result))
        self.assertNotIn(CORRECTION["rcept_no"], str(result))
        self.assertEqual(result["ordering"], "DISABLED")
        for label in ("m20_feature_pit_admitted", "m20_performance_run_authorized",
                      "independent_holdout_authorized", "real_orders_authorized"):
            self.assertIs(result[label], False)

    def test_overflow_pages_does_not_trigger_extra_requests(self):
        def official(session, endpoint, params, zip_response=False):
            if endpoint == "corpCode.xml":
                return b"mock-registry"
            return {"status": "000", "total_page": str(census.MAX_PAGES + 1)}
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKE_SECRET_KEY"}),
            patch.object(census, "_official_get", side_effect=official),
            patch.object(census, "_registry", return_value={census.COHORT[5]: "00000001"}),
        ):
            result = census.run(object())
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "OFFICIAL_INDEX_EXCEEDS_APPROVED_BUDGET")

    def test_provider_exception_never_leaks_credentials(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKE_SECRET_KEY"}),
            patch.object(census, "_official_get", side_effect=ValueError("FAKE_SECRET_KEY provider body")),
        ):
            result = census.run(object())
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "OFFICIAL_PROVIDER_OR_REGISTRY_UNVERIFIED")
        self.assertNotIn("FAKE_SECRET_KEY", str(result))


if __name__ == "__main__":
    unittest.main()
