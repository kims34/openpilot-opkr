"""Network-free KRX OpenAPI current-session source normalizer.

Consumes already-retrieved raw responses from the separately approved KRX
OpenAPI security-master and KOSPI daily-trade services. It never performs a
network request and never treats retrieval time as historical publication time.

The output can feed the label-free prospective input builder structurally, but
source/finality/chronology admission remain independent and false.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
import re
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research_v1_krx_historical_fetchers import parse_openapi_raw
from research_v1_krx_official_status import (
    KRX_OPENAPI_BASIC_SOURCE,
    KRXOfficialStatusError,
    normalise_basic_info,
)
from research_v1_krx_openapi_connectivity_evidence import (
    EXPECTED_SERVICES,
    validate_evidence,
)


CLASSIFICATION = "KRX_OPENAPI_CURRENT_SESSION_SOURCE_CANDIDATE_NOT_ADMITTED"
ACCESS_ROUTE = "KRX_OPENAPI_APPROVED_SERVICE"
DAILY_DATASET = "stk_bydd_trd"
MASTER_DATASET = "stk_isu_base_info"
AVAILABILITY_SEMANTICS = (
    "OBSERVED_AVAILABLE_BY_RETRIEVAL_TIME_NOT_OFFICIAL_PUBLICATION_TIME"
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")

_DAILY_FIELDS = frozenset(EXPECTED_SERVICES["daily_trade"]["required_fields"])
_MASTER_FIELDS = frozenset(EXPECTED_SERVICES["security_master"]["required_fields"])
_RECEIPT_FIELDS = (
    "classification", "access_route", "session", "request_bas_dd_claimed",
    "daily_dataset_identifier", "master_dataset_identifier",
    "daily_endpoint_suffix", "master_endpoint_suffix",
    "daily_raw_sha256", "master_raw_sha256", "normalized_panel_sha256",
    "connectivity_evidence_sha256", "daily_retrieved_at", "master_retrieved_at",
    "observed_available_by", "availability_semantics",
    "daily_rows_observed", "master_rows_observed", "common_stock_rows",
    "daily_symbols_all_mapped_to_master", "common_stock_identity_structurally_joined",
    "current_session_finality_verified", "complete_universe_verified",
    "independent_source_admission_verified", "signal_generation_complete",
    "decision_recorded", "fresh_alpha_observation_admitted",
    "live_order_authorized",
)


class KRXProspectiveOpenAPISourceError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _aware(value: Any, field: str) -> pd.Timestamp:
    if not isinstance(value, (str, datetime, pd.Timestamp)) or pd.isna(value):
        raise KRXProspectiveOpenAPISourceError(
            f"{field} must be an explicit timezone-aware timestamp"
        )
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise KRXProspectiveOpenAPISourceError(f"{field} is invalid") from exc
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXProspectiveOpenAPISourceError(f"{field} must be timezone-aware")
    return ts.tz_convert("UTC")


def _session(value: Any) -> tuple[str, str, pd.Timestamp]:
    if type(value) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise KRXProspectiveOpenAPISourceError(
            "expected_session must be canonical YYYY-MM-DD"
        )
    try:
        day = pd.Timestamp(value)
    except ValueError as exc:
        raise KRXProspectiveOpenAPISourceError("expected_session is invalid") from exc
    if day.strftime("%Y-%m-%d") != value:
        raise KRXProspectiveOpenAPISourceError("expected_session is invalid")
    return value, day.strftime("%Y%m%d"), day


def _sha256(raw: bytes, field: str) -> str:
    if not isinstance(raw, (bytes, bytearray)) or not raw:
        raise KRXProspectiveOpenAPISourceError(f"{field} must be nonempty raw bytes")
    return hashlib.sha256(bytes(raw)).hexdigest()


def _short_code(series: pd.Series, field: str) -> pd.Series:
    raw = series.astype("string").fillna("").str.strip().str.upper()
    numeric = raw.str.fullmatch(r"[0-9]{1,6}", na=False)
    alnum6 = raw.str.fullmatch(r"[A-Z0-9]{6}", na=False)
    out = pd.Series("", index=raw.index, dtype="string")
    out.loc[numeric] = raw.loc[numeric].str.zfill(6)
    out.loc[~numeric & alnum6] = raw.loc[~numeric & alnum6]
    if out.eq("").any():
        raise KRXProspectiveOpenAPISourceError(
            f"{field} contains invalid KRX short issue code"
        )
    return out


def _number(series: pd.Series, field: str) -> pd.Series:
    if series.map(lambda value: isinstance(value, (bool, np.bool_))).any():
        raise KRXProspectiveOpenAPISourceError(f"{field} contains boolean")
    text = series.astype("string").str.strip().str.replace(",", "", regex=False)
    out = pd.to_numeric(text, errors="coerce")
    if out.isna().any() or not np.isfinite(out.to_numpy(dtype=float)).all():
        raise KRXProspectiveOpenAPISourceError(f"{field} contains nonnumeric/nonfinite value")
    return out.astype(float)


def _frame_sha256(panel: pd.DataFrame) -> str:
    records = []
    for row in panel.sort_values(["decision_date", "symbol"]).itertuples(index=False):
        records.append({
            "decision_date": pd.Timestamp(row.decision_date).strftime("%Y-%m-%d"),
            "symbol": str(row.symbol),
            "standard_code": str(row.standard_code),
            "open": float(row.open), "high": float(row.high),
            "low": float(row.low), "close": float(row.close),
            "volume": float(row.volume), "value": float(row.value),
            "krx_change_return": float(row.krx_change_return),
            "available_at": str(row.available_at),
        })
    return hashlib.sha256(_canonical(records)).hexdigest()


def build_current_session_openapi_source(
    *,
    daily_raw: bytes,
    master_raw: bytes,
    expected_session: str,
    daily_retrieved_at: str,
    master_retrieved_at: str,
    connectivity_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Normalize exact KRX OpenAPI daily/master responses into one safe panel."""
    session, bas_dd, session_day = _session(expected_session)
    daily_seen = _aware(daily_retrieved_at, "daily_retrieved_at")
    master_seen = _aware(master_retrieved_at, "master_retrieved_at")
    session_start = session_day.tz_localize("Asia/Seoul").tz_convert("UTC")
    if daily_seen < session_start or master_seen < session_start:
        raise KRXProspectiveOpenAPISourceError(
            "retrieval timestamp cannot precede the requested KRX session"
        )
    observed_available_by = max(daily_seen, master_seen)

    try:
        evidence = validate_evidence(connectivity_evidence)
    except Exception as exc:
        raise KRXProspectiveOpenAPISourceError(
            "invalid pinned KRX OpenAPI connectivity evidence"
        ) from exc
    services = connectivity_evidence.get("services") or {}
    daily_service = services.get("daily_trade") or {}
    master_service = services.get("security_master") or {}
    if not str(daily_service.get("endpoint") or "").endswith("/stk_bydd_trd"):
        raise KRXProspectiveOpenAPISourceError("daily-trade endpoint identity mismatch")
    if not str(master_service.get("endpoint") or "").endswith("/stk_isu_base_info"):
        raise KRXProspectiveOpenAPISourceError("security-master endpoint identity mismatch")

    try:
        daily = parse_openapi_raw(bytes(daily_raw))
        master = parse_openapi_raw(bytes(master_raw))
    except Exception as exc:
        raise KRXProspectiveOpenAPISourceError("invalid KRX OpenAPI raw response") from exc
    if daily.empty or master.empty:
        raise KRXProspectiveOpenAPISourceError("current-session OpenAPI response is empty")
    if daily.columns.duplicated().any() or master.columns.duplicated().any():
        raise KRXProspectiveOpenAPISourceError("OpenAPI response has duplicate columns")
    missing_daily = sorted(_DAILY_FIELDS - set(daily.columns))
    missing_master = sorted(_MASTER_FIELDS - set(master.columns))
    if missing_daily:
        raise KRXProspectiveOpenAPISourceError(
            f"daily-trade response missing fields: {missing_daily}"
        )
    if missing_master:
        raise KRXProspectiveOpenAPISourceError(
            f"security-master response missing fields: {missing_master}"
        )

    raw_dates = daily["BAS_DD"].astype("string").str.strip()
    if not raw_dates.eq(bas_dd).all():
        raise KRXProspectiveOpenAPISourceError(
            "daily-trade rows do not all match the exact requested session"
        )
    daily_symbol = _short_code(daily["ISU_CD"], "daily.ISU_CD")
    if daily_symbol.duplicated().any():
        raise KRXProspectiveOpenAPISourceError("duplicate daily-trade short issue code")

    try:
        identity = normalise_basic_info(
            master,
            asof_date=session_day,
            available_at=master_seen.isoformat(),
            source=KRX_OPENAPI_BASIC_SOURCE,
        )
    except KRXOfficialStatusError as exc:
        raise KRXProspectiveOpenAPISourceError(
            "invalid official security-master identity"
        ) from exc
    master_symbols = set(identity["symbol"].astype(str))
    missing_map = sorted(set(daily_symbol.astype(str)) - master_symbols)
    if missing_map:
        raise KRXProspectiveOpenAPISourceError(
            "daily-trade symbols missing from same-session security master"
        )

    daily_norm = pd.DataFrame({
        "decision_date": pd.Timestamp(session),
        "symbol": daily_symbol,
        "open": _number(daily["TDD_OPNPRC"], "TDD_OPNPRC"),
        "high": _number(daily["TDD_HGPRC"], "TDD_HGPRC"),
        "low": _number(daily["TDD_LWPRC"], "TDD_LWPRC"),
        "close": _number(daily["TDD_CLSPRC"], "TDD_CLSPRC"),
        "volume": _number(daily["ACC_TRDVOL"], "ACC_TRDVOL"),
        "value": _number(daily["ACC_TRDVAL"], "ACC_TRDVAL"),
        # KRX FLUC_RT is a percentage value. Prospective PIT features require
        # a decimal return, so 1.25 becomes 0.0125.
        "krx_change_return": _number(daily["FLUC_RT"], "FLUC_RT") / 100.0,
    })
    joined = daily_norm.merge(
        identity[[
            "symbol", "standard_code", "market_type_official",
            "security_group_official", "stock_type_official",
            "common_stock_identity_official",
        ]],
        on="symbol", how="left", validate="one_to_one",
    )
    if joined["standard_code"].isna().any():
        raise KRXProspectiveOpenAPISourceError("security-master join is incomplete")
    common = joined[joined["common_stock_identity_official"].eq(True)].copy()
    if common.empty:
        raise KRXProspectiveOpenAPISourceError("no KOSPI common-stock rows")
    market = common["market_type_official"].astype(str).str.upper()
    if not (
        market.str.contains("KOSPI", na=False)
        | common["market_type_official"].astype(str).str.contains("유가증권", na=False)
    ).all():
        raise KRXProspectiveOpenAPISourceError("non-KOSPI row in common-stock scope")
    if (common[["open", "high", "low", "close"]] <= 0).any().any():
        raise KRXProspectiveOpenAPISourceError(
            "common-stock current-session OHLC contains nonpositive value; "
            "do not silently drop an unknown/halted row"
        )
    if (common[["volume", "value"]] < 0).any().any():
        raise KRXProspectiveOpenAPISourceError("negative volume/value")
    if (
        (common["low"] > common[["open", "close"]].min(axis=1))
        | (common["high"] < common[["open", "close"]].max(axis=1))
        | (common["low"] > common["high"])
    ).any():
        raise KRXProspectiveOpenAPISourceError("inconsistent current-session OHLC")
    if (common["krx_change_return"] <= -1.0).any():
        raise KRXProspectiveOpenAPISourceError("invalid KRX fluctuation return")

    common["available_at"] = observed_available_by.isoformat()
    common["source_route"] = ACCESS_ROUTE
    common["source_dataset"] = DAILY_DATASET
    common["availability_semantics"] = AVAILABILITY_SEMANTICS
    panel_columns = [
        "decision_date", "symbol", "standard_code",
        "open", "high", "low", "close", "volume", "value",
        "krx_change_return", "available_at", "source_route",
        "source_dataset", "availability_semantics",
    ]
    panel = common[panel_columns].sort_values("symbol").reset_index(drop=True)
    panel_sha = _frame_sha256(panel)
    daily_sha = _sha256(daily_raw, "daily_raw")
    master_sha = _sha256(master_raw, "master_raw")
    receipt_body = {
        "classification": CLASSIFICATION,
        "access_route": ACCESS_ROUTE,
        "session": session,
        "request_bas_dd_claimed": bas_dd,
        "daily_dataset_identifier": DAILY_DATASET,
        "master_dataset_identifier": MASTER_DATASET,
        "daily_endpoint_suffix": "/stk_bydd_trd",
        "master_endpoint_suffix": "/stk_isu_base_info",
        "daily_raw_sha256": daily_sha,
        "master_raw_sha256": master_sha,
        "normalized_panel_sha256": panel_sha,
        "connectivity_evidence_sha256": evidence["evidence_fingerprint_sha256"],
        "daily_retrieved_at": daily_seen.isoformat(),
        "master_retrieved_at": master_seen.isoformat(),
        "observed_available_by": observed_available_by.isoformat(),
        "availability_semantics": AVAILABILITY_SEMANTICS,
        "daily_rows_observed": int(len(daily)),
        "master_rows_observed": int(len(master)),
        "common_stock_rows": int(len(panel)),
        "daily_symbols_all_mapped_to_master": True,
        "common_stock_identity_structurally_joined": True,
        "current_session_finality_verified": False,
        "complete_universe_verified": False,
        "independent_source_admission_verified": False,
        "signal_generation_complete": False,
        "decision_recorded": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }
    receipt_sha = hashlib.sha256(_canonical(receipt_body)).hexdigest()
    return {
        **receipt_body,
        "source_receipt_sha256": receipt_sha,
        "panel": panel,
    }


def validate_source_receipt(source: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(source, Mapping):
        raise KRXProspectiveOpenAPISourceError("source receipt must be an object")
    receipt = {field: source.get(field) for field in _RECEIPT_FIELDS}
    if set(source) - (set(_RECEIPT_FIELDS) | {"source_receipt_sha256", "panel"}):
        raise KRXProspectiveOpenAPISourceError("source receipt has unsupported fields")
    for field in (
        "daily_raw_sha256", "master_raw_sha256", "normalized_panel_sha256",
        "connectivity_evidence_sha256", "source_receipt_sha256",
    ):
        value = source.get(field)
        if type(value) is not str or not HEX64.fullmatch(value):
            raise KRXProspectiveOpenAPISourceError(f"{field} must be lowercase SHA-256")
    if source.get("classification") != CLASSIFICATION:
        raise KRXProspectiveOpenAPISourceError("source classification mismatch")
    if source.get("access_route") != ACCESS_ROUTE:
        raise KRXProspectiveOpenAPISourceError("source route mismatch")
    if source.get("availability_semantics") != AVAILABILITY_SEMANTICS:
        raise KRXProspectiveOpenAPISourceError("availability semantics mismatch")
    if source.get("daily_dataset_identifier") != DAILY_DATASET:
        raise KRXProspectiveOpenAPISourceError("daily dataset mismatch")
    if source.get("master_dataset_identifier") != MASTER_DATASET:
        raise KRXProspectiveOpenAPISourceError("master dataset mismatch")
    for field in ("daily_rows_observed", "master_rows_observed", "common_stock_rows"):
        if type(source.get(field)) is not int or source[field] <= 0:
            raise KRXProspectiveOpenAPISourceError(f"{field} must be positive exact integer")
    for field in (
        "daily_symbols_all_mapped_to_master", "common_stock_identity_structurally_joined",
    ):
        if source.get(field) is not True:
            raise KRXProspectiveOpenAPISourceError(f"{field} must be true")
    for field in (
        "current_session_finality_verified", "complete_universe_verified",
        "independent_source_admission_verified", "signal_generation_complete",
        "decision_recorded", "fresh_alpha_observation_admitted",
        "live_order_authorized",
    ):
        if source.get(field) is not False:
            raise KRXProspectiveOpenAPISourceError(f"{field} must remain exact false")
    actual = hashlib.sha256(_canonical(receipt)).hexdigest()
    if source["source_receipt_sha256"] != actual:
        raise KRXProspectiveOpenAPISourceError("source receipt fingerprint mismatch")
    panel = source.get("panel")
    if panel is not None:
        if not isinstance(panel, pd.DataFrame) or panel.empty:
            raise KRXProspectiveOpenAPISourceError("panel must be a nonempty DataFrame")
        if _frame_sha256(panel) != source["normalized_panel_sha256"]:
            raise KRXProspectiveOpenAPISourceError("normalized panel fingerprint mismatch")
    return {
        "valid": True,
        "source_receipt_sha256": actual,
        "independent_source_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }
