"""Bounded, resumable KRX *approved OpenAPI* private history acquisition.

One-shot Railway historical-worker job only, never the public runtime. Explicit
user-approved 2015-2026 personal-research scope. ONLY approved KOSPI basic
information and daily-trading APIs; Data Marketplace web-session endpoints,
KOSDAQ APIs, trades and account operations are absent.

Default is DRY_RUN. A real run needs an exact CLI opt-in and per-run ENV
sentinel; at most 60 requests across <=30 calendar days. Original provider
responses are stored **only** in the existing private mounted volume with
SHA256 binding. Logs contain counts/quality codes only, no issuer identifiers,
prices, raw data, API key, or credentials.

The historical snapshots were retrieved *now*. Do NOT infer historical PIT
published-at, contemporaneous status or survivorship completeness; no
performance, sealed holdout, Champion, real orders or account authority.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
from typing import Any, Mapping

import requests

from research_v1_krx_private_store import (
    KRXPrivateStoreError, read_private_json, validate_private_root,
    verify_raw_object, write_private_json, write_raw_object,
)

BASE = "https://data-dbg.krx.co.kr/svc/apis/sto/"
ENDPOINTS = {
    "daily_trade": BASE + "stk_bydd_trd",
    "security_master": BASE + "stk_isu_base_info",
}
REQUIRED = {
    "daily_trade": frozenset({
        "BAS_DD", "ISU_CD", "TDD_OPNPRC", "TDD_HGPRC", "TDD_LWPRC",
        "TDD_CLSPRC", "ACC_TRDVOL", "ACC_TRDVAL", "MKTCAP",
        "LIST_SHRS", "FLUC_RT",
    }),
    "security_master": frozenset({
        "ISU_CD", "ISU_SRT_CD", "ISU_NM", "LIST_DD",
        "MKT_TP_NM", "SECUGRP_NM", "KIND_STKCERT_TP_NM", "LIST_SHRS",
    }),
}
CONSENT = "I_AUTHORIZE_INDEXALERT_KRX_OPENAPI_HISTORY_20261012"
ENV_CONSENT = "KRX_OPENAPI_HISTORY_SCOPED_CONSENT"
WORKER = "indexalert-krx-historical-worker"
PRIVATE_SUBDIR = "openapi_kospi_history_v1"
MAX_REQUESTS = 60
MAX_CALENDAR_DAYS = 30
MAX_BYTES = 12 * 1024 * 1024
LOW_STORAGE_BYTES = 400 * 1024 * 1024
CANONICAL_SYMBOL = re.compile(r"[0-9A-Z]{6}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
NUMERIC = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?\Z")
STAMP = "%Y-%m-%dT%H:%M:%S.%f%z"
AUTHORITY = {
    "source_admitted": False,
    "historical_publication_pit_verified": False,
    "historical_security_status_verified": False,
    "corporate_actions_verified": False,
    "krx_cost_return_path_verified": False,
    "m20_performance_testing_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "live_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "ordering": "DISABLED",
}


class PrivateOpenAPIHistoryError(ValueError):
    """Only constant public-safe error codes."""


def _safe_day(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise PrivateOpenAPIHistoryError("INVALID_CALENDAR_DAY")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise PrivateOpenAPIHistoryError("INVALID_CALENDAR_DAY") from None
    if parsed.isoformat() != value:
        raise PrivateOpenAPIHistoryError("INVALID_CALENDAR_DAY")
    return parsed


def _calendar(start: str, end: str, max_requests: int) -> list[str]:
    lo, hi = _safe_day(start), _safe_day(end)
    if lo < date(2015, 1, 1) or hi > date(2026, 10, 12) or hi < lo:
        raise PrivateOpenAPIHistoryError("USER_APPROVED_DATE_SCOPE_EXCEEDED")
    if (hi - lo).days + 1 > MAX_CALENDAR_DAYS:
        raise PrivateOpenAPIHistoryError("CALENDAR_SPAN_EXCEEDS_BATCH_LIMIT")
    if type(max_requests) is not int or max_requests < 2 or max_requests > MAX_REQUESTS:
        raise PrivateOpenAPIHistoryError("REQUEST_BUDGET_INVALID")
    days = [
        (lo + timedelta(days=i)).strftime("%Y%m%d")
        for i in range((hi - lo).days + 1)
        if (lo + timedelta(days=i)).weekday() < 5
    ]
    if 2 * len(days) > max_requests:
        raise PrivateOpenAPIHistoryError("REQUEST_BUDGET_BELOW_PLANNED_CALLS")
    return days


def _preflight(env: Mapping[str, str], *, execute: bool) -> Path:
    if not execute:
        raise PrivateOpenAPIHistoryError("EXPLICIT_EXECUTE_FLAG_REQUIRED")
    if env.get(ENV_CONSENT) != CONSENT:
        raise PrivateOpenAPIHistoryError("SCOPED_USER_CONSENT_SENTINEL_REQUIRED")
    if env.get("RAILWAY_SERVICE_NAME") != WORKER:
        raise PrivateOpenAPIHistoryError("PRIVATE_DEDICATED_WORKER_REQUIRED")
    if not str(env.get("KRX_AUTH_KEY") or "").strip():
        raise PrivateOpenAPIHistoryError("APPROVED_OPENAPI_KEY_MISSING")
    private_root = str(env.get("KRX_PRIVATE_RAW_DIR") or "").strip()
    if not private_root:
        raise PrivateOpenAPIHistoryError("PERSISTENT_PRIVATE_ROOT_MISSING")
    path = Path(private_root)
    if not path.is_absolute() or path.parts[:2] != ("/", "data"):
        raise PrivateOpenAPIHistoryError("PERSISTENT_PRIVATE_VOLUME_REQUIRED")
    try:
        # Must be on existing persistent private volume, never CWD or /tmp.
        if not path.is_dir():
            raise PrivateOpenAPIHistoryError("PERSISTENT_PRIVATE_ROOT_MISSING")
        if shutil.disk_usage(path).free < LOW_STORAGE_BYTES:
            raise PrivateOpenAPIHistoryError("PRIVATE_STORAGE_HEADROOM_EXHAUSTED")
        root = validate_private_root(path / PRIVATE_SUBDIR, git_worktree=Path.cwd())
    except (KRXPrivateStoreError, OSError):
        raise PrivateOpenAPIHistoryError("PERSISTENT_PRIVATE_ROOT_INVALID") from None
    return root


def _canon(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _symbol(value: Any) -> str:
    if type(value) is not str:
        raise PrivateOpenAPIHistoryError("SOURCE_SECURITY_CODE_INVALID")
    val = value.strip().upper()
    if val.isdigit() and 1 <= len(val) <= 6:
        val = val.zfill(6)
    if not CANONICAL_SYMBOL.fullmatch(val):
        raise PrivateOpenAPIHistoryError("SOURCE_SECURITY_CODE_INVALID")
    return val


def _number(value: Any, *, integer: bool = False) -> Decimal:
    if type(value) not in (str, int, Decimal):
        raise PrivateOpenAPIHistoryError("SOURCE_NUMERIC_SHAPE_INVALID")
    if type(value) is str:
        value = value.strip().replace(",", "")
        if not NUMERIC.fullmatch(value):
            raise PrivateOpenAPIHistoryError("SOURCE_NUMERIC_SHAPE_INVALID")
    try:
        num = Decimal(value)
    except (ValueError, InvalidOperation):
        raise PrivateOpenAPIHistoryError("SOURCE_NUMERIC_SHAPE_INVALID") from None
    if not num.is_finite() or (integer and num != num.to_integral_value()):
        raise PrivateOpenAPIHistoryError("SOURCE_NUMERIC_SHAPE_INVALID")
    return num


def _parse(raw: bytes, service: str) -> tuple[list[dict], str]:
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        raise PrivateOpenAPIHistoryError("SOURCE_RESPONSE_NON_JSON") from None
    if type(data) is not dict:
        raise PrivateOpenAPIHistoryError("SOURCE_ENVELOPE_INVALID")
    blocks = [k for k in ("OutBlock_1", "output") if k in data]
    if len(blocks) != 1:
        raise PrivateOpenAPIHistoryError("SOURCE_ENVELOPE_INVALID")
    rows = data[blocks[0]]
    if type(rows) is not list or any(type(r) is not dict or not r for r in rows):
        raise PrivateOpenAPIHistoryError("SOURCE_ROW_BLOCK_INVALID")
    if rows:
        columns = set(rows[0])
        if not REQUIRED[service].issubset(columns) or any(set(row) != columns for row in rows):
            raise PrivateOpenAPIHistoryError("SOURCE_SCHEMA_DRIFT")
    return rows, _digest(_canon(sorted(rows[0])) if rows else b"empty")


def _inspect(daily: list[dict], master: list[dict], day: str) -> dict:
    # An empty pair can be a holiday, but it must not be promoted to a verified
    # trading-calendar entry. One empty source paired with non-empty is invalid.
    if not daily or not master:
        if not daily and not master:
            return {"calendar_day_class": "PROVIDER_BOTH_EMPTY_UNVERIFIED_HOLIDAY",
                    "master_rows": 0, "daily_rows": 0, "common_rows": 0,
                    "normal_ohlc_common_rows": 0, "nonpositive_zero_activity_rows": 0,
                    "other_invalid_price_rows": 0, "daily_all_mapped_to_master": False}
        raise PrivateOpenAPIHistoryError("PARTIAL_SOURCE_CALENDAR_SCOPE")
    identities: dict[str, dict] = {}
    for row in master:
        code = _symbol(row.get("ISU_SRT_CD"))
        if code in identities:
            raise PrivateOpenAPIHistoryError("DUPLICATE_BASIC_INFO_SECURITY")
        if not row.get("ISU_NM") or not row.get("ISU_CD"):
            raise PrivateOpenAPIHistoryError("BASIC_INFO_IDENTITY_MISSING")
        identities[code] = row
    seen: set[str] = set()
    common = good = zero = other = 0
    for row in daily:
        if row.get("BAS_DD") != day:
            raise PrivateOpenAPIHistoryError("SOURCE_DAILY_DATE_MISMATCH")
        code = _symbol(row.get("ISU_CD"))
        if code in seen:
            raise PrivateOpenAPIHistoryError("SOURCE_DAILY_DUPLICATE_CODE")
        seen.add(code)
        if code not in identities:
            raise PrivateOpenAPIHistoryError("SOURCE_SECURITY_MASTER_UNMAPPED")
        b = identities[code]
        if b.get("SECUGRP_NM") != "주권" or b.get("KIND_STKCERT_TP_NM") != "보통주":
            continue
        if b.get("MKT_TP_NM") not in ("KOSPI", "유가증권"):
            raise PrivateOpenAPIHistoryError("COMMON_STOCK_MARKET_SCOPE_INVALID")
        common += 1
        op, hi, low, close = (
            _number(row[f]) for f in ("TDD_OPNPRC", "TDD_HGPRC", "TDD_LWPRC", "TDD_CLSPRC")
        )
        vol = _number(row["ACC_TRDVOL"], integer=True)
        val = _number(row["ACC_TRDVAL"], integer=True)
        cap = _number(row["MKTCAP"])
        shares = _number(row["LIST_SHRS"], integer=True)
        if min(vol, val, cap, shares) < 0:
            raise PrivateOpenAPIHistoryError("SOURCE_CAP_VOLUME_NEGATIVE")
        if min(op, hi, low, close) <= 0:
            if op == hi == low == 0 and close > 0 and vol == val == 0:
                zero += 1
            else:
                other += 1
        elif low <= op <= hi and low <= close <= hi:
            good += 1
        else:
            other += 1
    if common < 1 or len(seen) != len(daily) or good + zero + other != common:
        raise PrivateOpenAPIHistoryError("SOURCE_COMMON_COUNT_INVALID")
    return {
        "calendar_day_class": "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED",
        "daily_rows": len(daily),
        "master_rows": len(master),
        "common_rows": common,
        "normal_ohlc_common_rows": good,
        "nonpositive_zero_activity_rows": zero,
        "other_invalid_price_rows": other,
        "daily_all_mapped_to_master": True,
    }


def _get(session, url: str, key: str, day: str) -> tuple[bytes, str]:
    if url not in ENDPOINTS.values() or not re.fullmatch(r"\d{8}", day):
        raise PrivateOpenAPIHistoryError("UNAPPROVED_API_REQUEST")
    try:
        with session.get(url, headers={"AUTH_KEY": key}, params={"basDd": day},
                         allow_redirects=False, stream=True, timeout=25) as response:
            if response.status_code != 200:
                raise PrivateOpenAPIHistoryError("OPENAPI_NON_200")
            data = bytearray()
            for chunk in response.iter_content(chunk_size=65536):
                data.extend(chunk)
                if len(data) > MAX_BYTES:
                    raise PrivateOpenAPIHistoryError("OPENAPI_RESPONSE_SIZE_LIMIT")
    except requests.RequestException:
        raise PrivateOpenAPIHistoryError("OPENAPI_REQUEST_FAILED") from None
    if not data:
        raise PrivateOpenAPIHistoryError("OPENAPI_RESPONSE_EMPTY")
    return bytes(data), datetime.now(timezone.utc).isoformat()


def _checkpoint(root: Path, day: str) -> str:
    path = root / "acquisitions" / f"{day}.json"
    if not path.is_file():
        return "MISSING"
    try:
        saved = read_private_json(root, f"acquisitions/{day}.json", git_worktree=Path.cwd())["value"]
        if saved.get("session") != day or saved.get("source_pair_complete") is not True:
            raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_INVALID")
        if saved.get("performance_run_authorized") is not False:
            raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_AUTHORITY_DRIFT")
        if saved.get("real_orders_authorized") is not False:
            raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_AUTHORITY_DRIFT")
        pair = saved.get("sources")
        if type(pair) is not dict or set(pair) != set(ENDPOINTS):
            raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_SCOPE_INVALID")
        for service, record in pair.items():
            digest = record.get("raw_sha256")
            if type(digest) is not str or not SHA.fullmatch(digest):
                raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_INVALID")
            checked = verify_raw_object(
                root, digest, expected_size=record.get("raw_byte_length"),
                git_worktree=Path.cwd(),
            )
            if checked["raw_object_sha256"] != digest:
                raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_RAW_MISMATCH")
        return "VERIFIED_EXISTS"
    except (OSError, KeyError, TypeError, ValueError, KRXPrivateStoreError):
        raise PrivateOpenAPIHistoryError("PREVIOUS_CHECKPOINT_INVALID") from None


def run(
    *, start: str, end: str, max_requests: int = 60, execute: bool = False,
    environment: Mapping[str, str] | None = None, session=None,
) -> dict:
    report: dict[str, Any] = {
        "classification": "KRX_APPROVED_KOSPI_OPENAPI_PRIVATE_HISTORY_BATCH_RESEARCH_ONLY",
        "status": "DRY_RUN_NO_NETWORK",
        "requested_start": start, "requested_end": end, "max_requests": max_requests,
        "attempted_requests": 0, "new_completed_date_pairs": 0,
        "previous_verified_date_pairs_skipped": 0,
        "provider_empty_pairs_not_calendar_attested": 0,
        "new_stored_raw_objects": 0, "batch_sampled_common_rows": 0,
        "batch_sampled_ohlc_zero_activity_rows": 0,
        "raw_security_rows_disclosed": False,
        "private_storage_only": True, "historical_retrieval_is_not_historical_publication": True,
        **AUTHORITY,
    }
    try:
        days = _calendar(start, end, max_requests)
        report["weekdays_in_requested_span"] = len(days)
        env = os.environ if environment is None else environment
        if not execute:
            return report
        root = _preflight(env, execute=execute)
        if session is None:
            session = requests.Session()
        report["status"] = "RUNNING_NOT_ADMITTED"
        for day in days:
            if _checkpoint(root, day) == "VERIFIED_EXISTS":
                report["previous_verified_date_pairs_skipped"] += 1
                continue
            if shutil.disk_usage(root).free < LOW_STORAGE_BYTES:
                raise PrivateOpenAPIHistoryError("PRIVATE_STORAGE_HEADROOM_EXHAUSTED")
            acquired: dict[str, tuple[bytes, str, list[dict], str]] = {}
            for name, url in ENDPOINTS.items():
                if report["attempted_requests"] >= max_requests:
                    raise PrivateOpenAPIHistoryError("NETWORK_REQUEST_BUDGET_EXHAUSTED")
                report["attempted_requests"] += 1
                raw, retrieved = _get(session, url, env["KRX_AUTH_KEY"], day)
                rows, schema = _parse(raw, name)
                acquired[name] = (raw, retrieved, rows, schema)
                time.sleep(0.2)
            meta = _inspect(
                acquired["daily_trade"][2], acquired["security_master"][2], day
            )
            sources = {}
            for name in ENDPOINTS:
                raw, retrieved, rows, schema = acquired[name]
                saved = write_raw_object(root, raw, git_worktree=Path.cwd())
                report["new_stored_raw_objects"] += int(saved["created"])
                sources[name] = {
                    "dataset": name, "source_endpoint_suffix": ENDPOINTS[name].removeprefix(BASE),
                    "source_access_route": "KRX_APPROVED_OPENAPI_ONLY",
                    "request_bas_dd": day,
                    "retrieved_at_utc": retrieved,
                    "observed_available_by": retrieved,
                    "official_original_publication_timestamp_verified": False,
                    "raw_sha256": saved["raw_object_sha256"],
                    "raw_byte_length": saved["raw_bytes_size"],
                    "schema_sha256": schema,
                    "observed_rows": len(rows),
                }
            write_private_json(
                root, f"acquisitions/{day}.json",
                {
                    "version": "2026-10-12.v1",
                    "session": day,
                    "user_approved_use": "PRIVATE_NONCOMMERCIAL_2015_2026",
                    "source_pair_complete": True,
                    "sources": sources,
                    "quality": meta,
                    "performance_run_authorized": False,
                    "real_orders_authorized": False,
                    "official_trading_status_verified": False,
                    "historical_pit_source_admitted": False,
                },
                git_worktree=Path.cwd(),
            )
            report["new_completed_date_pairs"] += 1
            report["batch_sampled_common_rows"] += meta["common_rows"]
            report["batch_sampled_ohlc_zero_activity_rows"] += meta["nonpositive_zero_activity_rows"]
            if meta["calendar_day_class"] == "PROVIDER_BOTH_EMPTY_UNVERIFIED_HOLIDAY":
                report["provider_empty_pairs_not_calendar_attested"] += 1
        report["status"] = "PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED"
    except Exception as exc:
        report["status"] = "FAIL_CLOSED_NO_PROFIT_AUTHORITY"
        allowed = {
            "INVALID_CALENDAR_DAY", "USER_APPROVED_DATE_SCOPE_EXCEEDED",
            "CALENDAR_SPAN_EXCEEDS_BATCH_LIMIT", "REQUEST_BUDGET_INVALID",
            "REQUEST_BUDGET_BELOW_PLANNED_CALLS", "EXPLICIT_EXECUTE_FLAG_REQUIRED",
            "SCOPED_USER_CONSENT_SENTINEL_REQUIRED",
            "PRIVATE_DEDICATED_WORKER_REQUIRED", "APPROVED_OPENAPI_KEY_MISSING",
            "PERSISTENT_PRIVATE_ROOT_MISSING", "PERSISTENT_PRIVATE_VOLUME_REQUIRED",
            "PRIVATE_STORAGE_HEADROOM_EXHAUSTED", "PERSISTENT_PRIVATE_ROOT_INVALID",
            "SOURCE_SECURITY_CODE_INVALID", "SOURCE_NUMERIC_SHAPE_INVALID",
            "SOURCE_RESPONSE_NON_JSON", "SOURCE_ENVELOPE_INVALID",
            "SOURCE_ROW_BLOCK_INVALID", "SOURCE_SCHEMA_DRIFT",
            "PARTIAL_SOURCE_CALENDAR_SCOPE", "DUPLICATE_BASIC_INFO_SECURITY",
            "BASIC_INFO_IDENTITY_MISSING", "SOURCE_DAILY_DATE_MISMATCH",
            "SOURCE_DAILY_DUPLICATE_CODE", "SOURCE_SECURITY_MASTER_UNMAPPED",
            "COMMON_STOCK_MARKET_SCOPE_INVALID", "SOURCE_CAP_VOLUME_NEGATIVE",
            "SOURCE_COMMON_COUNT_INVALID", "UNAPPROVED_API_REQUEST",
            "OPENAPI_NON_200", "OPENAPI_RESPONSE_SIZE_LIMIT",
            "OPENAPI_REQUEST_FAILED", "OPENAPI_RESPONSE_EMPTY",
            "PREVIOUS_CHECKPOINT_INVALID", "PREVIOUS_CHECKPOINT_AUTHORITY_DRIFT",
            "PREVIOUS_CHECKPOINT_SCOPE_INVALID", "PREVIOUS_CHECKPOINT_RAW_MISMATCH",
            "NETWORK_REQUEST_BUDGET_EXHAUSTED",
        }
        reason = str(exc) if type(exc) is PrivateOpenAPIHistoryError else ""
        report["failure_reason"] = reason if reason in allowed else "UNCLASSIFIED"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2015-01-05")
    parser.add_argument("--end", default="2015-01-30")
    parser.add_argument("--max-requests", type=int, default=60)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    out = run(start=args.start, end=args.end,
              max_requests=args.max_requests, execute=args.execute)
    print("INDEXALERT_PRIVATE_KRX_OPENAPI_BATCH=" + json.dumps(out, sort_keys=True),
          flush=True)
    if args.execute and out["status"] != "PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED":
        raise SystemExit(1)
