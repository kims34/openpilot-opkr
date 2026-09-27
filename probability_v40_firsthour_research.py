"""Research-only v4.0 first-hour nowcast challenger.

Target: target-session regular close > previous completed regular close.
Timing: may be evaluated only after the first regular-session 60-minute bar is complete.
The challenger is compared against the already validated v3.9 open nowcast.  It
uses only information available by ~10:30 ET and is never wired to production
unless an untouched final holdout improves Brier loss in both chronological halves.
"""
from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

import next_day_probability as data
import probability_v39_open_nowcast as v39

NY = ZoneInfo("America/New_York")
SYMBOLS = ("SPY", "QQQ", "SCHD")
V39_CONFIG = {
    "SPY": (504, 100.0, 0.15),
    "QQQ": (756, 100.0, 0.15),
    "SCHD": (252, 100.0, 0.15),
}
HOLDOUT = 126
MIN_TRAIN = 126
CONFIGS = [
    (window, ridge, cap)
    for window in (126, 252, 378)
    for ridge in (10.0, 30.0, 100.0, 300.0)
    for cap in (0.03, 0.05, 0.08)
]
UA = {"User-Agent": "Mozilla/5.0 IndexAlert/4.0-research"}


def _chart(symbol: str, range_: str, interval: str):
    encoded = requests.utils.quote(symbol, safe="")
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}",
        params={
            "range": range_,
            "interval": interval,
            "includePrePost": "false",
            "events": "div,splits",
        },
        headers=UA,
        timeout=25,
    )
    r.raise_for_status()
    chart = r.json().get("chart", {})
    if chart.get("error"):
        raise RuntimeError(f"vendor error: {symbol}")
    z = (chart.get("result") or [None])[0]
    if not z:
        raise RuntimeError(f"no data: {symbol}")
    return z


def daily_ohlcv(symbol: str):
    z = _chart(symbol, "10y", "1d")
    q = (z.get("indicators", {}).get("quote") or [{}])[0]
    out = {}
    for i, stamp in enumerate(z.get("timestamp") or []):
        day = datetime.fromtimestamp(int(stamp), timezone.utc).astimezone(NY).date().isoformat()
        try:
            vals = tuple(float((q.get(k) or [])[i]) for k in ("open", "high", "low", "close", "volume"))
        except Exception:
            continue
        if all(np.isfinite(vals)) and min(vals[:4]) > 0:
            out[day] = vals
    return out


def first_hour(symbol: str):
    """Return first regular 60m bar per NY session from the vendor's 2y archive."""
    z = _chart(symbol, "2y", "60m")
    q = (z.get("indicators", {}).get("quote") or [{}])[0]
    out = {}
    for i, stamp in enumerate(z.get("timestamp") or []):
        local = datetime.fromtimestamp(int(stamp), timezone.utc).astimezone(NY)
        # Yahoo regular 60m bars are normally timestamped 09:30.  Accept the
        # earliest bar in [09:30,10:30) to tolerate vendor timestamp quirks.
        minute = local.hour * 60 + local.minute
        if not (9 * 60 + 30 <= minute < 10 * 60 + 30):
            continue
        day = local.date().isoformat()
        if day in out:
            continue
        try:
            vals = tuple(float((q.get(k) or [])[i]) for k in ("open", "high", "low", "close", "volume"))
        except Exception:
            continue
        if all(np.isfinite(vals)) and min(vals[:4]) > 0 and vals[4] >= 0:
            out[day] = vals
    return out


def _v39_series(symbol, rows, meta, daily):
    dates = [d for d, _ in rows]
    closes = np.asarray([p for _, p in rows], float)
    if any(d not in daily for d in dates):
        raise RuntimeError(f"daily OHLC alignment failed: {symbol}")
    opens = np.asarray([daily[d][0] for d in dates], float)
    trace = v39._previous_trace(closes, dates, meta["target_date"])
    pos = np.asarray([int(x["t"]) for x in trace], int)
    previous = np.asarray([float(x["probability"]) for x in trace], float)
    outcomes = np.asarray([float(x["outcome"]) for x in trace], float)
    x = v39._features(opens, closes, pos)
    p39 = v39._ridge_predictions(x, outcomes, previous, V39_CONFIG[symbol])
    return dates, closes, pos, outcomes, p39


def _hour_features(symbol, dates, closes, pos, own, spy, qqq, vix):
    rows = []
    volumes = []
    for j, t in enumerate(pos):
        if t + 1 >= len(dates):
            continue
        target = dates[t + 1]
        if target not in own or target not in spy or target not in qqq or target not in vix:
            continue
        o, h, l, c, vol = own[target]
        so, sh, sl, sc, sv = spy[target]
        qo, qh, ql, qc, qv = qqq[target]
        vo, vh, vl, vc, vv = vix[target]
        prev = float(closes[t])
        if prev <= 0 or min(o, h, l, c, so, sc, qo, qc, vo, vc) <= 0:
            continue
        prior_vol = [x for _, x in volumes[-20:] if x > 0]
        med_vol = float(np.median(prior_vol)) if len(prior_vol) >= 10 else float("nan")
        volume_ratio = math.log(max(vol / med_vol, 1e-6)) if math.isfinite(med_vol) and med_vol > 0 else float("nan")
        close_loc = (c - l) / max(h - l, 1e-12)
        feat = np.asarray([
            o / prev - 1.0,                  # opening gap
            c / o - 1.0,                     # first-hour return
            c / prev - 1.0,                  # move from prior close
            (h - l) / prev,                  # first-hour range
            close_loc,                       # first-hour close location
            volume_ratio,                    # first-hour volume vs prior 20 sessions
            sc / so - 1.0,                   # SPY first-hour breadth proxy
            qc / qo - 1.0,                   # QQQ first-hour breadth proxy
            math.log(vc),                    # VIX level
            vc / vo - 1.0,                   # VIX first-hour change
        ], float)
        volumes.append((target, vol))
        if not np.all(np.isfinite(feat)):
            continue
        rows.append((j, int(t), target, feat))
    return rows


def _causal_predictions(prior, outcomes, features, config):
    window, ridge, cap = config
    n = len(prior)
    pred = np.asarray(prior, float).copy()
    active = np.zeros(n, dtype=bool)
    for j in range(n):
        if j < MIN_TRAIN:
            continue
        lo = max(0, j - window)
        idx = np.arange(lo, j)
        valid = np.all(np.isfinite(features[idx]), axis=1)
        idx = idx[valid]
        if len(idx) < MIN_TRAIN or not np.all(np.isfinite(features[j])):
            continue
        train = features[idx]
        mean = train.mean(axis=0)
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
        z = (train - mean) / sd
        residual = outcomes[idx] - prior[idx]
        beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)
        adj = float(np.clip(((features[j] - mean) / sd) @ beta, -cap, cap))
        pred[j] = float(np.clip(prior[j] + adj, 0.05, 0.95))
        active[j] = True
    return pred, active


def _brier(p, y):
    return float(np.mean((np.asarray(p, float) - np.asarray(y, float)) ** 2))


def _parts(p, y):
    p = np.asarray(p, float); y = np.asarray(y, float)
    mid = len(y) // 2
    return {
        "all": _brier(p, y),
        "first": _brier(p[:mid], y[:mid]),
        "second": _brier(p[mid:], y[mid:]),
    }


def evaluate_symbol(symbol, shared):
    rows, meta = data.fetch_history(symbol, time.time())
    daily = daily_ohlcv(symbol)
    dates, closes, pos, outcomes, p39 = _v39_series(symbol, rows, meta, daily)
    own = shared[symbol]
    hour_rows = _hour_features(symbol, dates, closes, pos, own, shared["SPY"], shared["QQQ"], shared["^VIX"])
    if len(hour_rows) < HOLDOUT + 2 * MIN_TRAIN:
        return {"error": f"first-hour sample too small: {len(hour_rows)}"}

    # Compress to only dates for which the complete first-hour feature vector exists.
    source_idx = np.asarray([x[0] for x in hour_rows], int)
    x = np.vstack([x[3] for x in hour_rows])
    y = outcomes[source_idx]
    prior = p39[source_idx]
    targets = [x[2] for x in hour_rows]
    split = len(y) - HOLDOUT
    dev_y, test_y = y[:split], y[split:]
    prev_dev, prev_test = prior[:split], prior[split:]

    stable = []
    for cfg in CONFIGS:
        candidate, active = _causal_predictions(prior, y, x, cfg)
        dev = candidate[:split]
        gain = {
            k: _parts(prev_dev, dev_y)[k] - _parts(dev, dev_y)[k]
            for k in ("all", "first", "second")
        }
        if min(gain.values()) > 0:
            stable.append((_brier(dev, dev_y), cfg, candidate, active, gain))
    if not stable:
        return {
            "sample_count": int(len(y)),
            "holdout_count": HOLDOUT,
            "selected": None,
            "reason": "no stable development winner versus v3.9",
        }

    _, cfg, candidate, active, dev_gain = min(stable, key=lambda row: row[0])
    test = candidate[split:]
    test_prev_parts = _parts(prev_test, test_y)
    test_parts = _parts(test, test_y)
    test_gain = {k: test_prev_parts[k] - test_parts[k] for k in test_parts}
    return {
        "sample_count": int(len(y)),
        "development_count": int(split),
        "holdout_count": HOLDOUT,
        "holdout_start": targets[split],
        "holdout_end": targets[-1],
        "selected": {"window": cfg[0], "ridge": cfg[1], "cap_pp": cfg[2] * 100.0},
        "development_gain": dev_gain,
        "previous_holdout_brier": test_prev_parts["all"],
        "candidate_holdout_brier": test_parts["all"],
        "holdout_gain": test_gain,
        "holdout_passed": bool(min(test_gain.values()) > 0),
        "active_holdout_days": int(np.sum(active[split:])),
    }


def main():
    shared = {s: first_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
    out = {}
    for symbol in SYMBOLS:
        try:
            out[symbol] = evaluate_symbol(symbol, shared)
        except Exception as exc:
            out[symbol] = {"error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
