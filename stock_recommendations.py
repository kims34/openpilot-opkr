"""Daily constituent screener for IndexAlert.

Ranks the union of current S&P 500, NASDAQ-100 and SCHD holdings by the
validated next-session close-rise model, then computes the existing mutually
exclusive six-bin 21-session terminal-return distribution for the top three.

The job is intentionally server-side and cached by completed US trading session
so the phone does no constituent scanning and the upstream market-data load is
bounded to roughly one pass per trading day.
"""
import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import requests

import laggards
import monitor
import next_day_probability as base
import one_month_calibrated
from probability_model_v31_runtime import MODEL_VERSION, estimate_prices

LOCK = threading.Lock()
MAX_WORKERS = 6
MIN_COVERAGE_RATIO = 0.80
UA = {"User-Agent": "Mozilla/5.0 IndexAlert/3.1"}


def init_db():
    with monitor.db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS stock_recommendation_cache(
            rank INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            payload TEXT NOT NULL,
            as_of TEXT NOT NULL,
            target_date TEXT NOT NULL,
            updated REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS stock_recommendation_meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)


def _set_meta(key, value):
    with monitor.db() as con:
        con.execute(
            "INSERT INTO stock_recommendation_meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )


def _get_meta():
    with monitor.db() as con:
        return dict(con.execute("SELECT key,value FROM stock_recommendation_meta").fetchall())


def _yahoo_symbol(symbol):
    return str(symbol).strip().upper().replace(".", "-")


def _split_adjusted_history(symbol, now=None):
    """Return split-adjusted, dividend-unadjusted completed daily closes."""
    ys = _yahoo_symbol(symbol)
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ys}",
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "splits"},
        headers=UA,
        timeout=20,
    )
    r.raise_for_status()
    chart = r.json().get("chart", {})
    if chart.get("error"):
        raise ValueError("vendor error")
    result = (chart.get("result") or [None])[0]
    if not result:
        raise ValueError("history unavailable")
    timestamps = result.get("timestamp") or []
    closes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    if len(timestamps) != len(closes):
        raise ValueError("history length mismatch")

    split_events = (result.get("events") or {}).get("splits") or {}
    splits = []
    for ev in split_events.values():
        try:
            ts = int(ev.get("date") or 0)
            num = float(ev.get("numerator") or 0)
            den = float(ev.get("denominator") or 0)
            if num > 0 and den > 0:
                ratio = num / den
            else:
                raw = str(ev.get("splitRatio") or "")
                if ":" in raw:
                    a, b = raw.split(":", 1)
                    ratio = float(a) / float(b)
                else:
                    ratio = float(raw)
            if ts > 0 and math.isfinite(ratio) and ratio > 0:
                splits.append((ts, ratio))
        except Exception:
            continue
    splits.sort()

    adjusted = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            adjusted.append(None)
            continue
        px = float(close)
        factor = 1.0
        for split_ts, ratio in splits:
            if split_ts > int(ts):
                factor *= ratio
        adjusted.append(px / factor if factor > 0 else px)

    fake = dict(result)
    indicators = dict(result.get("indicators") or {})
    quote_blocks = list(indicators.get("quote") or [{}])
    quote0 = dict(quote_blocks[0] if quote_blocks else {})
    quote0["close"] = adjusted
    quote_blocks = [quote0]
    indicators["quote"] = quote_blocks
    fake["indicators"] = indicators
    return base.parse_history(fake, now)


def _universe():
    sp_list = laggards.sp500_constituents()
    sp_names = {s: n for s, n in sp_list}
    sp500 = set(sp_names)
    ndx = set(laggards.nasdaq100_symbols())
    schd = set(laggards.schd_symbols())
    members = sorted(sp500 | ndx | schd)
    return members, sp_names, sp500, ndx, schd


def _score(symbol, now):
    rows, meta = _split_adjusted_history(symbol, now)
    result = estimate_prices(
        [p for _, p in rows],
        dates=[d for d, _ in rows],
        target_date=meta["target_date"],
    )
    p = float(result.get("probability"))
    base_rate = float(result.get("base_rate"))
    if not (math.isfinite(p) and 0 <= p <= 100 and math.isfinite(base_rate)):
        raise ValueError("invalid model probability")
    return {
        "symbol": symbol,
        "probability": p,
        "base_rate": base_rate,
        "as_of": meta["as_of"],
        "target_date": meta["target_date"],
        "validation_count": int(result.get("validation_count") or 0),
        "backtest_brier": result.get("backtest_brier"),
        "baseline_brier": result.get("baseline_brier"),
        "backtest_skill": result.get("backtest_skill"),
        "skill_range_low": result.get("skill_range_low"),
        "current_strategy": result.get("current_strategy"),
        "candidate_strategy": result.get("candidate_strategy"),
        "verified_advantage": bool(result.get("verified_advantage")),
        "reliability": result.get("reliability"),
        "method": result.get("method"),
        "model_version": MODEL_VERSION,
        "rows": rows,
    }


def _six_bins(rows):
    dist = one_month_calibrated.estimate_distribution(rows)
    bins = dist.get("terminal_return_six_bins") or []
    expected = ["up10_plus", "up5_10", "up0_5", "down0_5", "down5_10", "down10_minus"]
    if len(bins) != 6 or [x.get("key") for x in bins] != expected:
        raise ValueError("six-bin distribution unavailable")
    total = sum(float(x.get("probability") or 0) for x in bins)
    if abs(total - 100.0) > 0.2:
        raise ValueError("six-bin probability total invalid")
    return {
        "horizon_sessions": 21,
        "terminal_return_six_bins": bins,
        "terminal_return_six_total_probability": total,
        "terminal_return_six_selection": dist.get("terminal_return_six_selection"),
        "terminal_return_six_validation": dist.get("terminal_return_six_validation"),
        "terminal_return_six_effective_sample": dist.get("terminal_return_six_effective_sample"),
        "trend_regime": dist.get("trend_regime"),
        "volatility_regime": dist.get("volatility_regime"),
        "annualized_volatility": dist.get("annualized_volatility"),
        "features": dist.get("features"),
    }


def _quote(symbol):
    try:
        return laggards._market_quote(monitor, symbol)
    except Exception:
        return {"symbol": symbol, "name": symbol, "current": None, "previous_close": None,
                "day_change": None, "day_change_pct": None}


def _existing_as_of():
    with monitor.db() as con:
        row = con.execute("SELECT as_of FROM stock_recommendation_cache ORDER BY rank LIMIT 1").fetchone()
        return row[0] if row else None


def refresh(force=False):
    if not LOCK.acquire(blocking=False):
        return get()
    try:
        init_db()
        now = time.time()
        _, expected_last, target = base.completed_session_info(now)
        if not force and _existing_as_of() == expected_last:
            return get()

        _set_meta("status", "building")
        _set_meta("expected_as_of", expected_last)
        members, sp_names, sp500, ndx, schd = _universe()
        total = len(members)
        scored = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(_score, symbol, now): symbol for symbol in members}
            for future in as_completed(futures):
                try:
                    scored.append(future.result())
                except Exception:
                    pass

        coverage = len(scored)
        _set_meta("coverage", f"{coverage}/{total}")
        if total <= 0 or coverage < max(30, int(total * MIN_COVERAGE_RATIO)):
            _set_meta("status", "insufficient_coverage")
            raise RuntimeError(f"stock screener coverage {coverage}/{total}")

        # Highest emitted next-day probability first. Historical skill is used
        # only as a deterministic tie-breaker; it never overrides probability.
        def rank_key(x):
            skill = x.get("backtest_skill")
            skill = float(skill) if skill is not None and math.isfinite(float(skill)) else -999.0
            return (x["probability"], bool(x.get("verified_advantage")), skill, x["base_rate"])

        top = sorted(scored, key=rank_key, reverse=True)[:3]
        payloads = []
        for rank, item in enumerate(top, 1):
            symbol = item["symbol"]
            quote = _quote(symbol)
            month = _six_bins(item.pop("rows"))
            payload = {
                **item,
                "rank": rank,
                "name": sp_names.get(symbol) or quote.get("name") or symbol,
                "current": quote.get("current"),
                "previous_close": quote.get("previous_close"),
                "day_change": quote.get("day_change"),
                "day_change_percent": quote.get("day_change_pct"),
                "sp500": symbol in sp500,
                "nasdaq100": symbol in ndx,
                "schd": symbol in schd,
                "one_month": month,
            }
            payloads.append(payload)

        updated = time.time()
        with monitor.db() as con:
            con.execute("DELETE FROM stock_recommendation_cache")
            con.executemany(
                "INSERT INTO stock_recommendation_cache(rank,symbol,payload,as_of,target_date,updated) VALUES(?,?,?,?,?,?)",
                [(x["rank"], x["symbol"], json.dumps(x, ensure_ascii=False, separators=(",", ":")),
                  x["as_of"], x["target_date"], updated) for x in payloads],
            )
        _set_meta("status", "ready")
        _set_meta("updated_at", updated)
        _set_meta("model_version", MODEL_VERSION)
        print("stock recommendations ready", {
            "coverage": f"{coverage}/{total}",
            "as_of": expected_last,
            "target": str(target.date()),
            "top3": [(x["symbol"], round(x["probability"], 2)) for x in payloads],
        }, flush=True)
        return get()
    except Exception as exc:
        _set_meta("error", f"{type(exc).__name__}: {exc}")
        print("stock recommendations failed", type(exc).__name__, str(exc), flush=True)
        return get()
    finally:
        LOCK.release()


def get():
    init_db()
    meta = _get_meta()
    with monitor.db() as con:
        rows = con.execute("SELECT payload FROM stock_recommendation_cache ORDER BY rank").fetchall()
    items = []
    for (raw,) in rows:
        try:
            items.append(json.loads(raw))
        except Exception:
            continue
    return {
        "status": meta.get("status", "building"),
        "coverage": meta.get("coverage", "0/0"),
        "updated_at": float(meta.get("updated_at", "0") or 0),
        "model_version": meta.get("model_version", MODEL_VERSION),
        "items": items,
        "note": "통계 모델 순위이며 매수·수익을 보장하지 않습니다.",
    }
