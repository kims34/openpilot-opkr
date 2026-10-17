"""Offline fail-closed evidence tests; never need credentials."""
import hashlib
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_source_proof as target
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT

FIRST = {
    "rcept_no": "20221114000001",
    "rcept_dt": "20221114",
    "report_nm": "분기보고서 (2022.09)",
}
LATER = {
    "rcept_no": "20221116000002",
    "rcept_dt": "20221116",
    "report_nm": "[기재정정]분기보고서 (2022.09)",
}
INDEX = {
    "status": "000",
    "total_count": "2",
    "total_page": "1",
    "page_no": "1",
    "list": [FIRST, LATER],
}
DIAG = {
    "official_original_document_zip_received": True,
    "zip_crc_and_bounded_read_completed": True,
    "structured_markup_entries_inspected": 1,
    "non_xml_sgml_html_layout_entries": 1,
    "safely_parsed_strict_xml_count": 0,
    "tables_with_exact_operating_row": 15,
    "tables_profit_2022_q3_window_in_first_twelve_rows": 0,
    "tables_profit_2021_q3_window_in_first_twelve_rows": 0,
    "original_q3_cfs_three_month_profit_bound": False,
    "original_document_financial_semantics_validated": False,
}


class SourceProofTests(unittest.TestCase):
    def test_correct_first_edition_and_later_window_versions(self):
        r = target._bounded_revision_shape(INDEX, FIRST["rcept_no"])
        self.assertTrue(r["original_receipt_date_confirmed_from_official_index"])
        self.assertEqual(r["same_period_later_version_rows_in_initial_window"], 1)
        self.assertTrue(r["full_later_correction_history_not_enumerated"])

    def test_official_correction_and_attachment_addition_are_separate(self):
        added = {
            "rcept_no": "20221117000003",
            "rcept_dt": "20221117",
            "report_nm": "[첨부추가]분기보고서 (2022.09)",
        }
        amended = {
            "rcept_no": "20221118000004",
            "rcept_dt": "20221118",
            "report_nm": "[첨부정정]분기보고서 (2022.09)",
        }
        listing = {**INDEX, "list": [FIRST, LATER, added, amended]}
        proof = target._bounded_revision_shape(listing, FIRST["rcept_no"])
        self.assertEqual(proof["same_period_later_version_rows_in_initial_window"], 3)
        self.assertEqual(proof["same_period_confirmed_corrections_in_initial_window"], 2)
        self.assertEqual(
            proof["same_period_attachment_additions_not_corrections_in_initial_window"], 1
        )
        self.assertTrue(proof["full_later_correction_history_not_enumerated"])

    def test_nonstandard_prefix_and_suffix_fail_closed_not_counted_as_correction(self):
        names = (
            "[기타]분기보고서 (2022.09)",
            "분기보고서 (2022.09) [정정]",
            "[기재정정]분기보고서 (2022.09) 추가문서",
        )
        for i, name in enumerate(names):
            with self.subTest(name=name):
                unclassified = dict(
                    LATER, rcept_no=f"2022111700000{i + 1}", rcept_dt="20221117",
                    report_nm=name,
                )
                with self.assertRaisesRegex(
                    target.SourceGap, "UNCLASSIFIED_SAME_PERIOD_FOLLOWUP"
                ):
                    target._bounded_revision_shape(
                        {**INDEX, "list": [FIRST, unclassified]}, FIRST["rcept_no"]
                    )

    def test_official_rm_correction_notice_is_not_full_lineage(self):
        original = dict(FIRST, rm="연정")
        result = target._bounded_revision_shape(
            {**INDEX, "list": [original]}, FIRST["rcept_no"]
        )
        self.assertTrue(result["original_index_indicates_possible_later_correction"])
        self.assertEqual(result["same_period_confirmed_corrections_in_initial_window"], 0)
        self.assertTrue(result["full_later_correction_history_not_enumerated"])

    def test_official_withdrawal_notice_fails_closed(self):
        original = dict(FIRST, rm="철")
        with self.assertRaisesRegex(target.SourceGap, "FIRST_FILING_WITHDRAWAL_MARKED"):
            target._bounded_revision_shape(
                {**INDEX, "list": [original]}, FIRST["rcept_no"]
            )

    def test_bad_original_edition_blocked(self):
        with self.assertRaises(target.SourceGap):
            target._bounded_revision_shape(INDEX, LATER["rcept_no"])

    def test_same_day_ambiguous_blocked(self):
        another = dict(LATER, rcept_dt=FIRST["rcept_dt"],
                       rcept_no="20221114000002")
        with self.assertRaises(target.SourceGap):
            target._bounded_revision_shape({**INDEX, "list": [FIRST, another]},
                                           FIRST["rcept_no"])

    def test_missing_key_no_network(self):
        with patch.dict(os.environ, {"OPENDART_API_KEY": ""}):
            proof = target.run(object())
        self.assertEqual(proof["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertNotIn("document_sha256", proof)

    def test_real_path_mocks_no_pit_or_identifiers_disclosed(self):
        binary = b"PK\\x03\\x04-test-only"
        def stub(session, endpoint, params, zip_response=False):
            self.assertIn(endpoint, ("corpCode.xml", "list.json"))
            if endpoint == "list.json":
                self.assertEqual(params["last_reprt_at"], "N")
            return b"registry" if endpoint == "corpCode.xml" else INDEX
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKEKEY"}),
            patch.object(target, "_official_get", side_effect=stub),
            patch.object(target, "_registry", return_value={COHORT[5]: "00000001"}),
            patch.object(target, "_fetch_first_document", return_value=binary),
            patch.object(target, "inspect_original_document_layout", return_value=DIAG),
            patch.object(target, "EXPECTED_ORIGINAL_DOCUMENT_SHA256", hashlib.sha256(binary).hexdigest()),
        ):
            proof = target.run(object())
        self.assertEqual(proof["source_status"],
                         "FIRST_FILED_2022_DOCUMENT_PROVENANCE_ONLY_NOT_PIT")
        self.assertEqual(proof["document_sha256"], hashlib.sha256(binary).hexdigest())
        self.assertEqual(proof["same_period_later_version_rows_in_initial_window"], 1)
        for flag in target.SAFE_FALSE:
            self.assertIs(proof[flag], False)
        serialized = str(proof)
        for sensitive in ("FAKEKEY", "00000001", FIRST["rcept_no"],
                          LATER["rcept_no"]):
            self.assertNotIn(sensitive, serialized)

    def test_sha256_drift_fails_closed_before_layout_or_pit(self):
        binary = b"untrusted-altered-or-repacked-first-document"
        calls = []

        def stub(session, endpoint, params, zip_response=False):
            calls.append(endpoint)
            return b"registry" if endpoint == "corpCode.xml" else INDEX

        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKEKEY"}),
            patch.object(target, "_official_get", side_effect=stub),
            patch.object(target, "_registry", return_value={COHORT[5]: "00000001"}),
            patch.object(target, "_fetch_first_document", return_value=binary),
            patch.object(target, "inspect_original_document_layout") as layout,
        ):
            proof = target.run(object())
        self.assertEqual(calls, ["corpCode.xml", "list.json"])
        layout.assert_not_called()
        self.assertEqual(proof["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(proof["failure_stage"], "ORIGINAL_DOCUMENT_ZIP")
        self.assertEqual(proof["failure_code"], "ORIGINAL_DOCUMENT_SHA256_DRIFT")
        self.assertNotIn("document_sha256", proof)
        self.assertFalse(proof["m20_feature_pit_admitted"])
        self.assertFalse(proof["m20_performance_run_authorized"])
        self.assertFalse(proof["real_orders_authorized"])
        self.assertNotIn("FAKEKEY", str(proof))

    def test_expected_original_digest_is_pinned_to_previous_official_evidence(self):
        self.assertEqual(
            target.EXPECTED_ORIGINAL_DOCUMENT_SHA256,
            "56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb",
        )

    def test_exception_never_leaks_provider_key_or_response(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKEKEY"}),
            patch.object(target, "_official_get", side_effect=ValueError("FAKEKEY private issuer data")),
        ):
            proof = target.run(object())
        self.assertEqual(proof["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(proof["failure_code"], "OFFICIAL_SOURCE_OR_LAYOUT_UNVERIFIED")
        self.assertNotIn("FAKEKEY", str(proof))


if __name__ == "__main__":
    unittest.main()
