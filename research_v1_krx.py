"""KRX point-in-time daily panel builder for IndexAlert Research v1.

Uses pykrx's date-specific KOSPI market snapshots. The resulting panel keeps
symbols that existed on each historical date instead of projecting today's
constituents backward.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from exchange_calendars import get_calendar
from pykrx import stock


SCHEMA_VERSION = "krx-pit-daily-v1"
DEFAULT_CACHE = Path("research_data/krx_daily")


@dataclass(frozen=True)
class BuildStats:
    start: str
    end: str
    sessions_requested: int
    sessions_written: int
    sessions_existing: int
    sessions_failed: int
    rows_written: int
    schema_version: str = SCHEMA_VERSION


def _sessions(start: str, end: str) -> list[str]:
    cal = get_calendar("XKRX")
    idx = cal.sessions_in_range(pd.Timestamp(start), pd.Timestamp(end))
    return [pd.Timestamp(x).date().strftime("%Y%m%d") for x in idx]


def _normalize_day(df: pd.DataFrame, ymd: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy().reset_index()
    # pykrx uses ticker as index; tolerate localized index labels.
    first = x.columns[0]
    x = x.rename(columns={first: "symbol"})
    mapping = {
        "시가": "open",
        "고가": "high",
        "저가": "low",
        "종가": "close",
        "거래량": "volume",
        "거래대금": "value",
        "등락률": "day_return_pct",
    }
    x = x.rename(columns={k: v for k, v in mapping.items() if k in x.columns})
    required = ["symbol", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in x.columns]
    if missing:
        raise RuntimeError(f"pykrx schema missing {missing} on {ymd}: {list(x.columns)}")
    if "value" not in x.columns:
        x["value"] = x["close"].astype(float) * x["volume"].astype(float)
    x["decision_date"] = pd.to_datetime(ymd, format="%Y%m%d")
    x["market"] = "KOSPI"
    x["source"] = "KRX via pykrx"
    x["schema_version"] = SCHEMA_VERSION
    for c in ["open", "high", "low", "close", "volume", "value"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    x["symbol"] = x["symbol"].astype(str).str.zfill(6)
    x = x.dropna(subset=["open", "high", "low", "close"])
    x = x[(x[["open", "high", "low", "close"]] > 0).all(axis=1)]
    x = x[(x["low"] <= x[["open", "close"]].min(axis=1)) & (x["high"] >= x[["open", "close"]].max(axis=1))]
    return x[[
        "decision_date", "symbol", "market", "open", "high", "low", "close",
        "volume", "value", "source", "schema_version",
    ]].sort_values("symbol").reset_index(drop=True)


def fetch_day(ymd: str) -> pd.DataFrame:
    # Date-specific call is the PIT boundary: only securities returned for the
    # historical KOSPI session enter that session's universe.
    raw = stock.get_market_ohlcv_by_ticker(ymd, market="KOSPI")
    return _normalize_day(raw, ymd)


def build(start: str, end: str, cache_dir: Path = DEFAULT_CACHE, sleep_seconds: float = 0.15) -> BuildStats:
    cache_dir.mkdir(parents=True, exist_ok=True)
    sessions = _sessions(start, end)
    written = existing = failed = rows = 0
    failures: list[dict] = []
    for i, ymd in enumerate(sessions, 1):
        out = cache_dir / f"{ymd}.parquet"
        if out.exists() and out.stat().st_size > 0:
            existing += 1
            continue
        try:
            frame = fetch_day(ymd)
            if frame.empty:
                raise RuntimeError("empty KOSPI snapshot")
            frame.to_parquet(out, index=False)
            written += 1
            rows += len(frame)
            print(f"[{i}/{len(sessions)}] {ymd} rows={len(frame)}", flush=True)
        except Exception as exc:
            failed += 1
            failures.append({"date": ymd, "error": f"{type(exc).__name__}: {exc}"})
            print(f"[{i}/{len(sessions)}] {ymd} FAILED {type(exc).__name__}: {exc}", flush=True)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    stats = BuildStats(
        start=start,
        end=end,
        sessions_requested=len(sessions),
        sessions_written=written,
        sessions_existing=existing,
        sessions_failed=failed,
        rows_written=rows,
    )
    (cache_dir / "build_stats.json").write_text(json.dumps(asdict(stats), ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        (cache_dir / "failures.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def load_panel(cache_dir: Path = DEFAULT_CACHE) -> pd.DataFrame:
    files = sorted(p for p in cache_dir.glob("*.parquet") if p.is_file())
    if not files:
        raise RuntimeError(f"no parquet data in {cache_dir}")
    frames = [pd.read_parquet(p) for p in files]
    x = pd.concat(frames, ignore_index=True)
    x["decision_date"] = pd.to_datetime(x["decision_date"])
    return x.sort_values(["decision_date", "symbol"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--end", default=date.today().isoformat())
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--sleep", type=float, default=0.15)
    args = ap.parse_args()
    stats = build(args.start, args.end, Path(args.cache), args.sleep)
    print(json.dumps(asdict(stats), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
