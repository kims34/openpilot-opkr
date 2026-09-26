"""Validated 21-session +/-10% barrier-touch probability model.

Production model goals:
- Interpret "within one month" as the next 21 NYSE sessions.
- Prefer daily intraday highs/lows for barrier hits when available.
- Compare the current market with historical analogs using only causal features.
- Select analogue neighborhood size on an earlier chronological validation slice.
- Evaluate the selected model on a later untouched validation slice.
- Serve the analogue estimate only when it beats a causal unconditional baseline;
  otherwise fall back to the baseline instead of manufacturing confidence.
"""
import math
import statistics
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

HORIZON = 21
THRESHOLD = 0.10
MIN_HISTORY = 420
MIN_FEATURE_INDEX = 252
PRIOR_STRENGTH = 30.0
K_CANDIDATES = (60, 100, 160)
VALIDATION_DAYS = 504
TUNE_FRACTION = 0.50
METHOD = "validated-historical-analogs-barrier-touch-v2"
NY = ZoneInfo("America/New_York")

# Fixed, economically interpretable scales avoid using future observations to
# standardize a historical forecast during walk-forward validation.
FEATURE_SCALES = (0.04, 0.08, 0.15, 0.12, 0.15, 0.08, 0.15)
FEATURE_WEIGHTS = (1.0, 1.25, 1.0, 1.25, 1.35, 0.85, 0.85)


def fetch_ohlc(symbol, close_rows):
    """Fetch completed daily highs/lows aligned to already-validated close_rows."""
    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert/2.4"}, timeout=20,
    )
    response.raise_for_status()
    result = (response.json().get("chart", {}).get("result") or [None])[0]
    if not result or result.get("meta", {}).get("symbol") != symbol:
        raise ValueError("OHLC symbol mismatch")
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    if not (len(timestamps) == len(highs) == len(lows) == len(closes)):
        raise ValueError("OHLC length mismatch")
    by_day = {}
    for ts, hi, lo, cl in zip(timestamps, highs, lows, closes):
        if hi is None or lo is None or cl is None:
            continue
        day = datetime.fromtimestamp(int(ts), timezone.utc).astimezone(NY).date().isoformat()
        h, l, c = float(hi), float(lo), float(cl)
        if all(math.isfinite(v) and v > 0 for v in (h, l, c)) and h >= l:
            by_day[day] = (h, l, c)
    aligned = []
    for day, close in close_rows:
        h, l, _ = by_day.get(str(day), (float(close), float(close), float(close)))
        aligned.append((str(day), float(h), float(l), float(close)))
    return aligned


def _features(prices, i):
    if i < MIN_FEATURE_INDEX:
        raise ValueError("insufficient feature history")
    p = prices[i]
    r5 = p / prices[i - 5] - 1.0
    r21 = p / prices[i - 21] - 1.0
    r63 = p / prices[i - 63] - 1.0
    log_returns = [math.log(prices[j] / prices[j - 1]) for j in range(i - 20, i + 1)]
    vol21 = statistics.stdev(log_returns) * math.sqrt(252.0) if len(log_returns) > 1 else 0.0
    high252 = max(prices[i - 251 : i + 1])
    drawdown252 = p / high252 - 1.0
    ma50 = sum(prices[i - 49 : i + 1]) / 50.0
    ma200 = sum(prices[i - 199 : i + 1]) / 200.0
    gap50 = p / ma50 - 1.0
    gap200 = p / ma200 - 1.0
    return (r5, r21, r63, vol21, drawdown252, gap50, gap200)


def _distance(a, b):
    total = 0.0
    for av, bv, scale, weight in zip(a, b, FEATURE_SCALES, FEATURE_WEIGHTS):
        z = (av - bv) / scale
        total += weight * z * z
    return math.sqrt(total)


def _barrier_outcome(prices, highs, lows, i):
    anchor = prices[i]
    up_level = anchor * (1.0 + THRESHOLD)
    down_level = anchor * (1.0 - THRESHOLD)
    future_highs = highs[i + 1 : i + HORIZON + 1]
    future_lows = lows[i + 1 : i + HORIZON + 1]
    return int(any(v >= up_level for v in future_highs)), int(any(v <= down_level for v in future_lows))


def _records(prices, highs, lows):
    out = []
    last = len(prices) - HORIZON - 1
    for i in range(MIN_FEATURE_INDEX, last + 1):
        up, down = _barrier_outcome(prices, highs, lows, i)
        out.append((i, _features(prices, i), up, down))
    return out


def _baseline(records, outcome_pos):
    if not records:
        return 0.0
    return sum(r[outcome_pos] for r in records) / len(records)


def _analog_probability(target_features, training, k, outcome_pos):
    base = _baseline(training, outcome_pos)
    ranked = sorted((_distance(target_features, r[1]), r) for r in training)
    # De-cluster neighbours so a single multi-week episode cannot dominate.
    selected = []
    selected_indices = []
    for distance, record in ranked:
        idx = record[0]
        if any(abs(idx - old) < 3 for old in selected_indices):
            continue
        selected.append((distance, record))
        selected_indices.append(idx)
        if len(selected) >= k:
            break
    if not selected:
        return base, 0, 0.0
    distances = [d for d, _ in selected]
    bandwidth = max(statistics.median(distances), 0.35)
    weights = [math.exp(-0.5 * (d / bandwidth) ** 2) for d in distances]
    weight_sum = sum(weights)
    hits = sum(w * record[outcome_pos] for w, (_, record) in zip(weights, selected))
    probability = (hits + PRIOR_STRENGTH * base) / (weight_sum + PRIOR_STRENGTH)
    effective_n = (weight_sum * weight_sum / sum(w * w for w in weights)) if weights else 0.0
    return min(1.0, max(0.0, probability)), len(selected), effective_n


def _walk_forward(prices, records, k, outcome_pos, targets):
    model_sq = []
    base_sq = []
    used = 0
    for t in targets:
        # At forecast date t, only labels whose 21-session horizon has already
        # completed are eligible for training.
        training = [r for r in records if r[0] <= t - HORIZON - 1]
        if len(training) < 300:
            continue
        y_record = next((r for r in records if r[0] == t), None)
        if y_record is None:
            continue
        base = _baseline(training, outcome_pos)
        pred, _, _ = _analog_probability(_features(prices, t), training, k, outcome_pos)
        y = y_record[outcome_pos]
        model_sq.append((pred - y) ** 2)
        base_sq.append((base - y) ** 2)
        used += 1
    if not used:
        return None
    mb = sum(model_sq) / used
    bb = sum(base_sq) / used
    skill = (1.0 - mb / bb) * 100.0 if bb > 0 else 0.0
    return {"count": used, "model_brier": mb, "baseline_brier": bb, "skill": skill}


def _choose_and_validate(prices, records, outcome_pos):
    eligible = [r[0] for r in records if r[0] >= max(MIN_FEATURE_INDEX + 300 + HORIZON, len(prices) - VALIDATION_DAYS - HORIZON)]
    if len(eligible) < 120:
        return K_CANDIDATES[1], None, None
    split = max(60, int(len(eligible) * TUNE_FRACTION))
    tune_targets = eligible[:split]
    test_targets = eligible[split:]
    tune_results = []
    for k in K_CANDIDATES:
        result = _walk_forward(prices, records, k, outcome_pos, tune_targets)
        if result:
            tune_results.append((result["model_brier"], k, result))
    if not tune_results:
        return K_CANDIDATES[1], None, None
    _, best_k, tune = min(tune_results, key=lambda x: x[0])
    test = _walk_forward(prices, records, best_k, outcome_pos, test_targets)
    return best_k, tune, test


def estimate(rows, ohlc_rows=None):
    """Estimate validated P(+10% touch) and P(-10% touch) in next 21 sessions."""
    clean = [(str(d), float(p)) for d, p in rows if float(p) > 0]
    if len(clean) < MIN_HISTORY:
        raise ValueError("insufficient history for one-month probability")
    dates = [d for d, _ in clean]
    prices = [p for _, p in clean]

    if ohlc_rows and len(ohlc_rows) == len(clean):
        high_map = {str(d): float(h) for d, h, l, c in ohlc_rows}
        low_map = {str(d): float(l) for d, h, l, c in ohlc_rows}
        highs = [max(prices[i], high_map.get(dates[i], prices[i])) for i in range(len(prices))]
        lows = [min(prices[i], low_map.get(dates[i], prices[i])) for i in range(len(prices))]
        price_basis = "daily_high_low"
    else:
        highs = list(prices)
        lows = list(prices)
        price_basis = "daily_close"

    records = _records(prices, highs, lows)
    if len(records) < 300:
        raise ValueError("insufficient labelled monthly windows")
    current_features = _features(prices, len(prices) - 1)
    base_up = _baseline(records, 2)
    base_down = _baseline(records, 3)

    k_up, tune_up, test_up = _choose_and_validate(prices, records, 2)
    k_down, tune_down, test_down = _choose_and_validate(prices, records, 3)
    analog_up, sample_up, eff_up = _analog_probability(current_features, records, k_up, 2)
    analog_down, sample_down, eff_down = _analog_probability(current_features, records, k_down, 3)

    use_analog_up = bool(test_up and test_up["count"] >= 80 and test_up["skill"] > 0.0)
    use_analog_down = bool(test_down and test_down["count"] >= 80 and test_down["skill"] > 0.0)
    served_up = analog_up if use_analog_up else base_up
    served_down = analog_down if use_analog_down else base_down

    f = current_features
    return {
        "horizon_sessions": HORIZON,
        "threshold_percent": int(THRESHOLD * 100),
        "price_basis": price_basis,
        "up_10_probability": round(100.0 * served_up, 1),
        "down_10_probability": round(100.0 * served_down, 1),
        "analog_up_10_probability": round(100.0 * analog_up, 1),
        "analog_down_10_probability": round(100.0 * analog_down, 1),
        "baseline_sample_size": len(records),
        "baseline_up_10_probability": round(100.0 * base_up, 1),
        "baseline_down_10_probability": round(100.0 * base_down, 1),
        "sample_size": min(sample_up, sample_down),
        "effective_sample_up": round(eff_up, 1),
        "effective_sample_down": round(eff_down, 1),
        "selected_k_up": k_up,
        "selected_k_down": k_down,
        "validation_up": test_up,
        "validation_down": test_down,
        "tuning_up": tune_up,
        "tuning_down": tune_down,
        "selection_up": "analog" if use_analog_up else "baseline",
        "selection_down": "analog" if use_analog_down else "baseline",
        "trend_regime": "up" if f[1] >= 0 else "down",
        "volatility_regime": "high" if f[3] >= 0.20 else "low",
        "annualized_volatility": round(100.0 * f[3], 1),
        "features": {
            "return_5d": round(100.0 * f[0], 2),
            "return_21d": round(100.0 * f[1], 2),
            "return_63d": round(100.0 * f[2], 2),
            "drawdown_252d": round(100.0 * f[4], 2),
            "ma50_gap": round(100.0 * f[5], 2),
            "ma200_gap": round(100.0 * f[6], 2),
        },
        "prior_strength": int(PRIOR_STRENGTH),
        "method": METHOD,
        "as_of": clean[-1][0],
    }
