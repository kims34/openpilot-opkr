"""Fail-closed adapters for official KRX security identity/status evidence.

This module is data-quality infrastructure, not alpha research.  It accepts
already-retrieved official KRX OpenAPI/Data Marketplace tables and normalises
only fields needed by the IndexAlert promotion blockers:

- point-in-time security identity / stock type,
- trading-halt intervals,
- delisting date/reason,
- delisted-security regular-session prices.

No heuristic is allowed to turn a security into Judge-eligible evidence.  The
caller must explicitly attest the official source and availability timestamp.
If required columns or lineage are missing, validation fails closed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd


KRX_OPENAPI_BASIC_SOURCE = "KRX_OPENAPI_STK_ISU_BASE_INFO"
KRX_HALT_SOURCE = "KRX_DATA_MARKETPLACE_MDCSTAT213"
KRX_DELIST_SOURCE = "KRX_DATA_MARKETPLACE_MDCSTAT238"
KRX_DELIST_PRICE_SOURCE = "KRX_DATA_MARKETPLACE_MDCSTAT239"


class KRXOfficialStatusError(ValueError):
    """Raised when official-source evidence is incomplete or ambiguous."""


@dataclass(frozen=True)
class CoverageAudit:
    requested_start: str
    requested_end: str
    identity_asof_dates: int
    halt_rows: int
    delist_rows: int
    delist_price_rows: int
    identity_official: bool
    halt_official: bool
    delist_official: bool
    delist_price_official: bool
    availability_lineage_complete: bool
    judge_security_status_ready: bool


def _pick(df: pd.DataFrame, aliases: Iterable[str], logical_name: str) -> pd.Series:
    for name in aliases:
        if name in df.columns:
            return df[name]
    raise KRXOfficialStatusError(
        f"official KRX table missing {logical_name}; accepted aliases={list(aliases)}; "
        f"columns={list(df.columns)}"
    )


def _optional(df: pd.DataFrame, aliases: Iterable[str], default="") -> pd.Series:
    for name in aliases:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


def _symbol(series: pd.Series) -> pd.Series:
    x = series.astype(str).str.strip().str.upper().str.replace(r"\.0$", "", regex=True)
    return x.map(lambda s: s.zfill(6) if s.isdigit() else s)


def _date(series: pd.Series) -> pd.Series:
    # KRX exports commonly use YYYY/MM/DD, YYYY-MM-DD or YYYYMMDD.
    s = series.astype(str).str.strip().replace({"": pd.NA, "-": pd.NA, "nan": pd.NA, "None": pd.NA})
    return pd.to_datetime(s, errors="coerce")


def _require_source(actual: str, expected: str) -> None:
    if str(actual).strip() != expected:
        raise KRXOfficialStatusError(
            f"source must be exactly {expected}; got {actual!r}. "
            "Unofficial mirrors/proxies cannot close a promotion blocker."
        )


def normalise_basic_info(
    table: pd.DataFrame,
    *,
    asof_date,
    available_at,
    source: str = KRX_OPENAPI_BASIC_SOURCE,
) -> pd.DataFrame:
    """Normalise one official KRX stock-basic-info snapshot.

    `available_at` is mandatory.  A historical snapshot without explicit
    availability lineage may be useful descriptively, but it cannot be used as
    point-in-time Judge evidence.
    """
    _require_source(source, KRX_OPENAPI_BASIC_SOURCE)
    if available_at is None or pd.isna(pd.Timestamp(available_at)):
        raise KRXOfficialStatusError("official basic-info snapshot requires available_at lineage")
    if table is None or table.empty:
        raise KRXOfficialStatusError("official basic-info snapshot is empty")

    symbol = _symbol(_pick(table, ["ISU_SRT_CD", "단축코드", "종목코드"], "short issue code"))
    issue_name = _pick(table, ["ISU_NM", "한글 종목명", "종목명"], "issue name").astype(str).str.strip()
    market = _pick(table, ["MKT_TP_NM", "시장구분"], "market type").astype(str).str.strip()
    security_group = _pick(table, ["SECUGRP_NM", "증권구분"], "security group").astype(str).str.strip()
    stock_type = _pick(table, ["KIND_STKCERT_TP_NM", "주식종류"], "stock type").astype(str).str.strip()
    list_date = _date(_pick(table, ["LIST_DD", "상장일"], "listing date"))

    if symbol.duplicated().any():
        dup = sorted(symbol[symbol.duplicated(keep=False)].unique().tolist())[:10]
        raise KRXOfficialStatusError(f"duplicate security codes in official basic-info snapshot: {dup}")
    if list_date.isna().any():
        raise KRXOfficialStatusError("official basic-info snapshot contains unparseable listing date")

    out = pd.DataFrame({
        "decision_date": pd.Timestamp(asof_date).normalize(),
        "symbol": symbol,
        "name": issue_name,
        "market_type_official": market,
        "security_group_official": security_group,
        "stock_type_official": stock_type,
        "listing_date_official": list_date.dt.normalize(),
    })
    out["common_stock_identity_official"] = (
        out["security_group_official"].eq("주권")
        & out["stock_type_official"].eq("보통주")
    )
    out["security_scope_identity_validated"] = True
    out["source"] = source
    out["source_asof_date"] = pd.Timestamp(asof_date).normalize()
    out["available_at"] = pd.Timestamp(available_at)
    out["ingested_at_required"] = True
    return out.sort_values("symbol").reset_index(drop=True)


def normalise_halt_history(
    table: pd.DataFrame,
    *,
    available_at,
    source: str = KRX_HALT_SOURCE,
) -> pd.DataFrame:
    """Normalise official KRX individual-security halt/resumption history."""
    _require_source(source, KRX_HALT_SOURCE)
    if available_at is None:
        raise KRXOfficialStatusError("halt history requires available_at lineage")
    if table is None:
        raise KRXOfficialStatusError("halt history table is None")
    if table.empty:
        return pd.DataFrame(columns=[
            "symbol", "market", "halt_date", "resume_date", "source", "available_at"
        ])

    out = pd.DataFrame({
        "symbol": _symbol(_pick(table, ["종목코드", "ISU_SRT_CD"], "security code")),
        "market": _pick(table, ["시장구분", "MKT_TP_NM"], "market").astype(str).str.strip(),
        "halt_date": _date(_pick(table, ["정지일", "HALT_DD"], "halt date")),
        "resume_date": _date(_optional(table, ["재개일", "RESUME_DD"])),
    })
    if out["halt_date"].isna().any():
        raise KRXOfficialStatusError("halt history contains unparseable halt date")
    invalid = out["resume_date"].notna() & (out["resume_date"] < out["halt_date"])
    if invalid.any():
        raise KRXOfficialStatusError("halt history contains resume date before halt date")
    out["source"] = source
    out["available_at"] = pd.Timestamp(available_at)
    return out.sort_values(["symbol", "halt_date"]).reset_index(drop=True)


def normalise_delisting_history(
    table: pd.DataFrame,
    *,
    available_at,
    source: str = KRX_DELIST_SOURCE,
) -> pd.DataFrame:
    """Normalise official KRX delisted-security status history."""
    _require_source(source, KRX_DELIST_SOURCE)
    if available_at is None:
        raise KRXOfficialStatusError("delisting history requires available_at lineage")
    if table is None:
        raise KRXOfficialStatusError("delisting history table is None")
    if table.empty:
        return pd.DataFrame(columns=[
            "symbol", "name", "market", "security_group", "stock_type",
            "listing_date", "delisting_date", "delisting_reason", "source", "available_at",
        ])

    out = pd.DataFrame({
        "symbol": _symbol(_pick(table, ["종목코드", "ISU_SRT_CD"], "security code")),
        "name": _pick(table, ["종목명", "ISU_NM"], "issue name").astype(str).str.strip(),
        "market": _pick(table, ["시장구분", "MKT_TP_NM"], "market").astype(str).str.strip(),
        "security_group": _pick(table, ["증권구분", "SECUGRP_NM"], "security group").astype(str).str.strip(),
        "stock_type": _pick(table, ["주식종류", "KIND_STKCERT_TP_NM"], "stock type").astype(str).str.strip(),
        "listing_date": _date(_pick(table, ["상장일", "LIST_DD"], "listing date")),
        "delisting_date": _date(_pick(table, ["폐지일", "DELIST_DD"], "delisting date")),
        "delisting_reason": _pick(table, ["폐지사유", "DELIST_REASON"], "delisting reason").astype(str).str.strip(),
    })
    if out[["listing_date", "delisting_date"]].isna().any().any():
        raise KRXOfficialStatusError("delisting history contains unparseable listing/delisting date")
    if (out["delisting_date"] < out["listing_date"]).any():
        raise KRXOfficialStatusError("delisting history contains delisting before listing")
    out["source"] = source
    out["available_at"] = pd.Timestamp(available_at)
    return out.sort_values(["delisting_date", "symbol"]).reset_index(drop=True)


def normalise_delisted_prices(
    table: pd.DataFrame,
    *,
    available_at,
    source: str = KRX_DELIST_PRICE_SOURCE,
) -> pd.DataFrame:
    """Normalise official regular-session prices for delisted securities."""
    _require_source(source, KRX_DELIST_PRICE_SOURCE)
    if available_at is None:
        raise KRXOfficialStatusError("delisted-price history requires available_at lineage")
    if table is None:
        raise KRXOfficialStatusError("delisted-price history table is None")
    if table.empty:
        return pd.DataFrame(columns=[
            "date", "symbol", "open", "high", "low", "close", "volume", "value",
            "source", "available_at",
        ])

    out = pd.DataFrame({
        "date": _date(_pick(table, ["일자", "BAS_DD"], "price date")),
        "symbol": _symbol(_pick(table, ["종목코드", "ISU_SRT_CD"], "security code")),
        "open": pd.to_numeric(_pick(table, ["시가", "TDD_OPNPRC"], "open"), errors="coerce"),
        "high": pd.to_numeric(_pick(table, ["고가", "TDD_HGPRC"], "high"), errors="coerce"),
        "low": pd.to_numeric(_pick(table, ["저가", "TDD_LWPRC"], "low"), errors="coerce"),
        "close": pd.to_numeric(_pick(table, ["종가", "TDD_CLSPRC"], "close"), errors="coerce"),
        "volume": pd.to_numeric(_optional(table, ["거래량", "ACC_TRDVOL"], pd.NA), errors="coerce"),
        "value": pd.to_numeric(_optional(table, ["거래대금", "ACC_TRDVAL"], pd.NA), errors="coerce"),
    })
    if out["date"].isna().any() or out[["open", "high", "low", "close"]].isna().any().any():
        raise KRXOfficialStatusError("delisted-price history contains missing/unparseable OHLC/date")
    bad = (
        (out[["open", "high", "low", "close"]] <= 0).any(axis=1)
        | (out["high"] < out[["open", "close"]].max(axis=1))
        | (out["low"] > out[["open", "close"]].min(axis=1))
    )
    if bad.any():
        raise KRXOfficialStatusError("delisted-price history contains invalid regular-session OHLC")
    out["source"] = source
    out["available_at"] = pd.Timestamp(available_at)
    return out.sort_values(["date", "symbol"]).reset_index(drop=True)


def halt_mask_for_dates(decision_rows: pd.DataFrame, halts: pd.DataFrame) -> pd.Series:
    """Return whether each (decision_date, symbol) lies inside a halt interval.

    KRX `재개일` is treated as the first resumed/tradable date, so the halt
    interval is [정지일, 재개일).  Open-ended rows remain halted thereafter.
    """
    required = {"decision_date", "symbol"}
    if not required.issubset(decision_rows.columns):
        raise KRXOfficialStatusError(f"decision rows require {sorted(required)}")
    if halts is None:
        raise KRXOfficialStatusError("halt evidence is required")
    mask = []
    for row in decision_rows[["decision_date", "symbol"]].itertuples(index=False):
        d = pd.Timestamp(row.decision_date).normalize()
        s = str(row.symbol).strip().upper().zfill(6)
        h = halts[halts["symbol"] == s]
        active = False
        for event in h.itertuples(index=False):
            start = pd.Timestamp(event.halt_date).normalize()
            resume = pd.Timestamp(event.resume_date).normalize() if pd.notna(event.resume_date) else None
            if d >= start and (resume is None or d < resume):
                active = True
                break
        mask.append(active)
    return pd.Series(mask, index=decision_rows.index, dtype=bool)


def delisted_mask_for_dates(decision_rows: pd.DataFrame, delistings: pd.DataFrame) -> pd.Series:
    """Return whether a security is already delisted on a decision date."""
    required = {"decision_date", "symbol"}
    if not required.issubset(decision_rows.columns):
        raise KRXOfficialStatusError(f"decision rows require {sorted(required)}")
    if delistings is None:
        raise KRXOfficialStatusError("delisting evidence is required")
    by_symbol = (
        delistings.groupby("symbol")["delisting_date"].min().to_dict()
        if not delistings.empty else {}
    )
    out = []
    for row in decision_rows[["decision_date", "symbol"]].itertuples(index=False):
        s = str(row.symbol).strip().upper().zfill(6)
        dd = by_symbol.get(s)
        out.append(bool(dd is not None and pd.Timestamp(row.decision_date).normalize() >= pd.Timestamp(dd).normalize()))
    return pd.Series(out, index=decision_rows.index, dtype=bool)


def audit_official_coverage(
    *,
    requested_start,
    requested_end,
    identity_snapshots: pd.DataFrame,
    halts: pd.DataFrame,
    delistings: pd.DataFrame,
    delisted_prices: pd.DataFrame,
) -> dict:
    """Audit whether official identity/status evidence is structurally complete.

    This does not assert empirical completeness of KRX downloads by itself; it
    only verifies that all mandatory official feeds and availability lineage are
    present.  A caller must separately compare source date coverage/counts before
    setting any Final-Judge flag.
    """
    frames = [identity_snapshots, halts, delistings, delisted_prices]
    official = [
        identity_snapshots is not None and (identity_snapshots.empty or set(identity_snapshots.get("source", [])) <= {KRX_OPENAPI_BASIC_SOURCE}),
        halts is not None and (halts.empty or set(halts.get("source", [])) <= {KRX_HALT_SOURCE}),
        delistings is not None and (delistings.empty or set(delistings.get("source", [])) <= {KRX_DELIST_SOURCE}),
        delisted_prices is not None and (delisted_prices.empty or set(delisted_prices.get("source", [])) <= {KRX_DELIST_PRICE_SOURCE}),
    ]
    lineage_complete = all(
        frame is not None
        and "available_at" in frame.columns
        and (frame.empty or frame["available_at"].notna().all())
        for frame in frames
    )
    identity_dates = 0 if identity_snapshots is None or identity_snapshots.empty else int(
        pd.to_datetime(identity_snapshots["decision_date"]).dt.normalize().nunique()
    )
    structurally_ready = bool(all(official) and lineage_complete and identity_dates > 0)
    audit = CoverageAudit(
        requested_start=str(pd.Timestamp(requested_start).date()),
        requested_end=str(pd.Timestamp(requested_end).date()),
        identity_asof_dates=identity_dates,
        halt_rows=0 if halts is None else int(len(halts)),
        delist_rows=0 if delistings is None else int(len(delistings)),
        delist_price_rows=0 if delisted_prices is None else int(len(delisted_prices)),
        identity_official=official[0],
        halt_official=official[1],
        delist_official=official[2],
        delist_price_official=official[3],
        availability_lineage_complete=lineage_complete,
        # Deliberately false until an external coverage check verifies that the
        # downloads span the entire requested period and all relevant symbols.
        judge_security_status_ready=False,
    )
    out = asdict(audit)
    out["structural_inputs_ready_for_coverage_check"] = structurally_ready
    out["guardrail"] = (
        "Official source labels and available_at lineage are necessary but not sufficient. "
        "Do not set Judge-ready until full requested-period/source coverage is independently verified."
    )
    return out
