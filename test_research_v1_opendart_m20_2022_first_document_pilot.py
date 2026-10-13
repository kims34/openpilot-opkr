"""Offline, credential-free tests for one 2022 original-document pilot."""
from __future__ import annotations

import io
import json
import os
from unittest.mock import Mock, patch
import unittest
import zipfile

from research_v1_opendart_m20_2022_first_document_pilot import (
    COHORT, DOCUMENT_ERROR_CODES, FROZEN_SLOT,
    OriginalDocumentGap, SAFETY,
    _fetch_first_document, inspect_official_original_document, inspect_original_document_layout, run,
)


def valid_zip(name="original.xml", payload=b"<document/>"):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(name, payload)
    return b.getvalue()


class OriginalDocument2022Tests(unittest.TestCase):
    def test_original_zip_verified_not_financial_value_and_all_gates_false(self):
        r = inspect_official_original_document(valid_zip())
        self.assertTrue(r["official_original_document_zip_received"])
        self.assertTrue(r["zip_crc_and_bounded_read_completed"])
        self.assertEqual(r["structured_document_entry_count"], 1)
        self.assertFalse(r["original_document_financial_semantics_validated"])
        self.assertTrue(all(SAFETY[k] is False for k in (
            "m20_feature_pit_admitted", "m20_performance_run_authorized",
            "independent_holdout_authorized", "real_orders_authorized",
            "funds_movement_authorized", "permissions_change_authorized",
        )))


    def test_coarse_layout_labels_never_admit_numeric_pit_or_orders(self):
        raw = valid_zip(payload=(
            "<DOCUMENT><TITLE>연결 재무제표</TITLE>"
            "<TABLE><TR><TD>영업이익</TD><TD>987654321</TD></TR></TABLE>"
            "<TITLE>포괄손익계산서</TITLE></DOCUMENT>"
        ).encode("utf-8"))
        report = inspect_original_document_layout(raw)
        for name in ("document_contains_consolidated_term",
                     "document_contains_income_statement_term",
                     "document_contains_table_tags",
                     "document_contains_operating_profit_term",
                     "document_contains_operating_profit_cell_text"):
            self.assertTrue(report[name], name)
        self.assertFalse(report["original_q3_cfs_three_month_profit_bound"])
        self.assertFalse(report["original_document_financial_semantics_validated"])
        self.assertFalse(report["raw_source_text_or_financial_values_persisted"])
        self.assertNotIn("987654321", json.dumps(report))

    def test_narrative_profits_are_not_financial_fact_evidence(self):
        raw = valid_zip(payload="<document><p>연결재무제표 영업이익</p></document>".encode())
        report = inspect_original_document_layout(raw)
        self.assertTrue(report["document_contains_operating_profit_term"])
        self.assertFalse(report["document_contains_table_tags"])
        self.assertFalse(report["document_contains_operating_profit_cell_text"])
        self.assertFalse(report["original_q3_cfs_three_month_profit_bound"])


    def test_safe_dtd_without_entities_does_not_block_layout(self):
        raw = valid_zip(payload=(
            '<!DOCTYPE DOCUMENT SYSTEM "https://unused.invalid/disclosure.dtd">'
            '<DOCUMENT><TITLE>연결재무제표</TITLE></DOCUMENT>'
        ).encode("utf-8"))
        report = inspect_original_document_layout(raw)
        self.assertTrue(report["document_contains_consolidated_term"])
        self.assertFalse(report["original_q3_cfs_three_month_profit_bound"])


    def test_dart_style_non_xml_html_layout_only_never_admits_earnings(self):
        raw = valid_zip(payload=(
            "<DOCUMENT><TITLE>연결 재무제표</TITLE>"
            "<TABLE><TR><TD>영업이익&nbsp;<TD>987654321</TR>"
            "<P>포괄손익계산서</DOCUMENT>"
        ).encode("utf-8"))
        report = inspect_original_document_layout(raw)
        self.assertEqual(report["non_xml_sgml_html_layout_entries"], 1)
        self.assertEqual(report["safely_parsed_strict_xml_count"], 0)
        self.assertTrue(report["document_contains_operating_profit_term"])
        self.assertTrue(report["document_contains_operating_profit_cell_text"])
        self.assertTrue(report["document_contains_income_statement_term"])
        self.assertFalse(report["original_q3_cfs_three_month_profit_bound"])
        self.assertFalse(SAFETY["m20_feature_pit_admitted"])
        self.assertFalse(SAFETY["real_orders_authorized"])
        self.assertNotIn("987654321", json.dumps(report))

    def test_legacy_cp949_markup_layout_only(self):
        data = "<DOCUMENT><TABLE><TD>영업이익&nbsp;<TD>10</TABLE></DOCUMENT>".encode("cp949")
        result = inspect_original_document_layout(valid_zip(payload=data))
        self.assertTrue(result["document_contains_operating_profit_term"])
        self.assertFalse(SAFETY["original_statement_binding_verified"])


    def test_profit_row_shape_counts_are_not_financial_fact_admission(self):
        sgml = (
            "<DOCUMENT><TABLE>"
            "<TR><TH>과목</TH><TH>당분기 3개월</TH><TH>전분기 3개월</TH>"
            "<TR><TD>영업이익<TD>1,200<TD>(900)</TR>"
            "<TR><TD>영업이익<TD>1,300<TD>1,400<TD>1,500<TD>1,600</TR>"
            "<TR><TD>영업이익 주석<TD>5,000<TD>9,999</TR>"
            "</TABLE><P>누적 9개월 연결재무제표</DOCUMENT>"
        ).encode("utf-8")
        report = inspect_original_document_layout(valid_zip(payload=sgml))
        self.assertEqual(report["profit_row_shape_count_not_facts"], 2)
        self.assertEqual(report["profit_row_with_2_numeric_peer_cells_count"], 1)
        self.assertEqual(report["profit_row_with_4_numeric_peer_cells_count"], 1)
        self.assertTrue(report["document_has_three_month_period_hint"])
        self.assertTrue(report["document_has_nine_month_cumulative_hint"])
        self.assertTrue(report["document_has_prior_comparative_hint"])
        self.assertFalse(report["original_q3_cfs_three_month_profit_bound"])
        self.assertFalse(report["original_document_financial_semantics_validated"])
        for amount in ("1,200", "1,300", "1,400", "1,500", "1,600"):
            self.assertNotIn(amount, json.dumps(report))

    def test_narrative_only_no_shape_candidates(self):
        markup = "<DOCUMENT><P>당분기 영업이익 1,234 입니다.</P></DOCUMENT>"
        report = inspect_original_document_layout(valid_zip(payload=markup.encode()))
        self.assertEqual(report["profit_row_shape_count_not_facts"], 0)
        self.assertEqual(report["profit_row_with_2_numeric_peer_cells_count"], 0)
        self.assertFalse(report["original_q3_cfs_three_month_profit_bound"])

    def test_label_with_fuzzy_profit_not_considered_exact(self):
        markup = "<DOCUMENT><TABLE><TR><TD>영업이익 조정액</TD><TD>100</TD><TD>200</TD></TR></TABLE></DOCUMENT>"
        report = inspect_original_document_layout(valid_zip(payload=markup.encode()))
        self.assertEqual(report["profit_row_shape_count_not_facts"], 0)

    def test_entity_declaration_blocks_even_html_fallback(self):
        data = b'<!DOCTYPE DOCUMENT [<!ENTITY x SYSTEM "file:///etc/passwd">]><DOCUMENT><TABLE>&x;</TABLE></DOCUMENT>'
        with self.assertRaisesRegex(OriginalDocumentGap, "DOCUMENT_LAYOUT_ENTITY_DECLARATION"):
            inspect_original_document_layout(valid_zip(payload=data))

    def test_valid_crc_but_unsafe_xml_must_fail_closed(self):
        for payload in (
            b"<document><bad></document>",
            b'<!DOCTYPE DOC [<!ENTITY x SYSTEM "file:///secret">]><DOC>&x;</DOC>',
        ):
            with self.subTest(payload=payload[:10]), self.assertRaisesRegex(
                OriginalDocumentGap, "DOCUMENT_LAYOUT_(XML_UNSAFE|ENTITY_DECLARATION)"
            ):
                inspect_original_document_layout(valid_zip(payload=payload))

    def test_status_014_and_020_are_distinguished_without_exposing_message(self):
        for code in ("013", "014", "020", "010"):
            raw = (
                '<result><status>' + code +
                '</status><message>ACCESS_KEY_SHOULD_NEVER_PRINT_123</message></result>'
            ).encode("utf-8")
            with self.subTest(code=code), self.assertRaises(OriginalDocumentGap) as cm:
                inspect_official_original_document(raw)
            self.assertEqual(str(cm.exception), DOCUMENT_ERROR_CODES[code])
            self.assertNotIn("ACCESS_KEY", str(cm.exception))

    def test_unknown_status_malformed_xml_and_dtd_fail_closed(self):
        for raw in (
            b'<result><status>999</status></result>',
            b'<unknown><status>014</status></unknown>',
            b'<?xml version="1.0"?><!DOCTYPE result [<!ENTITY x SYSTEM "file:///secret">]><result><status>&x;</status></result>',
            b'<result><status>014',
            b'provider-secret-is-not-a-zip',
            b'<result><status>014</status></result>' + b' ' * 5000,
            b'',
        ):
            with self.subTest(n=len(raw)), self.assertRaises(OriginalDocumentGap):
                inspect_official_original_document(raw)

    def test_zip_path_traversal_rejected_and_no_silent_best_effort(self):
        for filename in ("../secret.xml", "/absolute.xml", "./doc.xml", "a//b.xml"):
            with self.subTest(name=filename), self.assertRaisesRegex(
                OriginalDocumentGap, "DOCUMENT_ARCHIVE_ENTRY_UNSAFE"
            ):
                inspect_official_original_document(valid_zip(filename))

    def test_unstructured_or_bad_zip_rejected(self):
        with self.assertRaisesRegex(OriginalDocumentGap, "DOCUMENT_STRUCTURED_SOURCE_ABSENT"):
            inspect_official_original_document(valid_zip("notes.txt"))
        with self.assertRaises(OriginalDocumentGap):
            inspect_official_original_document(b"PK\\x03\\x04bad")

    def test_exact_three_approved_calls_and_fixed_2022_issuer(self):
        fake_session = Mock()
        with patch.dict(os.environ, {"OPENDART_API_KEY": "TEST_KEY_ONLY"}, clear=True):
            with patch(
                "research_v1_opendart_m20_2022_first_document_pilot._official_get",
                side_effect=[b"registry", {"status": "000"}],
            ) as official, patch(
                "research_v1_opendart_m20_2022_first_document_pilot._registry",
                return_value={COHORT[FROZEN_SLOT]: "00000001"},
            ), patch(
                "research_v1_opendart_m20_2022_first_document_pilot.original_first_receipt",
                return_value="20221114000001",
            ) as first, patch(
                "research_v1_opendart_m20_2022_first_document_pilot._fetch_first_document",
                return_value=valid_zip(),
            ) as doc:
                r = run(fake_session)
        self.assertEqual(official.call_count, 2)
        self.assertEqual(official.call_args_list[0].args[1], "corpCode.xml")
        self.assertEqual(official.call_args_list[1].args[1], "list.json")
        self.assertEqual(official.call_args_list[1].args[2]["bgn_de"], "20221001")
        self.assertEqual(official.call_args_list[1].args[2]["end_de"], "20230228")
        first.assert_called_once_with({"status": "000"}, 2022)
        doc.assert_called_once_with(fake_session, "TEST_KEY_ONLY", "20221114000001")
        self.assertEqual(r["source_status"], "ORIGINAL_2022_DOCUMENT_LAYOUT_DIAGNOSTIC_ONLY")
        self.assertFalse(r["m20_performance_run_authorized"])
        self.assertEqual(r["max_official_requests"], 3)
        self.assertNotIn("TEST_KEY_ONLY", json.dumps(r))

    def test_document_fetch_max_response_and_secret_safe_errors(self):
        class Resp:
            status_code = 200
            def iter_content(self, chunk_size):
                yield b"X" * (32 * 1024 * 1024)
                yield b"X"
            def close(self):
                self.closed = True
        resp = Resp()
        sess = Mock()
        sess.get.return_value = resp
        with self.assertRaisesRegex(OriginalDocumentGap, "DOCUMENT_RESPONSE_BYTES_INVALID"):
            _fetch_first_document(sess, "TEST_KEY", "20221114000001")
        self.assertTrue(resp.closed)
        self.assertEqual(sess.get.call_args.kwargs["allow_redirects"], False)
        self.assertEqual(sess.get.call_args.kwargs["stream"], True)

    def test_source_failure_never_opens_pit(self):
        sess=Mock()
        with patch.dict(os.environ, {"OPENDART_API_KEY": "TEST_KEY_ONLY"}, clear=True):
            with patch(
                "research_v1_opendart_m20_2022_first_document_pilot._official_get",
                side_effect=[b"registry", {"status": "000"}],
            ), patch(
                "research_v1_opendart_m20_2022_first_document_pilot._registry",
                return_value={COHORT[FROZEN_SLOT]: "00000001"},
            ), patch(
                "research_v1_opendart_m20_2022_first_document_pilot.original_first_receipt",
                return_value="20221114000001",
            ), patch(
                "research_v1_opendart_m20_2022_first_document_pilot._fetch_first_document",
                return_value=b"<result><status>014</status></result>",
            ):
                r=run(sess)
        self.assertEqual(r["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(r["failure_code"], "DOCUMENT_FILE_NOT_FOUND")
        self.assertEqual(r["failure_stage"], "EXACT_FIRST_SUBMITTED_2022_DOCUMENT_ZIP")
        self.assertFalse(r["real_orders_authorized"])
        self.assertFalse(r["original_2022_standalone_cfs_earnings_value_verified"])


if __name__ == "__main__":
    unittest.main()
