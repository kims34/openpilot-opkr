"""Read-only KRX approved OpenAPI private price-history integrity audit.

Inspects the dedicated Railway private-volume content-addressed store, without
network, market orders, source/feature admission or any filesystem mutation.
All per-security source rows, identifiers, daily financial values and raw source
hashes remain private; only annual/month-range aggregate counts are emitted.

Successful hash and coverage validation is NOT historical PIT proof, an
authenticated official exchange holiday/status feed, tax/execution validation,
an independent profitability test, or authorization to trade.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from research_v1_krx_private_store import (
    KRXPrivateStoreError, read_private_json, read_raw_object,
    validate_private_root_path,
)
from research_v1_krx_openapi_private_history_batch import (
    PRIVATE_SUBDIR, BASE, ENDPOINTS, _parse, _inspect,
)

SHA = re.compile(r"[a-f0-9]{64}\Z")
ROOT_VERS = "2026-10-12.v1"
EXPECTED_PERMISSIONS = {
    "source_pair_complete": True,
    "historical_pit_source_admitted": False,
    "official_trading_status_verified": False,
    "performance_run_authorized": False,
    "real_orders_authorized": False,
}
ADMISSION = {
    "raw_source_rows_exposed": False,
    "network_request_attempted": False,
    "storage_mutated": False,
    "historical_publication_pit_verified": False,
    "official_halt_and_delist_status_verified": False,
    "source_admitted": False,
    "m20_performance_testing_authorized": False,
    "sealed_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permission_change_authorized": False,
    "ordering": "DISABLED",
}


class OfflinePrivateAuditError(ValueError):
    """Fixed disclosure-safe reason codes only."""


def _bounds(start: str, end: str) -> list[str]:
    try:
        lo, hi = date.fromisoformat(start), date.fromisoformat(end)
        if (lo.isoformat() != start or hi.isoformat() != end
                or lo.year != hi.year or lo.year < 2015
                or hi > date(2026, 10, 12)
                or lo > hi or (hi-lo).days >= 366):
            raise ValueError
    except (TypeError, ValueError):
        raise OfflinePrivateAuditError("AUDIT_DATE_SCOPE_INVALID") from None
    return [
        (lo+timedelta(days=i)).strftime("%Y%m%d")
        for i in range((hi-lo).days+1)
        if (lo+timedelta(days=i)).weekday() < 5
    ]


def _trusted_private_root(root: Path) -> Path:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise OfflinePrivateAuditError("PRIVATE_STORE_ROOT_INVALID")
    if root.name != PRIVATE_SUBDIR:
        raise OfflinePrivateAuditError("PRIVATE_STORE_SCOPE_MISMATCH")
    if root.parent != Path("/data") and not os.getenv("INDEXALERT_TEST_PRIVATE_AUDIT"):
        # Production mount may be /data/<private-dir>/...; lower-level
        # validator rules out public and worktree paths as well.
        if "/data" not in (str(root) + "/"):
            raise OfflinePrivateAuditError("PRIVATE_STORE_NOT_ON_MOUNT")
    try:
        return validate_private_root_path(root, git_worktree=Path.cwd())
    except KRXPrivateStoreError:
        raise OfflinePrivateAuditError("PRIVATE_STORE_ROOT_INVALID") from None


def _parse_retrieved(value: Any) -> None:
    if type(value) is not str:
        raise OfflinePrivateAuditError("OBSERVATION_TIMESTAMP_INVALID")
    try:
        dt = datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError:
        raise OfflinePrivateAuditError("OBSERVATION_TIMESTAMP_INVALID") from None
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise OfflinePrivateAuditError("OBSERVATION_TIMESTAMP_INVALID")
    # Historical docs were fetched in 2026, and may not be backdated to 2015.
    if dt.date() < date(2026, 10, 1):
        raise OfflinePrivateAuditError("OBSERVATION_TIMESTAMP_BACKDATED")


def _check_one(root: Path, day: str) -> dict:
    rel = f"acquisitions/{day}.json"
    cpath = root / rel
    if cpath.is_symlink():
        raise OfflinePrivateAuditError("CHECKPOINT_SYMLINK_INVALID")
    try:
        raw = read_private_json(root, rel, git_worktree=Path.cwd())["value"]
    except (KRXPrivateStoreError, OSError, ValueError):
        raise OfflinePrivateAuditError("CHECKPOINT_READ_INVALID") from None
    if (raw.get("version") != ROOT_VERS
            or raw.get("trading_day") != day
            or raw.get("user_approved_use") != "PRIVATE_NONCOMMERCIAL_2015_2026"
            or any(raw.get(key) is not expected for key,expected in EXPECTED_PERMISSIONS.items())):
        raise OfflinePrivateAuditError("CHECKPOINT_IDENTITY_OR_AUTHORITY_INVALID")
    sources = raw.get("sources")
    if type(sources) is not dict or set(sources) != set(ENDPOINTS):
        raise OfflinePrivateAuditError("CHECKPOINT_SOURCE_SCOPE_INVALID")
    raw_rows: dict[str,list[dict]] = {}
    raw_sha: dict[str,str] = {}
    for service, endpoint in ENDPOINTS.items():
        source = sources[service]
        if (type(source) is not dict
                or source.get("dataset") != service
                or source.get("source_endpoint_suffix") != endpoint.removeprefix(BASE)
                or source.get("source_access_route") != "KRX_APPROVED_OPENAPI_ONLY"
                or source.get("request_bas_dd") != day
                or source.get("official_original_publication_timestamp_verified") is not False):
            raise OfflinePrivateAuditError("SOURCE_BINDING_OR_ADMISSION_INVALID")
        _parse_retrieved(source.get("retrieved_at_utc"))
        if source.get("observed_available_by") != source.get("retrieved_at_utc"):
            raise OfflinePrivateAuditError("SOURCE_TIME_BOUNDARY_MISMATCH")
        digest = source.get("raw_sha256")
        nbytes = source.get("raw_byte_length")
        if (type(digest) is not str or not SHA.fullmatch(digest)
                or type(nbytes) is not int or nbytes <= 0):
            raise OfflinePrivateAuditError("SOURCE_DIGEST_OR_SIZE_INVALID")
        try:
            rawbytes = read_raw_object(
                root, digest, expected_size=nbytes, git_worktree=Path.cwd())
        except (KRXPrivateStoreError, OSError):
            raise OfflinePrivateAuditError("PRIVATE_SOURCE_OBJECT_DAMAGED") from None
        try:
            parsed, schema_sha = _parse(rawbytes, service)
        except (ValueError, TypeError):
            raise OfflinePrivateAuditError("PRIVATE_SOURCE_JSON_SCHEMA_DRIFT") from None
        if (schema_sha != source.get("schema_sha256")
                or len(parsed) != source.get("observed_rows")):
            raise OfflinePrivateAuditError("SOURCE_SCHEMA_OR_COUNT_MISMATCH")
        raw_rows[service] = parsed
        raw_sha[service] = digest
    try:
        quality = _inspect(
            raw_rows["daily_trade"], raw_rows["security_master"], day)
    except (ValueError, TypeError):
        raise OfflinePrivateAuditError("PRIVATE_SOURCE_QUALITY_INVALID") from None
    if quality != raw.get("quality"):
        raise OfflinePrivateAuditError("PRIVATE_SOURCE_QUALITY_MISMATCH")
    pair_hash = hashlib.sha256(
        json.dumps({"day":day, "sources":raw_sha, "quality":quality},
                   sort_keys=True, separators=(",",":")).encode("utf-8")
    ).hexdigest()
    return {
        "day": day,
        "pair_sha256": pair_hash,
        "daily_rows": len(raw_rows["daily_trade"]),
        "common_rows": quality["common_rows"],
        "normal_ohlc_common_rows": quality["normal_ohlc_common_rows"],
        "nonpositive_zero_activity_rows": quality["nonpositive_zero_activity_rows"],
        "other_invalid_price_rows": quality["other_invalid_price_rows"],
        "source_day_class": quality["calendar_day_class"],
    }


def audit_private_range(*, root: Path, start: str, end: str) -> dict:
    out: dict[str,Any] = {
        "purpose": "KRX_APPROVED_OPENAPI_STORED_ORIGINAL_SOURCE_INTEGRITY_NOT_PIT",
        "status": "NOT_EVALUATED",
        "start": start, "end": end,
        "expected_weekdays": 0,
        "found_checkpoint_count": 0,
        "verified_date_pairs": 0,
        "missing_weekday_pair_count": 0,
        "invalid_pair_count": 0,
        "empty_daily_unverified_calendar_or_source_gap_days": 0,
        "sampled_ohlc_zero_activity_rows": 0,
        "sampled_other_invalid_price_rows": 0,
        "original_security_rows_persisted_in_private_store_only": True,
        "snapshot_fingerprint_sha256": None,
        "failure_codes": {},
        **ADMISSION,
    }
    try:
        dates = _bounds(start, end)
        out["expected_weekdays"] = len(dates)
        if not dates:
            raise OfflinePrivateAuditError("EMPTY_AUDIT_WORKDAY_SCOPE")
        private = _trusted_private_root(Path(root))
    except OfflinePrivateAuditError as exc:
        out["status"] = "FAIL_CLOSED_AUDIT_SCOPE_INVALID"
        out["failure_codes"] = {str(exc):1}
        return out
    reasons = Counter()
    fingerprints = []
    for d in dates:
        rel = private / "acquisitions" / (d+".json")
        if not rel.exists() and not rel.is_symlink():
            out["missing_weekday_pair_count"] += 1
            continue
        out["found_checkpoint_count"] += 1
        try:
            row = _check_one(private,d)
        except OfflinePrivateAuditError as exc:
            out["invalid_pair_count"] += 1
            reasons[str(exc)] += 1
            continue
        fingerprints.append({"day":d,"pair_sha256":row["pair_sha256"]})
        out["verified_date_pairs"] += 1
        out["sampled_ohlc_zero_activity_rows"] += row["nonpositive_zero_activity_rows"]
        out["sampled_other_invalid_price_rows"] += row["other_invalid_price_rows"]
        if row["source_day_class"] != "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED":
            out["empty_daily_unverified_calendar_or_source_gap_days"] += 1
    out["failure_codes"] = dict(sorted(reasons.items()))
    if fingerprints:
        out["snapshot_fingerprint_sha256"] = hashlib.sha256(
            json.dumps(fingerprints,sort_keys=True,separators=(",",":")).encode()
        ).hexdigest()
    if out["invalid_pair_count"]:
        out["status"] = "FAIL_CLOSED_PRIVATE_SOURCE_INTEGRITY_ERROR"
    elif out["missing_weekday_pair_count"]:
        out["status"] = "INCOMPLETE_WEEKDAY_COVERAGE_NOT_PIT_ADMITTED"
    else:
        out["status"] = "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED"
    return out


if __name__=="__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    args = p.parse_args()
    path = Path(os.getenv("KRX_PRIVATE_RAW_DIR") or "/data") / PRIVATE_SUBDIR
    result = audit_private_range(root=path,start=args.start,end=args.end)
    print("INDEXALERT_PRIVATE_KRX_OPENAPI_INTEGRITY=" + json.dumps(
        result,sort_keys=True), flush=True)
    if result["status"] != "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED":
        raise SystemExit(1)
