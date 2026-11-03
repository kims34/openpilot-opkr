"""Offline tests: M20 original SGML explicit structural ancestry is not PIT."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_original_sgml_tag_ancestry as p


def earns():
    return "<table><tr><td>영업이익</td><td>100</td><td>200</td></tr></table>"


def feed(fragment):
    scanner = p.SectionStructure()
    scanner.feed(fragment)
    scanner.close()
    return scanner.finish()


class FirstSGMLTagAncestryTests(unittest.TestCase):
    def test_explicit_section_cfs_title_is_only_a_hint(self):
        # Keep the exact immutable 1570-table / 15-operating-row census.
        other = "<table><tr><td>매출액</td></tr></table>"
        raw = ("<document><section><title>연결손익계산서</title>"
               + earns()*15 + other*1555 + "</section></document>")
        result = feed(raw)
        self.assertEqual(result["operating_candidate_explicit_section_or_subsection_count"], 15)
        self.assertEqual(result["operating_candidate_explicit_scoped_cfs_title_count"], 15)
        self.assertEqual(result["explicit_title_category_exact_cfs_income_count"], 1)
        self.assertEqual(result["source_status"],
                         "FIRST_ORIGINAL_SGML_EXPLICIT_TAG_STRUCTURE_ONLY")
        self.assertTrue(result["explicit_scope_tag_presence_does_not_establish_financial_values"])

    def test_scope_unlabeled_is_not_accounting_identity(self):
        raw = "<document><section>" + earns()*15 + "</section></document>"
        with patch.object(p, "MAX_TABLES", 20):
            with self.assertRaisesRegex(p.SectionGap, "SGML_SOURCE_TABLE_COUNT_DRIFTED"):
                feed(raw)

    def test_title_and_notes_within_scoped_section_still_not_original_fact(self):
        raw = ("<document><section><title>재무제표</title>"
               + earns()*8 + "</section>"
               "<section><title>주석</title>" + earns()*7 +
               "</section></document>")
        # Inspect parser internals without invoking the real-document-only
        # strict 1,570-table finish() cardinality requirement.
        scanner = p.SectionStructure()
        scanner.feed(raw)
        scanner.close()
        self.assertEqual(scanner.operating_rows, 15)
        self.assertEqual(scanner.earnings_structures["explicit_scoped_generic_financial_title"], 8)
        self.assertEqual(scanner.earnings_structures["explicit_scoped_notes_title"], 7)
        self.assertEqual(scanner.heading_kind_counts["notes"], 1)

    def test_table_outside_scope_is_unclassified(self):
        scanner = p.SectionStructure()
        scanner.feed(earns()*15)
        scanner.close()
        self.assertEqual(scanner.earnings_structures["no_explicit_scope"], 15)
        self.assertEqual(scanner.earnings_structures["explicit_scoped_cfs_title"], 0)

    def test_missing_section_close_fails_closed(self):
        x = p.SectionStructure()
        x.feed("<section><title>연결포괄손익계산서</title>" + earns()*15)
        with self.assertRaisesRegex(p.SectionGap, "SGML_UNCLOSED_SCOPE_OR_TABLE"):
            x.finish()

    def test_misnested_section_fails_closed(self):
        x = p.SectionStructure()
        x.feed("<section><article>" + earns()*15 + "</section></article>")
        with self.assertRaisesRegex(p.SectionGap, "SGML_SCOPE_STRUCTURE_AMBIGUOUS"):
            x.finish()

    def test_limits_and_signature_shape_fail_closed(self):
        with patch.object(p, "MAX_CELL_CHARS", 3):
            with self.assertRaisesRegex(p.SectionGap, "SGML_CELL_BUDGET_EXCEEDED"):
                x = p.SectionStructure()
                x.feed("<table><tr><td>영업이익</td></tr></table>")
        with patch.object(p, "MAX_NODES", 1):
            with self.assertRaisesRegex(p.SectionGap, "SGML_NODE_BUDGET_EXCEEDED"):
                x = p.SectionStructure()
                x.feed(earns())

    def test_only_pinned_first_original_archive_accepted(self):
        with patch.object(p, "inspect_official_original_document") as check:
            with self.assertRaisesRegex(p.SectionGap, "PINNED_ORIGINAL_ARCHIVE_SHA_DRIFT"):
                p.inspect(b"unverified-document")
        check.assert_not_called()

    def test_no_key_no_api_request(self):
        with patch.dict(os.environ, {"OPENDART_API_KEY": ""}), patch.object(
            p, "_official_get"
        ) as network:
            result = p.run(object())
        network.assert_not_called()
        self.assertEqual(result["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertFalse(result["m20_feature_pit_admitted"])

    def test_secrets_and_amounts_not_reported_after_provider_failure(self):
        with patch.dict(os.environ, {"OPENDART_API_KEY": "TESTSECRET"}), patch.object(
            p, "_official_get", side_effect=ValueError("TESTSECRET 9999 20221114000001")
        ):
            report = p.run(object())
        self.assertEqual(report["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn("TESTSECRET", str(report))
        self.assertNotIn("9999", str(report))
        self.assertFalse(report["real_orders_authorized"])
        self.assertFalse(report["m20_performance_run_authorized"])
        self.assertEqual(report["ordering"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
