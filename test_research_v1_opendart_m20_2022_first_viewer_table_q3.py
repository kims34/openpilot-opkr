"""Offline-only original DART viewer per-table source/period hints, no PIT."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_first_viewer_table_q3 as p

FIRST = "20221114000001"


def html(body="", profit=True, two=True):
    cells = "<td>영업이익</td><td>100</td><td>200</td>" if profit else (
        "<td>매출액</td><td>100</td>")
    if not two:
        cells = "<td>영업이익</td><td>100</td>"
    return "<html><table>" + body + "<tr>" + cells + "</tr></table></html>"


class OriginalTableQuarterTests(unittest.TestCase):
    def scan(self, content):
        x=p.TableHints()
        x.feed(content)
        x.close()
        return x.finish()

    def test_profit_and_three_month_in_same_table_are_still_not_facts(self):
        source=html("<tr><th>당분기 3개월</th><th>전분기 3개월</th></tr>")
        x=self.scan(source)
        self.assertEqual(x["profit_candidate_tables"], 1)
        self.assertEqual(x["profit_rows_with_two_numeric_peer_cells"], 1)
        self.assertEqual(x["profit_tables_with_three_month_header"], 1)
        self.assertEqual(x["profit_tables_with_current_and_prior_quarter_headers"], 1)
        self.assertEqual(x["profit_tables_with_both_complete_q3_date_windows"], 0)
        for amount in ("100", "200"):
            self.assertNotIn(amount,str(x))

    def test_year_mentions_not_full_periods(self):
        source=html("<tr><th>2022 / 2021 당분기 전분기</th></tr>")
        x=self.scan(source)
        self.assertEqual(x["profit_tables_with_complete_2022_q3_date_window"],0)
        self.assertEqual(x["profit_tables_with_complete_2021_q3_date_window"],0)

    def test_explicit_full_q3_windows_within_table_are_hints_only(self):
        source=html("<tr><th>2022.07.01 - 2022.09.30 "
                    "2021.07.01 - 2021.09.30 "
                    "연결손익계산서 3개월 단위:백만원</th></tr>")
        x=self.scan(source)
        self.assertEqual(x["profit_tables_with_both_complete_q3_date_windows"],1)
        self.assertEqual(x["profit_tables_with_explicit_cfs_income_heading"],1)
        self.assertEqual(x["profit_tables_with_currency_unit_lexical_hint"],1)

    def test_profit_in_separate_table_does_not_join_other_table_header(self):
        source="<html><table><tr><td>3개월</td></tr></table>" \
               "<table><tr><td>영업이익</td><td>100</td><td>200</td>" \
               "</tr></table></html>"
        x=self.scan(source)
        self.assertEqual(x["profit_candidate_tables"],1)
        self.assertEqual(x["profit_tables_with_three_month_header"],0)

    def test_nested_profit_table_is_marked_separately(self):
        source="<html><table><tr><td>" \
               "<table><tr><td>영업이익</td><td>100</td>" \
               "<td>200</td></tr></table>" \
               "</td></tr></table></html>"
        x=self.scan(source)
        self.assertEqual(x["profit_candidate_tables"],1)
        self.assertEqual(x["profit_nested_candidate_tables"],1)
        self.assertEqual(x["profit_in_outer_table_with_nested_children"],0)

    def test_too_many_tables_or_open_frames_fail_closed(self):
        with patch.object(p,"MAX_TABLES",1):
            with self.assertRaisesRegex(p.SectionGap,"TABLE_Q3_TABLE_LIMIT"):
                self.scan(html()+html())
        a=p.TableHints()
        a.feed("<html><table><tr><td>영업이익</td></tr>")
        with self.assertRaisesRegex(p.SectionGap,"TABLE_Q3_UNBALANCED"):
            a.finish()

    def test_exactly_four_first_receipt_sections_and_no_facts(self):
        metadata=[{"receipt":FIRST,"document":"1","element":str(i),
                  "offset":str(i*100),"length":"500","dtd":"dart3.xsd"}
                  for i in range(1,5)]
        with (patch.object(p,"_choose_first_edition_sections",return_value=metadata),
              patch.object(p,"_bounded_public_get",side_effect=[
                  html("3개월"),html("당분기 / 전분기 3개월"),html(profit=False),
                  html("2022 2021", profit=False)
              ]) as get):
            x=p.inspect(object(), "<html/>", FIRST)
        self.assertEqual(get.call_count,4)
        self.assertEqual(x["first_original_financial_viewer_sections"],4)
        self.assertEqual(x["profit_candidate_tables"],2)
        self.assertEqual(x["profit_rows_with_two_numeric_peer_cells"],2)
        self.assertEqual(x["profit_tables_with_three_month_header"],2)
        self.assertTrue(x["same_table_header_is_not_source_financial_semantics"])
        for value in ("영업이익","100",FIRST,"dart3.xsd"):
            self.assertNotIn(value,str(x))

    def test_missing_sections_block(self):
        with patch.object(p,"_choose_first_edition_sections",return_value=[{}]):
            with self.assertRaisesRegex(p.SectionGap,"TABLE_Q3_FOUR_SECTIONS_REQUIRED"):
                p.inspect(object(),"<html/>",FIRST)

    def test_no_key_no_api_calls(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), patch.object(p,"_official_get") as api:
            x=p.run(object())
        api.assert_not_called()
        self.assertEqual(x["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(x["m20_performance_run_authorized"])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_provider_exception_fails_closed_and_redacts(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"SENSITIVE"}), patch.object(
            p,"_official_get",side_effect=ValueError("SENSITIVE 20221114000001 99,999")
        ):
            x=p.run(object())
        self.assertEqual(x["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for value in ("SENSITIVE","20221114000001","99,999"):
            self.assertNotIn(value,str(x))
        self.assertFalse(x["original_2022_2021_three_month_cfs_profit_cells_verified"])
        self.assertFalse(x["m20_feature_pit_admitted"])
        self.assertFalse(x["real_orders_authorized"])


if __name__=="__main__":
    unittest.main()
