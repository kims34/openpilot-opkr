"""Fail-closed normaliser for official KRX cleanup-trading status evidence.

This module models *status/timing only*. It deliberately does not invent an
execution return, fill price or delisting recovery value. Those economics must
come from official price/status evidence and an explicit execution policy.

Official screen contract: KRX Data Marketplace issue statistics, MDCSTAT237
([20036] 정리매매종목 현황).
"""
from __future__ import annotations

from typing import Iterable

import pandas as pd


KRX_CLEANUP_SOURCE = "KRX_DATA_MARKETPLACE_MDCSTAT237"


class KRXCleanupStatusError(ValueError):
    """Raised when cleanup-trading evidence is incomplete or ambiguous."""


def _pick(df: pd.DataFrame, aliases: Iterable[str], logical_name: str) -> pd.Series:
    for name in aliases:
        if name in df.columns:
            return df[name]
    raise KRXCleanupStatusError(
        f"official KRX cleanup table missing {logical_name}; "
        f"accepted aliases={list(aliases)}; columns={list(df.columns)}"
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
    s = series.astype(str).str.strip().replace(
        {"": pd.NA, "-": pd.NA, "nan": pd.NA, "None": pd.NA}
    )
    return pd.to_datetime(s, errors="coerce").dt.normalize()


def normalise_cleanup_trading(
    table: pd.DataFrame,
    *,
    available_at,
    source: str = KRX_CLEANUP_SOURCE,
) -> pd.DataFrame:
    """Normalise official KRX cleanup-trading intervals.

    Required official fields mirror the MDCSTAT237 screen: security code/name,
    market/security group, cleanup-trading start/end, planned delisting date and
    delisting reason. `available_at` is mandatory for PIT use.
    """
    if str(source).strip() != KRX_CLEANUP_SOURCE:
        raise KRXCleanupStatusError(
            f"source must be exactly {KRX_CLEANUP_SOURCE}; got {source!r}"
        )
    if available_at is None or pd.isna(pd.Timestamp(available_at)):
        raise KRXCleanupStatusError("cleanup-trading evidence requires available_at lineage")
    if table is None:
        raise KRXCleanupStatusError("cleanup-trading table is None")
    if table.empty:
        return pd.DataFrame(columns=[
            "symbol", "name", "market", "security_group",
            "cleanup_start", "cleanup_end", "planned_delisting_date",
            "delisting_reason", "source", "available_at",
        ])

    out = pd.DataFrame({
        "symbol": _symbol(_pick(table, ["종목코드", "ISU_SRT_CD"], "security code")),
        "name": _pick(table, ["종목명", "ISU_NM"], "issue name").astype(str).str.strip(),
        "market": _pick(table, ["시장구분", "MKT_TP_NM"], "market").astype(str).str.strip(),
        "security_group": _pick(
            table, ["증권구분", "SECUGRP_NM"], "security group"
        ).astype(str).str.strip(),
        "cleanup_start": _date(_pick(
            table,
            ["정리매매 시작일", "정리매매기간 시작일", "CLEANUP_START_DD"],
            "cleanup-trading start date",
        )),
        "cleanup_end": _date(_pick(
            table,
            ["정리매매 종료일", "정리매매기간 종료일", "CLEANUP_END_DD"],
            "cleanup-trading end date",
        )),
        "planned_delisting_date": _date(_pick(
            table,
            ["상장폐지 예정일", "상장폐지예정일", "DELIST_PLAN_DD"],
            "planned delisting date",
        )),
        "delisting_reason": _pick(
            table, ["상장폐지사유", "폐지사유", "DELIST_REASON"], "delisting reason"
        ).astype(str).str.strip(),
    })

    if out[["cleanup_start", "cleanup_end", "planned_delisting_date"]].isna().any().any():
        raise KRXCleanupStatusError("cleanup-trading table contains unparseable required dates")
    if (out["cleanup_end"] < out["cleanup_start"]).any():
        raise KRXCleanupStatusError("cleanup-trading end date precedes start date")
    if (out["planned_delisting_date"] <= out["cleanup_end"]).any():
        raise KRXCleanupStatusError(
            "planned delisting date must be after the cleanup-trading end date"
        )
    if out[["symbol", "name", "market", "security_group"]].astype(str).apply(
        lambda c: c.str.strip().eq("")
    ).any().any():
        raise KRXCleanupStatusError("cleanup-trading identity fields must not be blank")

    out["source"] = KRX_CLEANUP_SOURCE
    out["available_at"] = pd.Timestamp(available_at)
    return out.sort_values(["cleanup_start", "symbol"]).reset_index(drop=True)


def cleanup_mask_for_dates(decision_rows: pd.DataFrame, cleanup: pd.DataFrame) -> pd.Series:
    """Whether each (decision_date, symbol) lies in an official cleanup period.

    Cleanup trading is treated as an inclusive status interval [start, end].
    This helper says only that the special status is active; it does not imply a
    fill, a tradable open, or any particular execution price.
    """
    required = {"decision_date", "symbol"}
    if not required.issubset(decision_rows.columns):
        raise KRXCleanupStatusError(f"decision rows require {sorted(required)}")
    if cleanup is None:
        raise KRXCleanupStatusError("cleanup-trading evidence is required")

    out: list[bool] = []
    for row in decision_rows[["decision_date", "symbol"]].itertuples(index=False):
        d = pd.Timestamp(row.decision_date).normalize()
        s = str(row.symbol).strip().upper().zfill(6)
        events = cleanup[cleanup["symbol"] == s]
        active = False
        for event in events.itertuples(index=False):
            start = pd.Timestamp(event.cleanup_start).normalize()
            end = pd.Timestamp(event.cleanup_end).normalize()
            if start <= d <= end:
                active = True
                break
        out.append(active)
    return pd.Series(out, index=decision_rows.index, dtype=bool)


def planned_delisting_mask_for_dates(
    decision_rows: pd.DataFrame, cleanup: pd.DataFrame
) -> pd.Series:
    """Whether planned delisting is already effective on a decision date.

    This is a fail-closed timing flag, not a realized-delist confirmation. Final
    Judge use still requires reconciliation to MDCSTAT238 actual delisting data.
    """
    required = {"decision_date", "symbol"}
    if not required.issubset(decision_rows.columns):
        raise KRXCleanupStatusError(f"decision rows require {sorted(required)}")
    if cleanup is None:
        raise KRXCleanupStatusError("cleanup-trading evidence is required")

    earliest = (
        cleanup.groupby("symbol")["planned_delisting_date"].min().to_dict()
        if not cleanup.empty else {}
    )
    flags = []
    for row in decision_rows[["decision_date", "symbol"]].itertuples(index=False):
        s = str(row.symbol).strip().upper().zfill(6)
        dd = earliest.get(s)
        flags.append(bool(
            dd is not None
            and pd.Timestamp(row.decision_date).normalize() >= pd.Timestamp(dd).normalize()
        ))
    return pd.Series(flags, index=decision_rows.index, dtype=bool)
