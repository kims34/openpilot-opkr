"""One-shot recent-years KOSPI official OpenAPI PRIVATE collection continuation.

Fixed dates only: 2024, 2025, and completed historical dates through
2026-10-08. Full year 2023 is separately acquired and audited.

Requires exact CLI --execute; each year is split into <=28-day/<=60-GET
windows by the existing annually bounded collector, which independently checks
the user-approved key and consent sentinel, exact dedicated Railway service,
persistent /data private store, and approved two KOSPI OpenAPI endpoints.

No exchange-wide status/delist evidence, no PIT, alpha, holdout, returns
simulation, model changes, broker/order/funds routes, or any LIVE permission.
A year failure ends the entire job with no later years attempted. Logs contain
only aggregate counts and fixed reason codes, never securities or prices.
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from research_v1_krx_openapi_private_year_runner import (
    execute_annual_stage,
    split_annual_windows,
)
from research_v1_krx_openapi_private_history_batch import AUTHORITY

PINNED_YEARS = (
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-10-08"),
)
MAX_TOTAL_REQUESTS = 1600


class RecentCaptureError(ValueError):
    pass


def fixed_recent_plan() -> list[dict]:
    summary=[]
    for start,end in PINNED_YEARS:
        windows=split_annual_windows(start,end)
        planned=sum(p[2] for p in windows)
        if planned<=0 or planned>650:
            raise RecentCaptureError("ANNUAL_QUOTA_INVALID")
        summary.append({"start":start,"end":end,"planned_windows":len(windows),
                        "planned_max_requests":planned})
    if sum(item["planned_max_requests"] for item in summary)>MAX_TOTAL_REQUESTS:
        raise RecentCaptureError("RECENT_COLLECTION_TOTAL_QUOTA_EXCEEDED")
    return summary


def execute_recent(
    *, execute: bool = False,
    year_runner: Callable[...,dict] = execute_annual_stage,
    send_progress: Callable[[dict],None] | None = None,
) -> dict[str,Any]:
    report:dict[str,Any] = {
        "classification": "KRX_KOSPI_OFFICIAL_APPROVED_RECENT_PRIVATE_COLLECTION_ONLY",
        "status": "DRY_RUN_NO_NETWORK",
        "requested_years": [2024,2025,2026],
        "planned_max_api_requests": 0,
        "actual_api_requests": 0,
        "completed_years": [],
        "new_completed_date_pairs": 0,
        "previous_verified_date_pairs_skipped": 0,
        "empty_daily_unverified_calendar_or_source_gap_days": 0,
        "new_private_raw_objects": 0,
        "year_stage_results": [],
        "private_content_not_uploaded": True,
        "same_day_2026_10_12_not_requested": True,
        **AUTHORITY,
    }
    try:
        plan=fixed_recent_plan()
        report["planned_max_api_requests"]=sum(x["planned_max_requests"] for x in plan)
        if not execute:
            return report
        report["status"]="RUNNING_PRIVATE_NO_SOURCE_ADMISSION"
        for item in plan:
            result=year_runner(start=item["start"],end=item["end"],execute=True)
            req=result.get("actual_api_requests")
            if (type(req) is not int or req<0
                    or req>item["planned_max_requests"]
                    or report["actual_api_requests"]+req>MAX_TOTAL_REQUESTS):
                report["status"]="FAIL_CLOSED_UNVERIFIABLE_REQUEST_COUNTS"
                report["failure_year"]=int(item["start"][:4])
                break
            report["actual_api_requests"]+=req
            if result.get("status")!="PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED":
                report["status"]="FAIL_CLOSED_SOURCE_OR_PRIVATE_STORAGE_GAP"
                report["failure_year"]=int(item["start"][:4])
                report["failure_reason_code"]=str(
                    result.get("failure_reason_code","SOURCE_YEAR_NOT_COMPLETE"))
                break
            if (result.get("source_admitted") is not False
                    or result.get("m20_performance_testing_authorized") is not False
                    or result.get("live_orders_authorized") is not False
                    or result.get("ordering")!="DISABLED"):
                report["status"]="FAIL_CLOSED_CHILD_AUTHORITY_DRIFT"
                report["failure_year"]=int(item["start"][:4])
                break
            metrics={
                "year":int(item["start"][:4]),
                "status":"PRIVATE_YEAR_STORED_NOT_SOURCE_ADMITTED",
                "requests":req,
                "verified_existing_pairs_skipped":int(result["already_verified_pairs_skipped"]),
                "new_date_pairs":int(result["new_completed_date_pairs"]),
                "unverified_calendar_gaps":int(result["unverified_empty_daily_date_pairs"]),
                "new_raw_objects":int(result["new_raw_content_objects"]),
                "historical_publication_pit_verified":False,
                "performance_run_authorized":False,
                "real_orders_authorized":False,
            }
            report["year_stage_results"].append(metrics)
            report["completed_years"].append(metrics["year"])
            report["new_completed_date_pairs"]+=metrics["new_date_pairs"]
            report["previous_verified_date_pairs_skipped"]+=metrics["verified_existing_pairs_skipped"]
            report["empty_daily_unverified_calendar_or_source_gap_days"]+=metrics["unverified_calendar_gaps"]
            report["new_private_raw_objects"]+=metrics["new_raw_objects"]
            if send_progress is not None:
                send_progress(metrics)
        else:
            report["status"]="PRIVATE_RECENT_THREE_YEAR_SOURCE_CAPTURE_COMPLETE_NOT_PIT_ADMITTED"
    except (RecentCaptureError, ValueError, TypeError, KeyError) as exc:
        report["status"]="FAIL_CLOSED_STAGE_EXCEPTION"
        report["failure_code"]="INVALID_RECENT_CAPTURE_STAGE"
    return report


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--execute",action="store_true")
    args=cli.parse_args()
    def safe_log_year(data):
        print("INDEXALERT_PRIVATE_KRX_RECENT_YEAR="+json.dumps(
            data,sort_keys=True),flush=True)
    out=execute_recent(execute=args.execute,send_progress=safe_log_year)
    print("INDEXALERT_PRIVATE_KRX_RECENT_ALL="+json.dumps(out,sort_keys=True),flush=True)
    if args.execute and out["status"]!="PRIVATE_RECENT_THREE_YEAR_SOURCE_CAPTURE_COMPLETE_NOT_PIT_ADMITTED":
        raise SystemExit(1)
