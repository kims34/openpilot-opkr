"""Offline tests: candidate row differences are non-authoritative and secret-safe."""
from collections import Counter
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_correction_row_diff as target


class CandidateRowsTests(unittest.TestCase):
    def _scan(self, html):
        parser = target._CandidateRows()
        parser.feed(html)
        parser.close()
        return parser.finish()

    def test_nonprofit_rows_ignored_and_exact_labels_detected(self):
        orig = "<table><tr><td>매출액</td><td>100</td></tr><tr><td>영업이익</td><td>10</td><td>9</td></tr></table>"
        a, anum = self._scan(orig)
        self.assertEqual(sum(a.values()), 1)
        self.assertEqual(sum(anum.values()), 1)
        self.assertNotIn(("매출액", "100"), a)

    def test_whitespace_unicode_normalized_without_financial_fact_admission(self):
        a, _ = self._scan("<tr><td>영업 이익</td><td>1,000</td><td>900</td></tr>")
        self.assertEqual(sum(a.values()), 1)

    def test_row_comparison_reports_change_without_public_values(self):
        a = Counter({("영업이익", "10", "9"): 1})
        anum = Counter({("영업이익", ("10", "9")): 1})
        b = Counter({("영업이익", "11", "9"): 1})
        bnum = Counter({("영업이익", ("11", "9")): 1})
        with patch.object(target, "_diagnostic_rows", side_effect=[(a, anum), (b, bnum)]):
            result = target.compare(b"fake-original", b"fake-amended")
        self.assertTrue(result["exact_label_row_text_multisets_differ"])
        self.assertTrue(result["numeric_peer_shape_multisets_differ"])
        self.assertEqual(result["identical_exact_label_row_candidates_multiset"], 0)
        self.assertTrue(result["financial_semantic_differences_still_unverified"])
        self.assertNotIn("11", str(result))
        self.assertNotIn("10", str(result))

    def test_identical_candidates_do_not_override_different_document_hashes(self):
        a = Counter({("영업이익", "10", "9"): 1})
        n = Counter({("영업이익", ("10", "9")): 1})
        with patch.object(target, "_diagnostic_rows", side_effect=[(a, n), (a, n)]):
            result = target.compare(b"original", b"amended")
        self.assertFalse(result["exact_label_row_text_multisets_differ"])
        self.assertFalse(result["numeric_peer_shape_multisets_differ"])
        self.assertTrue(result["financial_semantic_differences_still_unverified"])

    def test_layout_budget_hard_stop(self):
        with patch.object(target, "MAX_CELLS_PER_ROW", 1):
            scanner = target._CandidateRows()
            with self.assertRaises(target.RowShapeGap):
                scanner.feed("<tr><td>영업이익</td><td>10</td></tr>")

    def test_real_zip_digest_check_runs_before_any_markups(self):
        with patch.object(target, "inspect_official_original_document") as validator:
            with self.assertRaisesRegex(target.RowShapeGap, "DOCUMENT_SHA256_CHANGED"):
                target._diagnostic_rows(b"badzip", expected_digest="0" * 64)
        validator.assert_not_called()

    def test_secret_and_provider_error_not_exposed(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": "TESTSECRET"}),
            patch.object(target, "_official_get", side_effect=ValueError("TESTSECRET raw financial 987654")),
        ):
            result = target.run(object())
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "OFFICIAL_CANDIDATE_ROW_SOURCE_UNVERIFIED")
        self.assertNotIn("TESTSECRET", str(result))
        self.assertNotIn("987654", str(result))
        self.assertFalse(result["m20_feature_pit_admitted"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertFalse(result["real_orders_authorized"])

    def test_no_key_does_not_fetch(self):
        with (
            patch.dict(os.environ, {"OPENDART_API_KEY": ""}),
            patch.object(target, "_official_get") as network,
        ):
            result = target.run(object())
        network.assert_not_called()
        self.assertEqual(result["source_status"], "AUTH_NOT_CONFIGURED")


if __name__ == "__main__":
    unittest.main()
