"""Read-only offline regression for exact 2022 Q3 source-table order census."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_source_table_order as p


def flags(**custom):
    return {
        "nested": False,
        "nearby_exact_cfs": False,
        "nearby_notes": False,
        "mentions_operating_income": False,
        **custom,
    }


class TableOrderTests(unittest.TestCase):
    def test_unique_insertion_is_attributed_only_as_source_position(self):
        orig = ["a", "b", "c"]
        corrected = ["a", "x", "b", "c"]
        x = p.assess_order(orig, corrected, [
            flags(), flags(nearby_notes=True), flags(), flags()
        ])
        self.assertTrue(x["original_order_preserved_as_subsequence"])
        self.assertEqual(x["minimum_insertions_if_subsequence"], 1)
        self.assertEqual(x["forced_new_table_positions"], 1)
        self.assertEqual(x["insertions_not_position_uniquely_attributable"], 0)
        self.assertEqual(x["forced_new_nearby_notes_hints"], 1)
        self.assertFalse(x["forced_new_table_is_authoritative_cfs_earnings"])

    def test_duplicate_table_can_be_inserted_at_multiple_positions(self):
        # The middle 'a' is never matched by either greedy extreme in
        # some cases, yet it CAN match the original. Do not claim it forced.
        a = p.assess_order(["a"], ["a", "a", "a"], [flags()]*3)
        self.assertEqual(a["minimum_insertions_if_subsequence"], 2)
        self.assertEqual(a["forced_new_table_positions"], 0)
        self.assertEqual(a["insertions_not_position_uniquely_attributable"], 2)

    def test_mixed_unique_and_duplicate_insertions(self):
        a = p.assess_order(["a", "b"], ["a", "a", "x", "b"], [
            flags(), flags(), flags(mentions_operating_income=True), flags()
        ])
        self.assertEqual(a["minimum_insertions_if_subsequence"], 2)
        self.assertEqual(a["forced_new_table_positions"], 1)
        self.assertEqual(a["insertions_not_position_uniquely_attributable"], 1)
        self.assertEqual(a["forced_new_operating_income_mentions"], 1)
        self.assertFalse(a["unclassified_insertions_remain_source_gap"] is False)

    def test_reordered_table_order_returns_blocked_lcs_evidence(self):
        result = p.assess_order(["a", "b", "c"], ["b", "c", "a", "x"], [flags()]*4)
        self.assertFalse(result["original_order_preserved_as_subsequence"])
        self.assertEqual(result["order_lcs_shared_table_members"], 2)
        self.assertEqual(result["minimum_table_removals_for_sequence_alignment"], 1)
        self.assertEqual(result["minimum_table_insertions_for_sequence_alignment"], 2)
        self.assertFalse(result["correction_financial_cell_changes_verified"])

    def test_lcs_duplicate_source_values(self):
        old = ["a", "b", "a"]
        new = ["a", "a", "b", "x", "a"]
        self.assertEqual(p._lcs_length_bounded(old, new), 3)
        self.assertTrue(p.assess_order(old, new, [flags()]*len(new))[
            "original_order_preserved_as_subsequence"
        ])

    def test_lcs_computation_bounded(self):
        with patch.object(p, "_lcs_length_bounded",
                          side_effect=p.OrderGap("TABLE_ORDER_LCS_BUDGET_EXCEEDED")):
            with self.assertRaisesRegex(p.OrderGap, "TABLE_ORDER_LCS_BUDGET_EXCEEDED"):
                p.assess_order(["a", "b"], ["b", "a", "x"], [flags()]*3)

    def test_mismatched_contexts_fail_closed(self):
        with self.assertRaisesRegex(p.OrderGap, "ORDER_INPUT_CARDINALITY_INVALID"):
            p.assess_order(["a"], ["a", "x"], [flags()])

    def test_ordered_scanner_normalizes_text_and_respects_nested_context(self):
        scan = p._OrderedTableScanner()
        scan.feed("<p>주석</p><table><td>영업 이익"
                  "<table><td>메모</td></table></td></table>")
        scan.close()
        digests, contexts = scan.finish()
        self.assertEqual(len(digests), 2)
        self.assertEqual(len(contexts), 2)
        self.assertTrue(contexts[0]["nested"])
        self.assertFalse(contexts[1]["nested"])
        self.assertTrue(contexts[1]["nearby_notes"])
        self.assertFalse(contexts[0]["nearby_exact_cfs"])

    def test_bad_nesting_and_bounds_fail_closed(self):
        with self.assertRaisesRegex(p.OrderGap, "TABLE_NESTING_UNVERIFIED"):
            scan = p._OrderedTableScanner()
            scan.feed("<table><td>not closed</td>")
            scan.finish()
        with patch.object(p, "MAX_TABLE_TEXT_CHARS", 2):
            with self.assertRaisesRegex(p.OrderGap, "TABLE_TEXT_BUDGET_EXCEEDED"):
                scan = p._OrderedTableScanner()
                scan.feed("<table><td>abc</td></table>")

    def test_two_pinned_official_archives_and_exact_source_counts_gate(self):
        original = [f"original-{i}" for i in range(p.EXPECTED_ORIGINAL_TABLES)]
        corrected = original[:700] + ["added-"+str(i) for i in range(6)] + original[700:]
        state = [
            (original, [flags()] * len(original)),
            (corrected, [flags()] * len(corrected)),
        ]
        with patch.object(p, "_scan_official_document", side_effect=state):
            result = p.compare_source_archives(b"first", b"amended")
        self.assertEqual(result["source_status"], "OFFICIAL_SOURCE_TABLE_ORDER_DIAGNOSTIC_ONLY")
        self.assertEqual(result["forced_new_table_positions"], 6)
        self.assertEqual(result["minimum_insertions_if_subsequence"], 6)
        self.assertTrue(result["period_statement_and_financial_cells_unverified"])
        with patch.object(p, "_scan_official_document", side_effect=[
            (original[:-1], [flags()] * (len(original)-1)),
            (corrected, [flags()] * len(corrected)),
        ]):
            with self.assertRaisesRegex(p.OrderGap, "OFFICIAL_SOURCE_TABLE_COUNTS_DRIFTED"):
                p.compare_source_archives(b"first", b"amended")

    def test_source_digest_pinning_precedes_document_examination(self):
        with patch.object(p, "inspect_official_original_document") as z:
            with self.assertRaisesRegex(p.OrderGap, "OFFICIAL_DOCUMENT_SHA_DRIFT"):
                p._scan_official_document(b"tampered", "0"*64)
        z.assert_not_called()

    def test_no_key_never_calls_provider(self):
        with (patch.dict(os.environ, {"OPENDART_API_KEY": ""}),
              patch.object(p, "_official_get") as official):
            result = p.run(object())
        official.assert_not_called()
        self.assertEqual(result["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertFalse(result["m20_performance_run_authorized"])

    def test_provider_error_is_redacted_and_ordering_disabled(self):
        with (patch.dict(os.environ, {"OPENDART_API_KEY": "PRIVATEKEY"}),
              patch.object(p, "_official_get", side_effect=ValueError("PRIVATEKEY 20221114000001"))):
            result = p.run(object())
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "OFFICIAL_SOURCE_OR_LAYOUT_UNVERIFIED")
        self.assertNotIn("PRIVATEKEY", str(result))
        self.assertNotIn("20221114000001", str(result))
        self.assertFalse(result["m20_feature_pit_admitted"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertFalse(result["real_orders_authorized"])
        self.assertEqual(result["ordering"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
