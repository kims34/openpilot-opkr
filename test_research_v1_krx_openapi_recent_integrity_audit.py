"""Synthetic-only KRX 2023-2026 offline source integrity composition tests."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

import research_v1_krx_openapi_recent_integrity_audit as auditmod

VALID_ENV={
    "RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
    "KRX_PRIVATE_RAW_DIR":"/data/private-historical-kospi",
}


class FakeAudit:
    def __init__(self, fail_year=None, missing_year=None, drift_year=None):
        self.calls=[]
        self.fail_year=fail_year
        self.missing_year=missing_year
        self.drift_year=drift_year
    def __call__(self, *,root,start,end):
        self.calls.append((str(root),start,end))
        year=int(start[:4])
        n=len(auditmod._bounds(start,end))
        result={
            "status":"ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED",
            "verified_date_pairs":n,
            "missing_weekday_pair_count":0,
            "invalid_pair_count":0,
            "empty_daily_unverified_calendar_or_source_gap_days":12,
            "sampled_ohlc_zero_activity_rows":1200,
            "sampled_other_invalid_price_rows":2,
            "network_request_attempted":False,
            "storage_mutated":False,
            "source_admitted":False,
            "real_orders_authorized":False,
            "snapshot_fingerprint_sha256":"a"*64,
        }
        if year==self.fail_year:
            result["status"]="FAIL_CLOSED_PRIVATE_SOURCE_INTEGRITY_ERROR"
            result["invalid_pair_count"]=1
        if year==self.missing_year:
            result["status"]="INCOMPLETE_WEEKDAY_COVERAGE_NOT_PIT_ADMITTED"
            result["missing_weekday_pair_count"]=1
            result["verified_date_pairs"]=n-1
        if year==self.drift_year:
            result["real_orders_authorized"]=True
        return result


class RecentIntegrityContractTest(unittest.TestCase):
    def test_fixed_years_and_completed_2026_end_only(self):
        plan=auditmod.plan_years()
        self.assertEqual([z["start"][:4] for z in plan],
                         ["2023","2024","2025","2026"])
        self.assertEqual(plan[-1]["end"],"2026-10-08")
        self.assertGreater(sum(z["expected_weekdays"] for z in plan),700)
    def test_default_is_no_storage_access(self):
        spy=FakeAudit()
        out=auditmod.audit_all_recent(audit=spy)
        self.assertEqual(out["status"],"DRY_RUN_NO_STORAGE_ACCESS")
        self.assertEqual(spy.calls,[])
        self.assertFalse(out["real_orders_authorized"])
        self.assertFalse(out["m20_performance_testing_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
    def test_no_private_worker_is_hard_block(self):
        spy=FakeAudit()
        out=auditmod.audit_all_recent(execute=True,environment={},audit=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_NOT_DEDICATED_PRIVATE_WORKER")
        self.assertEqual(spy.calls,[])
    def test_no_private_mount_is_hard_block(self):
        spy=FakeAudit()
        env={**VALID_ENV,"KRX_PRIVATE_RAW_DIR":"/tmp/not-private"}
        out=auditmod.audit_all_recent(execute=True,environment=env,audit=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_MISSING_PRIVATE_VOLUME_ROOT")
        self.assertEqual(spy.calls,[])
    def test_all_years_full_integrity_is_not_pit_or_trade_permission(self):
        spy=FakeAudit()
        receipts=[]
        out=auditmod.audit_all_recent(
            execute=True,environment=VALID_ENV,audit=spy,report_year=receipts.append)
        self.assertEqual(out["status"],"PRIVATE_RECENT_YEARS_INTEGRITY_VERIFIED_NOT_PIT")
        self.assertEqual(out["completed_years"],[2023,2024,2025,2026])
        self.assertEqual(len(spy.calls),4)
        self.assertEqual(out["verified_weekday_pairs"],out["expected_weekday_pairs"])
        self.assertEqual(out["unverified_exchange_calendar_or_source_gap_days"],48)
        self.assertEqual(out["sampled_other_invalid_ohlc_rows"],8)
        self.assertEqual(len(out["combined_aggregate_fingerprint_sha256"]),64)
        self.assertEqual(len(receipts),4)
        self.assertTrue(all(v["historical_pit_source_admitted"] is False for v in receipts))
        for field in ("raw_security_rows_emitted","storage_mutated","network_request_attempted",
                      "historical_publication_pit_verified","official_trading_status_verified",
                      "corporate_action_paths_verified","full_universe_source_admitted",
                      "m20_performance_testing_authorized","independent_holdout_authorized",
                      "champion_change_authorized","live_orders_authorized",
                      "funds_movement_authorized","permissions_change_authorized"):
            self.assertIs(out[field],False,field)
        self.assertEqual(out["ordering"],"DISABLED")
        for blocked in ("005930","ISU_CD","10000","KRX_AUTH_KEY","PASSWORD"):
            self.assertNotIn(blocked,json.dumps(out))
    def test_any_missing_or_invalid_annual_date_stops_before_next_year(self):
        for mode in ("fail","missing"):
            spy=FakeAudit(**{"fail_year" if mode=="fail" else "missing_year":2024})
            out=auditmod.audit_all_recent(execute=True,environment=VALID_ENV,audit=spy)
            self.assertEqual(out["status"],"FAIL_CLOSED_MISSING_OR_INVALID_PRIVATE_SOURCE")
            self.assertEqual(out["failed_year"],2024)
            self.assertEqual(out["completed_years"],[2023])
            self.assertEqual(len(spy.calls),2)
            self.assertFalse(out["real_orders_authorized"])
    def test_any_attempted_real_order_flag_stops(self):
        spy=FakeAudit(drift_year=2023)
        out=auditmod.audit_all_recent(execute=True,environment=VALID_ENV,audit=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_MISSING_OR_INVALID_PRIVATE_SOURCE")
        self.assertEqual(out["completed_years"],[])
        self.assertEqual(len(spy.calls),1)
        self.assertFalse(out["live_orders_authorized"])
    def test_observations_outside_mounted_private_root_are_never_requested(self):
        spy=FakeAudit()
        auditmod.audit_all_recent(execute=True,environment=VALID_ENV,audit=spy)
        for dirname,start,end in spy.calls:
            self.assertTrue(dirname.startswith("/data/private-historical-kospi/"))
            self.assertTrue(start[:4] in ("2023","2024","2025","2026"))
            self.assertNotEqual(end,"2026-10-12")
    def test_unhandled_child_error_fail_closes(self):
        def broken(**kwargs):
            raise RuntimeError("contains potentially sensitive data: TEST_SYMBOL_000001")
        out=auditmod.audit_all_recent(execute=True,environment=VALID_ENV,audit=broken)
        self.assertEqual(out["status"],"FAIL_CLOSED_PRIVATE_AUDIT_UNHANDLED")
        self.assertNotIn("TEST_SYMBOL_000001",json.dumps(out))
        self.assertFalse(out["m20_performance_testing_authorized"])

if __name__=="__main__":
    unittest.main()
