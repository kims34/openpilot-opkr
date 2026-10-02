"""Sanitized, read-only KRX Open API connectivity/schema probe.

This module is operational plumbing only.  It never submits orders, never
changes model/promotion state, and never treats connectivity as research
admission.  The issued KRX key is read only from the process environment and is
never returned or logged.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import requests

AUTH_ENV = "KRX_AUTH_KEY"
SEOUL = ZoneInfo("Asia/Seoul")
TIMEOUT_SECONDS = 12

ENDPOINTS = {
    "security_master": {
        "url": "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info",
        "expected_fields": {
            "ISU_CD",
            "ISU_SRT_CD",
            "ISU_NM",
            "ISU_ABBRV",
            "ISU_ENG_NM",
            "LIST_DD",
            "MKT_TP_NM",
            "SECUGRP_NM",
            "SECT_TP_NM",
            "KIND_STKCERT_TP_NM",
            "PARVAL",
            "LIST_SHRS",
        },
    },
    "daily_trade": {
        "url": "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd",
        "expected_fields": {
            "BAS_DD",
            "ISU_CD",
            "ISU_NM",
            "MKT_NM",
            "SECT_TP_NM",
            "TDD_CLSPRC",
            "CMPPREVDD_PRC",
            "FLUC_RT",
            "TDD_OPNPRC",
            "TDD_HGPRC",
            "TDD_LWPRC",
            "ACC_TRDVOL",
            "ACC_TRDVAL",
            "MKTCAP",
            "LIST_SHRS",
        },
    },
}

_LOCK = threading.Lock()
_STATE: dict[str, Any] = {
    "ok": False,
    "probe_completed": False,
    "auth_key_present": False,
    "purpose": "KRX read-only connectivity/schema verification only",
    "promotion_authority": False,
    "krx_gate_closed": False,
    "sealed_holdout_authorized": False,
    "live_trading_authorized": False,
    "basDd": None,
    "endpoints": {},
}


def _candidate_dates(days: int = 8) -> list[str]:
    today = datetime.now(SEOUL).date()
    return [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(1, days + 1)]


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _safe_result(
    *,
    ok: bool,
    method: str,
    http_status: int | None,
    rows: int = 0,
    fields: set[str] | None = None,
    schema_ok: bool = False,
    error: str | None = None,
    observed_at: str | None = None,
    schema_sha256: str | None = None,
    payload_sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "ok": bool(ok),
        "method": method,
        "http_status": http_status,
        "json_parsed": error not in {"invalid_json"},
        "row_count": int(rows),
        "fields": sorted(fields or set()),
        "schema_ok": bool(schema_ok),
        "observed_at": observed_at,
        "response_schema_sha256": schema_sha256,
        "response_payload_sha256": payload_sha256,
        "error": error,
    }


def _attempt(session: Any, method: str, url: str, key: str, bas_dd: str, expected: set[str]) -> dict[str, Any]:
    headers = {"AUTH_KEY": key, "Accept": "application/json"}
    try:
        if method == "GET":
            response = session.get(
                url,
                headers=headers,
                params={"basDd": bas_dd},
                timeout=TIMEOUT_SECONDS,
            )
        else:
            response = session.post(
                url,
                headers={**headers, "Content-Type": "application/json"},
                json={"basDd": bas_dd},
                timeout=TIMEOUT_SECONDS,
            )
    except Exception as exc:
        return _safe_result(
            ok=False,
            method=method,
            http_status=None,
            error=f"request_error:{type(exc).__name__}",
        )

    status = int(getattr(response, "status_code", 0) or 0)
    if status != 200:
        return _safe_result(
            ok=False,
            method=method,
            http_status=status,
            error="http_status",
        )

    try:
        payload = response.json()
    except Exception:
        return _safe_result(
            ok=False,
            method=method,
            http_status=status,
            error="invalid_json",
        )

    rows = payload.get("OutBlock_1") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return _safe_result(
            ok=False,
            method=method,
            http_status=status,
            error="missing_outblock",
        )

    fields = set(rows[0].keys()) if rows and isinstance(rows[0], dict) else set()
    schema_ok = bool(rows) and expected.issubset(fields)
    observed_at = datetime.now(timezone.utc).isoformat()
    schema_sha256 = _canonical_sha256(sorted(fields))
    payload_sha256 = _canonical_sha256(payload)
    return _safe_result(
        ok=bool(rows) and schema_ok,
        method=method,
        http_status=status,
        rows=len(rows),
        fields=fields,
        schema_ok=schema_ok,
        observed_at=observed_at,
        schema_sha256=schema_sha256,
        payload_sha256=payload_sha256,
        error=None if rows and schema_ok else ("empty_rows" if not rows else "schema_mismatch"),
    )


def _fetch(session: Any, url: str, key: str, bas_dd: str, expected: set[str]) -> dict[str, Any]:
    # Historical KRX examples use query-string GET while newer integrations may
    # present JSON-body POST examples.  Both are read-only; try GET first and
    # use POST only as a compatibility fallback.
    first = _attempt(session, "GET", url, key, bas_dd, expected)
    if first["ok"]:
        return first
    if first.get("http_status") in {401, 403}:
        return first
    second = _attempt(session, "POST", url, key, bas_dd, expected)
    return second if second["ok"] else {
        **second,
        "get_attempt": {
            "http_status": first.get("http_status"),
            "error": first.get("error"),
        },
    }


def run_probe(*, session: Any | None = None, candidate_dates: list[str] | None = None) -> dict[str, Any]:
    key = os.getenv(AUTH_ENV, "").strip()
    base = {
        "ok": False,
        "probe_completed": True,
        "auth_key_present": bool(key),
        "purpose": "KRX read-only connectivity/schema verification only",
        "promotion_authority": False,
        "krx_gate_closed": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "basDd": None,
        "probe_observed_at": None,
        "endpoints": {},
    }
    if not key:
        base["error"] = "missing_auth_key"
        return base

    client = session or requests.Session()
    dates = candidate_dates or _candidate_dates()
    last: dict[str, Any] = {}

    for bas_dd in dates:
        current: dict[str, Any] = {}
        for name, spec in ENDPOINTS.items():
            current[name] = _fetch(
                client,
                str(spec["url"]),
                key,
                bas_dd,
                set(spec["expected_fields"]),
            )
        last = current
        if all(row.get("ok") for row in current.values()):
            base.update({"ok": True, "basDd": bas_dd, "probe_observed_at": datetime.now(timezone.utc).isoformat(), "endpoints": current})
            return base

        # Authentication rejection is date-independent; fail closed immediately.
        statuses = {row.get("http_status") for row in current.values()}
        if 401 in statuses or 403 in statuses:
            break

    base.update({"probe_observed_at": datetime.now(timezone.utc).isoformat(), "endpoints": last, "error": "no_verified_business_date"})
    return base


def refresh_probe() -> dict[str, Any]:
    global _STATE
    result = run_probe()
    with _LOCK:
        _STATE = result
        return dict(_STATE)


def get_probe_state() -> dict[str, Any]:
    with _LOCK:
        return dict(_STATE)


def attach(app: Any) -> None:
    if getattr(app.state, "krx_readonly_probe_attached", False):
        return
    app.state.krx_readonly_probe_attached = True

    @app.on_event("startup")
    def _krx_probe_startup() -> None:
        refresh_probe()

    @app.get("/krx-health")
    def krx_health() -> dict[str, Any]:
        # Cached only: requesting this endpoint never triggers another KRX call.
        return get_probe_state()
