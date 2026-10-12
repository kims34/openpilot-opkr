"""Network-free tests for dimensional/currency candidate cardinality, not alpha."""
import json
import os
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_q3_account_cardinality import (
    CandidateCardinalityError,
    inspect_m20_q3_original_financial_candidates,
    run,
)
from test_research_v1_opendart_original_xbrl_pilot import (
    FakeSession, FakeResponse, zipp, R24, R25,
)

def xml(year=2025, *, fact=True, dimensioned=False, ytd=False,
        unit="iso4217:KRW", value="123456789", duplicate_fact=False,
        nil=False, wrong_context=False, dtd=False):
    start=f"{year}-01-01" if ytd else f"{year}-07-01"
    end=f"{year}-09-30"
    extra=(
        '<xbrli:segment><xbrldi:explicitMember dimension="x:ScopeAxis">'
        "x:CustomMember</xbrldi:explicitMember></xbrli:segment>"
    ) if dimensioned else ""
    lines=[
        '<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" '
        'xmlns:dart="http://dart.fss.or.kr/xbrl" '
        'xmlns:xbrldi="http://xbrl.org/2006/xbrldi" '
        'xmlns:iso4217="http://www.xbrl.org/2003/iso4217" '
        'xmlns:x="http://example.com/x" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
        '<xbrli:context id="c"><xbrli:entity>'
        '<xbrli:identifier scheme="http://example.com/code">00000001</xbrli:identifier>'
        f'{extra}</xbrli:entity><xbrli:period>'
        f'<xbrli:startDate>{start}</xbrli:startDate>'
        f'<xbrli:endDate>{end}</xbrli:endDate>'
        '</xbrli:period></xbrli:context>',
        '<xbrli:unit id="u"><xbrli:measure>'
        f'{unit}</xbrli:measure></xbrli:unit>'
    ]
    if fact:
        attr=' xsi:nil="true"' if nil else ""
        ref="missing" if wrong_context else "c"
        tag=f'<dart:OperatingIncomeLoss contextRef="{ref}" unitRef="u"{attr}>{value}</dart:OperatingIncomeLoss>'
        lines.append(tag)
        if duplicate_fact:
            lines.append(tag)
    lines.append('</xbrli:xbrl>')
    doc="".join(lines)
    if dtd:
        doc='<!DOCTYPE xbrli:xbrl [<!ENTITY bad "secret">]>'+doc
    return doc.encode("utf-8")

def archive(year=2025, **kwargs):
    return zipp({"financial.xbrl": xml(year,**kwargs), "note.xml": b"<note/>"})

class M20OriginalCardinalityTest(unittest.TestCase):
    def test_one_dimensionless_krw_standalone_q3_fact_shape(self):
        a=inspect_m20_q3_original_financial_candidates(archive(2025),2025)
        self.assertEqual(a["exact_q3_contexts"],1)
        self.assertEqual(a["dimensionless_q3_operating_krw_facts"],1)
        self.assertEqual(a["dimensionless_q3_krw_numeric_candidate_facts"],1)
        self.assertTrue(a["strict_single_candidate_shape_only"])
        for key in ("historical_consolidated_statement_verified",
                    "quarter_and_q_minus_4_comparability_verified",
                    "historical_publication_time_verified",
                    "historic_pit_source_admitted",
                    "numeric_amounts_or_ids_saved"):
            self.assertFalse(a[key],key)
        self.assertNotIn("123456789",json.dumps(a))
        self.assertNotIn("00000001",json.dumps(a))
        self.assertNotIn("financial.xbrl",json.dumps(a))

    def test_dimensioned_q3_fact_is_not_taken_as_consolidated(self):
        a=inspect_m20_q3_original_financial_candidates(
            archive(2025,dimensioned=True),2025)
        self.assertEqual(a["dimensioned_q3_operating_facts"],1)
        self.assertEqual(a["dimensionless_q3_krw_numeric_candidate_facts"],0)
        self.assertFalse(a["strict_single_candidate_shape_only"])

    def test_ytd_nine_months_are_not_standalone_q3(self):
        a=inspect_m20_q3_original_financial_candidates(archive(2025,ytd=True),2025)
        self.assertEqual(a["exact_q3_operating_facts"],0)
        self.assertFalse(a["strict_single_candidate_shape_only"])

    def test_wrong_fiscal_year_is_not_q3(self):
        a=inspect_m20_q3_original_financial_candidates(archive(2025),2024)
        self.assertEqual(a["exact_q3_operating_facts"],0)
        with self.assertRaisesRegex(CandidateCardinalityError,"OUTSIDE_FIXED_Q3_SCOPE"):
            inspect_m20_q3_original_financial_candidates(archive(2025),2026)

    def test_non_krw_currency_is_not_eligible(self):
        a=inspect_m20_q3_original_financial_candidates(
            archive(2025,unit="iso4217:USD"),2025)
        self.assertEqual(a["non_krw_or_missing_unit_q3_facts"],1)
        self.assertFalse(a["strict_single_candidate_shape_only"])

    def test_duplicate_facts_never_silently_choose_one(self):
        a=inspect_m20_q3_original_financial_candidates(
            archive(2025,duplicate_fact=True),2025)
        self.assertEqual(a["dimensionless_q3_krw_numeric_candidate_facts"],2)
        self.assertFalse(a["strict_single_candidate_shape_only"])

    def test_invalid_amount_format_or_nil_only_counted_not_used(self):
        for kwargs in ({"value":"1,234"},{"value":"NaN"},{"value":"inf"},
                       {"nil":True},{"value":""}):
            with self.subTest(kwargs=kwargs):
                a=inspect_m20_q3_original_financial_candidates(
                    archive(2025,**kwargs),2025)
                self.assertEqual(a["invalid_numeric_shape_q3_facts"],1)
                self.assertFalse(a["strict_single_candidate_shape_only"])

    def test_missing_fact_or_context_is_not_imputed(self):
        a=inspect_m20_q3_original_financial_candidates(
            archive(2025,fact=False),2025)
        self.assertEqual(a["total_operating_concept_facts"],0)
        self.assertFalse(a["strict_single_candidate_shape_only"])
        b=inspect_m20_q3_original_financial_candidates(
            archive(2025,wrong_context=True),2025)
        self.assertEqual(b["unresolved_fact_contexts"],1)
        self.assertFalse(b["strict_single_candidate_shape_only"])

    def test_dtd_and_external_entities_rejected(self):
        with self.assertRaisesRegex(CandidateCardinalityError,"UNSAFE_OR_INVALID_XBRL"):
            inspect_m20_q3_original_financial_candidates(
                archive(2025,dtd=True),2025)

    def test_fake_official_original_receipts_and_both_years(self):
        s=FakeSession(response24=FakeResponse(archive(2024)),
                      response25=FakeResponse(archive(2025)))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"ORIGINAL_CANDIDATE_CARDINALITY_ONLY_NOT_PIT")
        self.assertEqual(out["original_reports_inspected"],2)
        self.assertTrue(out["two_years_unique_candidate_shapes_only"])
        self.assertEqual(s.calls,["corpCode.xml","list.json",
                                  "fnlttXbrl.xml","fnlttXbrl.xml"])
        for f in ("historic_consolidated_statement_verified",
                  "historical_publication_time_verified",
                  "historical_pit_source_admitted",
                  "performance_run_authorized",
                  "sealed_holdout_authorized",
                  "champion_change_authorized",
                  "real_orders_authorized",
                  "funds_movement_authorized",
                  "permission_change_authorized",
                  "original_numeric_amounts_or_ids_saved"):
            self.assertFalse(out[f],f)
        self.assertEqual(out["ordering"],"DISABLED")
        for private in ("123456789","synthetic-only-key", R24,R25):
            self.assertNotIn(private,json.dumps(out))

    def test_nonunique_year_blocks_two_year_pair_candidate_claim(self):
        s=FakeSession(response24=FakeResponse(archive(2024)),
                      response25=FakeResponse(archive(2025,duplicate_fact=True)))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"ORIGINAL_CANDIDATE_CARDINALITY_ONLY_NOT_PIT")
        self.assertFalse(out["two_years_unique_candidate_shapes_only"])
        self.assertFalse(out["performance_run_authorized"])

    def test_missing_official_original_fails_closed(self):
        s=FakeSession(response24=FakeResponse(b"<error>013</error>"))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertFalse(out["historical_pit_source_admitted"])
        self.assertFalse(out["real_orders_authorized"])

    def test_missing_key_never_calls_out(self):
        s=FakeSession()
        with patch.dict(os.environ,{},clear=True):
            out=run(s)
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(s.calls,[])
        self.assertFalse(out["performance_run_authorized"])


if __name__=="__main__":
    unittest.main()
