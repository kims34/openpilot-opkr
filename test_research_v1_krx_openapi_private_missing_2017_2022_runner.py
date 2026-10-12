"""Zero-network synthetic tests of 2017-2022 private official KOSPI capture."""
from __future__ import annotations

import json
import unittest

import research_v1_krx_openapi_private_missing_2017_2022_runner as gap
from research_v1_krx_openapi_private_history_batch import AUTHORITY


class SyntheticAnnual:
    def __init__(self,*,fail_year=None,drift_year=None,overrun_year=None):
        self.calls=[]
        self.fail_year=fail_year
        self.drift_year=drift_year
        self.overrun_year=overrun_year
    def __call__(self,*,start,end,execute):
        self.calls.append((start,end,execute))
        year=int(start[:4])
        allowed=sum(x[2] for x in gap.split_annual_windows(start,end))
        result={
            "status":"PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED",
            "actual_api_requests":allowed,
            "new_completed_date_pairs":allowed//2,
            "already_verified_pairs_skipped":0,
            "new_raw_content_objects":allowed,
            "unverified_empty_daily_date_pairs":13,
            **AUTHORITY,
        }
        if year==self.fail_year:
            result["status"]="FAIL_CLOSED_SOURCE_OR_STORAGE_GAP"
            result["failure_reason_code"]="SYNTHETIC_SOURCE_MISSING"
        if year==self.drift_year:
            result["live_orders_authorized"]=True
        if year==self.overrun_year:
            result["actual_api_requests"]=allowed+1
        return result


class KRXMissingSourceTests(unittest.TestCase):
    def test_fixed_year_ranges_strictly_2017_to_2022(self):
        self.assertEqual(len(gap.PINNED_YEAR_RANGES),6)
        self.assertEqual(gap.PINNED_YEAR_RANGES[0],("2017-01-01","2017-12-31"))
        self.assertEqual(gap.PINNED_YEAR_RANGES[-1],("2022-01-01","2022-12-31"))
        plan=gap.plan_missing_years()
        self.assertEqual([x["start"][:4] for x in plan],
                         ["2017","2018","2019","2020","2021","2022"])
        self.assertGreater(sum(x["max_requests"] for x in plan),3000)
        self.assertLessEqual(sum(x["max_requests"] for x in plan),3300)
        self.assertTrue(all(0<x["max_requests"]<=650 for x in plan))
    def test_dry_run_does_not_attempt_network_or_private_writes(self):
        spy=SyntheticAnnual()
        out=gap.execute_missing_years(year_runner=spy)
        self.assertEqual(out["status"],"DRY_RUN_NO_NETWORK")
        self.assertEqual(spy.calls,[])
        self.assertEqual(out["actual_api_requests"],0)
        self.assertFalse(out["live_orders_authorized"])
        self.assertFalse(out["m20_performance_testing_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
    def test_staged_six_year_completion_is_only_unadmitted_source(self):
        spy=SyntheticAnnual()
        progress=[]
        out=gap.execute_missing_years(execute=True,year_runner=spy,
                                      progress=progress.append)
        self.assertEqual(out["status"],gap.SUCCESS)
        self.assertEqual(out["completed_years"],[2017,2018,2019,2020,2021,2022])
        self.assertEqual(len(spy.calls),6)
        self.assertEqual(len(progress),6)
        self.assertEqual(out["actual_api_requests"],out["planned_max_api_requests"])
        self.assertEqual(out["completed_date_pairs_new"],
                         out["actual_api_requests"]//2)
        self.assertEqual(out["calendar_or_source_gap_days_unverified"],78)
        self.assertEqual(out["new_raw_source_objects_private_only"],
                         out["actual_api_requests"])
        self.assertFalse(out["source_admitted"])
        self.assertFalse(out["historical_publication_pit_verified"])
        self.assertFalse(out["independent_holdout_authorized"])
        self.assertFalse(out["funds_movement_authorized"])
        self.assertFalse(out["live_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
        logged=json.dumps(out)
        for secret in ("005930","ISU_CD","AUTH_KEY","TDD_CLSPRC","1000000","api.kiwoom.com"):
            self.assertNotIn(secret,logged)
    def test_failed_source_year_disallows_all_later_years(self):
        spy=SyntheticAnnual(fail_year=2019)
        out=gap.execute_missing_years(execute=True,year_runner=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_SOURCE_OR_PRIVATE_VOLUME_ERROR")
        self.assertEqual(out["completed_years"],[2017,2018])
        self.assertEqual(len(spy.calls),3)
        self.assertEqual(out["failed_year"],2019)
        self.assertFalse(out["live_orders_authorized"])
    def test_permission_drift_fails_before_following_year(self):
        spy=SyntheticAnnual(drift_year=2018)
        out=gap.execute_missing_years(execute=True,year_runner=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_CHILD_SCOPE_OR_PERMISSION_DRIFT")
        self.assertEqual(out["completed_years"],[2017])
        self.assertEqual(out["failed_year"],2018)
        self.assertEqual(len(spy.calls),2)
        self.assertFalse(out["live_orders_authorized"])
    def test_per_year_budget_exceedance_fails_before_next_year(self):
        spy=SyntheticAnnual(overrun_year=2018)
        out=gap.execute_missing_years(execute=True,year_runner=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_UNVERIFIED_SOURCE_REQUEST_COUNT")
        self.assertEqual(out["failed_year"],2018)
        self.assertEqual(out["completed_years"],[2017])
        self.assertEqual(len(spy.calls),2)
    def test_no_2026_same_day_or_unapproved_endpoints_requested(self):
        spy=SyntheticAnnual()
        gap.execute_missing_years(execute=True,year_runner=spy)
        self.assertEqual(spy.calls,[(a,b,True) for a,b in gap.PINNED_YEAR_RANGES])
        self.assertTrue(all(b<"2023-01-01" for _,b,_ in spy.calls))


if __name__=="__main__":
    unittest.main()
