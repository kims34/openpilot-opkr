"""Stage-two annual KRX approved OPEN API private history acquisition runner.

Strictly one calendar year (2015-2026), <=366 calendar days, <=650
potential daily/master GETs, <=20 separate <=28-calendar-day guarded batches,
read-only KOSPI official OpenAPI only. Each one-shot invocation requires
explicit --execute plus the preexisting private historical-worker scope sentinel.
Provider raw data are stored only on the persistent private volume by the
already tested low-level worker. No public raw artifacts.

This run does NOT admit PIT/status, compute M20 returns, change Frozen rules,
access sealed holdout, or enable broker/real orders.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import os
from typing import Any, Callable

import requests

from research_v1_krx_openapi_private_history_batch import (
    AUTHORITY, MAX_REQUESTS as PER_WINDOW_MAX_REQUESTS, _calendar,
    PrivateOpenAPIHistoryError, run as small_batch,
)

MAX_ANNUAL_CALLS = 650
MAX_WINDOWS = 20
MAX_SPAN = 366
WINDOW_DAYS = 28


class AnnualHistoryScopeError(ValueError):
    pass


def split_annual_windows(start: str, end: str) -> list[tuple[str, str, int]]:
    try:
        lo, hi = date.fromisoformat(start), date.fromisoformat(end)
    except (ValueError, TypeError):
        raise AnnualHistoryScopeError("ANNUAL_DATES_INVALID") from None
    if (lo.isoformat() != start or hi.isoformat() != end
            or lo.year != hi.year or lo.year < 2015 or hi.year > 2026
            or hi < lo or (hi - lo).days + 1 > MAX_SPAN
            or hi > date(2026, 10, 12)):
        raise AnnualHistoryScopeError("YEAR_OR_USER_SCOPE_EXCEEDED")
    days = []
    chunk_start = lo
    while chunk_start <= hi:
        chunk_end = min(chunk_start + timedelta(days=WINDOW_DAYS - 1), hi)
        left, right = chunk_start.isoformat(), chunk_end.isoformat()
        expected = len(_calendar(left, right, PER_WINDOW_MAX_REQUESTS)) * 2
        days.append((left, right, expected))
        chunk_start = chunk_end + timedelta(days=1)
    if len(days) > MAX_WINDOWS or sum(v[2] for v in days) > MAX_ANNUAL_CALLS:
        raise AnnualHistoryScopeError("ANNUAL_BUDGET_EXCEEDED")
    return days


def execute_annual_stage(
    *, start: str, end: str, execute: bool = False,
    batch_runner: Callable[..., dict] = small_batch,
    session=None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "classification": "KRX_KOSPI_APPROVED_PRIVATE_YEAR_STAGE_NOT_SOURCE_ADMITTED",
        "status": "DRY_RUN_NO_NETWORK",
        "start": start, "end": end,
        "planned_windows": 0, "planned_max_api_requests": 0,
        "completed_windows": 0, "actual_api_requests": 0,
        "new_completed_date_pairs": 0, "already_verified_pairs_skipped": 0,
        "new_raw_content_objects": 0, "observed_ohlc_zero_activity_rows": 0,
        "source_provider_raw_rows_in_public_report": False,
        "private_volume_only": True, "historical_pit_not_proven": True,
        **AUTHORITY,
    }
    try:
        windows = split_annual_windows(start, end)
        result["planned_windows"] = len(windows)
        result["planned_max_api_requests"] = sum(i[2] for i in windows)
        if not execute:
            return result
        # Each child also checks the exact per-run consent sentinel, private
        # dedicated service identity, official endpoint, auth and store.
        result["status"] = "RUNNING_NOT_ADMITTED"
        if session is None:
            session = requests.Session()
        for left, right, estimated_requests in windows:
            child = batch_runner(
                start=left, end=right,
                max_requests=PER_WINDOW_MAX_REQUESTS,
                execute=True, session=session,
            )
            result["actual_api_requests"] += int(child.get("attempted_requests", 0))
            if child.get("status") != "PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED":
                result["status"] = "FAIL_CLOSED_SOURCE_OR_STORAGE_GAP"
                result["failure_stage_start"] = left
                result["failure_stage_end"] = right
                result["failure_reason_code"] = str(
                    child.get("failure_reason", "CHILD_STAGE_FAILED")
                )
                return result
            result["completed_windows"] += 1
            result["new_completed_date_pairs"] += int(child["new_completed_date_pairs"])
            result["already_verified_pairs_skipped"] += int(child["previous_verified_date_pairs_skipped"])
            result["new_raw_content_objects"] += int(child["new_stored_raw_objects"])
            result["observed_ohlc_zero_activity_rows"] += int(child["batch_sampled_ohlc_zero_activity_rows"])
        result["status"] = "PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED"
    except (AnnualHistoryScopeError, PrivateOpenAPIHistoryError) as exc:
        result["status"] = "FAIL_CLOSED_SCOPE_INVALID"
        result["failure_reason_code"] = str(exc)
    except (ValueError, TypeError):
        result["status"] = "FAIL_CLOSED_CHILD_RESULT_INVALID"
    return result


if __name__ == "__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--start",required=True)
    cli.add_argument("--end",required=True)
    cli.add_argument("--execute",action="store_true")
    args=cli.parse_args()
    report=execute_annual_stage(
        start=args.start,end=args.end,execute=args.execute,
    )
    print("INDEXALERT_PRIVATE_KRX_OPENAPI_YEAR_STAGE=" +
          json.dumps(report,sort_keys=True),flush=True)
    if args.execute and report["status"] != "PRIVATE_ANNUAL_YEAR_STAGE_COMPLETE_NOT_PIT_ADMITTED":
        raise SystemExit(1)
