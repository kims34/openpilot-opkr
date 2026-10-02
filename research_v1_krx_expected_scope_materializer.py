"""Offline materializer for independently attested KRX expected scopes.

The caller supplies already-acquired official OpenAPI frames. This module never
performs network access and never creates trading dates, securities, or zero
rows that are absent from the official attestation inputs.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

import pandas as pd

from research_v1_krx_expected_scope_attestation import CONTRACT_ID, validate_file


class KRXExpectedScopeMaterializerError(ValueError):
    pass


DAILY_REQUIRED = {
    "BAS_DD", "ISU_CD", "ISU_NM", "MKT_NM",
}
MASTER_REQUIRED = {
    "ISU_CD", "ISU_SRT_CD", "ISU_NM", "LIST_DD",
    "MKT_TP_NM", "SECUGRP_NM", "KIND_STKCERT_TP_NM",
}
COMMON_SECURITY_GROUP = "주권"
COMMON_STOCK_KIND = "보통주"


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXExpectedScopeMaterializerError(msg)


def _sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _yyyymmdd(value: Any, field: str) -> str:
    text = re.sub(r"[^0-9]", "", str(value or ""))
    _require(len(text) == 8, f"{field} must be YYYYMMDD")
    try:
        pd.to_datetime(text, format="%Y%m%d", errors="raise")
    except Exception as exc:
        raise KRXExpectedScopeMaterializerError(f"{field} invalid") from exc
    return text


def _standard(value: Any) -> str:
    text = str(value or "").strip().upper()
    _require(bool(re.fullmatch(r"[0-9A-Z]{10,20}", text)), "invalid ISU_CD")
    return text


def _short(value: Any) -> str:
    text = re.sub(r"\.0$", "", str(value or "").strip())
    if text.isdigit():
        text = text.zfill(6)
    _require(bool(re.fullmatch(r"[0-9A-Z]{6,12}", text)), "invalid ISU_SRT_CD")
    return text


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    _require(not missing, f"{label} missing columns: {missing}")


def materialize_one_date(
    *,
    requested_date: str,
    daily_trade: pd.DataFrame,
    security_master: pd.DataFrame | None,
) -> dict[str, Any]:
    """Create same-date expected keys from official attestation inputs only."""
    validate_file()
    day = _yyyymmdd(requested_date, "requested_date")

    if daily_trade is None:
        raise KRXExpectedScopeMaterializerError("daily_trade frame is required")
    _require_columns(daily_trade, DAILY_REQUIRED, "daily_trade")

    if daily_trade.empty:
        _require(
            security_master is None or security_master.empty,
            "empty daily-trade date must not carry an identity snapshot into scope",
        )
        return {
            "contract_id": CONTRACT_ID,
            "requested_date": day,
            "official_trading_date_observed": False,
            "daily_trade_rows": 0,
            "security_master_rows": 0,
            "investor_expected_scope": pd.DataFrame(
                columns=["event_date","symbol","isu_cd"]
            ),
            "status_expected_scope": pd.DataFrame(
                columns=["snapshot_date","symbol","isu_cd"]
            ),
            "network_request_attempted": False,
        }

    dates = {_yyyymmdd(v, "BAS_DD") for v in daily_trade["BAS_DD"]}
    _require(dates == {day}, "daily-trade BAS_DD does not exactly match requested date")

    _require(security_master is not None, "same-date security_master required for non-empty daily date")
    _require_columns(security_master, MASTER_REQUIRED, "security_master")
    _require(not security_master.empty, "same-date security_master is empty")

    master = security_master.copy()
    master["isu_cd"] = master["ISU_CD"].map(_standard)
    master["symbol"] = master["ISU_SRT_CD"].map(_short)
    master["security_group"] = master["SECUGRP_NM"].astype(str).str.strip()
    master["stock_kind"] = master["KIND_STKCERT_TP_NM"].astype(str).str.strip()
    master["market_name"] = master["MKT_TP_NM"].astype(str).str.strip()
    _require(master["market_name"].ne("").all(), "security_master market identity missing")

    common = master[
        master["security_group"].eq(COMMON_SECURITY_GROUP)
        & master["stock_kind"].eq(COMMON_STOCK_KIND)
    ].copy()
    _require(not common.empty, "same-date common-stock identity scope is empty")
    _require(not common["isu_cd"].duplicated().any(), "duplicate ISU_CD in same-date common-stock identity")
    _require(not common["symbol"].duplicated().any(), "duplicate symbol in same-date common-stock identity")

    daily = daily_trade.copy()
    daily["isu_cd"] = daily["ISU_CD"].map(_standard)
    _require(not daily["isu_cd"].duplicated().any(), "duplicate ISU_CD in same-date daily-trade rows")

    daily_common = daily[["isu_cd"]].merge(
        common[["isu_cd","symbol"]],
        on="isu_cd",
        how="inner",
        validate="one_to_one",
    )

    event_date = pd.Timestamp(day).strftime("%Y-%m-%d")
    investor = daily_common.assign(event_date=event_date)[
        ["event_date","symbol","isu_cd"]
    ].sort_values(["symbol","isu_cd"]).reset_index(drop=True)

    status = common.assign(snapshot_date=event_date)[
        ["snapshot_date","symbol","isu_cd"]
    ].sort_values(["symbol","isu_cd"]).reset_index(drop=True)

    _require(not investor.duplicated(["event_date","symbol","isu_cd"]).any(), "duplicate investor expected key")
    _require(not status.duplicated(["snapshot_date","symbol","isu_cd"]).any(), "duplicate status expected key")

    return {
        "contract_id": CONTRACT_ID,
        "requested_date": day,
        "official_trading_date_observed": True,
        "daily_trade_rows": int(len(daily_trade)),
        "security_master_rows": int(len(security_master)),
        "investor_expected_scope": investor,
        "status_expected_scope": status,
        "network_request_attempted": False,
    }


def bind_scope_contract_fingerprint(
    frame: pd.DataFrame,
    *,
    date_column: str,
    fingerprint: str,
) -> pd.DataFrame:
    """Attach one externally frozen contract fingerprint without changing keys."""
    fp = str(fingerprint or "").strip().lower()
    _require(bool(re.fullmatch(r"[0-9a-f]{64}", fp)), "scope contract fingerprint must be SHA-256")
    _require(date_column in frame.columns, "date column missing from expected scope")
    out = frame.copy()
    out["scope_contract_fingerprint_sha256"] = fp
    return out


def public_date_summary(result: dict[str, Any]) -> dict[str, Any]:
    investor = result["investor_expected_scope"]
    status = result["status_expected_scope"]
    return {
        "contract_id": result["contract_id"],
        "requested_date": result["requested_date"],
        "official_trading_date_observed": bool(result["official_trading_date_observed"]),
        "daily_trade_rows": int(result["daily_trade_rows"]),
        "security_master_rows": int(result["security_master_rows"]),
        "investor_expected_key_count": int(len(investor)),
        "status_expected_key_count": int(len(status)),
        "investor_expected_keys_sha256": _sha256(
            investor.astype(str).to_dict(orient="records")
        ),
        "status_expected_keys_sha256": _sha256(
            status.astype(str).to_dict(orient="records")
        ),
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "network_request_attempted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
