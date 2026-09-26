import math
import threading
import time
from datetime import datetime, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import monitor

SYMBOLS = {"sp500": "SPY", "ndx": "QQQ", "djdiv": "SCHD"}
CACHE_SECONDS = 30 * 60
CACHE = {"updated": 0.0, "items": {}}
LOCK = threading.Lock()
NY = ZoneInfo("America/New_York")
MODEL_VERSION = "2.1-calibrated-knn"


def _fetch_prices(symbol: str):
    url = monitor.YAHOO.format(symbol=quote(symbol, safe=""))
    r = monitor.requests.get(
        url,
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers=monitor.UA,
        timeout=20,
    )
    r.raise_for_status()
    result = (r.json().get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError(f"no probability history for {symbol}")
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators", {})
    quote_data = (indicators.get("quote") or [{}])[0]
    closes = quote_data.get("close") or []
    adj_blocks = indicators.get("adjclose") or []
    adj = (adj_blocks[0].get("adjclose") if adj_blocks else None) or []
    use_adj = len(adj) == len(timestamps)

    rows = []
    for i, ts in enumerate(timestamps):
        source = adj if use_adj else closes
        if i >= len(source) or source[i] is None:
            continue
        px = float(source[i])
        if math.isfinite(px) and px > 0:
            rows.append((int(ts), px))

    # Never use an unfinished U.S. regular-session daily bar as a completed day.
    meta = result.get("meta", {})
    regular = (meta.get("currentTradingPeriod") or {}).get("regular") or {}
    regular_end = int(regular.get("end") or 0)
    if rows and regular_end and int(time.time()) < regular_end:
        last_day = datetime.fromtimestamp(rows[-1][0], tz=timezone.utc).astimezone(NY).date()
        today = datetime.now(NY).date()
        if last_day == today:
            rows.pop()

    if len(rows) < 520:
        raise RuntimeError(f"insufficient probability history for {symbol}")
    return rows


def _feature(prices, i):
    r1 = prices[i] / prices[i - 1] - 1.0
    r5 = prices[i] / prices[i - 5] - 1.0
    r20 = prices[i] / prices[i - 20] - 1.0
    returns = [prices[j] / prices[j - 1] - 1.0 for j in range(i - 19, i + 1)]
    mean = sum(returns) / len(returns)
    vol20 = math.sqrt(sum((x - mean) ** 2 for x in returns) / len(returns))
    high60 = max(prices[i - 59:i + 1])
    dd60 = prices[i] / high60 - 1.0
    return (r1, r5, r20, vol20, dd60)


def _stdev(values):
    if len(values) < 2:
        return 1.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(max(variance, 1e-12))


def _core_predict(prices, t):
    # Predict t+1 using only outcomes known through t.
    rows = []
    for i in range(60, t):
        rows.append((i, _feature(prices, i), 1.0 if prices[i + 1] > prices[i] else 0.0))
    if len(rows) < 260:
        raise RuntimeError("probability training history too short")

    current = _feature(prices, t)
    floors = (0.003, 0.010, 0.020, 0.003, 0.020)
    scales = []
    for k in range(5):
        scales.append(max(_stdev([row[1][k] for row in rows]), floors[k]))

    ranked = []
    for i, feat, outcome in rows:
        d2 = sum(((feat[k] - current[k]) / scales[k]) ** 2 for k in range(5)) / 5.0
        ranked.append((d2, i, outcome))
    ranked.sort(key=lambda x: x[0])

    k_neighbors = min(180, max(80, int(math.sqrt(len(rows)) * 2.5)))
    neighbors = ranked[:k_neighbors]
    sw = sy = sw2 = 0.0
    for d2, i, outcome in neighbors:
        similarity = math.exp(-0.5 * d2)
        age_years = (t - i) / 252.0
        recency = 0.5 ** (age_years / 4.0)
        weight = max(similarity, 1e-8) * recency
        sw += weight
        sy += weight * outcome
        sw2 += weight * weight

    raw = sy / sw if sw > 0 else 0.5
    effective_n = (sw * sw / sw2) if sw2 > 0 else 0.0

    base_sw = base_sy = 0.0
    for i, _feat, outcome in rows:
        age_years = (t - i) / 252.0
        weight = 0.5 ** (age_years / 5.0)
        base_sw += weight
        base_sy += weight * outcome
    base_rate = base_sy / base_sw if base_sw > 0 else 0.5

    # Bayesian shrinkage keeps noisy similarity samples from producing extreme odds.
    prior_strength = 80.0
    posterior = (raw * effective_n + base_rate * prior_strength) / (effective_n + prior_strength)
    return {
        "posterior": posterior,
        "base_rate": base_rate,
        "effective_n": effective_n,
        "neighbor_count": k_neighbors,
    }


def _walk_forward(prices):
    n = len(prices)
    start = max(400, n - 1 - 504)  # roughly last two trading years
    model_sq = base_sq = 0.0
    count = 0
    # Every fifth trading day keeps runtime modest while preserving multiple regimes.
    for t in range(start, n - 1, 5):
        try:
            estimate = _core_predict(prices, t)
        except Exception:
            continue
        outcome = 1.0 if prices[t + 1] > prices[t] else 0.0
        model_sq += (estimate["posterior"] - outcome) ** 2
        base_sq += (estimate["base_rate"] - outcome) ** 2
        count += 1
    if count < 40:
        return {"count": count, "model_brier": None, "base_brier": None, "skill": 0.0, "trust": 0.0}
    model_brier = model_sq / count
    base_brier = base_sq / count
    skill = 1.0 - model_brier / base_brier if base_brier > 0 else 0.0
    # Require actual out-of-sample improvement before allowing the signal to move
    # materially away from the ETF's own long-run rise rate.
    trust = max(0.0, min(1.0, skill / 0.05))
    return {
        "count": count,
        "model_brier": model_brier,
        "base_brier": base_brier,
        "skill": skill,
        "trust": trust,
    }


def estimate(symbol: str):
    rows = _fetch_prices(symbol)
    prices = [p for _ts, p in rows]
    latest_ts = rows[-1][0]
    core = _core_predict(prices, len(prices) - 1)
    validation = _walk_forward(prices)
    trust = validation["trust"]
    probability = core["base_rate"] + trust * (core["posterior"] - core["base_rate"])

    # 80% statistical interval around the shrunken estimate. Low validation trust
    # deliberately widens the interval a little to avoid false precision.
    information_n = max(30.0, core["effective_n"] + 80.0)
    se = math.sqrt(max(probability * (1.0 - probability), 1e-9) / information_n)
    half_width = 1.2816 * se + (1.0 - trust) * 0.01
    low = max(0.0, probability - half_width)
    high = min(1.0, probability + half_width)

    skill = validation["skill"]
    if validation["count"] >= 80 and skill >= 0.03 and core["effective_n"] >= 70:
        reliability = "높음"
    elif validation["count"] >= 60 and skill > 0.0 and core["effective_n"] >= 45:
        reliability = "보통"
    else:
        reliability = "낮음"

    return {
        "symbol": symbol,
        "probability": round(probability * 100.0, 2),
        "range_low": round(low * 100.0, 2),
        "range_high": round(high * 100.0, 2),
        "sample_size": int(round(core["effective_n"])),
        "neighbor_count": int(core["neighbor_count"]),
        "base_rate": round(core["base_rate"] * 100.0, 2),
        "raw_similarity_probability": round(core["posterior"] * 100.0, 2),
        "validation_count": int(validation["count"]),
        "backtest_brier": round(validation["model_brier"], 5) if validation["model_brier"] is not None else None,
        "baseline_brier": round(validation["base_brier"], 5) if validation["base_brier"] is not None else None,
        "backtest_skill": round(skill * 100.0, 2),
        "validation_trust": round(trust * 100.0, 1),
        "reliability": reliability,
        "as_of": datetime.fromtimestamp(latest_ts, tz=timezone.utc).astimezone(NY).date().isoformat(),
        "method": "10년·5요인 유사도 + 최근가중 + 베이지안 수축 + 2년 워크포워드 검증",
        "model_version": MODEL_VERSION,
    }


def refresh(force=False):
    with LOCK:
        now = time.time()
        if not force and CACHE["items"] and now - CACHE["updated"] < CACHE_SECONDS:
            return {"items": CACHE["items"], "updated_at": CACHE["updated"], "model_version": MODEL_VERSION}
        items = {}
        for index_id, symbol in SYMBOLS.items():
            try:
                items[index_id] = estimate(symbol)
            except Exception as exc:
                items[index_id] = {"symbol": symbol, "error": f"{type(exc).__name__}: {exc}"}
        CACHE["items"] = items
        CACHE["updated"] = now
        summary = {
            key: (
                value.get("probability"), value.get("range_low"), value.get("range_high"),
                value.get("backtest_skill"), value.get("reliability")
            ) if "error" not in value else value.get("error")
            for key, value in items.items()
        }
        print("next-day probabilities ready", summary, flush=True)
        return {"items": items, "updated_at": now, "model_version": MODEL_VERSION}


def get_all():
    return refresh(False)
