"""IndexAlert KOSPI research v1: point-in-time daily universe + baseline backtest.

This module is deliberately separate from the production recommendation stack.
It builds a dated KOSPI universe from KRX data (via pykrx), caches raw daily
cross-sections, then evaluates simple baseline champions using information
available at each completed close and an executable next-session open entry.

The first purpose is falsification, not optimization: if simple baselines do not
show stable cost-adjusted value, later ML stages must not be promoted just
because they look more sophisticated.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Tuple

from pykrx import stock

SCHEMA_VERSION = "kospi-pit-daily-v1"
MODEL_VERSION = "baseline-v1"
DEFAULT_DB = os.environ.get("INDEXALERT_RESEARCH_DB", "/tmp/indexalert-research.sqlite")

# These are stress assumptions, not claims about exact realized costs.  They are
# reported side by side so a gross edge that disappears under small friction is
# never mistaken for a deployable strategy.
COST_SCENARIOS = {
    "gross": 0.0,
    "low_10bp": 0.0010,
    "base_25bp": 0.0025,
    "stress_50bp": 0.0050,
}

HORIZONS = (1, 2, 3, 5)
TOP_K = 3


def _ymd(x) -> str:
    if isinstance(x, (datetime, date)):
        return x.strftime("%Y%m%d")
    s = str(x).replace("-", "")
    if len(s) != 8 or not s.isdigit():
        raise ValueError(f"invalid date: {x}")
    return s


def _median(xs: Iterable[float]) -> float:
    vals = [float(x) for x in xs if x is not None and math.isfinite(float(x))]
    return statistics.median(vals) if vals else 0.0


def _percentile(values: Iterable[float], q: float) -> float:
    vals = sorted(float(v) for v in values if v is not None and math.isfinite(float(v)))
    if not vals:
        return 0.0
    q = min(1.0, max(0.0, float(q)))
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def _rank_pct(values: Dict[str, float]) -> Dict[str, float]:
    ordered = sorted(values.items(), key=lambda kv: (kv[1], kv[0]))
    n = len(ordered)
    if n <= 1:
        return {k: 0.5 for k, _ in ordered}
    return {k: i / (n - 1) for i, (k, _) in enumerate(ordered)}


def _profit_factor(returns: Iterable[float]):
    vals = [float(x) for x in returns if x is not None and math.isfinite(float(x))]
    gains = sum(x for x in vals if x > 0)
    losses = -sum(x for x in vals if x < 0)
    if losses <= 0:
        return None if gains <= 0 else float("inf")
    return gains / losses


def _max_drawdown(daily_returns: Iterable[float]) -> float:
    wealth = 1.0
    peak = 1.0
    worst = 0.0
    for r in daily_returns:
        wealth *= max(0.0, 1.0 + float(r))
        peak = max(peak, wealth)
        dd = wealth / peak - 1.0
        worst = min(worst, dd)
    return worst


@dataclass(frozen=True)
class Bar:
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    value: float


class ResearchStore:
    def __init__(self, path: str = DEFAULT_DB):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.con = sqlite3.connect(path, timeout=60)
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.execute("PRAGMA synchronous=NORMAL")
        self._init()

    def _init(self):
        self.con.executescript(
            """
            CREATE TABLE IF NOT EXISTS research_daily_ohlcv(
                trade_date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                trade_value REAL NOT NULL,
                source TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                ingested_at REAL NOT NULL,
                PRIMARY KEY(trade_date, ticker)
            );
            CREATE TABLE IF NOT EXISTS research_daily_meta(
                trade_date TEXT PRIMARY KEY,
                row_count INTEGER NOT NULL,
                source TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                ingested_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS research_runs(
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                market TEXT NOT NULL,
                from_date TEXT NOT NULL,
                to_date TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                model_version TEXT NOT NULL,
                created_at REAL NOT NULL,
                payload TEXT NOT NULL
            );
            """
        )
        self.con.commit()

    def has_date(self, d: str) -> bool:
        row = self.con.execute(
            "SELECT row_count FROM research_daily_meta WHERE trade_date=? AND schema_version=?",
            (d, SCHEMA_VERSION),
        ).fetchone()
        return bool(row and int(row[0]) > 0)

    def write_date(self, d: str, bars: List[Bar]):
        now = time.time()
        with self.con:
            self.con.execute("DELETE FROM research_daily_ohlcv WHERE trade_date=?", (d,))
            self.con.executemany(
                "INSERT INTO research_daily_ohlcv VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                [
                    (
                        d, b.ticker, b.open, b.high, b.low, b.close, b.volume,
                        b.value, "KRX/pykrx", SCHEMA_VERSION, now,
                    )
                    for b in bars
                ],
            )
            self.con.execute(
                "INSERT INTO research_daily_meta(trade_date,row_count,source,schema_version,ingested_at) "
                "VALUES(?,?,?,?,?) ON CONFLICT(trade_date) DO UPDATE SET "
                "row_count=excluded.row_count,source=excluded.source," 
                "schema_version=excluded.schema_version,ingested_at=excluded.ingested_at",
                (d, len(bars), "KRX/pykrx", SCHEMA_VERSION, now),
            )

    def read_date(self, d: str) -> Dict[str, Bar]:
        rows = self.con.execute(
            "SELECT ticker,open,high,low,close,volume,trade_value "
            "FROM research_daily_ohlcv WHERE trade_date=? ORDER BY ticker",
            (d,),
        ).fetchall()
        return {
            r[0]: Bar(r[0], *(float(x) for x in r[1:]))
            for r in rows
        }

    def save_run(self, from_date: str, to_date: str, payload: dict):
        with self.con:
            cur = self.con.execute(
                "INSERT INTO research_runs(market,from_date,to_date,schema_version,model_version,created_at,payload) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    "KOSPI", from_date, to_date, SCHEMA_VERSION, MODEL_VERSION,
                    time.time(), json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                ),
            )
        return int(cur.lastrowid)


COL = {
    "open": "시가",
    "high": "고가",
    "low": "저가",
    "close": "종가",
    "volume": "거래량",
    "value": "거래대금",
}


def fetch_krx_date(d: str, retries: int = 4) -> List[Bar]:
    d = _ymd(d)
    last = None
    for attempt in range(retries):
        try:
            df = stock.get_market_ohlcv_by_ticker(d, market="KOSPI", alternative=False)
            if df is None or df.empty:
                raise RuntimeError("empty KOSPI cross-section")
            missing = [v for v in COL.values() if v not in df.columns]
            if missing:
                raise RuntimeError(f"missing columns: {missing}")
            bars = []
            for ticker, row in df.iterrows():
                try:
                    vals = {k: float(row[v]) for k, v in COL.items()}
                    if not all(math.isfinite(x) for x in vals.values()):
                        continue
                    if vals["open"] <= 0 or vals["close"] <= 0 or vals["value"] <= 0:
                        continue
                    if not (vals["low"] <= vals["open"] <= vals["high"] and vals["low"] <= vals["close"] <= vals["high"]):
                        continue
                    bars.append(
                        Bar(
                            str(ticker).zfill(6), vals["open"], vals["high"], vals["low"],
                            vals["close"], vals["volume"], vals["value"],
                        )
                    )
                except Exception:
                    continue
            if len(bars) < 100:
                raise RuntimeError(f"suspicious KOSPI coverage: {len(bars)}")
            return bars
        except Exception as exc:
            last = exc
            time.sleep(1.0 + attempt * 1.5)
    raise RuntimeError(f"KRX fetch failed {d}: {type(last).__name__}: {last}")


def business_days(from_date: str, to_date: str) -> List[str]:
    start, end = _ymd(from_date), _ymd(to_date)
    days = stock.get_previous_business_days(fromdate=start, todate=end)
    return [x.strftime("%Y%m%d") for x in days if start <= x.strftime("%Y%m%d") <= end]


def build_dataset(from_date: str, to_date: str, store: ResearchStore, *, sleep_s: float = 0.08):
    days = business_days(from_date, to_date)
    fetched = 0
    cached = 0
    for i, d in enumerate(days, 1):
        if store.has_date(d):
            cached += 1
            continue
        bars = fetch_krx_date(d)
        store.write_date(d, bars)
        fetched += 1
        if sleep_s:
            time.sleep(sleep_s)
        if i % 25 == 0:
            print("dataset", {"day": i, "total": len(days), "fetched": fetched, "cached": cached}, flush=True)
    return days, {"fetched_days": fetched, "cached_days": cached, "total_days": len(days)}


def _features_for_day(history: Dict[str, List[Tuple[str, Bar]]], current: Dict[str, Bar]):
    mom5 = {}
    mom20 = {}
    liq20 = {}
    invalid_jump = set()
    for ticker, bar in current.items():
        rows = history.get(ticker, [])
        if len(rows) < 20:
            continue
        # history contains only sessions strictly before the current date.
        c5 = rows[-5][1].close
        c20 = rows[-20][1].close
        if c5 <= 0 or c20 <= 0:
            continue
        m5 = bar.close / c5 - 1.0
        m20 = bar.close / c20 - 1.0
        # Raw KRX prices are intentionally used.  Very large discontinuities can
        # be splits/mergers or bad data, so quarantine them rather than inventing
        # an adjusted history that was unavailable in this v1 data layer.
        recent_closes = [x[1].close for x in rows[-20:]] + [bar.close]
        for a, b in zip(recent_closes, recent_closes[1:]):
            if a > 0 and abs(b / a - 1.0) >= 0.45:
                invalid_jump.add(ticker)
                break
        mom5[ticker] = m5
        mom20[ticker] = m20
        liq20[ticker] = _median([x[1].value for x in rows[-20:]])

    for ticker in invalid_jump:
        mom5.pop(ticker, None)
        mom20.pop(ticker, None)
        liq20.pop(ticker, None)

    common = set(mom5) & set(mom20) & set(liq20)
    if not common:
        return {}
    cutoff = _percentile((liq20[t] for t in common), 0.20)
    eligible = [t for t in common if liq20[t] >= cutoff and liq20[t] > 0]
    if len(eligible) < TOP_K:
        return {}
    r20 = _rank_pct({t: mom20[t] for t in eligible})
    rliq = _rank_pct({t: math.log1p(liq20[t]) for t in eligible})
    return {
        "mom5": {t: mom5[t] for t in eligible},
        "mom20": {t: mom20[t] for t in eligible},
        "mom20_liq": {t: 0.80 * r20[t] + 0.20 * rliq[t] for t in eligible},
        "liquidity_cutoff": cutoff,
        "eligible_count": len(eligible),
    }


def _summarize_trade_returns(returns: List[float]):
    if not returns:
        return {"n": 0, "mean": None, "median": None, "precision_positive": None, "profit_factor": None}
    vals = [float(x) for x in returns]
    pf = _profit_factor(vals)
    if pf == float("inf"):
        pf = "inf"
    return {
        "n": len(vals),
        "mean": sum(vals) / len(vals),
        "median": statistics.median(vals),
        "precision_positive": sum(x > 0 for x in vals) / len(vals),
        "profit_factor": pf,
        "p10": _percentile(vals, 0.10),
        "p90": _percentile(vals, 0.90),
    }


def backtest(days: List[str], store: ResearchStore):
    daily = {d: store.read_date(d) for d in days}
    history: Dict[str, List[Tuple[str, Bar]]] = defaultdict(list)
    selections = []

    for idx, d in enumerate(days):
        current = daily[d]
        feats = _features_for_day(history, current)
        if feats:
            for model in ("mom5", "mom20", "mom20_liq"):
                scores = feats[model]
                top = sorted(scores.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:TOP_K]
                selections.append(
                    {
                        "decision_index": idx,
                        "decision_date": d,
                        "model": model,
                        "eligible_count": feats["eligible_count"],
                        "liquidity_cutoff": feats["liquidity_cutoff"],
                        "top": [t for t, _ in top],
                    }
                )
        for ticker, bar in current.items():
            history[ticker].append((d, bar))

    returns = {
        model: {h: {name: [] for name in COST_SCENARIOS} for h in HORIZONS}
        for model in ("mom5", "mom20", "mom20_liq")
    }
    missed = defaultdict(int)
    day1_portfolio = {model: {name: [] for name in COST_SCENARIOS} for model in returns}

    for sel in selections:
        i = sel["decision_index"]
        if i + 1 >= len(days):
            continue
        entry_day = days[i + 1]
        day1_by_cost = {name: [] for name in COST_SCENARIOS}
        for ticker in sel["top"]:
            entry_bar = daily[entry_day].get(ticker)
            if entry_bar is None or entry_bar.open <= 0:
                missed[(sel["model"], "entry")] += 1
                continue
            for h in HORIZONS:
                exit_i = i + h
                # h=1 means next session open -> that same session close.
                if exit_i >= len(days):
                    continue
                exit_bar = daily[days[exit_i]].get(ticker)
                if exit_bar is None or exit_bar.close <= 0:
                    missed[(sel["model"], f"exit_{h}")] += 1
                    continue
                gross = exit_bar.close / entry_bar.open - 1.0
                for cost_name, cost in COST_SCENARIOS.items():
                    net = gross - cost
                    returns[sel["model"]][h][cost_name].append(net)
                    if h == 1:
                        day1_by_cost[cost_name].append(net)
        for cost_name, vals in day1_by_cost.items():
            if vals:
                day1_portfolio[sel["model"]][cost_name].append(sum(vals) / len(vals))

    models = {}
    for model, horizons in returns.items():
        models[model] = {"horizons": {}, "day1_portfolio": {}}
        for h, costs in horizons.items():
            models[model]["horizons"][str(h)] = {
                cost_name: _summarize_trade_returns(vals)
                for cost_name, vals in costs.items()
            }
        for cost_name, vals in day1_portfolio[model].items():
            models[model]["day1_portfolio"][cost_name] = {
                "n_days": len(vals),
                "mean_daily": (sum(vals) / len(vals)) if vals else None,
                "precision_positive_days": (sum(x > 0 for x in vals) / len(vals)) if vals else None,
                "max_drawdown": _max_drawdown(vals) if vals else None,
                "compounded_return": (math.prod(1.0 + x for x in vals) - 1.0) if vals else None,
            }

    return {
        "schema_version": SCHEMA_VERSION,
        "model_version": MODEL_VERSION,
        "market": "KOSPI",
        "decision_rule": "completed_close_signal_then_next_regular_open_entry",
        "top_k": TOP_K,
        "horizons_sessions": list(HORIZONS),
        "cost_scenarios": COST_SCENARIOS,
        "selection_days": len({x["decision_date"] for x in selections}),
        "selection_rows": len(selections),
        "models": models,
        "execution_misses": {f"{k[0]}:{k[1]}": v for k, v in missed.items()},
        "limitations": [
            "pykrx/KRX daily raw prices are used; >=45% discontinuity windows are quarantined instead of retroactively adjusted",
            "cost scenarios are stress assumptions until broker/quote execution residuals are estimated",
            "sector-relative baseline and intraday OPEN/+5/+15 comparison require the next data stage",
        ],
    }


def run(from_date: str, to_date: str, db_path: str = DEFAULT_DB):
    start, end = _ymd(from_date), _ymd(to_date)
    store = ResearchStore(db_path)
    days, build = build_dataset(start, end, store)
    if len(days) < 35:
        raise RuntimeError("at least ~35 trading days required; >1 year is preferred")
    result = backtest(days, store)
    result.update(
        {
            "from_date": start,
            "to_date": end,
            "trading_days": len(days),
            "data_build": build,
            "research_db": db_path,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
    )
    result["run_id"] = store.save_run(start, end, result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default="20250101")
    parser.add_argument("--to-date", default="20260925")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    payload = run(args.from_date, args.to_date, args.db)
    text = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
