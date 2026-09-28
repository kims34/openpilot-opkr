"""Public-data smoke-test builder for IndexAlert Research v1.

This path deliberately does NOT claim point-in-time universe safety. It uses a
current large-cap KOSPI universe from Naver and historical daily bars from
Naver's public mobile endpoint. It exists to validate the research/backtest
plumbing in CI while the authenticated/licensed PIT source remains separate.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

DEFAULT_CACHE = Path("research_data/public_smoke_daily")
SCHEMA_VERSION = "naver-current-universe-smoke-v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IndexAlertResearch/1.0)",
    "Referer": "https://finance.naver.com/",
}


@dataclass(frozen=True)
class BuildStats:
    source: str
    start: str
    end: str
    universe_size: int
    symbols_written: int
    symbols_failed: int
    rows_written: int
    point_in_time_universe: bool = False
    survivorship_bias_possible: bool = True
    schema_version: str = SCHEMA_VERSION


def current_largecap_kospi(limit: int = 50) -> list[tuple[str, str]]:
    """Return current KOSPI names in Naver market-cap ordering."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    page = 1
    with requests.Session() as s:
        s.headers.update(HEADERS)
        while len(out) < limit and page <= 10:
            url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page={page}"
            r = s.get(url, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.content.decode("euc-kr", errors="ignore"), "html.parser")
            for a in soup.select('a[href*="/item/main.naver?code="]'):
                m = re.search(r"code=(\d{6})", a.get("href", ""))
                if not m:
                    continue
                code = m.group(1)
                if code in seen:
                    continue
                name = a.get_text(strip=True)
                if not name:
                    continue
                seen.add(code)
                out.append((code, name))
                if len(out) >= limit:
                    break
            page += 1
    if len(out) < min(10, limit):
        raise RuntimeError(f"Naver KOSPI universe discovery returned only {len(out)} symbols")
    return out[:limit]


def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    text = str(v).replace(",", "").strip()
    if text in {"", "-", "None"}:
        return None
    return float(text)


def fetch_history(code: str, start: str, end: str, page_size: int = 1000) -> pd.DataFrame:
    rows: list[dict] = []
    page = 1
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    with requests.Session() as s:
        s.headers.update(HEADERS)
        while page <= 10:
            url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page={page}"
            r = s.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list) or not data:
                break
            oldest = None
            for item in data:
                dt = pd.Timestamp(item.get("localTradedAt"))
                oldest = dt if oldest is None else min(oldest, dt)
                if dt < start_ts or dt > end_ts:
                    continue
                o = _num(item.get("openPrice"))
                h = _num(item.get("highPrice"))
                l = _num(item.get("lowPrice"))
                c = _num(item.get("closePrice"))
                vol = _num(item.get("accumulatedTradingVolume")) or 0.0
                if not all(v is not None and v > 0 for v in (o, h, l, c)):
                    continue
                rows.append({
                    "decision_date": dt,
                    "symbol": code,
                    "market": "KOSPI",
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": c,
                    "volume": vol,
                    "value": c * vol,
                    "source": "Naver Finance public mobile API",
                    "schema_version": SCHEMA_VERSION,
                    "point_in_time_universe": False,
                })
            if oldest is not None and oldest <= start_ts:
                break
            if len(data) < page_size:
                break
            page += 1
    if not rows:
        raise RuntimeError(f"no historical bars returned for {code}")
    x = pd.DataFrame(rows).drop_duplicates(["decision_date", "symbol"])
    return x.sort_values("decision_date").reset_index(drop=True)


def build(start: str, end: str, cache_dir: Path = DEFAULT_CACHE, universe_size: int = 50, sleep_seconds: float = 0.12) -> BuildStats:
    cache_dir.mkdir(parents=True, exist_ok=True)
    universe = current_largecap_kospi(universe_size)
    (cache_dir / "universe.json").write_text(
        json.dumps([{"symbol": c, "name": n} for c, n in universe], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    success = failed = rows = 0
    failures: list[dict] = []
    frames: list[pd.DataFrame] = []
    for i, (code, name) in enumerate(universe, 1):
        try:
            frame = fetch_history(code, start, end)
            frame["name"] = name
            frames.append(frame)
            success += 1
            rows += len(frame)
            print(f"[{i}/{len(universe)}] {code} {name} rows={len(frame)}", flush=True)
        except Exception as exc:
            failed += 1
            failures.append({"symbol": code, "name": name, "error": f"{type(exc).__name__}: {exc}"})
            print(f"[{i}/{len(universe)}] {code} {name} FAILED {type(exc).__name__}: {exc}", flush=True)
        time.sleep(max(0.0, sleep_seconds))
    if not frames:
        raise RuntimeError("public smoke source returned zero usable symbols")
    panel = pd.concat(frames, ignore_index=True).sort_values(["decision_date", "symbol"])
    # Reuse the same loader contract: one parquet per session.
    for dt, day in panel.groupby("decision_date"):
        day.to_parquet(cache_dir / f"{pd.Timestamp(dt).strftime('%Y%m%d')}.parquet", index=False)
    stats = BuildStats(
        source="Naver Finance current KOSPI large-cap universe + historical bars",
        start=start, end=end, universe_size=len(universe), symbols_written=success,
        symbols_failed=failed, rows_written=rows,
    )
    (cache_dir / "build_stats.json").write_text(json.dumps(asdict(stats), ensure_ascii=False, indent=2), encoding="utf-8")
    (cache_dir / "limitations.json").write_text(json.dumps({
        "judge_eligible": False,
        "reason": "Current-constituent universe is not historical point-in-time and can contain survivorship bias.",
        "allowed_use": "CI/data-pipeline smoke testing and provisional baseline diagnostics only.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        (cache_dir / "failures.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2025-01-01")
    ap.add_argument("--end", default="2026-09-28")
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--universe-size", type=int, default=50)
    ap.add_argument("--sleep", type=float, default=0.12)
    args = ap.parse_args()
    stats = build(args.start, args.end, Path(args.cache), args.universe_size, args.sleep)
    print(json.dumps(asdict(stats), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
