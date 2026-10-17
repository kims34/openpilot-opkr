"""Synthetic header/cell structure proof test; NEVER historical PIT facts."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_first_viewer_header_layout as p

FIRST = "20221114000001"


def table(headers="", profit="영업이익", amounts=None):
    if amounts is None:
        amounts=["100","200","300","400"]
    cells="".join("<td>"+x+"</td>" for x in [profit]+amounts)
    return "<html><table>"+headers+"<tr>"+cells+"</tr></table></html>"


class HeaderRowLayoutTests(unittest.TestCase):
    def scan(self, page):
        s=p.HeaderRows()
        s.feed(page)
        s.close()
        return s.finish()

    def test_explicit_separate_th_row_preceding_profit_is_only_source_hint(self):
        raw=table("<tr><th colspan='2'>당분기 3개월</th>"
                  "<th colspan='2'>전분기 누적</th></tr>")
        z=self.scan(raw)
        self.assertEqual(z["operating_candidate_tables"],1)
        self.assertEqual(z["operating_candidate_rows"],1)
        self.assertEqual(z["operating_with_four_numeric_peers"],1)
        self.assertEqual(z["operating_with_preceding_th_cell"],1)
        self.assertEqual(z["operating_with_preceding_current_and_prior_quarter_words"],1)
        self.assertEqual(z["operating_with_same_header_row_current_and_prior_words"],1)
        self.assertEqual(z["operating_with_preceding_three_month_word"],1)
        self.assertEqual(z["operating_with_preceding_cumulative_word"],1)
        self.assertEqual(z["operating_with_preceding_colspan_or_rowspan"],1)
        for leaked in ("100","200","300","400","영업이익"):
            self.assertNotIn(leaked,str(z))

    def test_quarter_words_only_after_profit_cannot_backfill_header(self):
        raw=table()+ "<table><tr><th>당분기</th><th>전분기</th></tr></table>"
        z=self.scan(raw)
        self.assertEqual(z["operating_candidate_tables"],1)
        self.assertEqual(z["operating_with_preceding_explicit_quarter_words"],0)
        self.assertEqual(z["operating_with_preceding_th_cell"],0)

    def test_only_accounting_peer_cells_not_source_quarter_admission(self):
        z=self.scan(table())
        self.assertEqual(z["operating_with_four_numeric_peers"],1)
        self.assertEqual(z["operating_with_preceding_three_month_word"],0)
        self.assertEqual(z["operating_with_preceding_current_and_prior_quarter_words"],0)

    def test_two_different_header_rows_not_same_explicit_group(self):
        z=self.scan(table("<tr><td>당분기</td></tr><tr><td>전분기</td></tr>"))
        self.assertEqual(z["operating_with_preceding_current_and_prior_quarter_words"],1)
        self.assertEqual(z["operating_with_same_header_row_current_and_prior_words"],0)
        self.assertEqual(z["operating_with_preceding_th_cell"],0)

    def test_nested_income_row_is_ambiguous(self):
        nested = "<html><table><tr><td><table><tr><th>당분기</th></tr><tr>" \
                 "<td>영업이익</td><td>100</td></tr></table></td></tr></table></html>"
        z=self.scan(nested)
        self.assertEqual(z["operating_candidate_tables"],1)
        self.assertEqual(z["operating_candidate_in_nested_table"],1)

    def test_finite_budgets_fail_closed(self):
        with patch.object(p,"MAX_ROWS_PER_TABLE",1):
            with self.assertRaisesRegex(p.SectionGap,"HEADER_ROW_COUNT_LIMIT"):
                self.scan(table("<tr><th>당분기</th></tr>"))
        with patch.object(p,"MAX_CELL_LENGTH",3):
            with self.assertRaisesRegex(p.SectionGap,"HEADER_CELL_TEXT_LIMIT"):
                self.scan(table())

    def test_invalid_spans_keep_original_column_geometry_unverified(self):
        z=self.scan(table("<tr><th colspan='10000'>3개월</th>"
                          "<th rowspan='0'>당분기</th></tr>"))
        self.assertEqual(z["unsupported_span_attributes_encountered"],2)
        self.assertEqual(z["operating_candidate_tables_with_unsupported_span"],1)
        self.assertEqual(z["operating_with_preceding_three_month_word"],1)
        self.assertEqual(z["operating_with_preceding_colspan_or_rowspan"],0)

    def test_invalid_span_in_other_table_not_attributed_to_operating_row(self):
        z=self.scan("<table><tr><th rowspan='1000'>기타</th></tr></table>"
                    +table())
        self.assertEqual(z["unsupported_span_attributes_encountered"],1)
        self.assertEqual(z["operating_candidate_tables_with_unsupported_span"],0)

    def test_four_exact_first_receipt_sections_and_safe_aggregate(self):
        sections=[{"receipt":FIRST,"document":"1","element":str(i),
                   "offset":"0","length":"150","dtd":"dart3.xsd"} for i in range(1,5)]
        with (patch.object(p,"_choose_first_edition_sections",return_value=sections),
              patch.object(p,"_bounded_public_get",side_effect=[
                  table("<tr><th>당분기</th><th>전분기</th></tr>"),
                  table(),
                  table(profit="매출액"),
                  table(profit="매출액"),
              ]) as fetch):
            result=p.inspect(object(),"<html/>",FIRST)
        self.assertEqual(fetch.call_count,4)
        self.assertEqual(result["fixed_first_filing_financial_subdocuments"],4)
        self.assertEqual(result["operating_candidate_tables"],2)
        self.assertEqual(result["operating_with_preceding_current_and_prior_quarter_words"],1)
        self.assertFalse(result["header_word_column_or_group_identity_verified"])
        self.assertFalse(result["original_profit_numeric_column_assignment_verified"])
        self.assertTrue(result["any_unsupported_span_makes_column_geometry_unverified"])
        self.assertTrue(result["viewer_header_row_is_not_original_accounting_fact"])
        for raw in ("100",FIRST,"dart3.xsd"):
            self.assertNotIn(raw,str(result))

    def test_auth_empty_cannot_open_provider(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), patch.object(p,"_official_get") as provider:
            result=p.run(object())
        provider.assert_not_called()
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertEqual(result["ordering"],"DISABLED")

    def test_untrusted_errors_redacted(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"SECRET_TEST"}), patch.object(
            p,"_official_get",side_effect=ValueError("SECRET_TEST 99,999 20221114000001")
        ):
            result=p.run(object())
        self.assertEqual(result["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for private in ("SECRET_TEST","99,999",FIRST):
            self.assertNotIn(private,str(result))
        self.assertFalse(result["original_cfs_identity_and_profit_colmap_verified"])
        self.assertFalse(result["real_orders_authorized"])


if __name__=="__main__":
    unittest.main()
