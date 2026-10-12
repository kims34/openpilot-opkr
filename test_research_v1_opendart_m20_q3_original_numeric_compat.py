"""Offline tests: original, fixed-issuer Q3 numbers are format checks only."""
import json
import os
import unittest
from unittest.mock import patch

from research_v1_opendart_m20_q3_original_numeric_compat import (
    check_two_original_q3_numbers, run, OriginalQ3NumberCompatibilityError,
)
from test_research_v1_opendart_original_xbrl_pilot import (
    zipp, FakeSession, FakeResponse,
)


def filing(year, *, amount="123456", decimals="0", member="ConsolidatedMember",
           concept="dart:OperatingIncomeLoss", entity="SYNTHETIC_CORP",
           quarters=True, duplicate=False):
    start=f"{year}-07-01" if quarters else f"{year}-01-01"
    fact=(f'<{concept} contextRef="c" unitRef="u"'
          + (f' decimals="{decimals}"' if decimals is not None else "")
          + f'>{amount}</{concept}>')
    xml=(
        '<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" '
        'xmlns:xbrldi="http://xbrl.org/2006/xbrldi" '
        'xmlns:dart="http://dart.fss.or.kr/xbrl" '
        'xmlns:ifrs-full="http://xbrl.ifrs.org/taxonomy/2023/ifrs-full">'
        '<xbrli:context id="c"><xbrli:entity>'
        '<xbrli:identifier scheme="synthetic">'
        f'{entity}</xbrli:identifier></xbrli:entity>'
        f'<xbrli:period><xbrli:startDate>{start}</xbrli:startDate>'
        f'<xbrli:endDate>{year}-09-30</xbrli:endDate></xbrli:period>'
        '<xbrli:scenario><xbrldi:explicitMember '
        'dimension="ifrs-full:ConsolidatedAndSeparateFinancialStatementsAxis">'
        f'ifrs-full:{member}</xbrldi:explicitMember></xbrli:scenario>'
        '</xbrli:context><xbrli:unit id="u"><xbrli:measure>'
        'iso4217:KRW</xbrli:measure></xbrli:unit>'
        +fact+(fact if duplicate else "")+'</xbrli:xbrl>'
    )
    return zipp({"statement.xbrl":xml.encode("utf-8")})


class OriginalQ3FormatTests(unittest.TestCase):
    def pair(self, **change):
        return check_two_original_q3_numbers(
            original24=filing(2024),
            original25=filing(2025,**change))
    def test_only_format_can_pass_not_source_pit_or_performance(self):
        out=self.pair()
        self.assertTrue(out["minimal_original_pair_representation_consistent"])
        self.assertTrue(out["finite_in_memory_numeric_difference_possible"])
        for key in ("original_income_statement_table_binding_verified",
                    "historical_publication_instant_verified",
                    "historical_publication_pit_verified",
                    "m20_signal_pit_admitted","m20_performance_run_authorized",
                    "independent_holdout_authorized","champion_change_authorized",
                    "live_orders_authorized","real_orders_authorized",
                    "source_values_or_identifiers_saved",
                    "numeric_amounts_or_delta_or_sign_saved"):
            self.assertIs(out[key],False,key)
        self.assertEqual(out["ordering"],"DISABLED")
        self.assertNotIn("123456",json.dumps(out))
        self.assertNotIn("SYNTHETIC_CORP",json.dumps(out))
    def test_concept_mismatch_is_not_a_synonym(self):
        out=self.pair(concept="ifrs-full:ProfitLossFromOperatingActivities")
        self.assertFalse(out["same_exact_taxonomy_qname_across_years"])
        self.assertFalse(out["minimal_original_pair_representation_consistent"])
    def test_unmatched_accuracy_fails_pair_gate(self):
        out=self.pair(decimals="-3")
        self.assertFalse(out["same_declared_decimals_precision"])
        self.assertFalse(out["minimal_original_pair_representation_consistent"])
    def test_unmatched_reporter_fails_pair_gate(self):
        out=self.pair(entity="ANOTHER_SYNTHETIC_CORP")
        self.assertFalse(out["same_xbrl_context_entity_identifier"])
        self.assertFalse(out["minimal_original_pair_representation_consistent"])
    def test_duplicates_not_arbitrarily_selected(self):
        with self.assertRaises(Exception):
            self.pair(duplicate=True)
    def test_separate_only_not_consolidated(self):
        with self.assertRaises(Exception):
            self.pair(member="SeparateMember")
    def test_year_to_date_not_standalone_quarter(self):
        with self.assertRaises(Exception):
            self.pair(quarters=False)
    def test_undocumented_precision_is_fail_closed(self):
        for value in (None,"unknown","+2"):
            with self.subTest(value=value):
                with self.assertRaises(OriginalQ3NumberCompatibilityError):
                    self.pair(decimals=value)
    def test_no_original_archive_no_promotion(self):
        with self.assertRaises(Exception):
            check_two_original_q3_numbers(original24=b"not_a_zip",
                                          original25=filing(2025))
    def test_official_route_synthetic_no_network(self):
        session=FakeSession(
            response24=FakeResponse(filing(2024)),
            response25=FakeResponse(filing(2025)))
        with patch.dict(os.environ,{"OPENDART_API_KEY":"synthetic-only-key"},clear=True):
            out=run(session)
        self.assertEqual(out["source_status"],
                         "ORIGINAL_NUMERIC_REPRESENTATION_SHAPE_ONLY_NOT_PIT")
        self.assertEqual(session.calls,["corpCode.xml","list.json",
                                        "fnlttXbrl.xml","fnlttXbrl.xml"])
        self.assertFalse(out["m20_performance_run_authorized"])
    def test_missing_auth_uses_no_network(self):
        session=FakeSession()
        with patch.dict(os.environ,{},clear=True):
            out=run(session)
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertEqual(session.calls,[])
        self.assertFalse(out["real_orders_authorized"])

if __name__=="__main__":
    unittest.main()
