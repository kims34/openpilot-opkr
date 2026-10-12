"""Synthetic-only bounded annual KRX OpenAPI orchestration tests."""
from __future__ import annotations

import unittest
import research_v1_krx_openapi_private_year_runner as y


class FakeBatch:
    def __init__(self, fail_at=None):
        self.calls=[]
        self.fail_at=fail_at
    def __call__(self, *,start,end,max_requests,execute,session):
        self.calls.append((start,end,max_requests,execute))
        if self.fail_at is not None and len(self.calls)==self.fail_at:
            return {"status":"FAIL_CLOSED_NO_PROFIT_AUTHORITY",
                    "failure_reason":"SOURCE_SECURITY_MASTER_UNMAPPED",
                    "attempted_requests":5}
        return {
            "status":"PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED",
            "attempted_requests":y.len_nonexistent if False else
                len(y._calendar(start,end,y.PER_WINDOW_MAX_REQUESTS))*2,
            "new_completed_date_pairs":len(y._calendar(start,end,y.PER_WINDOW_MAX_REQUESTS)),
            "previous_verified_date_pairs_skipped":0,
            "new_stored_raw_objects":len(y._calendar(start,end,y.PER_WINDOW_MAX_REQUESTS))*2,
            "batch_sampled_ohlc_zero_activity_rows":0,
            "m20_performance_testing_authorized":False,
            "live_orders_authorized":False,
        }


class AnnualPrivateHistoryTests(unittest.TestCase):
    def test_single_year_2015_is_bounded_and_partitioned_without_overlap(self):
        windows=y.split_annual_windows("2015-01-01","2015-12-31")
        self.assertLessEqual(len(windows),20)
        self.assertLessEqual(sum(w[2] for w in windows),650)
        self.assertEqual(windows[0][0],"2015-01-01")
        self.assertEqual(windows[-1][1],"2015-12-31")
        for i,(start,end,quota) in enumerate(windows):
            self.assertLessEqual(quota,60)
            self.assertLessEqual((y.date.fromisoformat(end)-y.date.fromisoformat(start)).days,27)
            if i:
                self.assertEqual(
                    y.date.fromisoformat(start),
                    y.date.fromisoformat(windows[i-1][1])+y.timedelta(days=1),
                )
    def test_2015_reminder_dry_run_never_invokes_network_child(self):
        spy=FakeBatch()
        out=y.execute_annual_stage(start="2015-02-02",end="2015-12-31",
                                   execute=False,batch_runner=spy)
        self.assertEqual(out["status"],"DRY_RUN_NO_NETWORK")
        self.assertEqual(spy.calls,[])
        self.assertGreater(out["planned_max_api_requests"],0)
        self.assertFalse(out["live_orders_authorized"])
        self.assertFalse(out["m20_performance_testing_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
    def test_bounded_year_executor_handles_all_partitions_without_extra_calls(self):
        spy=FakeBatch()
        out=y.execute_annual_stage(start="2015-02-02",end="2015-12-31",
                                   execute=True,batch_runner=spy,session=object())
        self.assertEqual(out["status"],"PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED")
        self.assertEqual(len(spy.calls),out["planned_windows"])
        self.assertLessEqual(out["actual_api_requests"],650)
        self.assertEqual(out["new_completed_date_pairs"],out["actual_api_requests"]//2)
        self.assertFalse(out["historical_publication_pit_verified"])
        self.assertFalse(out["source_admitted"])
        self.assertFalse(out["independent_holdout_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")
    def test_an_unverified_partial_chunk_halts_future_requests(self):
        spy=FakeBatch(fail_at=3)
        out=y.execute_annual_stage(start="2015-02-02",end="2015-12-31",
                                   execute=True,batch_runner=spy,session=object())
        self.assertEqual(out["status"],"FAIL_CLOSED_SOURCE_OR_STORAGE_GAP")
        self.assertEqual(len(spy.calls),3)
        self.assertEqual(out["completed_windows"],2)
        self.assertEqual(out["failure_reason_code"],"SOURCE_SECURITY_MASTER_UNMAPPED")
        self.assertFalse(out["m20_performance_testing_authorized"])
    def test_years_cannot_be_joined_into_unbounded_history_job(self):
        for lo,hi in (
            ("2015-01-01","2016-01-01"),
            ("2014-12-31","2015-01-01"),
            ("2026-10-12","2026-10-13"),
            ("2017-02-01","2017-01-31"),
            ("2010-01-01","2010-12-31"),
        ):
            with self.subTest(start=lo):
                with self.assertRaises(y.AnnualHistoryScopeError):
                    y.split_annual_windows(lo,hi)
    def test_2016_leap_and_2026_partial_year_within_approved_scope(self):
        for lo,hi in (
            ("2016-01-01","2016-12-31"),
            ("2026-01-01","2026-10-12"),
        ):
            with self.subTest(start=lo):
                chunks=y.split_annual_windows(lo,hi)
                self.assertGreater(len(chunks),1)
                self.assertLessEqual(sum(x[2] for x in chunks),650)
    def test_no_trade_or_pit_authority_even_if_children_completed(self):
        result=y.execute_annual_stage(start="2015-02-02",end="2015-02-27",
                                      execute=True,batch_runner=FakeBatch(),session=object())
        self.assertEqual(result["status"],"PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED")
        for field in ("source_admitted","historical_publication_pit_verified",
                      "historical_security_status_verified","corporate_actions_verified",
                      "krx_cost_return_path_verified","m20_performance_testing_authorized",
                      "independent_holdout_authorized","champion_change_authorized",
                      "live_orders_authorized","funds_movement_authorized",
                      "permissions_change_authorized"):
            self.assertIs(result[field],False,field)

if __name__=="__main__":
    unittest.main()
