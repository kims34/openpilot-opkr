"""Offline only, synthetic recent three-year KRX history orchestrator tests."""
import json
import unittest

import research_v1_krx_openapi_private_recent_runner as recent
from research_v1_krx_openapi_private_history_batch import AUTHORITY


class SyntheticYear:
    def __init__(self, stop_year=None, drift_year=None, exceed_year=None):
        self.calls=[]
        self.stop_year=stop_year
        self.drift_year=drift_year
        self.exceed_year=exceed_year
    def __call__(self, *,start,end,execute):
        self.calls.append((start,end,execute))
        year=int(start[:4])
        planned=sum(w[2] for w in recent.split_annual_windows(start,end))
        result={
            "status":"PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED",
            "actual_api_requests": planned,
            "already_verified_pairs_skipped":0,
            "new_completed_date_pairs":planned//2,
            "unverified_empty_daily_date_pairs":10,
            "new_raw_content_objects":planned,
            **AUTHORITY,
        }
        if year==self.stop_year:
            result["status"]="FAIL_CLOSED_SOURCE_OR_STORAGE_GAP"
            result["failure_reason_code"]="SOURCE_SECURITY_MASTER_UNMAPPED"
        if year==self.drift_year:
            result["live_orders_authorized"]=True
        if year==self.exceed_year:
            result["actual_api_requests"]=planned+1
        return result


class RecentStageTests(unittest.TestCase):
    def test_exact_user_scope_pin_2024_2025_2026_before_current_day(self):
        plan=recent.fixed_recent_plan()
        self.assertEqual([(z["start"],z["end"]) for z in plan],list(recent.PINNED_YEARS))
        self.assertEqual(plan[-1]["end"],"2026-10-08")
        self.assertLessEqual(sum(z["planned_max_requests"] for z in plan),1600)
        for z in plan:
            self.assertGreater(z["planned_max_requests"],0)
            self.assertLessEqual(z["planned_max_requests"],650)
    def test_default_dry_run_never_calls_a_year_or_network(self):
        spy=SyntheticYear()
        out=recent.execute_recent(year_runner=spy)
        self.assertEqual(out["status"],"DRY_RUN_NO_NETWORK")
        self.assertEqual(spy.calls,[])
        self.assertGreater(out["planned_max_api_requests"],1200)
        self.assertTrue(out["same_day_2026_10_12_not_requested"])
        self.assertEqual(out["ordering"],"DISABLED")
        self.assertFalse(out["m20_performance_testing_authorized"])
    def test_all_three_years_success_but_not_admitted(self):
        spy=SyntheticYear()
        progress=[]
        out=recent.execute_recent(execute=True,year_runner=spy,send_progress=progress.append)
        self.assertEqual(out["status"],
                         "PRIVATE_RECENT_THREE_YEAR_SOURCE_CAPTURE_COMPLETE_NOT_PIT_ADMITTED")
        self.assertEqual(out["completed_years"],[2024,2025,2026])
        self.assertEqual(len(spy.calls),3)
        self.assertEqual(len(progress),3)
        self.assertEqual(out["actual_api_requests"],out["planned_max_api_requests"])
        self.assertEqual(out["empty_daily_unverified_calendar_or_source_gap_days"],30)
        self.assertEqual(out["new_completed_date_pairs"],out["actual_api_requests"]//2)
        self.assertTrue(all(p["real_orders_authorized"] is False for p in progress))
        self.assertFalse(out["source_admitted"])
        self.assertFalse(out["historical_publication_pit_verified"])
        self.assertFalse(out["m20_performance_testing_authorized"])
        self.assertFalse(out["live_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
        self.assertNotIn("ISU_CD",json.dumps(out))
        self.assertNotIn("KRX_AUTH_KEY",json.dumps(out))
    def test_source_failure_stops_future_years(self):
        spy=SyntheticYear(stop_year=2025)
        out=recent.execute_recent(execute=True,year_runner=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_SOURCE_OR_PRIVATE_STORAGE_GAP")
        self.assertEqual(out["completed_years"],[2024])
        self.assertEqual(len(spy.calls),2)
        self.assertEqual(out["failure_year"],2025)
        self.assertEqual(out["failure_reason_code"],"SOURCE_SECURITY_MASTER_UNMAPPED")
        self.assertFalse(out["m20_performance_testing_authorized"])
    def test_cannot_reuse_child_false_live_safety_as_approval(self):
        spy=SyntheticYear(drift_year=2024)
        out=recent.execute_recent(execute=True,year_runner=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_CHILD_AUTHORITY_DRIFT")
        self.assertEqual(len(spy.calls),1)
        self.assertFalse(out["live_orders_authorized"])
    def test_request_budget_violation_fails_before_next_year(self):
        spy=SyntheticYear(exceed_year=2025)
        out=recent.execute_recent(execute=True,year_runner=spy)
        self.assertEqual(out["status"],"FAIL_CLOSED_UNVERIFIABLE_REQUEST_COUNTS")
        self.assertEqual(out["completed_years"],[2024])
        self.assertEqual(len(spy.calls),2)
        self.assertFalse(out["funds_movement_authorized"])
    def test_never_print_security_ids_or_amounts_even_in_progress(self):
        spy=SyntheticYear()
        progress=[]
        recent.execute_recent(execute=True,year_runner=spy,send_progress=progress.append)
        packed=json.dumps(progress)
        for private in ("005930","12345.6","TDD_CLSPRC","AUTH_KEY","ISU_SRT_CD"):
            self.assertNotIn(private,packed)
    def test_only_pinned_approved_dates_and_year_order(self):
        spy=SyntheticYear()
        recent.execute_recent(execute=True,year_runner=spy)
        self.assertEqual(spy.calls,[(s,e,True) for s,e in recent.PINNED_YEARS])
        self.assertTrue(all(not str(e).endswith("10-12") for s,e,_ in spy.calls))

if __name__=="__main__":
    unittest.main()
