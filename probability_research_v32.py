"""Causal model-3.2 research against the deployed 3.1 policy.

The research adds a small set of price-regime challengers, but every decision
at forecast time t is made only from information and realised outcomes known by
t.  The promotion benchmark is model 3.1 itself, not merely the fixed base rate.
"""
import json, math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

SYMBOLS = ["SPY", "QQQ", "SCHD"]
HALF_LIVES = [126., 252., 504., 756., 1260., 2520.]
NY = ZoneInfo("America/New_York")
EVAL = 1008
LOOKBACK = 504
MIN_TRAIN = 300
BASE_HL = 1260.
COND_HL = 756.
SHRINK = 0.25
BASE_NAMES = ["fixed", "adaptive_hl", "prev_sign", "weekday"]
EXTRA_NAMES = ["ret_strength", "pattern2", "trend20", "drawdown60", "vol_regime"]


def fetch(symbol):
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert model-3.2 research"},
        timeout=30,
    )
    r.raise_for_status()
    x = (r.json().get("chart", {}).get("result") or [None])[0]
    if not x:
        raise RuntimeError(f"no data {symbol}")
    ts = x.get("timestamp") or []
    close = (x.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    rows = []
    for t, p in zip(ts, close):
        if p is None or not math.isfinite(float(p)) or float(p) <= 0:
            continue
        d = datetime.fromtimestamp(int(t), timezone.utc).astimezone(NY).date().isoformat()
        rows.append((d, float(p)))
    return rows


def weighted_rate(y, t, hl, mask=None):
    idx = np.arange(max(0, t - 2520), t)
    if mask is not None:
        idx = idx[mask[idx]]
    if len(idx) < 30:
        return None
    age = t - 1 - idx
    w = 0.5 ** (age / hl)
    # Beta(10,10) shrinkage keeps sparse conditional rates from becoming extreme.
    return float((w @ y[idx] + 10.0) / (w.sum() + 20.0))


def bucketize(x, cuts):
    out = np.full(len(x), -1, dtype=int)
    ok = np.isfinite(x)
    out[ok] = np.digitize(x[ok], cuts)
    return out


def rolling_vol(rets, window):
    out = np.full(len(rets), np.nan)
    for t in range(window, len(rets)):
        out[t] = float(np.std(rets[t - window + 1:t + 1]))
    return out


def regimes(prices):
    n = len(prices)
    rets = np.zeros(n)
    rets[1:] = prices[1:] / prices[:-1] - 1.0
    vol20 = rolling_vol(rets, 20)
    vol60 = rolling_vol(rets, 60)

    # Previous-session return strength, normalised by recent volatility.
    ret_z = np.full(n, np.nan)
    ok = np.isfinite(vol20) & (vol20 > 1e-8)
    ret_z[ok] = rets[ok] / vol20[ok]
    ret_strength = bucketize(ret_z, [-1.0, -0.25, 0.25, 1.0])

    # Last two session directions: --, -+, +-, ++.
    pattern2 = np.full(n, -1, dtype=int)
    for t in range(2, n):
        pattern2[t] = 2 * int(rets[t] > 0) + int(rets[t - 1] > 0)

    # 20-session trend normalised by 60-session daily volatility.
    trend_z = np.full(n, np.nan)
    for t in range(60, n):
        denom = vol60[t] * math.sqrt(20.0)
        if math.isfinite(denom) and denom > 1e-8:
            trend_z[t] = (prices[t] / prices[t - 20] - 1.0) / denom
    trend20 = bucketize(trend_z, [-0.75, -0.15, 0.15, 0.75])

    # Distance from the trailing 60-session high.
    dd = np.full(n, np.nan)
    for t in range(59, n):
        dd[t] = prices[t] / np.max(prices[t - 59:t + 1]) - 1.0
    drawdown60 = bucketize(dd, [-0.07, -0.02])

    # Volatility regime is defined causally by the current vol20 percentile
    # within the preceding year; no future distribution is used.
    vol_regime = np.full(n, -1, dtype=int)
    for t in range(272, n):
        hist = vol20[t - 252:t]
        hist = hist[np.isfinite(hist)]
        if len(hist) < 126 or not math.isfinite(vol20[t]):
            continue
        q1, q2 = np.quantile(hist, [1 / 3, 2 / 3])
        vol_regime[t] = int(vol20[t] > q1) + int(vol20[t] > q2)

    return {
        "ret_strength": ret_strength,
        "pattern2": pattern2,
        "trend20": trend20,
        "drawdown60": drawdown60,
        "vol_regime": vol_regime,
    }


def candidate_probs(prices, dates):
    n = len(prices)
    y = (prices[1:] > prices[:-1]).astype(float)
    rets = np.zeros(n)
    rets[1:] = prices[1:] / prices[:-1] - 1.0
    weekdays = np.array([datetime.fromisoformat(d).weekday() for d in dates])
    regime = regimes(prices)

    hl_probs = {hl: np.full(n - 1, np.nan) for hl in HALF_LIVES}
    for hl in HALF_LIVES:
        for t in range(MIN_TRAIN, n - 1):
            hl_probs[hl][t] = weighted_rate(y, t, hl)

    names = BASE_NAMES + EXTRA_NAMES
    out = {name: np.full(n - 1, np.nan) for name in names}
    out["fixed"][:] = hl_probs[BASE_HL]

    for t in range(MIN_TRAIN, n - 1):
        fixed = out["fixed"][t]
        hist = np.arange(max(MIN_TRAIN, t - LOOKBACK), t)
        best = (1e9, BASE_HL)
        for hl in HALF_LIVES:
            p = hl_probs[hl][hist]
            valid = ~np.isnan(p)
            if valid.sum() >= 126:
                loss = float(np.mean((p[valid] - y[hist][valid]) ** 2))
                if loss < best[0]:
                    best = (loss, hl)
        out["adaptive_hl"][t] = hl_probs[best[1]][t]

        sign = rets[t] > 0
        mask = np.zeros(n - 1, dtype=bool)
        mask[1:t] = ((rets[1:t] > 0) == sign)
        cond = weighted_rate(y, t, COND_HL, mask)
        out["prev_sign"][t] = fixed if cond is None else (1 - SHRINK) * fixed + SHRINK * cond

        target_wd = weekdays[t + 1]
        mask = np.zeros(n - 1, dtype=bool)
        mask[:t] = (weekdays[1:t + 1] == target_wd)
        cond = weighted_rate(y, t, BASE_HL, mask)
        out["weekday"][t] = fixed if cond is None else (1 - SHRINK) * fixed + SHRINK * cond

        for name in EXTRA_NAMES:
            code = regime[name][t]
            if code < 0:
                out[name][t] = fixed
                continue
            mask = np.zeros(n - 1, dtype=bool)
            mask[:t] = (regime[name][:t] == code)
            cond = weighted_rate(y, t, COND_HL, mask)
            out[name][t] = fixed if cond is None else (1 - SHRINK) * fixed + SHRINK * cond
    return y, out


def causal_selector(y, preds, t, allowed):
    fixed = preds["fixed"]
    start = max(MIN_TRAIN, t - LOOKBACK)
    mid = start + (t - start) // 2
    best = ("fixed", 0.0)
    for name in allowed:
        if name == "fixed":
            continue
        p = preds[name]
        if np.isnan(p[t]):
            continue
        gains = []
        okay = True
        for a, b in ((start, mid), (mid, t)):
            idx = np.arange(a, b)
            idx = idx[~np.isnan(p[idx]) & ~np.isnan(fixed[idx])]
            if len(idx) < 60:
                okay = False
                break
            paired = (fixed[idx] - y[idx]) ** 2 - (p[idx] - y[idx]) ** 2
            gain = float(np.mean(paired))
            # Require positive realised gain in both chronological halves.
            gains.append(gain)
        if okay and min(gains) > 0 and sum(gains) > best[1]:
            best = (name, sum(gains))
    return best[0]


def score(p, y):
    return float(np.mean((p - y) ** 2))


def main():
    results = []
    for s in SYMBOLS:
        rows = fetch(s)
        dates = [d for d, _ in rows]
        prices = np.array([p for _, p in rows], float)
        y, preds = candidate_probs(prices, dates)
        n = len(prices)
        start = n - 1 - EVAL
        p31 = np.full(n - 1, np.nan)
        p32 = np.full(n - 1, np.nan)
        c31, c32 = [], []
        for t in range(start, n - 1):
            a = causal_selector(y, preds, t, BASE_NAMES)
            b = causal_selector(y, preds, t, BASE_NAMES + EXTRA_NAMES)
            p31[t] = preds[a][t]
            p32[t] = preds[b][t]
            c31.append(a)
            c32.append(b)

        idx = np.arange(start, n - 1)
        fixed = preds["fixed"][idx]
        b32 = score(p32[idx], y[idx])
        b31 = score(p31[idx], y[idx])
        bfix = score(fixed, y[idx])
        mid = start + EVAL // 2
        h1_32, h1_31 = score(p32[start:mid], y[start:mid]), score(p31[start:mid], y[start:mid])
        h2_32, h2_31 = score(p32[mid:n - 1], y[mid:n - 1]), score(p31[mid:n - 1], y[mid:n - 1])
        extra_counts = {k: c32.count(k) for k in EXTRA_NAMES}
        all_counts = {k: c32.count(k) for k in BASE_NAMES + EXTRA_NAMES}
        results.append({
            "symbol": s,
            "brier_v32": b32,
            "brier_v31": b31,
            "brier_fixed": bfix,
            "skill_vs_v31": (1 - b32 / b31) * 100,
            "skill_vs_fixed": (1 - b32 / bfix) * 100,
            "first_half_skill_vs_v31": (1 - h1_32 / h1_31) * 100,
            "second_half_skill_vs_v31": (1 - h2_32 / h2_31) * 100,
            "v32_choices": all_counts,
            "extra_choice_days": int(sum(extra_counts.values())),
            "current_probability_v32": float(p32[n - 2]) * 100,
            "current_probability_v31": float(p31[n - 2]) * 100,
        })

    pooled32 = float(np.mean([r["brier_v32"] for r in results]))
    pooled31 = float(np.mean([r["brier_v31"] for r in results]))
    improved = sum(r["skill_vs_v31"] > 0 for r in results)
    recent_improved = sum(r["second_half_skill_vs_v31"] > 0 for r in results)
    deploy = bool(pooled32 < pooled31 and improved >= 2 and recent_improved >= 2)
    final = {
        "results": results,
        "pooled_brier_v32": pooled32,
        "pooled_brier_v31": pooled31,
        "pooled_skill_vs_v31": (1 - pooled32 / pooled31) * 100,
        "deploy": deploy,
        "promotion_rule": "pooled v3.2 < v3.1; >=2 symbols improve overall; >=2 improve in most-recent half",
    }
    print("FINAL", json.dumps(final, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
