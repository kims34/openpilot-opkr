"""Offline tests for immutable six-slot M20 source feasibility only."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_v1_m20_six_slot_feasibility_ledger import (
    DIAGNOSTIC, SOURCE_GAP, REQUIRED_FALSE, PARITY_FLAGS,
    LedgerError, summarize_six_slot_sources,
)


def fixed_reports():
    out = []
    for slot in range(6):
        row = {
            "cohort_slot": slot,
            "source_status": DIAGNOSTIC,
            "max_approved_official_requests": 6,
            "ordering": "DISABLED",
            "two_initial_original_Q3_XBRL_financial_facts_found": True,
            **{k: False for k in REQUIRED_FALSE},
            **{k: True for k in PARITY_FLAGS},
        }
        row["initial_qnames_same"] = False
        row["initial_source_namespace_same"] = False
        if slot in (0, 4):
            row["api_2022_comparative_3month_equals_2022_first_original"] = False
            row["origins_versus_current_2023_CFS_both_values_match"] = False
        if slot == 5:
            row = {
                "cohort_slot": slot,
                "source_status": SOURCE_GAP,
                "max_approved_official_requests": 6,
                "ordering": "DISABLED",
                "two_initial_original_Q3_XBRL_financial_facts_found": False,
                "failure_code": "OFFICIAL_XBRL_FILE_NOT_FOUND",
                "failure_stage": "ORIGINAL_2022_Q3_FACT_PARSE",
                **{k: False for k in REQUIRED_FALSE},
            }
        out.append(row)
    return out


class M20SourceLedgerTests(unittest.TestCase):
    def test_observed_pattern_six_fixed_slots_is_not_profitable_panel(self):
        report = summarize_six_slot_sources(fixed_reports())
        self.assertEqual(report["complete_original_pairs"], 5)
        self.assertEqual(report["missing_or_failed_original_pairs"], 1)
        self.assertEqual(report["current_api_both_three_month_amounts_match_originals"], 3)
        self.assertEqual(report["current_api_2022_comparative_mismatch_slots"], 2)
        self.assertEqual(report["original_qname_drift_slots"], 5)
        self.assertEqual(report["official_original_xbrl_file_not_found_slots"], 1)
        self.assertEqual(report["source_gap_categories"], {"ORIGINAL_XBRL_FILE_MISSING": 1})
        self.assertEqual(report["diagnostic_status"], "NEW_EVIDENCE_REQUIRED_NOT_PERFORMANCE")
        self.assertFalse(report["m20_performance_run_authorized"])
        self.assertFalse(report["independent_holdout_authorized"])
        self.assertFalse(report["real_orders_authorized"])
        self.assertEqual(report["ordering"], "DISABLED")

    def test_all_six_comparative_parity_cannot_grant_pit_or_live_trading(self):
        rows = fixed_reports()
        for row in rows:
            row.update(source_status=DIAGNOSTIC,
                       two_initial_original_Q3_XBRL_financial_facts_found=True,
                       **{f: True for f in PARITY_FLAGS})
            row["initial_qnames_same"] = True
        for row in rows:
            row.pop("failure_code", None)
            row.pop("failure_stage", None)
        result = summarize_six_slot_sources(rows)
        self.assertEqual(result["complete_original_pairs"], 6)
        self.assertEqual(result["current_api_both_three_month_amounts_match_originals"], 6)
        self.assertFalse(result["historical_publication_pit_verified"])
        self.assertFalse(result["semantic_statement_binding_verified"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertFalse(result["real_orders_authorized"])

    def test_missing_or_duplicate_slot_fail_closed(self):
        rows = fixed_reports()
        for candidate in (rows[:5], rows[:5] + [rows[0]], rows + [rows[0]]):
            with self.assertRaises(LedgerError):
                summarize_six_slot_sources(candidate)

    def test_promoted_flag_rejected_no_report(self):
        for key in REQUIRED_FALSE:
            with self.subTest(flag=key):
                rows = fixed_reports()
                rows[0][key] = True
                with self.assertRaisesRegex(LedgerError, "FORBIDDEN_ADMISSION_FLAG"):
                    summarize_six_slot_sources(rows)

    def test_unknown_or_missing_parity_boolean_fails_closed(self):
        rows = fixed_reports()
        rows[1]["api_2023_3month_equals_2023_first_original"] = None
        with self.assertRaisesRegex(LedgerError, "INVALID_BOUNDED_DIAGNOSTIC_FLAGS"):
            summarize_six_slot_sources(rows)
        rows = fixed_reports()
        rows[0]["origins_versus_current_2023_CFS_both_values_match"] = True
        with self.assertRaisesRegex(LedgerError, "PARITY_INTERNAL_CONTRADICTION"):
            summarize_six_slot_sources(rows)

    def test_secret_bearing_error_code_not_published(self):
        rows = fixed_reports()
        rows[5]["failure_code"] = "my_access_key_is_SECRET_NOT_FOR_LOGS"
        result = summarize_six_slot_sources(rows)
        self.assertEqual(result["source_gap_categories"], {"OTHER_SOURCE_GAP": 1})
        self.assertNotIn("SECRET", json.dumps(result))

    def test_wrong_ordering_or_requested_endpoint_budget_rejected(self):
        for field, value in (("ordering", "ENABLED"), ("max_approved_official_requests", 7)):
            rows = fixed_reports()
            rows[1][field] = value
            with self.assertRaisesRegex(LedgerError, "FORBIDDEN_ORDERING_OR_SOURCE_SCOPE"):
                summarize_six_slot_sources(rows)


if __name__ == "__main__":
    unittest.main()
