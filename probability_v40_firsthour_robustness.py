"""Frozen-config robustness audit for the v4.0 first-hour challenger.

The configurations below were selected strictly on the development sample by
probability_v40_firsthour_research.py.  This audit does not re-select them.  It
examines the untouched final 126 sessions with six non-overlapping 21-session
blocks and a moving-block bootstrap of Brier gain versus the validated v3.9
open nowcast.
"""
from __future__ import annotations

import json
import time

import numpy as np

import next_day_probability as data
import probability_v40_firsthour_research as r

FROZEN = {
    "SPY": (126, 30.0, 0.08),
    "QQQ": (126, 100.0, 0.08),
    "SCHD": (378, 10.0, 0.08),
}
HOLDOUT = 126
BLOCK = 10
BOOT = 10000


def _series(symbol, shared):
    rows, meta = data.fetch_history(symbol, time.time())
    daily = r.daily_ohlcv(symbol)
    dates, closes, pos, outcomes, p39 = r._v39_series(symbol, rows, meta, daily)
    hour_rows = r._hour_features(
        symbol, dates, closes, pos, shared[symbol], shared["SPY"], shared["QQQ"], shared["^VIX"]
    )
    source_idx = np.asarray([x[0] for x in hour_rows], int)
    x = np.vstack([x[3] for x in hour_rows])
    y = outcomes[source_idx]
    prior = p39[source_idx]
    targets = [x[2] for x in hour_rows]
    pred, active = r._causal_predictions(prior, y, x, FROZEN[symbol])
    if len(y) < HOLDOUT:
        raise RuntimeError("holdout too short")
    return targets[-HOLDOUT:], y[-HOLDOUT:], prior[-HOLDOUT:], pred[-HOLDOUT:], active[-HOLDOUT:]


def _bootstrap(diff, seed):
    rng = np.random.default_rng(seed)
    n = len(diff)
    starts_max = n - BLOCK + 1
    blocks_needed = int(np.ceil(n / BLOCK))
    means = np.empty(BOOT)
    for i in range(BOOT):
        starts = rng.integers(0, starts_max, size=blocks_needed)
        sample = np.concatenate([diff[s:s+BLOCK] for s in starts])[:n]
        means[i] = float(np.mean(sample))
    q = np.quantile(means, [0.025, 0.5, 0.975])
    return {
        "gain_ci95": [float(q[0]), float(q[1]), float(q[2])],
        "probability_gain_positive": float(np.mean(means > 0)),
    }


def audit(symbol, shared):
    targets, y, prior, pred, active = _series(symbol, shared)
    # Positive means the new first-hour model has lower squared error.
    diff = (prior - y) ** 2 - (pred - y) ** 2
    block_gains = []
    for k in range(6):
        a, b = k * 21, (k + 1) * 21
        block_gains.append(float(np.mean(diff[a:b])))
    full_gain = float(np.mean(diff))
    first_gain = float(np.mean(diff[:63]))
    second_gain = float(np.mean(diff[63:]))
    boot = _bootstrap(diff, 20260928 + list(FROZEN).index(symbol))
    return {
        "frozen_config": {
            "window": FROZEN[symbol][0],
            "ridge": FROZEN[symbol][1],
            "cap_pp": FROZEN[symbol][2] * 100.0,
        },
        "holdout_start": targets[0],
        "holdout_end": targets[-1],
        "holdout_count": int(len(y)),
        "active_count": int(np.sum(active)),
        "previous_brier": float(np.mean((prior - y) ** 2)),
        "candidate_brier": float(np.mean((pred - y) ** 2)),
        "gain": full_gain,
        "first_half_gain": first_gain,
        "second_half_gain": second_gain,
        "block21_gains": block_gains,
        "positive_blocks": int(sum(g > 0 for g in block_gains)),
        "worst_block_gain": float(min(block_gains)),
        **boot,
        "robust_pass": bool(
            full_gain > 0
            and first_gain > 0
            and second_gain > 0
            and sum(g > 0 for g in block_gains) >= 5
            and boot["gain_ci95"][0] > 0
        ),
    }


def main():
    shared = {s: r.first_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
    out = {}
    for symbol in FROZEN:
        try:
            out[symbol] = audit(symbol, shared)
        except Exception as exc:
            out[symbol] = {"error": f"{type(exc).__name__}: {exc}", "robust_pass": False}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
