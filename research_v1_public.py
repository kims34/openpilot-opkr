"""Public-data smoke-test builder for IndexAlert Research v1.

This path deliberately does NOT claim point-in-time universe safety. It uses a
fixed, explicitly non-PIT KOSPI smoke basket and historical daily bars from
Naver's public mobile endpoint. It exists only to validate data/backtest
plumbing in CI while the authenticated/licensed PIT source remains separate.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import requests

DEFAULT_CACHE = Path("research_data/public_smoke_daily")
SCHEMA_VERSION = "naver-fixed-universe-smoke-v3"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IndexAlertResearch/1.0)",
    "Referer": "https://m.stock.naver.com/",
}

# Reproducible engineering-smoke basket only. It is intentionally not described
# as current top-N or historical membership and must never be used for Judge claims.
SMOKE_UNIVERSE = [
    ("005930", "Samsung Electronics"), ("000660", "SK hynix"),
    ("373220", "LG Energy Solution"), ("207940", "Samsung Biologics"),
    ("005380", "Hyundai Motor"), ("000270", "Kia"),
    ("068270", "Celltrion"), ("105560", "KB Financial"),
    ("055550", "Shinhan Financial"), ("035420", "NAVER"),
    ("005490", "POSCO Holdings"), ("028260", "Samsung C&T"),
    ("012450", "Hanwha Aerospace"), ("012330", "Hyundai Mobis"),
    ("006400", "Samsung SDI"), ("051910", "LG Chem"),
    ("033780", "KT&G"), ("015760", "KEPCO"),
    ("035720", "Kakao"), ("032830", "Samsung Life"),
    ("138040", "Meritz Financial"), ("086790", "Hana Financial"),
    ("066570", "LG Electronics"), ("017670", "SK Telecom"),
    ("009150", "Samsung Electro-Mechanics"), ("034020", "Doosan Enerbility"),
    ("009540", "HD Korea Shipbuilding"), ("011200", "HMM"),
    ("096770", "SK Innovation"), ("003550", "LG"),
]


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


def smoke_universe(limit: int = 30) -> list[tuple[str, str]]:
    if limit <= 0:
        raise ValueError("universe_size must be positive")
    return SMOKE_UNIVERSE[: min(limit, len(SMOKE_UNIVERSE))]


def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    text = str(v).replace(",", "").strip()
    if text in {"", "-", "None"}:
        return None
    return float(text)


def fetch_history(code: str, start: str, end: str, page_size: int = 60) -> pd.DataFrame:
    """Fetch Naver daily bars using the endpoint's observed small-page contract.

    The endpoint currently rejects very large pageSize values with HTTP 400, so
    this smoke path uses 60 rows per page and paginates far enough for the
    requested research window.
    """
    rows: list[dict] = []
    page = 1
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    with requests.Session() as s:
        s.headers.update(HEADERS)
        while page <= 20:
            url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page={page}"
            r = s.get(url, timeout=20)
            if r.status_code >= 400:
                raise RuntimeError(
                    f"price HTTP {r.status_code} page={page} pageSize={page_size} body={r.text[:160]!r}"
                )
            try:
                data = r.json()
            except Exception as exc:
                raise RuntimeError(f"non-JSON price response status={r.status_code} prefix={r.text[:160]!r}") from exc
            if not isinstance(data, list) or not data:
                break
            oldest = None
            for item in data:
                traded = item.get("localTradedAt")
                if not traded:
                    continue
                dt = pd.Timestamp(traded)
                oldest = dt if oldest is None else min(oldest, dt)
                if dt < start_ts or dt > end_ts:
                    continue
                o = _num(item.get("openPrice")); h = _num(item.get("highPrice"))
                l = _num(item.get("lowPrice")); c = _num(item.get("closePrice"))
                vol = _num(item.get("accumulatedTradingVolume")) or 0.0
                if not all(v is not None and v > 0 for v in (o, h, l, c)):
                    continue
                if l > min(o, c) or h < max(o, c) or l > h:
                    continue
                rows.append({
                    "decision_date": dt, "symbol": code, "market": "KOSPI",
                    "open": o, "high": h, "low": l, "close": c,
                    "volume": vol, "value": c * vol,
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
    return pd.DataFrame(rows).drop_duplicates(["decision_date", "symbol"]).sort_values("decision_date").reset_index(drop=True)


def build(start: str, end: str, cache_dir: Path = DEFAULT_CACHE, universe_size: int = 30, sleep_seconds: float = 0.12) -> BuildStats:
    cache_dir.mkdir(parents=True, exist_ok=True)
    universe = smoke_universe(universe_size)
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
            success += 1; rows += len(frame)
            print(f"[{i}/{len(universe)}] {code} {name} rows={len(frame)}", flush=True)
        except Exception as exc:
            failed += 1
            failures.append({"symbol": code, "name": name, "error": f"{type(exc).__name__}: {exc}"})
            print(f"[{i}/{len(universe)}] {code} {name} FAILED {type(exc).__name__}: {exc}", flush=True)
        time.sleep(max(0.0, sleep_seconds))
    if not frames:
        raise RuntimeError("public smoke source returned zero usable symbols")
    panel = pd.concat(frames, ignore_index=True).sort_values(["decision_date", "symbol"])
    for dt, day in panel.groupby("decision_date"):
        day.to_parquet(cache_dir / f"{pd.Timestamp(dt).strftime('%Y%m%d')}.parquet", index=False)
    stats = BuildStats(
        source="Naver Finance fixed non-PIT KOSPI smoke basket + historical bars",
        start=start, end=end, universe_size=len(universe), symbols_written=success,
        symbols_failed=failed, rows_written=rows,
    )
    (cache_dir / "build_stats.json").write_text(json.dumps(asdict(stats), ensure_ascii=False, indent=2), encoding="utf-8")
    (cache_dir / "limitations.json").write_text(json.dumps({
        "judge_eligible": False,
        "reason": "Fixed smoke basket is not historical point-in-time membership and can contain survivorship/selection bias.",
        "allowed_use": "CI/data-pipeline smoke testing and provisional diagnostics only.",
        "forbidden_use": "strategy promotion, expected-return claim, or production candidate policy selection",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        (cache_dir / "failures.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2025-01-01")
    ap.add_argument("--end", default="2026-09-28")
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--universe-size", type=int, default=30)
    ap.add_argument("--sleep", type=float, default=0.12)
    args = ap.parse_args()
    stats = build(args.start, args.end, Path(args.cache), args.universe_size, args.sleep)
    print(json.dumps(asdict(stats), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
