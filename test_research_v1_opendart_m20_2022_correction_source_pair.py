"""Secret-free regression for original/corrected OpenDART source pairing."""
import hashlib
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_correction_source_pair as proof

FIRST = {"rcept_no": "20221114000001", "rcept_dt": "20221114",
         "report_nm": "분기보고서 (2022.09)", "rm": "정"}
CORRECTED = {"rcept_no": "20230401000001", "rcept_dt": "20230401",
             "report_nm": "[기재정정]분기보고서 (2022.09)"}
LATER = {"status": "000", "page_no": "1", "total_page": "1",
         "total_count": "1", "list": [CORRECTED]}
FIRST_INDEX = {"status": "000", "page_no": "1", "total_page": "1",
               "total_count": "1", "list": [FIRST]}


class SourcePairTests(unittest.TestCase):
    def test_exact_corrected_edition_selected_only_after_index_checks(self):
        receipt = proof._source_pair(FIRST_INDEX, LATER, FIRST["rcept_no"])
        self.assertEqual(receipt, CORRECTED["rcept_no"])

    def test_false_rm_hint_cannot_silently_admit_correction(self):
        first = dict(FIRST, rm="")
        with self.assertRaisesRegex(proof.CorrectionPairGap, "ORIGINAL_CORRECTION_MARKER_ABSENT"):
            proof._source_pair({**FIRST_INDEX, "list": [first]}, LATER, FIRST["rcept_no"])

    def test_ambiguous_edition_list_rejected(self):
        second = dict(CORRECTED, rcept_dt="20230501", rcept_no="20230501000001")
        later = {**LATER, "total_count": "2", "list": [CORRECTED, second]}
        with self.assertRaisesRegex(proof.CorrectionPairGap, "LATER_CORRECTION_CARDINALITY_CHANGED"):
            proof._source_pair(FIRST_INDEX, later, FIRST["rcept_no"])

    def test_archive_digest_original_drift_blocks_before_layout(self):
        data = b"corrupted-original-archive"
        with (
            patch.object(proof, "_fetch_first_document", return_value=data),
            patch.object(proof, "inspect_official_original_document") as inspection,
            patch.object(proof, "inspect_original_document_layout") as layout,
        ):
            with self.assertRaisesRegex(proof.CorrectionPairGap, "ORIGINAL_ARCHIVE_SHA_DRIFT"):
                proof._archive_fingerprint(object(), "FAKEKEY", FIRST["rcept_no"], original=True)
        inspection.assert_not_called()
        layout.assert_not_called()

    def test_corrected_archive_digest_is_only_evidence_not_financial_fact(self):
        blob = b"PK\\x03\\x04-fake-test-archive"
        verified = {"official_original_document_zip_received": True}
        layout = {
            "zip_crc_and_bounded_read_completed": True,
            "non_xml_sgml_html_layout_entries": 1,
            "safely_parsed_strict_xml_count": 0,
            "tables_with_exact_operating_row": 12,
            "tables_profit_2022_q3_window_in_first_twelve_rows": 0,
            "tables_profit_2021_q3_window_in_first_twelve_rows": 0,
        }
        with (
            patch.object(proof, "_fetch_first_document", return_value=blob),
            patch.object(proof, "inspect_official_original_document", return_value=verified),
            patch.object(proof, "inspect_original_document_layout", return_value=layout),
        ):
            result = proof._archive_fingerprint(object(), "FAKEKEY", CORRECTED["rcept_no"], original=False)
        self.assertEqual(result["digest"], hashlib.sha256(blob).hexdigest())
        self.assertFalse(result["cfs_three_month_financial_semantics_verified"])

    def test_approved_three_index_calls_before_ephemeral_document_reads(self):
        calls = []
        def official(session, endpoint, params, zip_response=False):
            calls.append(endpoint)
            if endpoint == "corpCode.xml":
                return b"registry"
            self.assertEqual(params["last_reprt_at"], "N")
            return FIRST_INDEX if params["bgn_de"] == "20221001" else LATER

        def archive(session, key, receipt, *, original):
            calls.append("original_zip" if original else "corrected_zip")
            if original:
                self.assertEqual(receipt, FIRST["rcept_no"])
            else:
                self.assertEqual(receipt, CORRECTED["rcept_no"])
            return {
                "digest": "a" * 64 if original else "b" * 64,
                "sgml_html_entries": 1,
                "strict_xml_entries": 0,
                "profit_row_candidate_tables_not_facts": 10,
                "q3_2022_profit_table_period_hint_not_fact": False,
                "q3_2021_profit_table_period_hint_not_fact": False,
            }

        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKEKEY"}),
            patch.object(proof, "_official_get", side_effect=official),
            patch.object(proof, "_registry", return_value={proof.COHORT[5]: "00000001"}),
            patch.object(proof, "original_first_receipt", return_value=FIRST["rcept_no"]),
            patch.object(proof, "_archive_fingerprint", side_effect=archive),
        ):
            result = proof.run(object())
        self.assertEqual(calls, ["corpCode.xml", "list.json", "list.json",
                                 "original_zip", "corrected_zip"])
        self.assertTrue(result["original_and_corrected_zip_bytes_differ"])
        self.assertEqual(result["verified_original_and_corrected_archives_count"], 2)
        self.assertTrue(result["source_pair_actual_financial_changes_unverified"])
        self.assertFalse(result["original_cfs_q3_2022_2021_three_month_profit_verified"])
        for x in ("m20_performance_run_authorized", "m20_feature_pit_admitted",
                  "independent_holdout_authorized", "real_orders_authorized"):
            self.assertFalse(result[x])
        for secret in ("FAKEKEY", "00000001", CORRECTED["rcept_no"]):
            self.assertNotIn(secret, str(result))

    def test_provider_errors_are_redacted(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "FAKEKEY"}),
            patch.object(proof, "_official_get", side_effect=ValueError("FAKEKEY secret receipt 20230401000001")),
        ):
            result = proof.run(object())
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "OFFICIAL_PAIR_SOURCE_OR_LAYOUT_UNVERIFIED")
        self.assertNotIn("FAKEKEY", str(result))
        self.assertNotIn(CORRECTED["rcept_no"], str(result))

    def test_missing_credential_does_not_call_external_sources(self):
        with patch.dict(os.environ, {"OPENDART_API_KEY": ""}):
            result = proof.run(object())
        self.assertEqual(result["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertFalse(result["m20_performance_run_authorized"])


if __name__ == "__main__":
    unittest.main()
