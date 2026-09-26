"""Conservative 21-session ±10% close-touch probabilities.

The estimate answers a simple historical question: from a completed close, how
frequently did any of the next 21 daily closes reach +10% or -10%? Historical
conditional rates are calculated only from fully completed forward windows.
The current regime uses information available at the as-of close only, and the
conditional rate is shrunk toward the unconditional rate to reduce sparse-bin
overconfidence. This module is part of the production probability response used
by IndexAlert v2.4 and later.
"""
import math
import statistics

HORIZON = 21
THRESHOLD = 0.10
VOL_CUTOFF = 0.20
PRIOR_STRENGTH = 40.0
MIN_HISTORY = 80
METHOD = "empirical-bayes-regime-close-touch-v1"


def _state(prices, i):
    """Return a causal trend/volatility state using closes through index i."""
    if i < 20:
        raise ValueError("need at least 21 closes for regime")
    trend = "up" if prices[i] >= prices[i - 20] else "down"
    returns = [math.log(prices[j] / prices[j - 1]) for j in range(i - 19, i + 1)]
    vol = statistics.stdev(returns) * math.sqrt(252.0) if len(returns) > 1 else 0.0
    vol_regime = "high" if vol >= VOL_CUTOFF else "low"
    return trend, vol_regime, vol


def estimate(rows):
    """Estimate P(+10% close touch) and P(-10% close touch) in next 21 sessions.

    rows: chronological sequence of (date, adjusted/close price) pairs.
    Only fully realized historical windows are used. Probabilities are returned
    on a 0..100 scale for the Android API.
    """
    clean = [(str(d), float(p)) for d, p in rows if float(p) > 0]
    if len(clean) < MIN_HISTORY:
        raise ValueError("insufficient history for one-month probability")
    prices = [p for _, p in clean]

    total_n = total_up = total_down = 0
    buckets = {}
    last_completed_asof = len(prices) - HORIZON - 1
    for i in range(20, last_completed_asof + 1):
        trend, vol_regime, _ = _state(prices, i)
        future = prices[i + 1 : i + HORIZON + 1]
        anchor = prices[i]
        up_hit = any(p >= anchor * (1.0 + THRESHOLD) for p in future)
        down_hit = any(p <= anchor * (1.0 - THRESHOLD) for p in future)
        total_n += 1
        total_up += int(up_hit)
        total_down += int(down_hit)
        bucket = buckets.setdefault((trend, vol_regime), [0, 0, 0])
        bucket[0] += 1
        bucket[1] += int(up_hit)
        bucket[2] += int(down_hit)

    if total_n <= 0:
        raise ValueError("no completed one-month windows")

    base_up = total_up / total_n
    base_down = total_down / total_n
    trend, vol_regime, annualized_vol = _state(prices, len(prices) - 1)
    cond_n, cond_up, cond_down = buckets.get((trend, vol_regime), [0, 0, 0])

    # Empirical-Bayes shrinkage: sparse regimes cannot create extreme confidence.
    up_p = (cond_up + PRIOR_STRENGTH * base_up) / (cond_n + PRIOR_STRENGTH)
    down_p = (cond_down + PRIOR_STRENGTH * base_down) / (cond_n + PRIOR_STRENGTH)

    return {
        "horizon_sessions": HORIZON,
        "threshold_percent": int(THRESHOLD * 100),
        "price_basis": "daily_close",
        "up_10_probability": round(100.0 * up_p, 1),
        "down_10_probability": round(100.0 * down_p, 1),
        "sample_size": int(cond_n),
        "baseline_sample_size": int(total_n),
        "baseline_up_10_probability": round(100.0 * base_up, 1),
        "baseline_down_10_probability": round(100.0 * base_down, 1),
        "trend_regime": trend,
        "volatility_regime": vol_regime,
        "annualized_volatility": round(100.0 * annualized_vol, 1),
        "prior_strength": int(PRIOR_STRENGTH),
        "method": METHOD,
        "as_of": clean[-1][0],
    }
