"""Offline, metadata-only KRX source-admission guard regression.

This intentionally DOES NOT test original KRX provider bytes or promote PIT data.
It protects the fail-closed decision recorded in the sanitized evidence manifest.
No network access, secrets, imports from broker modules or external packages.
"""
import json
import unittest
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent / "evidence" / "krx" / "2026-10-13-krx-market-source-pit-boundaries.json"


class TestKRXSourcePITAdmissionBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_source_integrity_totals_not_trading_days(self):
        item = self.v["offline_verification"]
        years = item["per_year"]
        self.assertEqual([x["year"] for x in years], list(range(2015, 2027)))
        self.assertEqual(sum(x["verified_weekday_pairs"] for x in years), 3071)
        self.assertEqual(sum(x["unverified_exchange_calendar_or_source_gap_days"] for x in years), 184)
        self.assertEqual(item["verified_weekday_pairs"], 3071)
        self.assertEqual(item["unverified_exchange_calendar_or_source_gap_days"], 184)
        self.assertTrue(all(x["integrity_class"] == "STORAGE_ONLY_NOT_PIT" for x in years))
        self.assertFalse(item["trading_days_officially_reconciled"])
        self.assertFalse(item["full_original_market_data_source_admitted"])

    def test_source_windows_nonoverlap_and_expected_totals(self):
        sub = self.v["offline_verification"]["subgroup_evidence"]
        self.assertEqual([(x["window"], x["verified_weekday_pairs"], x["calendar_or_source_gaps_unverified"]) for x in sub], [
            ("2015-2016", 522, 28),
            ("2017-2022", 1565, 90),
            ("2023-2026", 984, 66),
        ])

    def test_27_tradability_remains_quarantined(self):
        p = self.v["status_and_pit"]
        self.assertEqual(p["quarantined_issue_count"], 27)
        self.assertFalse(p["problem_27_tradability_admitted"])
        self.assertEqual(p["permitted_for_official_pit_profitability_backtest"], [])
        self.assertIn("problem 27 securities", p["not_permitted_for_official_pit_profitability_backtest"])

    def test_independent_status_pit_calendar_corporate_actions_still_missing(self):
        p = self.v["status_and_pit"]
        for field in (
            "official_halt_status_verified",
            "official_delisting_and_cleanup_status_verified",
            "historical_security_identity_pit_verified",
            "original_publication_and_available_at_lineage_verified",
            "complete_exchange_trading_calendar_attested",
            "corporate_actions_and_adjustment_lineage_verified",
            "true_fill_recovery_and_transaction_economics_verified",
            "independent_expected_universe_verified",
        ):
            with self.subTest(field=field):
                self.assertIs(p[field], False)
        self.assertEqual(p["source_contract_gates_C_and_D"], "BLOCKED")

    def test_manual_six_requests_cannot_expand_to_other_sources(self):
        p = self.v["controlled_openapi_sample"]
        self.assertEqual(p["maximum_requests"], 6)
        self.assertEqual(p["dates"], ["20150105", "20260928", "20261001"])
        self.assertEqual(len(p["approved_services"]), 2)
        self.assertTrue(p["manual_dispatch_only"])
        self.assertTrue(p["manual_toggle_required"])
        self.assertFalse(p["status_source_approval_included"])
        self.assertTrue(p["no_implicit_repeat_or_expansion"])

    def test_ordering_holdout_champion_funds_and_orders_locked(self):
        s = self.v["safety"]
        self.assertIs(s["ORDERING"], False)
        for key in (
            "real_orders_authorized", "funds_movement_authorized",
            "broker_permission_change_authorized", "champion_change_authorized",
            "frozen_h5_changed", "holdout_authorized", "performance_run_authorized",
            "additional_network_requests_executed_for_this_audit",
            "railway_config_changed",
        ):
            with self.subTest(key=key):
                self.assertIs(s[key], False)


if __name__ == "__main__":
    unittest.main()
