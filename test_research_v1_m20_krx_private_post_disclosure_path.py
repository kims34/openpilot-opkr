"""Offline KRX KOSPI retained-original price-path source reachability tests."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import research_v1_m20_krx_private_post_disclosure_path as m

ENV={
    "RAILWAY_SERVICE_NAME":m.WORKER,
    "KRX_PRIVATE_RAW_DIR":"/data/synthetic_private_volume",
}


def valid(day,*,share=1000):
    return {"kind":"VALID_PRICE_MCAP_OBSERVATION","shares_private":Decimal(share)}


class ReadOnlyPathGateTests(unittest.TestCase):
    def test_fixed_pinned_initial_filing_dates_are_not_changed(self):
        self.assertEqual(m.ORIGINAL_Q3_DATES,(
            ("2024Q3",date(2024,11,14)),
            ("2025Q3",date(2025,11,14)),
        ))
        self.assertEqual(m.FIXED_CODE,"005930")
        for _,filed in m.ORIGINAL_Q3_DATES:
            days=m._weekdays_after_filing(filed)
            self.assertTrue(days[0]>filed)
            self.assertTrue(all(day.weekday()<5 for day in days))
            self.assertGreaterEqual(len(days),40)
    def test_unauthorized_dynamic_disclosure_dates_not_accepted(self):
        with self.assertRaisesRegex(m.SourcePathError,"UNAPPROVED_FILING_DATE_SCOPE"):
            m._weekdays_after_filing(date(2025,11,13))
    def test_good_ordinary_price_path_still_does_not_admit_any_source(self):
        for _,filed in m.ORIGINAL_Q3_DATES:
            out=m._evaluate_period(filed,reader=valid)
            self.assertGreaterEqual(out["valid_observed_price_mcap_days"],40)
            self.assertTrue(out["first_post_filing_positive_mcap_candidate_observed"])
            self.assertTrue(out["has_at_least_21_tentative_market_price_observations"])
            self.assertTrue(out["tentative_price_source_path_without_known_target_anomalies"])
            self.assertFalse(out["observed_share_quantity_changed"])
            self.assertNotIn("shares_private",out)
            self.assertNotIn("005930",json.dumps(out))
            self.assertNotIn("1000",json.dumps(out))
    def test_blank_source_date_never_assumed_exchange_holiday(self):
        start=m.ORIGINAL_Q3_DATES[0][1]
        first=m._weekdays_after_filing(start)[0]
        def reader(day):
            return {"kind":"DAILY_EMPTY_CALENDAR_UNVERIFIED"} if day==first else valid(day)
        out=m._evaluate_period(start,reader=reader)
        self.assertEqual(out["calendar_source_empty_not_holiday_verified"],1)
        self.assertFalse(out["observed_share_quantity_changed"])
        self.assertNotIn("official_holiday_verified",out)
    def test_missing_symbol_source_never_backfilled_from_rank4_or_others(self):
        start=m.ORIGINAL_Q3_DATES[0][1]
        first=m._weekdays_after_filing(start)[0]
        def reader(day):
            return {"kind":"TARGET_IDENTITY_ABSENT_OR_NOT_UNIQUE"} if day==first else valid(day)
        out=m._evaluate_period(start,reader=reader)
        self.assertEqual(out["target_missing_or_ambiguous_market_days"],1)
        self.assertFalse(out["tentative_price_source_path_without_known_target_anomalies"])
    def test_zero_volume_or_mcap_rows_invalidate_source_path(self):
        start=m.ORIGINAL_Q3_DATES[1][1]
        first=m._weekdays_after_filing(start)[2]
        def reader(day):
            return {"kind":"TARGET_OHLC_OR_MCAP_PATH_INVALID"} if day==first else valid(day)
        out=m._evaluate_period(start,reader=reader)
        self.assertEqual(out["target_invalid_price_mcap_days"],1)
        self.assertFalse(out["tentative_price_source_path_without_known_target_anomalies"])
    def test_share_quantity_change_flags_corporate_action_unknown(self):
        start=m.ORIGINAL_Q3_DATES[1][1]
        days=m._weekdays_after_filing(start)
        first=days[5]
        def reader(day):
            return valid(day,share=2000 if day>first else 1000)
        out=m._evaluate_period(start,reader=reader)
        self.assertTrue(out["observed_share_quantity_changed"])
        self.assertFalse(out["tentative_price_source_path_without_known_target_anomalies"])
    def test_unrecognized_source_kind_fail_closed(self):
        with self.assertRaisesRegex(m.SourcePathError,"UNKNOWN_PRIVATE_OBSERVATION_CLASS"):
            m._evaluate_period(m.ORIGINAL_Q3_DATES[0][1],
                               reader=lambda day:{"kind":"FUTURE_PIT_PROFIT"})
    def test_bad_share_context_fail_closed(self):
        with self.assertRaisesRegex(m.SourcePathError,"PRIVATE_SHARE_CONTEXT_INVALID"):
            m._evaluate_period(m.ORIGINAL_Q3_DATES[1][1],
                               reader=lambda day:{
                                   "kind":"VALID_PRICE_MCAP_OBSERVATION",
                                   "shares_private":-1,
                               })
    def test_default_run_zero_network_and_storage_access(self):
        def bad(*args):
            raise RuntimeError("not expected")
        out=m.run(reader=bad,env=ENV)
        self.assertEqual(out["source_status"],"DRY_RUN_NO_STORAGE_OR_NETWORK")
        self.assertEqual(out["private_source_pairs_examined"],0)
        self.assertFalse(out["m20_performance_run_authorized"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
    def test_wrong_dedicated_service_or_mount_is_blocked(self):
        def bad(*args):
            raise RuntimeError("should not read")
        for env,status in (({}, "FAIL_CLOSED_WRONG_SERVICE"),
                           ({"RAILWAY_SERVICE_NAME":m.WORKER,
                             "KRX_PRIVATE_RAW_DIR":"/tmp/public"},
                            "FAIL_CLOSED_NO_PERSISTENT_PRIVATE_ROOT")):
            out=m.run(execute=True,env=env,reader=bad)
            self.assertEqual(out["source_status"],status)
            self.assertFalse(out["real_orders_authorized"])
    def test_synthetic_dual_report_actual_study_reports_only_counts(self):
        with patch.object(m,"_trusted_private_root",return_value=Path("/data/fixture")):
            out=m.run(execute=True,env=ENV,
                      reader=lambda root,day:valid(day))
        self.assertEqual(out["source_status"],
                         "PRIVATE_KRX_MCAP_PRICE_REACHABILITY_NOT_TRADABLE_NOT_PIT")
        self.assertEqual(len(out["stage_results"]),2)
        self.assertGreater(out["private_source_pairs_examined"],80)
        self.assertTrue(all(row["tentative_price_source_path_without_known_target_anomalies"]
                            for row in out["stage_results"]))
        for field in ("original_disclosure_pubtime_pit_verified",
                      "historical_security_master_pit_verified",
                      "official_security_status_halt_delist_verified",
                      "corporate_actions_and_true_fill_economics_verified",
                      "usable_entry_exit_price_path_source_admitted",
                      "m20_signal_pit_admitted","m20_performance_run_authorized",
                      "independent_holdout_authorized","champion_change_authorized",
                      "real_orders_authorized","funds_movement_authorized",
                      "permissions_change_authorized",
                      "raw_security_rows_or_earnings_saved",
                      "network_requests_made","private_storage_mutated"):
            self.assertIs(out[field],False,field)
        packed=json.dumps(out)
        for private in ("005930","1000","100000","MKTCAP","TDD_CLSPRC"):
            self.assertNotIn(private,packed)
    def test_private_source_reader_error_is_redacted(self):
        def bad(root,day):
            raise ValueError("SENSITIVE_ISSUER_PRICE=987654321")
        with patch.object(m,"_trusted_private_root",return_value=Path("/data/fixture")):
            out=m.run(execute=True,env=ENV,reader=bad)
        self.assertEqual(out["source_status"],"FAIL_CLOSED_PRIVATE_PRICE_PATH_GAP")
        self.assertFalse(out["m20_signal_pit_admitted"])
        self.assertNotIn("987654321",json.dumps(out))


if __name__=="__main__":
    unittest.main()
