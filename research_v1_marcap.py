"""Build a historical point-in-time KOSPI daily panel from FinanceData/marcap.

marcap is derived from KRX daily all-security market-cap files and therefore
reconstructs the set of securities present on each historical trading date. This
removes the fixed-current-universe survivorship problem from the smoke dataset.

The executable panel contains only interpretable positive-OHLC bars.  Separately,
a lineage membership ledger preserves *all* KOSPI rows, including halted/invalid
bars, so later diagnostics can distinguish a missing executable bar from a
security disappearing from the historical membership universe.

Phase 1 deliberately keeps *all KOSPI listed securities* because marcap does not
carry a validated common/preferred security-type field. The output is PIT for
membership but is marked Judge-preliminary until a separately validated common-
stock identity layer is attached.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

RAW_URL = "https://raw.githubusercontent.com/FinanceData/marcap/master/data/marcap-{year}.parquet"
SCHEMA_VERSION = "marcap-kospi-pit-v2"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download_year(year: int, raw_dir: Path, timeout: int = 120) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"marcap-{year}.parquet"
    if path.exists() and path.stat().st_size > 1024:
        return path
    url = RAW_URL.format(year=year)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path


def _normalise_year(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if "Date" not in df.columns:
        if df.index.name == "Date":
            df = df.reset_index()
        else:
            raise RuntimeError(f"Date not found in {path}")
    required = {"Date", "Code", "Name", "Open", "High", "Low", "Close", "Volume", "Amount", "Marcap", "Market"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"missing marcap columns {sorted(missing)} in {path}")

    df["Date"] = pd.to_datetime(df["Date"])
    x = df[(df["Date"] >= start) & (df["Date"] <= end) & (df["Market"].astype(str) == "KOSPI")].copy()
    if x.empty:
        return x

    x["Code"] = x["Code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    for col in ["Open", "High", "Low", "Close", "Volume", "Amount", "Marcap"]:
        x[col] = pd.to_numeric(x[col], errors="coerce")

    out = pd.DataFrame({
        "decision_date": x["Date"],
        "symbol": x["Code"],
        "name": x["Name"].astype(str),
        "market": x["Market"].astype(str),
        "dept": x["Dept"].astype(str) if "Dept" in x.columns else "",
        "open": x["Open"],
        "high": x["High"],
        "low": x["Low"],
        "close": x["Close"],
        "volume": x["Volume"].fillna(0.0),
        "value": x["Amount"].fillna(0.0),
        "market_cap": x["Marcap"].fillna(0.0),
        "rank": pd.to_numeric(x["Rank"], errors="coerce") if "Rank" in x.columns else pd.NA,
        "source": "FinanceData/marcap (KRX daily all-security data)",
        "point_in_time_universe": True,
        "survivorship_bias_possible": False,
        "security_scope": "ALL_KOSPI_LISTED_SECURITIES",
        "common_stock_identity_validated": False,
    })

    valid = (
        out[["open", "high", "low", "close"]].notna().all(axis=1)
        & (out[["open", "high", "low", "close"]] > 0).all(axis=1)
        & (out["low"] <= out[["open", "close"]].min(axis=1))
        & (out["high"] >= out[["open", "close"]].max(axis=1))
        & (out["low"] <= out["high"])
    )
    out["bar_valid_for_execution"] = valid
    return out.sort_values(["decision_date", "symbol"]).reset_index(drop=True)


def years_between(start: pd.Timestamp, end: pd.Timestamp) -> Iterable[int]:
    return range(start.year, end.year + 1)


def build(start: str, end: str, out_dir: str, raw_dir: str) -> dict:
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    if end_ts < start_ts:
        raise ValueError("end before start")

    out = Path(out_dir)
    raw = Path(raw_dir)
    lineage = out / "lineage"
    out.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    lineage.mkdir(parents=True, exist_ok=True)

    year_stats = []
    valid_frames = []
    rejected_frames = []
    membership_frames = []
    hashes = {}
    for year in years_between(start_ts, end_ts):
        p = _download_year(year, raw)
        hashes[str(year)] = _sha256(p)
        frame = _normalise_year(p, start_ts, end_ts)
        if frame.empty:
            year_stats.append({"year": year, "rows": 0, "valid_rows": 0})
            continue
        membership_frames.append(frame.copy())
        valid = frame[frame["bar_valid_for_execution"]].copy()
        rejected = frame[~frame["bar_valid_for_execution"]].copy()
        valid_frames.append(valid)
        if not rejected.empty:
            rejected_frames.append(rejected)
        year_stats.append({
            "year": year,
            "rows": int(len(frame)),
            "valid_rows": int(len(valid)),
            "rejected_bar_rows": int(len(rejected)),
            "symbols": int(frame["symbol"].nunique()),
            "dates": int(frame["decision_date"].nunique()),
        })

    if not valid_frames:
        raise RuntimeError("no valid KOSPI marcap rows in requested range")
    panel = pd.concat(valid_frames, ignore_index=True).sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    membership = pd.concat(membership_frames, ignore_index=True).sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    rejected = pd.concat(rejected_frames, ignore_index=True) if rejected_frames else pd.DataFrame(columns=panel.columns)

    for year, g in panel.groupby(panel["decision_date"].dt.year):
        g.to_parquet(out / f"kospi-pit-{int(year)}.parquet", index=False)
    if not rejected.empty:
        rejected.to_parquet(out / "rejected_invalid_bars.parquet", index=False)

    # Keep this under a subdirectory so load_panel(), which reads top-level
    # executable parquet files, can never ingest the lineage rows accidentally.
    membership.to_parquet(lineage / "membership_status.parquet", index=False)

    daily_counts = panel.groupby("decision_date")["symbol"].nunique()
    membership_daily_counts = membership.groupby("decision_date")["symbol"].nunique()
    invalid_membership = ~membership["bar_valid_for_execution"].fillna(False).astype(bool)
    stats = {
        "schema_version": SCHEMA_VERSION,
        "source": "FinanceData/marcap",
        "source_origin": "KRX daily all-security market-cap files",
        "start": str(panel["decision_date"].min().date()),
        "end": str(panel["decision_date"].max().date()),
        "rows_written": int(len(panel)),
        "membership_rows_preserved": int(len(membership)),
        "membership_rows_without_executable_bar": int(invalid_membership.sum()),
        "membership_lineage_path": "lineage/membership_status.parquet",
        "unique_symbols": int(panel["symbol"].nunique()),
        "trading_dates": int(panel["decision_date"].nunique()),
        "daily_universe_min": int(daily_counts.min()),
        "daily_universe_median": float(daily_counts.median()),
        "daily_universe_max": int(daily_counts.max()),
        "membership_daily_universe_min": int(membership_daily_counts.min()),
        "membership_daily_universe_median": float(membership_daily_counts.median()),
        "membership_daily_universe_max": int(membership_daily_counts.max()),
        "point_in_time_universe": True,
        "survivorship_bias_possible": False,
        "security_scope": "ALL_KOSPI_LISTED_SECURITIES",
        "common_stock_identity_validated": False,
        "judge_eligible": False,
        "judge_blocker": "Common-stock identity layer not yet validated; PIT membership itself is valid.",
        "year_stats": year_stats,
        "source_sha256": hashes,
    }
    (out / "build_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "limitations.json").write_text(json.dumps({
        "point_in_time_membership": "VALID_BY_DAILY_KRX_UNIVERSE",
        "survivorship_bias": "RESOLVED_FOR_LISTED_SECURITY_MEMBERSHIP",
        "security_type": "ALL_KOSPI_SECURITIES_NOT_YET_COMMON_ONLY",
        "intraday": "DAILY_OHLC_ONLY",
        "same_bar_target_stop": "PRIMARY_ENGINE_USES_CONSERVATIVE_STOP_FIRST",
        "membership_lineage": "ALL_KOSPI_ROWS_PRESERVED_SEPARATELY_INCLUDING_INVALID_OR_HALTED_BARS",
        "allowed_use": "PIT policy/model diagnostics and preliminary economic assessment",
        "forbidden_use": "Final KR-KOSPI Judge promotion until common-stock identity is validated",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2), flush=True)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default="2026-09-28")
    ap.add_argument("--out", default="research_data/marcap_kospi_pit")
    ap.add_argument("--raw", default="research_data/marcap_raw")
    args = ap.parse_args()
    build(args.start, args.end, args.out, args.raw)


if __name__ == "__main__":
    main()
