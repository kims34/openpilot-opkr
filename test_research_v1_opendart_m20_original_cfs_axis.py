"""Synthetic no-network tests for IFRS explicit consolidated Q3 axis only."""
import json
import os
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_original_cfs_axis import (
    CFSAxisError, inspect_explicit_cfs_axis, run,
)
from test_research_v1_opendart_original_xbrl_pilot import (
    FakeSession, FakeResponse, R24, R25, zipp,
)


def document(year=2025, *, scope="consolidated", ytd=False,
             two_same=False, missing_unit=False, extra_axis=False, dtd=False):
    start=f"{year}-01-01" if ytd else f"{year}-07-01"
    end=f"{year}-09-30"
    if scope=="consolidated":
        value="ifrs-full:ConsolidatedMember"
    elif scope=="separate":
        value="ifrs-full:SeparateMember"
    else:
        value="custom:ConsolidatedMember"
    scenario=(
        '<xbrli:scenario>'
        '<xbrldi:explicitMember dimension="ifrs-full:ConsolidatedAndSeparateFinancialStatementsAxis">'
        f'{value}</xbrldi:explicitMember>'
        + ('<xbrldi:explicitMember dimension="custom:AnotherAxis">'
           'custom:AnotherMember</xbrldi:explicitMember>' if extra_axis else '')
        + '</xbrli:scenario>'
    )
    parts=[
        '<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" '
        'xmlns:xbrldi="http://xbrl.org/2006/xbrldi" '
        'xmlns:dart="http://dart.fss.or.kr/xbrl" '
        'xmlns:ifrs-full="http://xbrl.ifrs.org/taxonomy/2023/ifrs-full" '
        'xmlns:custom="http://example.com/custom">',
        '<xbrli:context id="context-one">'
        '<xbrli:entity><xbrli:identifier scheme="test">dummy</xbrli:identifier></xbrli:entity>'
        f'<xbrli:period><xbrli:startDate>{start}</xbrli:startDate>'
        f'<xbrli:endDate>{end}</xbrli:endDate></xbrli:period>'
        f'{scenario}</xbrli:context>',
        '<xbrli:unit id="u"><xbrli:measure>iso4217:KRW</xbrli:measure></xbrli:unit>',
        '<dart:OperatingIncomeLoss contextRef="context-one" unitRef="'
        + ("not-present" if missing_unit else "u")
        + '">987654321</dart:OperatingIncomeLoss>'
    ]
    if two_same:
        parts.append(
            '<dart:OperatingIncomeLoss contextRef="context-one" unitRef="u">'
            '987654321</dart:OperatingIncomeLoss>'
        )
    parts.append("</xbrli:xbrl>")
    data="".join(parts)
    if dtd:
        data='<!DOCTYPE xbrli:xbrl [<!ENTITY x "PRIVATE">]>'+data
    return data.encode("utf-8")


def archive(year=2025,**kwargs):
    return zipp({"statement.xbrl":document(year,**kwargs),"meta.xml":b"<metadata/>"})


class M20CFSAxisTests(unittest.TestCase):
    def test_explicit_consolidated_axis_candidate_but_not_income_statement_admission(self):
        a=inspect_explicit_cfs_axis(archive(2025),2025)
        self.assertEqual(a["original_q3_operating_facts"],1)
        self.assertEqual(a["exact_axis_consolidated_facts"],1)
        self.assertEqual(a["exact_axis_separate_facts"],0)
        self.assertEqual(a["unknown_axis_or_extra_dimension_facts"],0)
        self.assertEqual(a["exact_axis_consolidated_krw_numeric_candidates"],1)
        self.assertTrue(a["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"])
        for field in ("historical_consolidated_income_statement_table_bound",
                      "same_filing_duplicate_equivalence_verified",
                      "quarter_and_q_minus_4_comparability_verified",
                      "original_publication_pit_verified",
                      "numeric_values_or_identifiers_saved"):
            self.assertFalse(a[field],field)
        for private in ("987654321","context-one","dummy","statement.xbrl"):
            self.assertNotIn(private,json.dumps(a))

    def test_explicit_separate_only_cannot_pass_as_consolidated(self):
        a=inspect_explicit_cfs_axis(archive(2025,scope="separate"),2025)
        self.assertEqual(a["exact_axis_separate_facts"],1)
        self.assertEqual(a["exact_axis_consolidated_krw_numeric_candidates"],0)
        self.assertFalse(a["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"])

    def test_unknown_member_cannot_claim_consolidated(self):
        a=inspect_explicit_cfs_axis(archive(2025,scope="custom"),2025)
        self.assertEqual(a["unknown_axis_or_extra_dimension_facts"],1)
        self.assertFalse(a["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"])

    def test_extra_axis_prevents_canonical_claim(self):
        a=inspect_explicit_cfs_axis(archive(2025,extra_axis=True),2025)
        self.assertEqual(a["unknown_axis_or_extra_dimension_facts"],1)
        self.assertEqual(a["exact_axis_consolidated_facts"],0)

    def test_nine_month_context_is_not_three_month_q3(self):
        a=inspect_explicit_cfs_axis(archive(2025,ytd=True),2025)
        self.assertEqual(a["original_q3_operating_facts"],0)
        self.assertFalse(a["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"])

    def test_duplicate_consolidated_candidates_do_not_pick_one(self):
        a=inspect_explicit_cfs_axis(archive(2025,two_same=True),2025)
        self.assertEqual(a["exact_axis_consolidated_krw_numeric_candidates"],2)
        self.assertFalse(a["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"])

    def test_missing_krw_unit_cannot_be_candidate(self):
        a=inspect_explicit_cfs_axis(archive(2025,missing_unit=True),2025)
        self.assertEqual(a["exact_axis_consolidated_facts"],1)
        self.assertEqual(a["consolidated_currency_or_numeric_invalid"],1)
        self.assertEqual(a["exact_axis_consolidated_krw_numeric_candidates"],0)

    def test_wrong_year_does_not_relabel_old_financials(self):
        a=inspect_explicit_cfs_axis(archive(2025),2024)
        self.assertEqual(a["original_q3_operating_facts"],0)
        with self.assertRaisesRegex(CFSAxisError,"OUTSIDE_FIXED_Q3_SCOPE"):
            inspect_explicit_cfs_axis(archive(2025),2023)

    def test_unsafe_xml_blocked(self):
        with self.assertRaisesRegex(CFSAxisError,"XML_UNSAFE_OR_INVALID"):
            inspect_explicit_cfs_axis(archive(2025,dtd=True),2025)

    def test_fixed_two_official_originals_remain_research_only(self):
        s=FakeSession(response24=FakeResponse(archive(2024)),
                      response25=FakeResponse(archive(2025)))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            result=run(s)
        self.assertEqual(result["source_status"],
                         "CONSOLIDATED_AXIS_METADATA_ONLY_NOT_PIT_ADMITTED")
        self.assertTrue(result["original_two_report_ifrs_consolidated_axis_cardinality_verified"])
        self.assertEqual(result["original_reports_checked"],2)
        self.assertEqual(s.calls,["corpCode.xml","list.json","fnlttXbrl.xml","fnlttXbrl.xml"])
        for field in ("historical_statement_table_pit_verified",
                      "quarter_and_q_minus_4_values_comparable_verified",
                      "full_universe_historical_source_admitted",
                      "historical_pit_source_admitted",
                      "performance_run_authorized",
                      "independent_holdout_authorized",
                      "champion_change_authorized",
                      "live_order_authorized",
                      "real_orders_authorized",
                      "funds_movement_authorized",
                      "permission_change_authorized",
                      "numerical_values_or_identifiers_saved"):
            self.assertFalse(result[field],field)
        self.assertEqual(result["ordering"],"DISABLED")
        for forbidden in ("987654321","dummy","context-one","synthetic-only-key",R24,R25):
            self.assertNotIn(forbidden,json.dumps(result))

    def test_multi_candidates_only_counted_not_promoted(self):
        s=FakeSession(response24=FakeResponse(archive(2024)),
                      response25=FakeResponse(archive(2025,two_same=True)))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"CONSOLIDATED_AXIS_METADATA_ONLY_NOT_PIT_ADMITTED")
        self.assertFalse(out["original_two_report_ifrs_consolidated_axis_cardinality_verified"])
        self.assertFalse(out["performance_run_authorized"])

    def test_unknown_official_archive_fails_closed(self):
        s=FakeSession(response24=FakeResponse(b"not a ZIP"))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertFalse(out["performance_run_authorized"])
        self.assertFalse(out["real_orders_authorized"])

    def test_no_credentials_no_requests(self):
        s=FakeSession()
        with patch.dict(os.environ,{},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(s.calls,[])
        self.assertFalse(out["historical_pit_source_admitted"])

if __name__=="__main__":
    unittest.main()
