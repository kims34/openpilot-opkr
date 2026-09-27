"""Daily constituent screener for IndexAlert.

Ranks the union of current S&P 500, NASDAQ-100 and SCHD holdings by the
validated next-session close-rise model. For each top-three stock it also
returns a mutually exclusive six-bin distribution for the NEXT trading day's
close-to-close return.

The job is server-side and cached by completed US trading session so the phone
does no constituent scanning and upstream market-data load is bounded.
"""
import json
import math
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import laggards
import monitor
import next_day_probability as base
from probability_model_v31_runtime import MODEL_VERSION, estimate_prices

LOCK = threading.Lock()
MAX_WORKERS = 6
MIN_COVERAGE_RATIO = 0.80
UA = {"User-Agent": "Mozilla/5.0 IndexAlert/3.1"}

SIX_KEYS = ["up2_plus", "up1_2", "up0_1", "down0_1", "down1_2", "down2_minus"]
SIX_LABELS = {
    "up2_plus": "+2% 이상",
    "up1_2": "+1% ~ +2%",
    "up0_1": "0% ~ +1%",
    "down0_1": "-1% ~ 0%",
    "down1_2": "-2% ~ -1%",
    "down2_minus": "-2% 이하",
}


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


def _completed_history(symbol, now=None):
    """Completed regular-session closes, split-adjusted by Yahoo, dividends excluded."""
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
    return base.parse_history(result, now)


def _universe():
    sp_list = laggards.sp500_constituents()
    sp_names = {s: n for s, n in sp_list}
    sp500 = set(sp_names)
    ndx = set(laggards.nasdaq100_symbols())
    schd = set(laggards.schd_symbols())
    members = sorted(sp500 | ndx | schd)
    return members, sp_names, sp500, ndx, schd


def _score(symbol, now):
    rows, meta = _completed_history(symbol, now)
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


def _bucket_key(r):
    if r >= 0.02:
        return "up2_plus"
    if r >= 0.01:
        return "up1_2"
    if r > 0.0:
        return "up0_1"
    if r > -0.01:
        return "down0_1"
    if r > -0.02:
        return "down1_2"
    return "down2_minus"


def _vol(values):
    if len(values) < 2:
        return 0.0
    return statistics.pstdev(values)


def _next_day_six_bins(rows, rise_probability):
    """Estimate next-session magnitude buckets and force positive mass to binary P(up).

    Shape is estimated from historical days with similar 1d/5d momentum and 20d
    realized volatility. Sparse conditional shapes are shrunk toward the stock's
    own long-run positive/negative magnitude distribution. This keeps all six
    buckets exhaustive while making the first three sum exactly to the validated
    binary next-close rise probability used for the TOP3 ranking.
    """
    prices = [float(p) for _, p in rows]
    if len(prices) < 260:
        raise ValueError("not enough history for next-day six bins")
    returns = [prices[i] / prices[i - 1] - 1.0 for i in range(1, len(prices))]
    cur_r1 = returns[-1]
    cur_r5 = prices[-1] / prices[-6] - 1.0
    cur_vol = _vol(returns[-20:])

    candidates = []
    for t in range(20, len(prices) - 1):
        hist_r1 = prices[t] / prices[t - 1] - 1.0
        hist_r5 = prices[t] / prices[t - 5] - 1.0
        hist_vol = _vol([prices[j] / prices[j - 1] - 1.0 for j in range(t - 19, t + 1)])
        next_r = prices[t + 1] / prices[t] - 1.0
        candidates.append((hist_r1, hist_r5, hist_vol, next_r))

    analog = []
    for b1, b5, bv in [
        (0.004, 0.012, 0.003),
        (0.0075, 0.020, 0.005),
        (0.012, 0.035, 0.008),
        (0.020, 0.060, 0.015),
        (0.035, 0.100, 0.025),
    ]:
        analog = [x[3] for x in candidates if abs(x[0] - cur_r1) <= b1 and abs(x[1] - cur_r5) <= b5 and abs(x[2] - cur_vol) <= bv]
        if len(analog) >= 80:
            break
    if len(analog) < 30:
        analog = [x[3] for x in candidates]
        selection = "long_run"
    else:
        selection = "similar_market"

    all_next = [x[3] for x in candidates]
    base_counts = {k: 0.0 for k in SIX_KEYS}
    analog_counts = {k: 0.0 for k in SIX_KEYS}
    for r in all_next:
        base_counts[_bucket_key(r)] += 1.0
    for r in analog:
        analog_counts[_bucket_key(r)] += 1.0

    pos_keys = SIX_KEYS[:3]
    neg_keys = SIX_KEYS[3:]

    def side_shape(keys):
        base_total = sum(base_counts[k] for k in keys)
        analog_total = sum(analog_counts[k] for k in keys)
        if base_total <= 0:
            return {k: 1.0 / len(keys) for k in keys}
        base_shape = {k: base_counts[k] / base_total for k in keys}
        if analog_total <= 0:
            return base_shape
        prior = 40.0
        weighted = {k: analog_counts[k] + prior * base_shape[k] for k in keys}
        total = sum(weighted.values())
        return {k: weighted[k] / total for k in keys}

    pos_shape = side_shape(pos_keys)
    neg_shape = side_shape(neg_keys)
    p_up = max(0.0, min(100.0, float(rise_probability)))
    p_not_up = 100.0 - p_up
    probs = {k: p_up * pos_shape[k] for k in pos_keys}
    probs.update({k: p_not_up * neg_shape[k] for k in neg_keys})

    # Remove tiny floating drift while preserving the positive-side sum.
    total = sum(probs.values())
    probs["down2_minus"] += 100.0 - total
    bins = [{"key": k, "label": SIX_LABELS[k], "probability": probs[k]} for k in SIX_KEYS]
    return {
        "horizon_sessions": 1,
        "price_basis": "next_regular_close_vs_completed_regular_close",
        "selection": selection,
        "analog_sample_size": len(analog),
        "baseline_sample_size": len(all_next),
        "rise_probability": p_up,
        "six_bins": bins,
        "six_total_probability": sum(x["probability"] for x in bins),
        "method": "검증된 다음날 상승확률 + 유사 1일·5일 모멘텀·20일 변동성의 다음날 변동폭 분포",
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
            existing = get()
            # Invalidate the previous 21-session payload after this schema change.
            if existing.get("items") and all((x.get("next_day_distribution") or {}).get("horizon_sessions") == 1 for x in existing["items"]):
                return existing

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

        def rank_key(x):
            skill = x.get("backtest_skill")
            skill = float(skill) if skill is not None and math.isfinite(float(skill)) else -999.0
            return (x["probability"], bool(x.get("verified_advantage")), skill, x["base_rate"])

        top = sorted(scored, key=rank_key, reverse=True)[:3]
        payloads = []
        for rank, item in enumerate(top, 1):
            symbol = item["symbol"]
            rows = item.pop("rows")
            quote = _quote(symbol)
            next_day_distribution = _next_day_six_bins(rows, item["probability"])
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
                "next_day_distribution": next_day_distribution,
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
            "top3": [
                (x["symbol"], round(x["probability"], 2),
                 round((x["next_day_distribution"]["six_total_probability"]), 4))
                for x in payloads
            ],
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
