"""Fail-closed historical KOSPI listing-episode reconstruction.

Pure/offline transformation.  It consumes already-normalized official KRX
basic-info snapshots plus new-listing/delisting history and produces one stable
listing episode per KOSPI common stock.  It never performs network access and
never invents a standard issue code from a later snapshot.
"""
from __future__ import annotations

from typing import Any

import pandas as pd


PLAN_START = pd.Timestamp("2015-06-15")
PLAN_END = pd.Timestamp("2026-10-01")


class KRXHistoricalIdentityError(ValueError):
    pass


def _text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def _date(series: pd.Series) -> pd.Series:
    raw = _text(series).str.replace(r"[^0-9]", "", regex=True)
    raw = raw.mask(raw.eq(""))
    return pd.to_datetime(raw, format="%Y%m%d", errors="coerce")


def _short_code(series: pd.Series) -> pd.Series:
    raw = _text(series).str.replace(r"[^0-9]", "", regex=True)
    raw = raw.where(raw.str.len() <= 6, raw.str[-6:])
    return raw.str.zfill(6)


def _market(series: pd.Series) -> pd.Series:
    s = _text(series).str.upper()
    out = pd.Series("", index=s.index, dtype="string")
    out = s.where(s.str.contains("KOSPI", na=False), out)
    out = out.mask(s.str.contains("유가증권", na=False), "KOSPI")
    out = out.mask(s.str.contains("KOSDAQ|코스닥", na=False), "KOSDAQ")
    out = out.mask(s.str.contains("KONEX|코넥스", na=False), "KONEX")
    return out


def _common_stock_mask(
    sec_group: pd.Series | None,
    stock_kind: pd.Series | None,
    index: pd.Index,
) -> pd.Series:
    mask = pd.Series(True, index=index, dtype=bool)
    if sec_group is not None:
        g = _text(sec_group)
        mask &= g.eq("") | g.str.contains("주권|주식", regex=True, na=False)
    if stock_kind is not None:
        k = _text(stock_kind)
        mask &= k.eq("") | k.str.contains("보통", regex=True, na=False)
    return mask


def _normal_history(frame: pd.DataFrame, *, delisted: bool) -> pd.DataFrame:
    date_col = "폐지일" if delisted else "상장폐지일"
    required = {"종목코드", "시장구분", "상장일"}
    missing = required - set(frame.columns)
    if missing:
        raise KRXHistoricalIdentityError(
            f"history identity missing columns: {sorted(missing)}"
        )
    out = pd.DataFrame(index=frame.index)
    out["short_code"] = _short_code(frame["종목코드"])
    out["name"] = _text(frame["종목명"]) if "종목명" in frame else ""
    out["market"] = _market(frame["시장구분"])
    out["listing_date"] = _date(frame["상장일"])
    out["delisting_date"] = _date(frame[date_col]) if date_col in frame else pd.NaT
    mask = _common_stock_mask(
        frame["증권구분"] if "증권구분" in frame else None,
        frame["주식종류"] if "주식종류" in frame else None,
        frame.index,
    )
    out = out[mask & out["market"].eq("KOSPI")].copy()
    if out["short_code"].eq("").any() or out["short_code"].str.len().ne(6).any():
        raise KRXHistoricalIdentityError("invalid short_code in history identity")
    if out["listing_date"].isna().any():
        raise KRXHistoricalIdentityError("missing listing_date in history identity")
    return out


def _validate_master_snapshots(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "decision_date",
        "standard_code",
        "symbol",
        "market_type_official",
        "listing_date_official",
        "common_stock_identity_official",
    }
    missing = required - set(frame.columns)
    if missing:
        raise KRXHistoricalIdentityError(
            f"security master snapshots missing columns: {sorted(missing)}"
        )
    if frame.empty:
        raise KRXHistoricalIdentityError("security master snapshots are empty")

    out = frame.copy()
    out["decision_date"] = pd.to_datetime(out["decision_date"], errors="coerce").dt.normalize()
    out["listing_date_official"] = pd.to_datetime(
        out["listing_date_official"], errors="coerce"
    ).dt.normalize()
    out["symbol"] = _short_code(out["symbol"])
    out["standard_code"] = _text(out["standard_code"]).str.upper()
    out["market_type_official"] = _market(out["market_type_official"])

    if out[["decision_date", "listing_date_official"]].isna().any().any():
        raise KRXHistoricalIdentityError("security master has invalid snapshot/listing date")
    if out["symbol"].eq("").any() or out["symbol"].str.len().ne(6).any():
        raise KRXHistoricalIdentityError("security master has invalid short code")
    bad_std = ~out["standard_code"].str.fullmatch(r"[A-Z0-9]{12}", na=False)
    if bad_std.any():
        raise KRXHistoricalIdentityError("security master has invalid standard code")
    if out.duplicated(["decision_date", "symbol"]).any():
        raise KRXHistoricalIdentityError("duplicate symbol inside security-master snapshot")

    out = out[
        out["market_type_official"].eq("KOSPI")
        & out["common_stock_identity_official"].astype(bool)
    ].copy()
    if out.empty:
        raise KRXHistoricalIdentityError("no KOSPI common-stock master rows")
    return out


def _episode_key(symbol: str, listing_date: pd.Timestamp) -> str:
    return f"KOSPI|{symbol}|{pd.Timestamp(listing_date).date().isoformat()}"


def reconstruct_historical_kospi_episodes(
    *,
    security_master_snapshots: pd.DataFrame,
    new_listing: pd.DataFrame,
    delisted: pd.DataFrame,
    plan_start: pd.Timestamp = PLAN_START,
    plan_end: pd.Timestamp = PLAN_END,
) -> pd.DataFrame:
    """Build stable KOSPI common-stock listing episodes.

    Required master snapshots:
    - exact plan-start snapshot;
    - exact plan-end snapshot;
    - one exact listing-date snapshot for every new-listing episode in the plan.

    A newly listed episode may not borrow a standard code from a later snapshot.
    """
    masters = _validate_master_snapshots(security_master_snapshots)
    new = _normal_history(new_listing, delisted=False)
    dl = _normal_history(delisted, delisted=True)

    start_master = masters[masters["decision_date"].eq(plan_start)].copy()
    end_master = masters[masters["decision_date"].eq(plan_end)].copy()
    if start_master.empty:
        raise KRXHistoricalIdentityError("missing exact research-start security master")
    if end_master.empty:
        raise KRXHistoricalIdentityError("missing exact research-end security master")

    episodes: dict[str, dict[str, Any]] = {}

    # Securities already active at research start derive their historical
    # standard code from the start snapshot, never from the end snapshot.
    for row in start_master.itertuples(index=False):
        key = _episode_key(row.symbol, row.listing_date_official)
        episodes[key] = {
            "episode_key": key,
            "market": "KOSPI",
            "short_code": str(row.symbol),
            "standard_code": str(row.standard_code),
            "name": str(getattr(row, "name", "") or ""),
            "listing_date": pd.Timestamp(row.listing_date_official),
            "delisting_date": pd.NaT,
            "source_start_master": True,
            "source_new_listing": False,
            "source_delisted": False,
            "source_end_master_reconciled": False,
        }

    # Every in-period new listing requires a same-day master row.
    new = new[
        new["listing_date"].between(plan_start, plan_end, inclusive="both")
    ].copy()
    for row in new.itertuples(index=False):
        same_day = masters[
            masters["decision_date"].eq(row.listing_date)
            & masters["symbol"].eq(row.short_code)
        ]
        if len(same_day) != 1:
            raise KRXHistoricalIdentityError(
                f"new listing lacks unique same-day standard-code mapping: "
                f"{row.short_code} {row.listing_date.date()}"
            )
        m = same_day.iloc[0]
        if pd.Timestamp(m["listing_date_official"]) != pd.Timestamp(row.listing_date):
            raise KRXHistoricalIdentityError("listing-date master disagrees with new-listing history")
        key = _episode_key(row.short_code, row.listing_date)
        existing = episodes.get(key)
        candidate = {
            "episode_key": key,
            "market": "KOSPI",
            "short_code": str(row.short_code),
            "standard_code": str(m["standard_code"]),
            "name": str(row.name or ""),
            "listing_date": pd.Timestamp(row.listing_date),
            "delisting_date": pd.NaT,
            "source_start_master": bool(existing and existing["source_start_master"]),
            "source_new_listing": True,
            "source_delisted": False,
            "source_end_master_reconciled": False,
        }
        if existing and existing["standard_code"] != candidate["standard_code"]:
            raise KRXHistoricalIdentityError("inconsistent standard code for listing episode")
        episodes[key] = candidate

    # Attach actual delisting records to an existing listing episode.
    dl = dl[
        (dl["listing_date"] <= plan_end)
        & (dl["delisting_date"].fillna(plan_end) >= plan_start)
    ].copy()
    for row in dl.itertuples(index=False):
        key = _episode_key(row.short_code, row.listing_date)
        if key not in episodes:
            raise KRXHistoricalIdentityError(
                f"delisted episode is not represented by start/new-listing identity: {key}"
            )
        ep = episodes[key]
        if pd.notna(ep["delisting_date"]) and pd.Timestamp(ep["delisting_date"]) != pd.Timestamp(row.delisting_date):
            raise KRXHistoricalIdentityError("conflicting delisting date")
        ep["delisting_date"] = pd.Timestamp(row.delisting_date)
        ep["source_delisted"] = True

    out = pd.DataFrame(list(episodes.values()))
    if out.empty:
        raise KRXHistoricalIdentityError("no identity episodes intersect required period")

    # End snapshot is reconciliation only.  Every episode still active at plan
    # end must be present with the same standard code and listing date.
    end_lookup = end_master.set_index("symbol", drop=False)
    for idx, row in out.iterrows():
        active_at_end = pd.isna(row["delisting_date"]) or pd.Timestamp(row["delisting_date"]) > plan_end
        if not active_at_end:
            continue
        symbol = row["short_code"]
        if symbol not in end_lookup.index:
            raise KRXHistoricalIdentityError(
                f"active episode missing from research-end master: {row['episode_key']}"
            )
        m = end_lookup.loc[symbol]
        if isinstance(m, pd.DataFrame):
            raise KRXHistoricalIdentityError("duplicate end-master symbol")
        if str(m["standard_code"]) != str(row["standard_code"]):
            raise KRXHistoricalIdentityError("standard code changed across episode snapshots")
        if pd.Timestamp(m["listing_date_official"]) != pd.Timestamp(row["listing_date"]):
            raise KRXHistoricalIdentityError("listing date changed across episode snapshots")
        out.at[idx, "source_end_master_reconciled"] = True

    # Every end-master common stock must correspond to a reconstructed episode.
    reconstructed_keys = set(out["episode_key"])
    for row in end_master.itertuples(index=False):
        key = _episode_key(row.symbol, row.listing_date_official)
        if key not in reconstructed_keys:
            raise KRXHistoricalIdentityError(
                f"research-end master contains unreconstructed episode: {key}"
            )

    out["coverage_start"] = out["listing_date"].clip(lower=plan_start)
    out["coverage_end"] = out["delisting_date"].fillna(plan_end).clip(upper=plan_end)
    if (out["coverage_end"] < out["coverage_start"]).any():
        raise KRXHistoricalIdentityError("episode has negative coverage interval")

    # Short-code reuse is allowed only for non-overlapping listing episodes.
    for code, group in out.groupby("short_code"):
        group = group.sort_values("coverage_start")
        prev_end = None
        for row in group.itertuples(index=False):
            if prev_end is not None and row.coverage_start <= prev_end:
                raise KRXHistoricalIdentityError(
                    f"overlapping listing episodes for short_code={code}"
                )
            prev_end = row.coverage_end

    bad_std = ~out["standard_code"].astype(str).str.fullmatch(r"[A-Z0-9]{12}", na=False)
    if bad_std.any():
        raise KRXHistoricalIdentityError("unresolved standard code in reconstructed episode")

    cols = [
        "episode_key",
        "market",
        "short_code",
        "standard_code",
        "name",
        "listing_date",
        "delisting_date",
        "coverage_start",
        "coverage_end",
        "source_start_master",
        "source_new_listing",
        "source_delisted",
        "source_end_master_reconciled",
    ]
    return out[cols].sort_values(["short_code", "listing_date"]).reset_index(drop=True)


def identity_summary(episodes: pd.DataFrame) -> dict[str, Any]:
    """Metadata-only summary safe for public logs."""
    if episodes is None or episodes.empty:
        raise KRXHistoricalIdentityError("episodes are empty")
    return {
        "episode_count": int(len(episodes)),
        "distinct_short_codes": int(episodes["short_code"].nunique()),
        "start_master_episode_count": int(episodes["source_start_master"].sum()),
        "new_listing_episode_count": int(episodes["source_new_listing"].sum()),
        "delisted_episode_count": int(episodes["source_delisted"].sum()),
        "end_reconciled_episode_count": int(episodes["source_end_master_reconciled"].sum()),
        "coverage_start": episodes["coverage_start"].min().date().isoformat(),
        "coverage_end": episodes["coverage_end"].max().date().isoformat(),
        "all_standard_codes_resolved": bool(
            episodes["standard_code"].astype(str).str.fullmatch(r"[A-Z0-9]{12}", na=False).all()
        ),
        "raw_identifiers_emitted": False,
    }
