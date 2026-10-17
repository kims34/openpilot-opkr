"""Offline deterministic tests of annual 2015-2026 candidate closures."""
import json
import unittest
from pathlib import Path
from research_v1_krx_calendar_count_triage import check_aggregate_calendar_candidate

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence/krx/2026-10-14-krx-calendar-count-candidates.json"
CORE = ROOT / "evidence/krx/2026-10-13-krx-market-source-pit-boundaries.json"


class CalendarCountTriage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.core = json.loads(CORE.read_text(encoding="utf-8"))
        cls.observed = {
            i["year"]: i["unverified_exchange_calendar_or_source_gap_days"]
            for i in cls.core["offline_verification"]["per_year"]
        }
        cls.secondary = {int(k): v for k, v in cls.e["secondary_xkrx_weekday_closure_counts"].items()}
        cls.exceptions = cls.e["2026_secondary_calendar_known_missing_officially_announced_closure_candidates"]

    def test_baseline_counts_exactly_match_stored_railway_yearly_receipts(self):
        self.assertEqual(sum(self.observed.values()), 184)
        self.assertEqual(self.observed[2026], 14)
        self.assertEqual(self.core["offline_verification"]["unverified_exchange_calendar_or_source_gap_days"], 184)

    def test_2015_to_2025_count_agreement_is_only_an_aggregate_hint(self):
        x = check_aggregate_calendar_candidate(self.observed, self.secondary, self.exceptions)
        self.assertEqual(x["exact_secondary_match_years"], list(range(2015, 2026)))
        self.assertEqual(x["annual_mismatch_years_before_exceptions"], [2026])
        self.assertEqual(x["secondary_closed_day_total"], 182)
        self.assertEqual(x["observed_unverified_gap_day_total"], 184)
        self.assertEqual(x["exception_count"], 2)
        self.assertEqual(x["annual_mismatch_years_after_exceptions"], [])
        self.assertEqual(x["status"], "COUNT_EQUALITY_TRIAGE_ONLY_NOT_DATE_ATTESTED")
        self.assertFalse(x["date_level_original_krx_calendar_attested"])
        self.assertFalse(x["source_pairs_at_date_level_reconciled"])
        self.assertFalse(x["pit_admitted"])
        self.assertFalse(x["performance_authorized"])
        self.assertFalse(x["orders_authorized"])

    def test_secondary_source_and_announcements_do_not_grant_original_pit(self):
        self.assertEqual(self.e["secondary_calendar_name"], "exchange_calendars/XKRX")
        self.assertEqual(self.e["secondary_calendar_version"], "4.13.1")
        self.assertFalse(self.e["official_original_date_level_reconciliation_completed"])
        self.assertFalse(self.e["original_publication_timestamp_pit_verified"])
        self.assertEqual(self.core["status_and_pit"]["source_contract_gates_C_and_D"], "BLOCKED")

    def test_unexplained_count_mismatch_fails_closed(self):
        wrong = dict(self.secondary)
        wrong[2020] -= 1
        x = check_aggregate_calendar_candidate(self.observed, wrong, self.exceptions)
        self.assertEqual(x["annual_mismatch_years_after_exceptions"], [2020])
        self.assertEqual(x["status"], "AGGREGATE_DISCREPANCIES_REMAIN_PIT_BLOCKED")

    def test_no_duplicate_or_out_of_scope_exception(self):
        for bad in (
            self.exceptions + [self.exceptions[0]],
            ["2027-01-01"],
            ["2026-10-09"],
            ["2026-02-30"],
            ["2026-07-18"],
        ):
            with self.subTest(bad=bad):
                x = check_aggregate_calendar_candidate(self.observed, self.secondary, bad)
                self.assertEqual(x["status"], "INVALID_REFERENCE_FAIL_CLOSED")

    def test_count_match_must_not_accept_arbitrary_2026_weekdays_as_holidays(self):
        # Two bogus open weekdays could previously explain the +2 count
        # without any secondary announcement matching those dates.
        for fake in (
            ["2026-06-02", "2026-07-16"],
            ["2026-06-03", "2026-07-16"],
            ["2026-06-02", "2026-07-17"],
        ):
            with self.subTest(fake=fake):
                x=check_aggregate_calendar_candidate(
                    self.observed, self.secondary, fake)
                self.assertEqual(x["status"], "INVALID_REFERENCE_FAIL_CLOSED")
                self.assertFalse(x["date_level_original_krx_calendar_attested"])
                self.assertFalse(x["pit_admitted"])
                self.assertEqual(x["ordering"], "DISABLED")

    def test_subset_of_known_exception_dates_does_not_falsely_fix_difference(self):
        for part in ([], ["2026-06-03"], ["2026-07-17"]):
            with self.subTest(part=part):
                x=check_aggregate_calendar_candidate(
                    self.observed, self.secondary, part)
                self.assertEqual(
                    x["status"], "AGGREGATE_DISCREPANCIES_REMAIN_PIT_BLOCKED")
                self.assertEqual(x["annual_mismatch_years_after_exceptions"], [2026])
                self.assertFalse(x["performance_authorized"])

    def test_production_baseline_stays_quarantined(self):
        x = check_aggregate_calendar_candidate(self.observed, self.secondary, self.exceptions)
        self.assertFalse(x["security_tradability_verified"])
        self.assertFalse(x["27_problem_securities_released"])
        self.assertFalse(x["holdout_authorized"])
        self.assertEqual(x["ordering"], "DISABLED")
        self.assertEqual(self.core["status_and_pit"]["quarantined_issue_count"], 27)

    def test_untrusted_missing_years_or_boolean_counts_fail_closed(self):
        wrong = dict(self.secondary)
        wrong.pop(2015)
        self.assertEqual(check_aggregate_calendar_candidate(self.observed, wrong, self.exceptions)["status"], "INVALID_REFERENCE_FAIL_CLOSED")
        wrong = dict(self.secondary)
        wrong[2020] = True
        self.assertEqual(check_aggregate_calendar_candidate(self.observed, wrong, self.exceptions)["status"], "INVALID_REFERENCE_FAIL_CLOSED")


if __name__ == "__main__":
    unittest.main()
