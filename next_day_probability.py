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
MODEL_VERSION = "2.2.1-holdout-selected"


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

    # Do not train on an unfinished U.S. regular-session daily bar.
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

    # First shrink noisy neighbors toward the ETF's own recent long-run rise rate.
    prior_strength = 80.0
    posterior = (raw * effective_n + base_rate * prior_strength) / (effective_n + prior_strength)
    return {
        "posterior": posterior,
        "base_rate": base_rate,
        "effective_n": effective_n,
        "neighbor_count": k_neighbors,
    }


def _brier(points, alpha):
    if not points:
        return None
    total = 0.0
    for posterior, base, outcome in points:
        p = max(0.01, min(0.99, base + alpha * (posterior - base)))
        total += (p - outcome) ** 2
    return total / len(points)


def _fit_alpha(points):
    # One-parameter calibration is intentionally simple to reduce overfitting.
    # alpha=0 means base rate only; 1 means the raw Bayesian KNN signal.
    best_alpha = 0.0
    best_score = float("inf")
    for step in range(0, 26):  # 0.00 .. 1.25
        alpha = step * 0.05
        score = _brier(points, alpha)
        if score is not None and score < best_score:
            best_score = score
            best_alpha = alpha
    return best_alpha, best_score


def _walk_forward(prices):
    n = len(prices)
    # About three trading years. Every fourth day keeps runtime reasonable while
    # giving enough chronologically ordered out-of-sample predictions to calibrate.
    start = max(400, n - 1 - 756)
    points = []
    for t in range(start, n - 1, 4):
        try:
            estimate = _core_predict(prices, t)
        except Exception:
            continue
        outcome = 1.0 if prices[t + 1] > prices[t] else 0.0
        points.append((estimate["posterior"], estimate["base_rate"], outcome))

    if len(points) < 60:
        return {
            "count": len(points), "alpha": 0.0, "model_brier": None,
            "uncalibrated_brier": None, "base_brier": None,
            "skill": 0.0, "trust": 0.0, "choice": "base",
        }

    # Fit calibration on the earlier portion, then choose among base/raw/calibrated
    # on the chronologically later holdout. The selected alpha is exactly the alpha
    # used for the live probability, so the reported validation matches the model.
    split = max(40, min(len(points) - 30, int(len(points) * 0.65)))
    fit_points = points[:split]
    holdout = points[split:]
    fitted_alpha, _ = _fit_alpha(fit_points)

    base_brier = _brier(holdout, 0.0)
    raw_brier = _brier(holdout, 1.0)
    calibrated_brier = _brier(holdout, fitted_alpha)

    choices = [
        (base_brier if base_brier is not None else float("inf"), 0.0, "base"),
        (raw_brier if raw_brier is not None else float("inf"), 1.0, "raw"),
        (calibrated_brier if calibrated_brier is not None else float("inf"), fitted_alpha, "calibrated"),
    ]
    best_holdout, selected_alpha, choice = min(choices, key=lambda x: x[0])

    if base_brier is None or best_holdout >= base_brier:
        selected_alpha = 0.0
        choice = "base"
        best_holdout = base_brier if base_brier is not None else best_holdout

    skill = 1.0 - best_holdout / base_brier if base_brier and base_brier > 0 else 0.0
    # Trust is now descriptive only. It widens/narrows the interval but does not
    # alter the selected probability a second time.
    trust = max(0.0, min(1.0, skill / 0.04))

    return {
        "count": len(holdout),
        "total_validation_count": len(points),
        "alpha": selected_alpha,
        "model_brier": best_holdout,
        "uncalibrated_brier": raw_brier,
        "base_brier": base_brier,
        "skill": skill,
        "trust": trust,
        "choice": choice,
    }


def estimate(symbol: str):
    rows = _fetch_prices(symbol)
    prices = [p for _ts, p in rows]
    latest_ts = rows[-1][0]
    core = _core_predict(prices, len(prices) - 1)
    validation = _walk_forward(prices)

    alpha = validation["alpha"]
    probability = core["base_rate"] + alpha * (core["posterior"] - core["base_rate"])
    probability = max(0.01, min(0.99, probability))
    trust = validation["trust"]

    # 80% statistical interval around the holdout-selected estimate.
    information_n = max(30.0, core["effective_n"] + 80.0)
    se = math.sqrt(max(probability * (1.0 - probability), 1e-9) / information_n)
    half_width = 1.2816 * se + (1.0 - trust) * 0.012
    low = max(0.0, probability - half_width)
    high = min(1.0, probability + half_width)

    skill = validation["skill"]
    if validation["count"] >= 60 and skill >= 0.03 and core["effective_n"] >= 65:
        reliability = "높음"
    elif validation["count"] >= 40 and skill >= 0.01 and core["effective_n"] >= 40:
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
        "calibration_alpha": round(alpha, 2),
        "validation_choice": validation["choice"],
        "validation_count": int(validation["count"]),
        "total_validation_count": int(validation.get("total_validation_count", validation["count"])),
        "backtest_brier": round(validation["model_brier"], 5) if validation["model_brier"] is not None else None,
        "uncalibrated_brier": round(validation["uncalibrated_brier"], 5) if validation["uncalibrated_brier"] is not None else None,
        "baseline_brier": round(validation["base_brier"], 5) if validation["base_brier"] is not None else None,
        "backtest_skill": round(skill * 100.0, 2),
        "validation_trust": round(trust * 100.0, 1),
        "reliability": reliability,
        "as_of": datetime.fromtimestamp(latest_ts, tz=timezone.utc).astimezone(NY).date().isoformat(),
        "method": "10년·5요인 유사도 + 베이지안 수축 + 3년 워크포워드 홀드아웃 선택",
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
                value.get("backtest_skill"), value.get("calibration_alpha"),
                value.get("validation_choice"), value.get("reliability")
            ) if "error" not in value else value.get("error")
            for key, value in items.items()
        }
        print("next-day probabilities ready", summary, flush=True)
        return {"items": items, "updated_at": now, "model_version": MODEL_VERSION}


def get_all():
    return refresh(False)
