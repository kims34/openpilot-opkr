"""Historical KOSPI security-episode reconstruction for KRX acquisitions.

Pure/offline transformation. It never performs a KRX request and never writes
raw rows. It combines current listed identity, new-listing history and delisted
history into non-overlapping common-stock listing episodes for the frozen
research coverage period.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


PLAN_START = pd.Timestamp("2015-06-15")
PLAN_END = pd.Timestamp("2026-10-01")


class KRXHistoricalIdentityError(ValueError):
    pass


def _text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def _date(series: pd.Series) -> pd.Series:
    raw=_text(series).str.replace(r"[^0-9]", "", regex=True)
    raw=raw.mask(raw.eq(""))
    out=pd.to_datetime(raw, format="%Y%m%d", errors="coerce")
    return out


def _short_code(series: pd.Series) -> pd.Series:
    raw=_text(series).str.replace(r"[^0-9]", "", regex=True)
    raw=raw.where(raw.str.len() <= 6, raw.str[-6:])
    return raw.str.zfill(6)


def _market(series: pd.Series) -> pd.Series:
    s=_text(series).str.upper()
    out=pd.Series("", index=s.index, dtype="string")
    out=s.where(s.str.contains("KOSPI", na=False), out)
    out=out.mask(s.str.contains("유가증권", na=False), "KOSPI")
    out=out.mask(s.str.contains("KOSDAQ|코스닥", na=False), "KOSDAQ")
    out=out.mask(s.str.contains("KONEX|코넥스", na=False), "KONEX")
    out=out.mask(out.ne("") & out.ne("KOSPI"), out)
    return out


def _common_stock_mask(sec_group: pd.Series | None, stock_kind: pd.Series | None, index: pd.Index) -> pd.Series:
    mask=pd.Series(True,index=index,dtype=bool)
    if sec_group is not None:
        g=_text(sec_group)
        mask &= g.eq("") | g.str.contains("주권|주식", regex=True, na=False)
    if stock_kind is not None:
        k=_text(stock_kind)
        mask &= k.eq("") | k.str.contains("보통", regex=True, na=False)
    return mask


def _normal_current(frame: pd.DataFrame) -> pd.DataFrame:
    required={"ISU_SRT_CD","LIST_DD","MKT_TP_NM"}
    missing=required-set(frame.columns)
    if missing:
        raise KRXHistoricalIdentityError(f"current identity missing columns: {sorted(missing)}")
    out=pd.DataFrame(index=frame.index)
    out["short_code"]=_short_code(frame["ISU_SRT_CD"])
    out["standard_code"]=_text(frame["ISU_CD"]) if "ISU_CD" in frame else ""
    out["name"]=_text(frame["ISU_NM"]) if "ISU_NM" in frame else ""
    out["market"]=_market(frame["MKT_TP_NM"])
    out["listing_date"]=_date(frame["LIST_DD"])
    out["delisting_date"]=pd.NaT
    mask=_common_stock_mask(
        frame["SECUGRP_NM"] if "SECUGRP_NM" in frame else None,
        frame["KIND_STKCERT_TP_NM"] if "KIND_STKCERT_TP_NM" in frame else None,
        frame.index,
    )
    out=out[mask & out["market"].eq("KOSPI")].copy()
    out["source_current"]=True
    out["source_new_listing"]=False
    out["source_delisted"]=False
    return out


def _normal_history(frame: pd.DataFrame, *, delisted: bool) -> pd.DataFrame:
    date_col="폐지일" if delisted else "상장폐지일"
    required={"종목코드","시장구분","상장일"}
    missing=required-set(frame.columns)
    if missing:
        raise KRXHistoricalIdentityError(f"history identity missing columns: {sorted(missing)}")
    out=pd.DataFrame(index=frame.index)
    out["short_code"]=_short_code(frame["종목코드"])
    out["standard_code"]=""
    out["name"]=_text(frame["종목명"]) if "종목명" in frame else ""
    out["market"]=_market(frame["시장구분"])
    out["listing_date"]=_date(frame["상장일"])
    out["delisting_date"]=_date(frame[date_col]) if date_col in frame else pd.NaT
    mask=_common_stock_mask(
        frame["증권구분"] if "증권구분" in frame else None,
        frame["주식종류"] if "주식종류" in frame else None,
        frame.index,
    )
    out=out[mask & out["market"].eq("KOSPI")].copy()
    out["source_current"]=False
    out["source_new_listing"]=not delisted
    out["source_delisted"]=delisted
    return out


def _coalesce_group(group: pd.DataFrame) -> dict[str, Any]:
    listing=group["listing_date"].dropna().unique()
    if len(listing) != 1:
        raise KRXHistoricalIdentityError("episode has missing/conflicting listing_date")
    delist=group["delisting_date"].dropna().unique()
    if len(delist) > 1:
        raise KRXHistoricalIdentityError("episode has conflicting delisting_date")
    std=[x for x in group["standard_code"].astype(str) if x and x.lower()!="nan"]
    names=[x for x in group["name"].astype(str) if x and x.lower()!="nan"]
    return {
        "market":"KOSPI",
        "short_code":str(group["short_code"].iloc[0]),
        "standard_code":std[0] if std else "",
        "name":names[0] if names else "",
        "listing_date":pd.Timestamp(listing[0]),
        "delisting_date":pd.Timestamp(delist[0]) if len(delist)==1 else pd.NaT,
        "source_current":bool(group["source_current"].any()),
        "source_new_listing":bool(group["source_new_listing"].any()),
        "source_delisted":bool(group["source_delisted"].any()),
    }


def reconstruct_historical_kospi_episodes(
    *,
    current_listed: pd.DataFrame,
    new_listing: pd.DataFrame,
    delisted: pd.DataFrame,
    plan_start: pd.Timestamp = PLAN_START,
    plan_end: pd.Timestamp = PLAN_END,
) -> pd.DataFrame:
    """Return one row per KOSPI common-stock listing episode."""
    parts=[
        _normal_current(current_listed),
        _normal_history(new_listing,delisted=False),
        _normal_history(delisted,delisted=True),
    ]
    raw=pd.concat(parts,ignore_index=True)
    if raw.empty:
        raise KRXHistoricalIdentityError("no KOSPI common-stock identity rows")
    if raw["short_code"].eq("").any() or raw["short_code"].str.len().ne(6).any():
        raise KRXHistoricalIdentityError("invalid short_code in identity seed")
    if raw["listing_date"].isna().any():
        raise KRXHistoricalIdentityError("missing listing_date in identity seed")

    raw["episode_key"]=(
        raw["market"]+"|"+raw["short_code"]+"|"+raw["listing_date"].dt.strftime("%Y-%m-%d")
    )
    rows=[_coalesce_group(g) for _,g in raw.groupby("episode_key",sort=True)]
    out=pd.DataFrame(rows)
    out["episode_key"]=(
        out["market"]+"|"+out["short_code"]+"|"+out["listing_date"].dt.strftime("%Y-%m-%d")
    )

    # Keep only episodes intersecting the required period.
    effective_end=out["delisting_date"].fillna(plan_end)
    keep=(out["listing_date"]<=plan_end) & (effective_end>=plan_start)
    out=out[keep].copy()
    if out.empty:
        raise KRXHistoricalIdentityError("no identity episodes intersect required period")

    out["coverage_start"]=out["listing_date"].clip(lower=plan_start)
    out["coverage_end"]=out["delisting_date"].fillna(plan_end).clip(upper=plan_end)
    if (out["coverage_end"] < out["coverage_start"]).any():
        raise KRXHistoricalIdentityError("episode has negative coverage interval")

    # Short-code reuse is allowed only as non-overlapping listing episodes.
    for code,g in out.groupby("short_code"):
        g=g.sort_values("coverage_start")
        prev_end=None
        for row in g.itertuples(index=False):
            if prev_end is not None and row.coverage_start <= prev_end:
                raise KRXHistoricalIdentityError(
                    f"overlapping listing episodes for short_code={code}"
                )
            prev_end=row.coverage_end

    cols=[
        "episode_key","market","short_code","standard_code","name",
        "listing_date","delisting_date","coverage_start","coverage_end",
        "source_current","source_new_listing","source_delisted",
    ]
    return out[cols].sort_values(["short_code","listing_date"]).reset_index(drop=True)


def identity_summary(episodes: pd.DataFrame) -> dict[str, Any]:
    """Metadata-only summary safe for public logs."""
    if episodes is None or episodes.empty:
        raise KRXHistoricalIdentityError("episodes are empty")
    return {
        "episode_count":int(len(episodes)),
        "distinct_short_codes":int(episodes["short_code"].nunique()),
        "current_episode_count":int(episodes["source_current"].sum()),
        "delisted_episode_count":int(episodes["source_delisted"].sum()),
        "coverage_start":episodes["coverage_start"].min().date().isoformat(),
        "coverage_end":episodes["coverage_end"].max().date().isoformat(),
        "raw_identifiers_emitted":False,
    }
