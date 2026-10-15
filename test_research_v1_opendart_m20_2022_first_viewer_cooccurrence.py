"""Offline-only original DART viewer Q3 source hint cooccurrence safeguards."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_first_viewer_cooccurrence as p

FIRST = "20221114000001"


def doc(profit=True, cfs=True, quarter=True, full=True):
    heading = ("연결손익계산서 " if cfs else "사업보고서 ")
    heading += ("3개월 " if quarter else "누적 ")
    heading += ("2022.07.01~2022.09.30 / 2021.07.01~2021.09.30"
                if full else "2022년 / 2021년")
    row = "<tr><td>영업이익</td><td>100</td><td>200</td></tr>" if profit else (
        "<tr><td>매출액</td><td>100</td></tr>")
    return "<html><p>"+heading+"</p><table>"+row+"</table></html>"


class OriginalViewerCooccurrenceTests(unittest.TestCase):
    def scan(self, html):
        x=p.SectionCoflag()
        x.feed(html)
        x.close()
        return x.result()

    def test_all_full_q3_terms_same_subdoc_still_no_accounting_fact(self):
        z=self.scan(doc())
        self.assertEqual(z["operating_profit_row_candidates"],1)
        self.assertTrue(z["profit_and_cfs_and_three_month_and_both_periods_cooccur"])
        self.assertTrue(z["profit_and_2022_full_q3_window_cooccur"])
        self.assertTrue(z["profit_and_2021_full_q3_window_cooccur"])
        self.assertFalse(z["viewer_subdocument_is_authoritative_original_profit_fact"])
        for amount in ("100", "200"):
            self.assertNotIn(amount,str(z))

    def test_year_mentions_without_explicit_dates_do_not_bind_q3(self):
        z=self.scan(doc(full=False))
        self.assertTrue(z["profit_and_cfs_cooccur_in_viewer_subdocument"])
        self.assertFalse(z["profit_and_both_full_q3_windows_cooccur"])

    def test_dates_in_subdoc_without_profit_never_count(self):
        z=self.scan(doc(profit=False))
        self.assertEqual(z["operating_profit_row_candidates"],0)
        self.assertFalse(z["profit_and_cfs_and_three_month_and_both_periods_cooccur"])

    def test_cfs_and_profit_in_different_subdocs_not_joined(self):
        z1=self.scan(doc(profit=False))
        z2=self.scan(doc(cfs=False,quarter=False,full=False))
        self.assertFalse(z1["profit_and_cfs_cooccur_in_viewer_subdocument"])
        self.assertFalse(z2["profit_and_cfs_cooccur_in_viewer_subdocument"])

    def test_all_four_selected_and_subdoc_source_metadata_not_persisted(self):
        sections=[{"receipt":FIRST,"document":"1","element":str(i),
                   "offset":str(i*100),"length":"100","dtd":"dart3.xsd"}
                  for i in range(1,5)]
        with patch.object(p,"_choose_first_edition_sections",return_value=sections), \
             patch.object(p,"_bounded_public_get",side_effect=[
                 doc(),doc(profit=False),doc(cfs=False,quarter=False,full=False),
                 doc(profit=False,cfs=False)
             ]) as getter:
            result=p.inspect_first_receipt_financial_sections(object(),"<html/>",FIRST)
        self.assertEqual(getter.call_count,4)
        self.assertEqual(result["first_original_viewer_financial_sections"],4)
        self.assertEqual(result["first_original_viewer_operating_candidates"],2)
        self.assertEqual(result["operating_and_cfs_same_section_count"],1)
        self.assertEqual(result["operating_and_both_complete_q3_windows_same_section_count"],1)
        self.assertEqual(result["operating_cfs_three_month_both_complete_periods_same_section_count"],1)
        self.assertTrue(result["viewer_cooccurrence_is_not_a_fact_period_or_edition_binding"])
        self.assertFalse(result["original_2022_2021_three_month_cfs_profit_values_verified"])
        for raw in (FIRST,"100","200","dart3.xsd","연결손익계산서"):
            self.assertNotIn(raw,str(result))

    def test_missing_exactly_four_sections_fails_closed(self):
        with patch.object(p,"_choose_first_edition_sections",return_value=[{"receipt":FIRST}]):
            with self.assertRaisesRegex(p.SectionGap,
                                        "COOCCURRENCE_FOUR_FIRST_FINANCIAL_SECTIONS_REQUIRED"):
                p.inspect_first_receipt_financial_sections(object(),"<html/>",FIRST)

    def test_bad_tabular_structure_still_fails_closed(self):
        x=p.SectionCoflag()
        x.feed("<html><table><tr><td>영업이익</td></tr>")
        with self.assertRaisesRegex(p.SectionGap,"VIEWER_SECTION_TABLE_UNBALANCED"):
            x.result()

    def test_missing_key_does_not_invoke_official_API(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), patch.object(
            p,"_official_get") as transport:
            result=p.run(object())
        transport.assert_not_called()
        self.assertEqual(result["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(result["real_orders_authorized"])
        self.assertFalse(result["m20_performance_run_authorized"])

    def test_provider_error_does_not_expose_secret_or_enable_orders(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"SENSITIVE"}), patch.object(
            p,"_official_get",side_effect=ValueError("SENSITIVE 99,999 20221114000001")):
            result=p.run(object())
        self.assertEqual(result["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for raw in ("SENSITIVE","99,999",FIRST):
            self.assertNotIn(raw,str(result))
        self.assertFalse(result["m20_feature_pit_admitted"])
        self.assertFalse(result["real_orders_authorized"])
        self.assertEqual(result["ordering"],"DISABLED")


if __name__=="__main__":
    unittest.main()
