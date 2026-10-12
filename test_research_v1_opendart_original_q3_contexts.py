"""Offline synthetic checks for original quarterly XBRL date-context metadata."""
import io
import json
import os
import unittest
from unittest.mock import patch
import zipfile

from research_v1_opendart_original_q3_contexts import (
    QuarterContextError, inspect_original_operating_contexts, run,
)
from test_research_v1_opendart_original_xbrl_pilot import (
    FakeSession, FakeResponse, R24, R25, zipp,
)


def xbrl(year=2025, *, fact=True, current_quarter=True,
         bad_context=False, doctype=False):
    xyear = str(year)
    start = (xyear + "-07-01") if current_quarter else (xyear + "-01-01")
    end = xyear + "-09-30"
    x = (
        '<xbrl xmlns:dart="http://dart.fss.or.kr/xbrl" '
        'xmlns:xbrli="http://www.xbrl.org/2003/instance">'
        '<xbrli:context id="ctx_q3"><xbrli:period>'
        f'<xbrli:startDate>{start}</xbrli:startDate>'
        f'<xbrli:endDate>{end}</xbrli:endDate>'
        '</xbrli:period></xbrli:context>'
    )
    if bad_context:
        x += ('<xbrli:context id="ctx_q3"><xbrli:period>'
              f'<xbrli:startDate>{start}</xbrli:startDate>'
              f'<xbrli:endDate>{end}</xbrli:endDate>'
              '</xbrli:period></xbrli:context>')
    if fact:
        x += '<dart:OperatingIncomeLoss contextRef="ctx_q3" unitRef="KRW">123456789</dart:OperatingIncomeLoss>'
    x += '</xbrl>'
    if doctype:
        x = '<!DOCTYPE xbrl [<!ENTITY risky "secret">]>' + x
    return zipp({"report.xbrl": x.encode("utf-8"),
                 "meta.xml": b"<metadata/>"})


class OriginalQ3ContextsTests(unittest.TestCase):
    def test_current_quarter_concept_in_context_without_amount_exposure(self):
        out = inspect_original_operating_contexts(xbrl(), 2025)
        self.assertEqual(out["fiscal_year"], 2025)
        self.assertEqual(out["xml_files_parsed"], 2)
        self.assertEqual(out["operating_profit_tagged_fact_count"], 1)
        self.assertEqual(out["exact_jul_to_sep_context_count"], 1)
        self.assertEqual(out["exact_jul_to_sep_tagged_fact_count"], 1)
        self.assertEqual(out["jan_to_sep_tagged_fact_count"], 0)
        self.assertFalse(out["standalone_quarter_operating_profit_semantics_verified"])
        self.assertFalse(out["historical_xbrl_pit_verified"])
        self.assertFalse(out["operating_amounts_or_context_ids_saved"])
        for sensitive in ("ctx_q3", "123456789", "dart.fss.or.kr"):
            self.assertNotIn(sensitive, json.dumps(out))

    def test_ytd_is_not_standalone_quarter(self):
        out = inspect_original_operating_contexts(xbrl(current_quarter=False), 2025)
        self.assertEqual(out["exact_jul_to_sep_tagged_fact_count"], 0)
        self.assertEqual(out["jan_to_sep_tagged_fact_count"], 1)
        self.assertFalse(out["standalone_quarter_operating_profit_semantics_verified"])

    def test_missing_fact_never_imputed(self):
        out = inspect_original_operating_contexts(xbrl(fact=False), 2025)
        self.assertEqual(out["exact_jul_to_sep_context_count"], 1)
        self.assertEqual(out["exact_jul_to_sep_tagged_fact_count"], 0)
        self.assertFalse(out["historical_xbrl_pit_verified"])

    def test_wrong_year_does_not_match_exact_period(self):
        out = inspect_original_operating_contexts(xbrl(2025), 2024)
        self.assertEqual(out["exact_jul_to_sep_tagged_fact_count"], 0)
        with self.assertRaisesRegex(QuarterContextError, "OUTSIDE_FIXED_Q3_SCOPE"):
            inspect_original_operating_contexts(xbrl(), 2023)

    def test_repeated_context_identifier_fails_closed(self):
        with self.assertRaisesRegex(QuarterContextError, "XBRL_CONTEXT_ID_INVALID"):
            inspect_original_operating_contexts(xbrl(bad_context=True), 2025)

    def test_malicious_dtd_is_disallowed(self):
        with self.assertRaisesRegex(QuarterContextError, "XBRL_XML_UNSAFE_OR_INVALID"):
            inspect_original_operating_contexts(xbrl(doctype=True), 2025)

    def test_corrupted_xml_is_not_silently_ignored(self):
        with self.assertRaisesRegex(QuarterContextError, "XBRL_XML_UNSAFE_OR_INVALID"):
            inspect_original_operating_contexts(zipp({"report.xbrl": b"<xbrl><notclosed/>"}), 2025)

    def test_missing_structured_xml_is_rejected(self):
        with self.assertRaises(Exception):
            inspect_original_operating_contexts(zipp({"not-xml.txt": b"any"}), 2025)

    def test_full_fake_two_report_probe_stays_unadmitted(self):
        session = FakeSession(
            response24=FakeResponse(xbrl(2024)),
            response25=FakeResponse(xbrl(2025)),
        )
        with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-only-key"}, clear=True):
            out = run(session)
        self.assertEqual(out["source_status"], "XBRL_ORIGINAL_Q3_CONTEXT_COUNTS_OBSERVED_NOT_PIT_ADMITTED")
        self.assertEqual(out["original_xbrl_q3_archive_received"], 2)
        self.assertEqual(out["q_minus_4_context_counts"]["exact_jul_to_sep_tagged_fact_count"], 1)
        self.assertEqual(out["q_current_context_counts"]["exact_jul_to_sep_tagged_fact_count"], 1)
        for key in (
            "original_report_intraday_publication_time_verified",
            "standalone_quarter_operating_profit_semantics_verified",
            "historical_quarter_amounts_and_comparability_verified",
            "original_financial_amounts_saved",
            "historical_pit_source_admitted",
            "feature_performance_testing_authorized",
            "independent_holdout_authorized",
            "champion_change_authorized",
            "live_order_authorized",
            "real_orders_authorized",
            "funds_movement_authorized",
            "permission_change_authorized",
        ):
            self.assertFalse(out[key], key)
        self.assertEqual(out["ordering"], "DISABLED")
        self.assertNotIn("synthetic-only-key", json.dumps(out))
        self.assertNotIn("123456789", json.dumps(out))
        self.assertNotIn(R24, json.dumps(out))
        self.assertNotIn(R25, json.dumps(out))

    def test_missing_key_never_calls_source(self):
        session = FakeSession()
        with patch.dict(os.environ, {}, clear=True):
            out = run(session)
        self.assertEqual(session.calls, [])
        self.assertEqual(out["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertFalse(out["historical_pit_source_admitted"])

    def test_one_xbrl_unavailable_blocks_without_authority(self):
        session = FakeSession(
            response24=FakeResponse(xbrl(2024)),
            response25=FakeResponse(b"<result><status>013</status></result>")
        )
        with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-only-key"}, clear=True):
            out = run(session)
        self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_stage"], "ORIGINAL_XBRL_Q_CURRENT")
        self.assertFalse(out["historical_pit_source_admitted"])
        self.assertFalse(out["real_orders_authorized"])


if __name__ == "__main__":
    unittest.main()
