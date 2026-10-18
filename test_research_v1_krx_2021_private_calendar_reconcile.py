"""Offline synthetic-only checks for exact 2021 calendar date-set logic."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_krx_2021_private_calendar_reconcile as m

DAYS = m._bounds("2021-01-01", "2021-12-31")
DIGESTS = [{"day": d, "pair_sha256": hashlib.sha256(d.encode()).hexdigest()} for d in DAYS]
PANEL = hashlib.sha256(json.dumps(DIGESTS, sort_keys=True, separators=(",",":")).encode()).hexdigest()
ENV = {"RAILWAY_SERVICE_NAME": m.WORKER, "KRX_PRIVATE_RAW_DIR": "/data"}


def check_calendar(empty):
    def one(root, day):
        blank = day in empty
        return {"day": day, "pair_sha256": hashlib.sha256(day.encode()).hexdigest(),
                "daily_rows": 0 if blank else 5,
                "source_day_class": (
                    "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
                    if blank else "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED")}
    with (patch.object(m, "_trusted_private_root", return_value=Path("/data/mock")),
          patch.object(m, "_check_one", side_effect=one),
          patch.object(m, "EXISTING_2021_PANEL_SHA256", PANEL)):
        return m.review_private_2021(execute=True, environment=ENV)


class ExactCalendarTests(unittest.TestCase):
    def test_13_exact_matches_are_not_pit(self):
        x = check_calendar(m.OFFICIAL_FINAL_2021)
        self.assertEqual(x["status"], "PRIVATE_2021_DATE_SET_SHAPE_MATCH_NOT_PIT")
        self.assertEqual(x["original_pairs_reverified"], 261)
        self.assertEqual(x["empty_daily_original_pairs_total"], 13)
        self.assertFalse(x["private_2021_original_date_set_independently_reconciled"])
        self.assertFalse(x["live_orders_authorized"])

    def test_13_count_but_swapped_date_is_not_a_match(self):
        x = check_calendar((m.OFFICIAL_FINAL_2021 - {"20210816"}) | {"20210817"})
        self.assertEqual(x["empty_daily_original_pairs_total"], 13)
        self.assertEqual(x["empty_daily_original_pairs_on_other_weekdays"], 1)
        self.assertEqual(x["expected_holidays_with_nonempty_daily_rows"], 1)
        self.assertEqual(x["status"], "PRIVATE_2021_DATE_SET_DISCREPANCY_NOT_PIT")

    def test_fourteenth_blank_day_is_a_data_gap(self):
        x = check_calendar(m.OFFICIAL_FINAL_2021 | {"20210817"})
        self.assertEqual(x["empty_daily_original_pairs_on_other_weekdays"], 1)
        self.assertFalse(x["m20_performance_run_authorized"])

    def test_dry_run_does_not_read_storage(self):
        with patch.object(m, "_check_one") as f:
            x = m.review_private_2021()
        f.assert_not_called()
        self.assertEqual(x["status"], "DRY_RUN_PRIVATE_ORIGINAL_NOT_READ")

    def test_wrong_worker_fails_closed(self):
        with patch.object(m, "_check_one") as f:
            x = m.review_private_2021(execute=True, environment={
                "RAILWAY_SERVICE_NAME": "synthetic",
                "KRX_PRIVATE_RAW_DIR": "/data"})
        f.assert_not_called()
        self.assertEqual(x["status"], "FAIL_CLOSED_NOT_DEDICATED_KRX_WORKER")

    def test_sha_drift_fails_closed(self):
        with (patch.object(m, "_trusted_private_root", return_value=Path("/data/mock")),
              patch.object(m, "_check_one", side_effect=lambda root, day: {
                  "day": day, "pair_sha256": hashlib.sha256(day.encode()).hexdigest(),
                  "daily_rows": 0, "source_day_class":
                  "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"}),
              patch.object(m, "EXISTING_2021_PANEL_SHA256", "0"*64)):
            x = m.review_private_2021(execute=True, environment=ENV)
        self.assertEqual(x["status"], "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED")


    def test_unexpected_private_store_exceptions_cannot_escape_with_source_details(self):
        # Private read/store libraries can fail with KeyError, RuntimeError
        # or AttributeError outside the known integrity exception families.
        for problem in (
            KeyError("PRIVATE_2021_SECURITY_IDENTIFIERS"),
            RuntimeError("PRIVATE_2021_SECRET_20210816"),
            AttributeError("PRIVATE_2021_SOURCE_PATH"),
        ):
            with self.subTest(error=type(problem).__name__):
                with (patch.object(m, "_trusted_private_root",
                                   return_value=Path("/data/mock")),
                      patch.object(m, "_check_one", side_effect=problem)):
                    x = m.review_private_2021(execute=True, environment=ENV)
                self.assertEqual(x["status"],
                                 "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED")
                self.assertNotIn("PRIVATE_2021_SECRET", str(x))
                self.assertNotIn("PRIVATE_2021_SECURITY", str(x))
                self.assertNotIn("PRIVATE_2021_SOURCE_PATH", str(x))
                self.assertEqual(x["original_pairs_reverified"], 0)
                self.assertFalse(x["original_panel_sha256_matches_prior_audit"])
                self.assertFalse(x["private_2021_original_date_set_independently_reconciled"])
                self.assertFalse(x["real_orders_authorized"])
                self.assertFalse(x["network_request_attempted"])
                self.assertEqual(x["ordering"], "DISABLED")

    def test_unexpected_private_root_validation_error_is_redacted(self):
        with (patch.object(m, "_trusted_private_root",
                           side_effect=RuntimeError("PRIVATE_PATH_LEAK")),
              patch.object(m, "_check_one") as check):
            x = m.review_private_2021(execute=True, environment=ENV)
        check.assert_not_called()
        self.assertEqual(x["status"], "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED")
        self.assertNotIn("PRIVATE_PATH_LEAK", str(x))
        self.assertFalse(x["m20_performance_run_authorized"])


if __name__ == "__main__":
    unittest.main()
