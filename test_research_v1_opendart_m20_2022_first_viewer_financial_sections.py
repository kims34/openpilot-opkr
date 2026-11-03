"""Offline source-shape tests for read-only original DART viewer subsection retrieval."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_first_viewer_financial_sections as p

FIRST = "20221114000001"


def node(title, i, receipt=FIRST, dtd="dart3.xsd"):
    return "\n".join([
        f'node1[\'text\'] = "{title}";',
        f'node1[\'id\'] = "{i}";',
        f'node1[\'rcpNo\'] = "{receipt}";',
        f'node1[\'dcmNo\'] = "123";',
        f'node1[\'eleId\'] = "{i}";',
        f'node1[\'offset\'] = "{i*100}";',
        f'node1[\'length\'] = "50";',
        f'node1[\'dtd\'] = "{dtd}";',
    ])


def toc():
    return "<html><script>"+ "\n".join(
        node("연결재무제표", 1)+"" for _ in []
    )+"</script></html>"


def sections():
    return "<html><script>" + "\n".join([
        node("III 재무제표", 1), node("연결재무제표", 2),
        node("재무제표", 3), node("재무제표 주석", 4),
    ]) + "</script></html>"


class ViewerFinancialSectionTests(unittest.TestCase):
    def test_four_first_original_sections_selected_from_toc(self):
        out = p._choose_first_edition_sections(sections(), FIRST)
        self.assertEqual(len(out), 4)
        self.assertEqual(len(set(x["element"] for x in out)), 4)
        self.assertTrue(all(x["receipt"] == FIRST for x in out))
        self.assertNotIn("연결재무제표", str(out))

    def test_mixed_receipts_and_toc_drift_fail_closed(self):
        fake = "<html><script>"+node("재무제표", 1, "20230401000001")+"</script></html>"
        with self.assertRaisesRegex(p.SectionGap, "VIEWER_RECEIPT_EDITION_MISMATCH"):
            p._choose_first_edition_sections(fake, FIRST)
        with self.assertRaisesRegex(p.SectionGap, "FINANCIAL_SUBDOCUMENT_COUNT_UNVERIFIED"):
            p._choose_first_edition_sections("<html><script>"+node("본문",1)+"</script></html>",FIRST)

    def test_duplicate_metadata_does_not_trigger_double_query(self):
        fake = "<html><script>"+node("재무제표", 1)+node("재무제표", 1)+"</script></html>"
        with self.assertRaisesRegex(p.SectionGap, "FINANCIAL_SUBDOCUMENT_DUPLICATE_METADATA"):
            p._choose_first_edition_sections(fake, FIRST)

    def test_html_earnings_row_is_only_lexical_shape(self):
        reader = p.SectionShape()
        reader.feed("<html><p>연결손익계산서 2022 2021 3개월</p><table><tr>"
                    "<td>영업이익</td><td>100</td><td>200</td>"
                    "</tr></table></html>")
        x = reader.result()
        self.assertTrue(x["exact_cfs_income_heading_lexical_hint"])
        self.assertTrue(x["three_month_lexical_hint"])
        self.assertEqual(x["exact_operating_row_candidates"], 1)
        self.assertEqual(x["table_tags"], 1)
        self.assertNotIn("100", str(x))
        self.assertNotIn("200", str(x))

    def test_all_sections_metadata_without_numbers_names_or_receipts(self):
        body = "<html><table><tr><td>영업이익</td><td>99</td></tr></table></html>"
        class Session: pass
        with patch.object(p, "_bounded_public_get", return_value=body) as call:
            result = p._inspect_sections(Session(), sections(), FIRST)
        self.assertEqual(call.call_count, 4)
        self.assertEqual(result["first_receipt_financial_toc_sections_selected"], 4)
        self.assertEqual(result["viewer_financial_total_operating_row_text_candidates"], 4)
        self.assertTrue(result["viewer_section_lexical_metadata_is_not_original_pit_proof"])
        for item in ("영업이익", FIRST, "99", "dart3.xsd"):
            self.assertNotIn(item, str(result))

    def test_subdoc_endpoint_no_api_credential_and_exact_receipt(self):
        class R:
            status_code=200
            headers={"Content-Type":"text/html; charset=utf-8"}
            def __init__(self):self.closed=False
            def iter_content(self,chunk_size):
                yield b"<html><table><tr><td>Financials</td></tr></table></html>"
            def close(self):self.closed=True
        class Session:
            def __init__(self):self.info=None;self.response=R()
            def get(self,url,**kw):self.info=(url,kw);return self.response
        s=Session()
        meta=p._choose_first_edition_sections(sections(),FIRST)[0]
        output=p._bounded_public_get(s,meta,FIRST)
        self.assertIn("<html>",output)
        url,kw=s.info
        self.assertEqual(url,"https://dart.fss.or.kr/report/viewer.do")
        self.assertFalse(kw["allow_redirects"])
        self.assertEqual(kw["params"]["rcpNo"],FIRST)
        self.assertNotIn("crtfc_key",str(kw))
        self.assertTrue(s.response.closed)

    def test_invalid_receipt_and_bad_mime_fail_closed(self):
        meta=p._choose_first_edition_sections(sections(),FIRST)[0]
        with self.assertRaisesRegex(p.SectionGap,"SUBDOC_ORIGINAL_RECEIPT_UNVERIFIED"):
            p._bounded_public_get(object(),meta,"20230401000001")
        class R:
            status_code=200
            headers={"Content-Type":"application/json"}
            def close(self):pass
        class Session:
            def get(self,*args,**kwargs):return R()
        with self.assertRaisesRegex(p.SectionGap,"VIEWER_SUBDOC_CONTENT_TYPE_UNEXPECTED"):
            p._bounded_public_get(Session(),meta,FIRST)

    def test_no_key_no_network_and_no_order(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), patch.object(p,"_official_get") as api:
            result=p.run(object())
        api.assert_not_called()
        self.assertFalse(result["m20_feature_pit_admitted"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertEqual(result["ordering"],"DISABLED")

    def test_provider_error_is_redacted(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":"PRIVATE_SECRET"}),
              patch.object(p,"_official_get",side_effect=ValueError("PRIVATE_SECRET 123456"))):
            result=p.run(object())
        self.assertEqual(result["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn("PRIVATE_SECRET",str(result))
        self.assertNotIn("123456",str(result))
        self.assertFalse(result["real_orders_authorized"])


    def test_hidden_revised_receipt_behind_valid_financial_sections_rejected(self):
        # A malformed/nonfinancial extra node must not smuggle a corrected
        # edition receipt past the four otherwise valid first-original items.
        altered = (sections()[:-16] +
                   "node2['rcpNo'] = '20230401000001';</script></html>")
        with self.assertRaisesRegex(p.SectionGap,
                                    "VIEWER_RECEIPT_EDITION_MISMATCH"):
            p._choose_first_edition_sections(altered, FIRST)

    def test_cross_node_financial_title_not_bound_to_other_document_fields(self):
        mixed = node("연결재무제표", 1).replace(
            "node1['text']", "node2['text']")
        with self.assertRaisesRegex(p.SectionGap,
                                    "VIEWER_RECEIPT_EDITION_MISMATCH"):
            p._choose_first_edition_sections(
                "<html><script>" + mixed + "</script></html>", FIRST)

    def test_genuine_four_original_financial_sections_no_pit_authorization(self):
        result = p._choose_first_edition_sections(sections(), FIRST)
        self.assertEqual(len(result), 4)
        self.assertTrue(all(v["receipt"] == FIRST for v in result))
        self.assertFalse(p.SAFE["m20_feature_pit_admitted"])
        self.assertFalse(p.SAFE["original_2022_cfs_profit_three_month_verified"])
        self.assertEqual(p.SAFE["ordering"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
