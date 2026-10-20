"""No-network historical DART listing first-receipt clock SHAPE tests."""
import os
import unittest
from unittest.mock import patch

import research_v1_m20_first_historic_dart_listing_clock as p

RECEIPT = "20221114000001"
OTHER = "20221114000002"


def row(receipt=RECEIPT, time="15:35"):
    return ("<tr><td>임의회사</td>"
            "<td><a href=\"javascript:openReport('" + receipt +
            "')\">분기보고서</a></td>"
            "<td>" + time + "</td></tr>")


def document(*rows):
    return "<html><table><tbody>" + "".join(rows) + "</tbody></table></html>"


class HistoricalDisclosureTimeTests(unittest.TestCase):
    def scan(self, html, receipt=RECEIPT):
        z=p.ExactReceiptRows(receipt)
        z.feed(html)
        z.close()
        return z.verdict()

    def test_unique_explicit_time_cell_is_untrusted_shape_only(self):
        x=self.scan(document(row()))
        self.assertEqual(x["source_status"],
                         "FIRST_RECEIPT_HISTORIC_LIST_ROW_CLOCK_SHAPE_ONLY")
        self.assertTrue(x["first_original_receipt_row_has_unique_time_cell"])
        self.assertFalse(x["row_clock_is_not_original_first_published_time"] is False)
        self.assertFalse(x["historical_listing_pagination_or_archive_completeness_verified"])
        for thing in ("15:35",RECEIPT,"임의회사"):
            self.assertNotIn(thing,str(x))

    def test_other_filing_clock_must_not_leak_across_rows(self):
        x=self.scan(document(row(RECEIPT,""),row(OTHER,"17:02")))
        self.assertFalse(x["first_original_receipt_row_has_unique_time_cell"])

    def test_earliest_receipt_not_in_selected_page_is_unknown_not_absent(self):
        with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_FIRST_RECEIPT_NOT_VISIBLE"):
            self.scan(document(row(OTHER)))

    def test_duplicate_first_receipt_rows_fail_closed(self):
        with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_DUPLICATE_FIRST_RECEIPT"):
            self.scan(document(row(),row()))

    def test_mixed_receipt_ids_on_same_row_are_rejected(self):
        bad=("<html><table><tr><td><a href='?rcpNo="+RECEIPT+
             "&prev="+OTHER+"'>두건</a></td><td>13:52</td></tr></table></html>")
        with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_MIXED_RECEIPTS_IN_ROW"):
            self.scan(bad)

    def test_multiple_different_time_cells_same_row_rejected(self):
        markup=row(time="14:29").replace("</tr>","<td>17:10</td></tr>")
        with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_MULTIPLE_ROW_CLOCKS"):
            self.scan(document(markup))

    def test_prevent_fake_time_and_header_without_receipt_binding(self):
        for false_time in ("2022.11.14","20221114","25:00","18:99"):
            with self.subTest(false_time=false_time):
                x=self.scan(document(row(time=false_time)))
                self.assertFalse(x["first_original_receipt_row_has_unique_time_cell"])

    def test_no_unsupported_source_html_or_missing_table(self):
        with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_TABLE_ROWS_UNVERIFIED"):
            self.scan("<html><div>해당없음</div></html>")
        with patch.object(p,"MAX_ROW_CHARS",1):
            with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_ROW_TEXT_LIMIT"):
                self.scan(document(row()))

    def test_receipt_date_from_official_first_index_not_receipt_serial_guess(self):
        filing={"list":[{"rcept_no":RECEIPT,"rcept_dt":"20221114"}]}
        with patch.object(p,"original_first_receipt",return_value=RECEIPT):
            self.assertEqual(p._first_receipt_and_day(filing),(RECEIPT,"20221114"))
        bad={"list":[{"rcept_no":RECEIPT,"rcept_dt":"20221115"}]}
        with patch.object(p,"original_first_receipt",return_value=RECEIPT):
            with self.assertRaisesRegex(p.ClockGap,"ORIGINAL_RECEIPT_DATE_UNVERIFIED"):
                p._first_receipt_and_day(bad)

    def test_exact_single_fixed_public_listing_request_without_key(self):
        class Fake:
            status_code=200
            headers={"Content-Type":"text/html; charset=utf-8"}
            def __init__(self): self.closed=False
            def iter_content(self,chunk_size): yield document(row()).encode()
            def close(self): self.closed=True
        class S:
            def __init__(self):self.info=None;self.response=Fake()
            def get(self,url,**kw):
                self.info=(url,kw)
                return self.response
        s=S()
        page=p._public_listing(s,"20221114")
        self.assertIn("<html>",page)
        url,kw=s.info
        self.assertEqual(url,"https://dart.fss.or.kr/dsac001/mainAll.do")
        self.assertEqual(kw["params"],{"selectDate":"2022.11.14"})
        self.assertFalse(kw["allow_redirects"])
        self.assertTrue(kw["stream"])
        self.assertNotIn("crtfc_key",str(s.info))
        self.assertTrue(s.response.closed)

    def test_unsupported_html_and_redirect_fail_closed(self):
        class R:
            status_code=302
            headers={"Content-Type":"text/html"}
            def close(self):pass
        class S:
            def get(self,*a,**kw):return R()
        with self.assertRaisesRegex(p.ClockGap,"HISTORIC_LIST_HTTP_UNAVAILABLE"):
            p._public_listing(S(),"20221114")

    def test_no_credentials_no_calls_and_trading_off(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}),patch.object(
            p,"_official_get") as official:
            x=p.run(object())
        official.assert_not_called()
        self.assertEqual(x["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(x["m20_feature_pit_admitted"])
        self.assertFalse(x["m20_performance_run_authorized"])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_network_exception_redacted(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"SECRET"}),patch.object(
            p,"_official_get",side_effect=ValueError("SECRET "+RECEIPT+" 17:42")):
            x=p.run(object())
        self.assertEqual(x["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for value in ("SECRET",RECEIPT,"17:42"):
            self.assertNotIn(value,str(x))
        self.assertFalse(x["exact_original_first_publication_timestamp_verified"])
        self.assertFalse(x["real_orders_authorized"])


if __name__=="__main__":
    unittest.main()
