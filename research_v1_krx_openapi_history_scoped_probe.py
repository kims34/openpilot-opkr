"""Consent-bound, *tiny* official KRX OPEN API historical readiness probe.

Only two previously approved KOSPI OPEN API services; 3 strictly pinned
trading dates, at most 6 GETs. Explicit manual-dispatch environment sentinel
is mandatory even with credentials. This module cannot contact KRX Data
Marketplace web-session endpoints, Kosdaq, non-approved APIs, broker or orders.

Raw provider rows, security identifiers, numeric securities data and AUTH_KEY
are NOT saved, logged or uploaded. Only non-secret aggregate counts, cryptographic
raw response fingerprints, date, schema identity and retrieval timestamps.
A successful probe is strictly NOT a full-history collection, PIT source
admission, halt-status evidence, a backtest, performance or live-trading pass.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping

import requests

CONSENT_FILE = Path("INDEXALERT_KRX_OPENAPI_HISTORY_USER_CONSENT_2026_10_12.json")
PINNED_CONNECTIVITY_FILE = Path("INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json")
OUTPUT = Path("research_results/krx_openapi_history_2015_2026_first_probe/summary.json")
ROOT_URL = "https://data-dbg.krx.co.kr/svc/apis/sto/"
ENDPOINTS = {
    "daily_trade": ROOT_URL + "stk_bydd_trd",
    "security_master": ROOT_URL + "stk_isu_base_info",
}
SAMPLE_DATES = ("20150105", "20260928", "20261001")
MANUAL_CONSENT_ENV = "KRX_HISTORY_SAMPLE_EXECUTE"
MANUAL_CONSENT_SENTINEL = "EXPLICIT_USER_APPROVED_20261012_OPENAPI_SAMPLE_ONLY"
MAX_BYTES_PER_RESPONSE = 12 * 1024 * 1024
REQUIRED = {
    "daily_trade": frozenset({
        "BAS_DD", "ISU_CD", "TDD_OPNPRC", "TDD_HGPRC",
        "TDD_LWPRC", "TDD_CLSPRC", "ACC_TRDVOL",
        "ACC_TRDVAL", "MKTCAP", "LIST_SHRS", "FLUC_RT"
    }),
    "security_master": frozenset({
        "ISU_CD", "ISU_SRT_CD", "ISU_NM", "LIST_DD",
        "MKT_TP_NM", "SECUGRP_NM", "KIND_STKCERT_TP_NM",
        "LIST_SHRS"
    }),
}
SYM = re.compile(r"[0-9A-Z]{6}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class KRXOpenAPIHistoricalSampleError(ValueError):
    """Use fixed safe codes only, never include credentials, row content or IDs."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(data: Any) -> bytes:
    return json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _date(value: str) -> date:
    if type(value) is not str or not re.fullmatch(r"[0-9]{8}", value):
        raise KRXOpenAPIHistoricalSampleError("DATE_NOT_CANONICAL")
    try:
        parsed = datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        raise KRXOpenAPIHistoricalSampleError("DATE_NOT_CANONICAL") from None
    if parsed.strftime("%Y%m%d") != value:
        raise KRXOpenAPIHistoricalSampleError("DATE_NOT_CANONICAL")
    return parsed


def _code(value: Any) -> str:
    if type(value) is not str:
        raise KRXOpenAPIHistoricalSampleError("SYMBOL_INVALID")
    value = value.strip().upper()
    if value.isdigit() and 1 <= len(value) <= 6:
        value = value.zfill(6)
    if not SYM.fullmatch(value):
        raise KRXOpenAPIHistoricalSampleError("SYMBOL_INVALID")
    return value


def _number(value: Any, *, integer: bool = False) -> Decimal:
    if type(value) not in (str, int, Decimal):
        raise KRXOpenAPIHistoricalSampleError("NUMERIC_FIELD_INVALID")
    if type(value) is str:
        value = value.strip().replace(",", "")
        if not re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?", value):
            raise KRXOpenAPIHistoricalSampleError("NUMERIC_FIELD_INVALID")
    try:
        n = Decimal(value)
    except (InvalidOperation, ValueError):
        raise KRXOpenAPIHistoricalSampleError("NUMERIC_FIELD_INVALID") from None
    if not n.is_finite() or (integer and n != n.to_integral_value()):
        raise KRXOpenAPIHistoricalSampleError("NUMERIC_FIELD_INVALID")
    return n


def _read_scoped_consents(
    *,
    consent_file: Path = CONSENT_FILE,
    connectivity_file: Path = PINNED_CONNECTIVITY_FILE,
) -> dict[str, Any]:
    try:
        consent_bytes = consent_file.read_bytes()
        connection_bytes = connectivity_file.read_bytes()
        consent = json.loads(consent_bytes)
        prior = json.loads(connection_bytes)
    except (OSError, UnicodeError, ValueError):
        raise KRXOpenAPIHistoricalSampleError("EVIDENCE_FILES_INVALID") from None
    approved_names = ["유가증권 종목기본정보", "유가증권 일별매매정보"]
    if (
        consent.get("evidence_id")
        != "INDEXALERT-KRX-OPENAPI-KOSPI-HISTORY-USER-CONSENT-2026-10-12-v1"
        or consent.get("authorization_source") != "USER_EXPLICIT_CHAT_APPROVAL"
        or consent.get("scope") != "NONCOMMERCIAL_PRIVATE_RESEARCH"
        or consent.get("user_approved_staged_historical_collection") is not True
        or consent.get("sample_dates") != list(SAMPLE_DATES)
        or consent.get("max_network_requests_first_stage") != 6
        or consent.get("approved_product_names") != approved_names
        or consent.get("api_endpoints") != ENDPOINTS
        or consent.get("approval_valid_from") != "2026-10-02"
        or consent.get("approval_valid_through") != "2027-10-01"
        or consent.get("first_stage_manual_dispatch_only") is not True
        or consent.get("normal_push_network_requests_allowed") is not False
        or any(consent.get(key) is not False for key in (
            "includes_kosdaq_apis", "includes_data_marketplace_authenticated_web_session",
            "includes_paid_products", "includes_independent_status_halt_delisting_source",
            "research_profitability_authorized", "sealed_holdout_authorized",
            "champion_change_authorized", "real_orders_authorized",
            "broker_permissions_change_authorized", "funds_movement_authorized",
            "exact_historical_pit_admitted"
        ))
        or consent.get("ordering") != "DISABLED"
    ):
        raise KRXOpenAPIHistoricalSampleError("USER_SCOPE_NOT_EXACT")
    for item, source_name in (
        ("daily_trade", "유가증권 일별매매정보"),
        ("security_master", "유가증권 종목기본정보"),
    ):
        service = (prior.get("services") or {}).get(item) or {}
        if (
            service.get("krx_service_name") != source_name
            or service.get("endpoint") != ENDPOINTS[item]
            or service.get("http_status") != 200
            or service.get("schema_ok") is not True
            or not REQUIRED[item].issubset(set(service.get("fields") or []))
            or not HEX64.fullmatch(str(service.get("response_payload_sha256") or ""))
        ):
            raise KRXOpenAPIHistoricalSampleError("PINNED_SERVICE_PROOF_MISMATCH")
    if prior.get("authentication", {}).get("route") != "KRX_OPENAPI":
        raise KRXOpenAPIHistoricalSampleError("PINNED_ROUTE_MISMATCH")
    return {
        "user_consent_sha256": _sha(consent_bytes),
        "pinned_connectivity_sha256": _sha(connection_bytes),
        "earliest_date": "2015-01-01",
        "latest_date": "2026-10-12",
    }


def _preflight(
    *,
    environment: Mapping[str, str],
    scope: Mapping[str, Any],
    today: date,
) -> dict[str, Any]:
    if (
        environment.get(MANUAL_CONSENT_ENV)
        != MANUAL_CONSENT_SENTINEL
    ):
        raise KRXOpenAPIHistoricalSampleError("MANUAL_EXECUTION_CONSENT_REQUIRED")
    key = environment.get("KRX_AUTH_KEY") or ""
    if type(key) is not str or not key.strip():
        raise KRXOpenAPIHistoricalSampleError("OPENAPI_AUTH_KEY_NOT_CONFIGURED")
    if today < date(2026, 10, 2) or today > date(2027, 10, 1):
        raise KRXOpenAPIHistoricalSampleError("API_APPROVAL_VALIDITY_DATE_EXCEEDED")
    if any(
        not (date.fromisoformat(scope["earliest_date"]) <= _date(day)
             <= date.fromisoformat(scope["latest_date"]))
        for day in SAMPLE_DATES
    ):
        raise KRXOpenAPIHistoricalSampleError("SAMPLE_DATE_OUT_OF_USER_SCOPE")
    return {"key": key.strip(), "dates": SAMPLE_DATES}


def _fetch(
    session: requests.Session,
    *,
    endpoint: str,
    key: str,
    day: str,
) -> tuple[bytes, str]:
    if endpoint not in ENDPOINTS.values() or day not in SAMPLE_DATES:
        raise KRXOpenAPIHistoricalSampleError("UNAUTHORIZED_ENDPOINT_OR_DATE")
    try:
        with session.get(
            endpoint, headers={"AUTH_KEY": key}, params={"basDd": day},
            timeout=20, allow_redirects=False, stream=True,
        ) as response:
            if response.status_code != 200:
                raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_HTTP_NOT_200")
            data = bytearray()
            for chunk in response.iter_content(chunk_size=65536):
                data.extend(chunk)
                if len(data) > MAX_BYTES_PER_RESPONSE:
                    raise KRXOpenAPIHistoricalSampleError("RESPONSE_EXCEEDS_SAFE_LIMIT")
    except requests.RequestException:
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_TRANSPORT_FAILURE") from None
    raw = bytes(data)
    if not raw:
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_RESPONSE_EMPTY")
    return raw, datetime.now(timezone.utc).isoformat()


def _rows(raw: bytes, service: str) -> tuple[list[dict[str, Any]], str]:
    try:
        data = json.loads(raw)
    except (UnicodeError, ValueError):
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_RESPONSE_NOT_JSON") from None
    if not isinstance(data, dict):
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_RESPONSE_NOT_OBJECT")
    blocks = [item for item in ("OutBlock_1", "output") if item in data]
    if len(blocks) != 1:
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_ROW_BLOCK_INVALID")
    rows = data[blocks[0]]
    if type(rows) is not list or not rows or any(type(r) is not dict or not r for r in rows):
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_ROW_BLOCK_EMPTY_OR_BAD")
    schema = set(rows[0])
    if (
        not REQUIRED[service].issubset(schema)
        or any(set(r) != schema for r in rows)
    ):
        raise KRXOpenAPIHistoricalSampleError("OFFICIAL_API_SCHEMA_DRIFT")
    return rows, _sha(_canonical(sorted(schema)))


def _inspect_pair(
    *,
    daily_rows: list[dict[str, Any]],
    master_rows: list[dict[str, Any]],
    day: str,
) -> dict[str, Any]:
    master: dict[str, dict[str, Any]] = {}
    for row in master_rows:
        symbol = _code(row["ISU_SRT_CD"])
        if symbol in master:
            raise KRXOpenAPIHistoricalSampleError("DUPLICATE_MASTER_CODE")
        if not row.get("ISU_CD") or not row.get("ISU_NM"):
            raise KRXOpenAPIHistoricalSampleError("MASTER_IDENTITY_MISSING")
        master[symbol] = row
    seen: set[str] = set()
    common = zero_activity = malformed_shape = normal = 0
    for row in daily_rows:
        if row.get("BAS_DD") != day:
            raise KRXOpenAPIHistoricalSampleError("DAILY_REQUEST_DATE_MISMATCH")
        symbol = _code(row["ISU_CD"])
        if symbol in seen:
            raise KRXOpenAPIHistoricalSampleError("DUPLICATE_DAILY_CODE")
        seen.add(symbol)
        if symbol not in master:
            raise KRXOpenAPIHistoricalSampleError("UNJOINED_DAILY_SECURITY_MASTER")
        m = master[symbol]
        if m["SECUGRP_NM"] != "주권" or m["KIND_STKCERT_TP_NM"] != "보통주":
            continue
        if m["MKT_TP_NM"] not in ("KOSPI", "유가증권"):
            raise KRXOpenAPIHistoricalSampleError("COMMON_STOCK_MARKET_MISMATCH")
        common += 1
        o, h, l, c = (
            _number(row[f]) for f in
            ("TDD_OPNPRC", "TDD_HGPRC", "TDD_LWPRC", "TDD_CLSPRC")
        )
        vol = _number(row["ACC_TRDVOL"], integer=True)
        val = _number(row["ACC_TRDVAL"], integer=True)
        cap = _number(row["MKTCAP"])
        shares = _number(row["LIST_SHRS"], integer=True)
        if min(vol, val, cap, shares) < 0:
            raise KRXOpenAPIHistoricalSampleError("NEGATIVE_ACTIVITY_OR_CAPITAL")
        if min(o, h, l, c) <= 0:
            if (
                o == h == l == 0 and c > 0
                and vol == val == 0
            ):
                zero_activity += 1
            else:
                malformed_shape += 1
        elif l <= o <= h and l <= c <= h:
            normal += 1
        else:
            malformed_shape += 1
    if not common:
        raise KRXOpenAPIHistoricalSampleError("NO_COMMON_KOSPI_ROWS")
    if common != normal + zero_activity + malformed_shape:
        raise KRXOpenAPIHistoricalSampleError("COMMON_STOCK_COUNTS_INCONSISTENT")
    return {
        "master_rows_observed": len(master_rows),
        "daily_rows_observed": len(daily_rows),
        "matched_common_stock_rows": common,
        "common_positive_coherent_ohlc_rows": normal,
        "common_nonpositive_zero_activity_shape_rows": zero_activity,
        "common_other_invalid_ohlc_shape_rows": malformed_shape,
        "full_trading_status_independently_verified": False,
        "remaining_symbols_approved_for_alpha": False,
        "held_position_economics_verified": False,
    }


def run(
    *,
    env: Mapping[str, str] | None = None,
    session: requests.Session | None = None,
    consent_file: Path = CONSENT_FILE,
    connectivity_file: Path = PINNED_CONNECTIVITY_FILE,
    now: datetime | None = None,
) -> dict:
    result = {
        "classification": "KRX_OPENAPI_APPROVED_KOSPI_2015_2026_SMALL_READONLY_PROBE_ONLY",
        "source_status": "BLOCKED_NO_NETWORK",
        "approved_product_scope": list(ENDPOINTS),
        "sample_dates": list(SAMPLE_DATES),
        "request_count": 0,
        "source_data_bytes_or_securities_saved": False,
        "private_full_history_acquisition_complete": False,
        "complete_historical_calendar_coverage_verified": False,
        "official_halt_delisting_status_verified": False,
        "exact_pit_publication_times_verified": False,
        "historical_m20_market_cap_pit_verified": False,
        "source_gate_full_admission_verified": False,
        "performance_run_authorized": False,
        "sealed_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "ordering": "DISABLED",
    }
    stage = "CONSENT_AND_PINNED_SERVICE_PROOF"
    environment = os.environ if env is None else env
    try:
        evidence = _read_scoped_consents(
            consent_file=consent_file, connectivity_file=connectivity_file
        )
        result["user_consent_sha256"] = evidence["user_consent_sha256"]
        result["pinned_connectivity_sha256"] = evidence["pinned_connectivity_sha256"]
        stage = "MANUAL_EXECUTION_PREFLIGHT"
        today = (now or datetime.now(timezone.utc)).date()
        authorized = _preflight(environment=environment, scope=evidence, today=today)
        if session is None:
            session = requests.Session()
        stage = "APPROVED_SERVICE_DATE_PROBE"
        receipts: list[dict[str, Any]] = []
        for day in authorized["dates"]:
            samples = {}
            for service in ("daily_trade", "security_master"):
                raw, stamp = _fetch(
                    session, endpoint=ENDPOINTS[service],
                    key=authorized["key"], day=day,
                )
                result["request_count"] += 1
                rows, schema_sha = _rows(raw, service)
                samples[service] = rows
                receipts.append({
                    "date": day, "service": service,
                    "endpoint_path": ENDPOINTS[service].removeprefix(ROOT_URL),
                    "retrieved_at_utc": stamp,
                    "raw_sha256": _sha(raw),
                    "schema_sha256": schema_sha,
                    "row_count": len(rows),
                })
            structural = _inspect_pair(
                daily_rows=samples["daily_trade"],
                master_rows=samples["security_master"],
                day=day,
            )
            result.setdefault("session_aggregate_diagnostics", []).append({
                "date": day, **structural,
                "session_source_or_pit_admitted": False,
            })
        result["request_metadata_receipts"] = receipts
        result["request_batch_fingerprint_sha256"] = _sha(_canonical(receipts))
        result["source_status"] = "SCOPED_OFFICIAL_SAMPLE_COMPLETED_NOT_ADMITTED"
    except Exception as exc:
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["failure_stage"] = stage
        known = {
            "EVIDENCE_FILES_INVALID", "USER_SCOPE_NOT_EXACT",
            "PINNED_SERVICE_PROOF_MISMATCH", "PINNED_ROUTE_MISMATCH",
            "MANUAL_EXECUTION_CONSENT_REQUIRED", "OPENAPI_AUTH_KEY_NOT_CONFIGURED",
            "API_APPROVAL_VALIDITY_DATE_EXCEEDED", "SAMPLE_DATE_OUT_OF_USER_SCOPE",
            "UNAUTHORIZED_ENDPOINT_OR_DATE", "OFFICIAL_API_HTTP_NOT_200",
            "RESPONSE_EXCEEDS_SAFE_LIMIT", "OFFICIAL_API_TRANSPORT_FAILURE",
            "OFFICIAL_API_RESPONSE_EMPTY", "OFFICIAL_API_RESPONSE_NOT_JSON",
            "OFFICIAL_API_RESPONSE_NOT_OBJECT", "OFFICIAL_API_ROW_BLOCK_INVALID",
            "OFFICIAL_API_ROW_BLOCK_EMPTY_OR_BAD", "OFFICIAL_API_SCHEMA_DRIFT",
            "DAILY_REQUEST_DATE_MISMATCH", "DUPLICATE_DAILY_CODE",
            "DUPLICATE_MASTER_CODE", "UNJOINED_DAILY_SECURITY_MASTER",
            "MASTER_IDENTITY_MISSING", "COMMON_STOCK_MARKET_MISMATCH",
            "NO_COMMON_KOSPI_ROWS", "COMMON_STOCK_COUNTS_INCONSISTENT",
            "NUMERIC_FIELD_INVALID", "NEGATIVE_ACTIVITY_OR_CAPITAL",
            "SYMBOL_INVALID", "DATE_NOT_CANONICAL",
        }
        reason = str(exc) if type(exc) is KRXOpenAPIHistoricalSampleError else ""
        result["failure_reason_code"] = reason if reason in known else "UNCLASSIFIED"
        # Never retain half-complete batch evidence as if it were valid.
        result.pop("session_aggregate_diagnostics", None)
        result.pop("request_metadata_receipts", None)
        result.pop("request_batch_fingerprint_sha256", None)
    return result


if __name__ == "__main__":
    report = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    print("INDEXALERT_KRX_OPENAPI_HISTORY_SAMPLE=" + json.dumps(report, sort_keys=True), flush=True)
