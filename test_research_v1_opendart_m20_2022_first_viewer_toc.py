"""Offline read-only viewer subdocument TOC and PIT safety tests."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_first_viewer_toc as p

FIRST = "20221114000001"
OTHER = "20230401000001"


def node(title="연결재무제표", receipt=FIRST, dtd="dart3.xsd"):
    return (
        'node1[\'text\'] = "'+title+'";\n'
        'node1[\'id\'] = "1";\n'
        'node1[\'rcpNo\'] = "'+receipt+'";\n'
        'node1[\'dcmNo\'] = "123456";\n'
        'node1[\'eleId\'] = "1";\n'
        'node1[\'offset\'] = "400";\n'
        'node1[\'length\'] = "1000";\n'
        'node1[\'dtd\'] = "'+dtd+'";\n'
    )


class FirstViewerTocTests(unittest.TestCase):
    def test_two_exact_first_edition_toc_nodes_are_source_hints_only(self):
        fake = "<html><script>"+node("연결손익계산서")+node("주석")+"</script></html>"
        result = p._safe_counts(fake,FIRST)
        self.assertEqual(result["source_status"],"FIRST_RECEIPT_VIEWER_TOC_METADATA_ONLY")
        self.assertEqual(result["matched_first_receipt_toc_entries"],2)
        self.assertEqual(result["toc_exact_cfs_income_heading_entries"],1)
        self.assertEqual(result["toc_notes_heading_entries"],1)
        self.assertTrue(result["toc_has_dart3_xsd_query_marker"])
        self.assertFalse(result["toc_structured_first_original_cfs_section_proven"])
        for forbidden in (FIRST,"123456","연결손익계산서","주석"):
            self.assertNotIn(forbidden,str(result))

    def test_revised_edition_mixed_in_is_hard_stop(self):
        fake = "<html><script>"+node("원본")+node("정정",OTHER)+"</script></html>"
        with self.assertRaisesRegex(p.ViewerGap,"VIEWER_MULTIPLE_RECEIPT_EDITIONS"):
            p._safe_counts(fake,FIRST)

    def test_single_doc_public_metadata_but_not_authority(self):
        fake = "<html><script>viewDoc('"+FIRST+"','1234','1','0','400','dart3.xsd','');</script></html>"
        result = p._safe_counts(fake,FIRST)
        self.assertEqual(result["source_status"],"FIRST_RECEIPT_VIEWER_SINGLE_DOC_METADATA_ONLY")
        self.assertEqual(result["matched_first_receipt_single_viewdoc_entries"],1)
        self.assertFalse(result["toc_structured_first_original_cfs_section_proven"])

    def test_missing_or_non_html_toc_blocks(self):
        with self.assertRaisesRegex(p.ViewerGap,"VIEWER_TOC_NOT_STRUCTURED"):
            p._safe_counts("<html><body>No indexed content</body></html>",FIRST)
        with self.assertRaisesRegex(p.ViewerGap,"VIEWER_NOT_HTML"):
            p._safe_counts('{"status":"014"}',FIRST)

    def test_viewer_fetch_has_one_fixed_https_endpoint_no_key_and_limit(self):
        class Fake:
            status_code=200
            headers={"Content-Type":"text/html;charset=utf-8"}
            def __init__(self): self.closed=False
            def iter_content(self,chunk_size=65536):
                yield b"<html><body>public-only</body></html>"
            def close(self):self.closed=True
        class Session:
            def __init__(self):self.args=None;self.response=Fake()
            def get(self,url,**kw):
                self.args=(url,kw)
                return self.response
        s=Session()
        html=p._viewer_fetch(s,FIRST)
        self.assertTrue(html.startswith("<html>"))
        url,kwargs=s.args
        self.assertEqual(url,"https://dart.fss.or.kr/dsaf001/main.do")
        self.assertEqual(kwargs["params"],{"rcpNo":FIRST})
        self.assertTrue(kwargs["stream"])
        self.assertFalse(kwargs["allow_redirects"])
        self.assertNotIn("crtfc_key",repr(s.args))
        self.assertTrue(s.response.closed)

    def test_viewer_blocks_wrong_receipt_and_content_type(self):
        class Bad:
            status_code=200
            headers={"Content-Type":"text/plain"}
            def close(self):pass
        class Session:
            def get(self,url,**kw):return Bad()
        with self.assertRaisesRegex(p.ViewerGap,"VIEWER_RESPONSE_NOT_HTML"):
            p._viewer_fetch(Session(),FIRST)
        with self.assertRaisesRegex(p.ViewerGap,"VIEWER_RECEIPT_SHAPE_INVALID"):
            p._viewer_fetch(Session(),"not-a-receipt")

    def test_exact_initial_filing_selected_and_one_viewer_call(self):
        calls=[]
        class Session: pass
        def official(session, endpoint, params, zip_response=False):
            calls.append(endpoint)
            if endpoint=="corpCode.xml":return b"registry"
            if endpoint=="list.json":return {"mock":"index"}
            raise AssertionError("unexpected request")
        with (patch.object(p,"_official_get",side_effect=official),
              patch.object(p,"_registry",return_value={p.COHORT[5]:"00000001"}),
              patch.object(p,"original_first_receipt",return_value=FIRST),
              patch.object(p,"_viewer_fetch",return_value="<html><script>"+node()+"</script></html>"),
              patch.dict(os.environ,{"OPENDART_API_KEY":"SENSITIVE_KEY"})):
            result=p.run(Session())
        self.assertEqual(calls,["corpCode.xml","list.json"])
        self.assertEqual(result["max_official_api_calls"],2)
        self.assertEqual(result["max_public_viewer_calls"],1)
        self.assertFalse(result["viewer_is_original_vintage_financial_proof"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertEqual(result["ordering"],"DISABLED")
        self.assertNotIn("SENSITIVE_KEY",str(result))

    def test_no_key_no_calls(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":""}),
              patch.object(p,"_official_get") as api):
            result=p.run(object())
        api.assert_not_called()
        self.assertEqual(result["source_status"],"AUTH_NOT_CONFIGURED")

    def test_unsafe_provider_error_is_redacted_and_no_trades(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":"SECRET_123"}),
              patch.object(p,"_official_get",side_effect=ValueError("SECRET_123 confidential"))):
            result=p.run(object())
        self.assertEqual(result["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn("SECRET_123",str(result))
        self.assertFalse(result["verified_original_2022_q3_cfs_profit"])
        self.assertFalse(result["real_orders_authorized"])


if __name__=="__main__":
    unittest.main()
