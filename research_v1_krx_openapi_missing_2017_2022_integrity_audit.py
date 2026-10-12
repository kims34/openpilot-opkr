"""Offline aggregate integrity audit for missing 2017–2022 KOSPI original history.

Pin only missing 2017–2022 complete calendar years. Reverify cryptographic original source storage + date/row/quality
bindings through the existing independent per-date audit.

Dry-run by default. --audit reads only the dedicated Railway /data private
volume; it never contacts providers or brokers, mutates files, emits security
identifiers/raw rows/prices or supplies PIT/performance/holdout/live authority.
Exactly one safe aggregate progress line per fully verified year.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from research_v1_krx_openapi_private_integrity_audit import (
    _bounds, audit_private_range,
)
from research_v1_krx_openapi_private_history_batch import (
    PRIVATE_SUBDIR, WORKER,
)

RANGES = (
    ("2017-01-01", "2017-12-31"),
    ("2018-01-01", "2018-12-31"),
    ("2019-01-01", "2019-12-31"),
    ("2020-01-01", "2020-12-31"),
    ("2021-01-01", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
)
SHA64 = set("0123456789abcdef")
SAFETY = {
    "raw_security_rows_emitted": False,
    "storage_mutated": False,
    "network_request_attempted": False,
    "historical_publication_pit_verified": False,
    "official_trading_status_verified": False,
    "corporate_action_paths_verified": False,
    "full_universe_source_admitted": False,
    "m20_performance_testing_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "live_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "ordering": "DISABLED",
}


def plan_years() -> list[dict]:
    return [
        {"start":start, "end":end, "expected_weekdays":len(_bounds(start,end))}
        for start,end in RANGES
    ]


def audit_all_missing(
    *, execute: bool=False, environment: Mapping[str,str]|None=None,
    audit: Callable[...,dict]=audit_private_range,
    report_year: Callable[[dict],None]|None=None,
) -> dict[str,Any]:
    plan=plan_years()
    report:dict[str,Any]={
        "purpose":"KRX_MISSING_2017_2022_RAW_STORAGE_INTEGRITY_ONLY",
        "status":"DRY_RUN_NO_STORAGE_ACCESS",
        "years": [2017,2018,2019,2020,2021,2022],
        "expected_weekday_pairs":sum(i["expected_weekdays"] for i in plan),
        "verified_weekday_pairs":0,
        "missing_weekday_pairs":0,
        "invalid_pair_count":0,
        "unverified_exchange_calendar_or_source_gap_days":0,
        "sampled_zero_activity_ohlc_rows":0,
        "sampled_other_invalid_ohlc_rows":0,
        "completed_years":[],
        "year_receipts":[],
        "combined_aggregate_fingerprint_sha256":None,
        **SAFETY,
    }
    if not execute:
        return report
    env=os.environ if environment is None else environment
    if env.get("RAILWAY_SERVICE_NAME")!=WORKER:
        report["status"]="FAIL_CLOSED_NOT_DEDICATED_PRIVATE_WORKER"
        return report
    raw_root=env.get("KRX_PRIVATE_RAW_DIR")
    if type(raw_root) is not str or not raw_root.startswith("/data"):
        report["status"]="FAIL_CLOSED_MISSING_PRIVATE_VOLUME_ROOT"
        return report
    root=Path(raw_root)/PRIVATE_SUBDIR
    report["status"]="RUNNING_READONLY_PRIVATE_INTEGRITY"
    for item in plan:
        year=int(item["start"][:4])
        try:
            result=audit(root=root,start=item["start"],end=item["end"])
        except Exception:
            report["status"]="FAIL_CLOSED_PRIVATE_AUDIT_UNHANDLED"
            report["failed_year"]=year
            return report
        digest=result.get("snapshot_fingerprint_sha256")
        if (result.get("status")!="ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED"
                or result.get("verified_date_pairs")!=item["expected_weekdays"]
                or result.get("missing_weekday_pair_count")!=0
                or result.get("invalid_pair_count")!=0
                or result.get("network_request_attempted") is not False
                or result.get("storage_mutated") is not False
                or result.get("source_admitted") is not False
                or result.get("real_orders_authorized") is not False
                or type(digest) is not str or len(digest)!=64
                or any(c not in SHA64 for c in digest)):
            report["status"]="FAIL_CLOSED_MISSING_OR_INVALID_PRIVATE_SOURCE"
            report["failed_year"]=year
            report["failure_scope"]="SOURCE_INTEGRITY_OR_CALENDAR_COVERAGE"
            return report
        receipt={
            "year":year,
            "status":"FULL_WEEKDAY_CAPTURE_INTEGRITY_ONLY_NOT_PIT",
            "expected_weekdays":item["expected_weekdays"],
            "verified_weekday_pairs":result["verified_date_pairs"],
            "unknown_calendar_or_source_gap_days":result["empty_daily_unverified_calendar_or_source_gap_days"],
            "sampled_zero_activity_ohlc_rows":result["sampled_ohlc_zero_activity_rows"],
            "sampled_other_invalid_ohlc_rows":result["sampled_other_invalid_price_rows"],
            "metadata_snapshot_sha256":digest,
            "historical_pit_source_admitted":False,
            "performance_run_authorized":False,
            "real_orders_authorized":False,
        }
        report["year_receipts"].append(receipt)
        report["completed_years"].append(year)
        report["verified_weekday_pairs"]+=receipt["verified_weekday_pairs"]
        report["unverified_exchange_calendar_or_source_gap_days"]+=receipt["unknown_calendar_or_source_gap_days"]
        report["sampled_zero_activity_ohlc_rows"]+=receipt["sampled_zero_activity_ohlc_rows"]
        report["sampled_other_invalid_ohlc_rows"]+=receipt["sampled_other_invalid_ohlc_rows"]
        if report_year is not None:
            report_year(receipt)
    report["combined_aggregate_fingerprint_sha256"]=hashlib.sha256(json.dumps(
        report["year_receipts"],sort_keys=True,separators=(",",":")
    ).encode("utf-8")).hexdigest()
    report["status"]="PRIVATE_MISSING_2017_2022_YEARS_INTEGRITY_VERIFIED_NOT_PIT"
    return report


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--audit",action="store_true")
    args=cli.parse_args()
    def log_receipt(row):
        print("INDEXALERT_MISSING_2017_2022_INTEGRITY_YEAR="+json.dumps(row,sort_keys=True),flush=True)
    out=audit_all_missing(execute=args.audit,report_year=log_receipt)
    print("INDEXALERT_MISSING_2017_2022_INTEGRITY_FINAL="+json.dumps(out,sort_keys=True),flush=True)
    if args.audit and out["status"]!="PRIVATE_MISSING_2017_2022_YEARS_INTEGRITY_VERIFIED_NOT_PIT":
        raise SystemExit(1)
