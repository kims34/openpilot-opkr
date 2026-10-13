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
            return b"registry" if endpoint == "corpCode.xml" else INDEX
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKEKEY"}),
            patch.object(target, "_official_get", side_effect=stub),
            patch.object(target, "_registry", return_value={COHORT[5]: "00000001"}),
            patch.object(target, "_fetch_first_document", return_value=binary),
            patch.object(target, "inspect_original_document_layout", return_value=DIAG),
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
