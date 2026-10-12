"""Approved KOSPI official OPEN API private missing 2017–2022 source backfill.

Six COMPLETE calendar years, fixed before viewing results, between the
already independently SHA-audited 2015–2016 and 2023–2026 source ranges.
Only the two user-approved KRX KOSPI OpenAPI master/daily endpoints through
the existing per-year provider source collector; source bytes stored ONLY
inside dedicated Railway /data private volume, never GitHub/logs.

NO PIT/market-status/delist/corporate-action proof, taxes, execution,
forecast/Net EV, WF, Holdout, Champion, broker/orders or funds actions.
Explicit --execute and existing exact per-window consent/key/service/
persistent-store preflight required. Dry-run (no KRX) by default.
Each partial/unsafe/year-error immediately terminates later years.
"""
from __future__ import annotations

import argparse
import json
from typing import Any,Callable

from research_v1_krx_openapi_private_year_runner import (
    execute_annual_stage,split_annual_windows,
)
from research_v1_krx_openapi_private_history_batch import AUTHORITY

PINNED_YEAR_RANGES=tuple(
    (f"{year}-01-01",f"{year}-12-31") for year in range(2017,2023)
)
REQUEST_BUDGET_TOTAL=3300
PER_YEAR_CAP=650
SUCCESS="PRIVATE_2017_2022_SIX_YEAR_SOURCE_CAPTURE_COMPLETE_NOT_PIT_ADMITTED"


class MissingHistoryScopeError(ValueError):
    pass


def plan_missing_years()->list[dict]:
    if len(PINNED_YEAR_RANGES)!=6 or PINNED_YEAR_RANGES[0][0]!="2017-01-01" or PINNED_YEAR_RANGES[-1][1]!="2022-12-31":
        raise MissingHistoryScopeError("FIXED_YEAR_COHORT_SCOPE_INVALID")
    planned=[]
    for start,end in PINNED_YEAR_RANGES:
        windows=split_annual_windows(start,end)
        requests=sum(x[2] for x in windows)
        if not windows or requests<=0 or requests>PER_YEAR_CAP:
            raise MissingHistoryScopeError("ANNUAL_SOURCE_REQUEST_BUDGET_EXCEEDED")
        planned.append({
            "start":start,"end":end,
            "bounded_windows":len(windows),
            "max_requests":requests,
        })
    if sum(x["max_requests"] for x in planned)>REQUEST_BUDGET_TOTAL:
        raise MissingHistoryScopeError("MULTI_YEAR_REQUEST_BUDGET_EXCEEDED")
    return planned


def execute_missing_years(*,execute:bool=False,
        year_runner:Callable[...,dict]=execute_annual_stage,
        progress:Callable[[dict],None]|None=None)->dict[str,Any]:
    report={
        "classification":"KRX_APPROVED_OPENAPI_PRIVATE_2017_2022_HISTORICAL_COLLECTION_NOT_PIT",
        "status":"DRY_RUN_NO_NETWORK",
        "fixed_years":[2017,2018,2019,2020,2021,2022],
        "planned_max_api_requests":0,
        "actual_api_requests":0,
        "year_count_completed":0,
        "completed_years":[],
        "completed_date_pairs_new":0,
        "already_verified_date_pairs_skipped":0,
        "new_raw_source_objects_private_only":0,
        "calendar_or_source_gap_days_unverified":0,
        "year_results":[],
        "provider_rows_security_ids_or_prices_in_report":False,
        "source_raw_bytes_only_under_private_mounted_volume":True,
        "official_market_halt_delist_status_verified":False,
        "corporate_action_costs_and_true_fill_returns_verified":False,
        **AUTHORITY,
    }
    try:
        plan=plan_missing_years()
        report["planned_max_api_requests"]=sum(item["max_requests"] for item in plan)
        if not execute:
            return report
        report["status"]="RUNNING_PRIVATE_SOURCE_CAPTURE_NOT_PIT"
        for item in plan:
            year=int(item["start"][:4])
            source=year_runner(start=item["start"],end=item["end"],execute=True)
            calls=source.get("actual_api_requests")
            if (type(calls) is not int or calls<0
                    or calls>item["max_requests"]
                    or report["actual_api_requests"]+calls>REQUEST_BUDGET_TOTAL):
                report["status"]="FAIL_CLOSED_UNVERIFIED_SOURCE_REQUEST_COUNT"
                report["failed_year"]=year
                break
            report["actual_api_requests"]+=calls
            if source.get("status")!="PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED":
                report["status"]="FAIL_CLOSED_SOURCE_OR_PRIVATE_VOLUME_ERROR"
                report["failed_year"]=year
                report["failure_reason_code"]=str(
                    source.get("failure_reason_code","YEAR_SOURCE_NOT_COMPLETE"))
                break
            if (source.get("source_admitted") is not False
                    or source.get("historical_publication_pit_verified") is not False
                    or source.get("m20_performance_testing_authorized") is not False
                    or source.get("independent_holdout_authorized") is not False
                    or source.get("live_orders_authorized") is not False
                    or source.get("funds_movement_authorized") is not False
                    or source.get("ordering")!="DISABLED"):
                report["status"]="FAIL_CLOSED_CHILD_SCOPE_OR_PERMISSION_DRIFT"
                report["failed_year"]=year
                break
            safe={
                "year":year,
                "status":"PRIVATE_RAW_SOURCE_CAPTURED_NOT_PIT",
                "official_api_requests":calls,
                "new_stored_weekday_pairs":int(source["new_completed_date_pairs"]),
                "verified_existing_pairs_skipped":int(source["already_verified_pairs_skipped"]),
                "new_sha_backed_private_raw_objects":int(source["new_raw_content_objects"]),
                "source_empty_days_not_holiday_verified":int(source["unverified_empty_daily_date_pairs"]),
                "original_pit_admitted":False,
                "trading_allowed":False,
            }
            report["year_results"].append(safe)
            report["completed_years"].append(year)
            report["year_count_completed"]+=1
            report["completed_date_pairs_new"]+=safe["new_stored_weekday_pairs"]
            report["already_verified_date_pairs_skipped"]+=safe["verified_existing_pairs_skipped"]
            report["new_raw_source_objects_private_only"]+=safe["new_sha_backed_private_raw_objects"]
            report["calendar_or_source_gap_days_unverified"]+=safe["source_empty_days_not_holiday_verified"]
            if progress is not None:
                progress(safe)
        else:
            report["status"]=SUCCESS
    except (MissingHistoryScopeError,ValueError,TypeError,KeyError):
        report["status"]="FAIL_CLOSED_RUNNER_EXCEPTION"
        report["failure_reason_code"]="INVALID_BACKFILL_STAGE"
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--execute",action="store_true")
    args=parser.parse_args()
    def safe_year_event(row):
        print("INDEXALERT_KRX_PRIVATE_MISSING_2017_2022_YEAR="+json.dumps(
            row,sort_keys=True),flush=True)
    report=execute_missing_years(execute=args.execute,progress=safe_year_event)
    print("INDEXALERT_KRX_PRIVATE_MISSING_2017_2022_ALL="+json.dumps(
        report,sort_keys=True),flush=True)
    if args.execute and report["status"]!=SUCCESS:
        raise SystemExit(1)
