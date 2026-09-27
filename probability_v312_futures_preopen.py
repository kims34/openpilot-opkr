"""Research-only v3.12 pre-open futures/context challenger.

Forecast timing
---------------
This challenger is evaluated at 09:05 America/New_York on the *target* U.S.
trading day. It may use only completed 60-minute bars whose timestamps are at
or before 08:00 ET, plus information from the previous completed cash session.
The target remains:

    close(target_session) > close(previous_completed_session)

Reference model
---------------
v3.12 is calibrated against the frozen causal *fixed/base rise rate* from the
validated v3.2 safety model. This is the same 55%-style baseline the app shows
when extra conditions have not demonstrated a robust advantage. Using the
fixed/base trace makes every historical reference forecast causal,
reproducible, and exactly reproducible in live runtime without a hindsight
selection gate.

The daily baseline itself is never overwritten by this research module. A
configuration is eligible for promotion only if it beats that frozen base on
development chronology blocks and on an untouched final 126-session holdout
overall and in both halves.
"""
from __future__ import annotations

from collections import defaultdict
import math

import numpy as np

import probability_model_v31_runtime as v32

MODEL_VERSION = "3.12-futures-preopen-research"
REFERENCE_MODEL = "3.2-live-guardrails:fixed-base-rate"
HOLDOUT = 126
MIN_TRAIN = 126
CONFIGS = [
    (window, ridge, cap)
    for window in (126, 252, 378)
    for ridge in (30.0, 100.0, 300.0, 1000.0)
    for cap in (0.02, 0.03, 0.05)
]
FUTURES = ("ES=F", "NQ=F", "CL=F", "DX-Y.NYB")


def _served_trace(prices, dates, target_date):
    """Return the frozen v3.2 fixed/base-rate trace.

    v3.2's historical audit contains both the selected historical challenger
    probability and its causal fixed base. v3.12 intentionally learns residuals
    from the base column so research and live runtime use the exact same
    reference definition.
    """
    raw = v32.estimate_prices(
        prices, include_trace=True, dates=dates, target_date=target_date
    )["audit_trace"]
    return [
        dict(
            t=int(row["t"]),
            probability=float(row["base"]),
            base=float(row["base"]),
            outcome=float(row["outcome"]),
            alpha=0.0,
            strategy="fixed",
        )
        for row in raw
    ]


def _by_day(hourly_rows):
    out = defaultdict(list)
    for stamp, close in hourly_rows:
        if close is None or not math.isfinite(float(close)) or float(close) <= 0:
            continue
        out[stamp.date().isoformat()].append((stamp, float(close)))
    for rows in out.values():
        rows.sort(key=lambda item: item[0])
    return dict(out)


def _completed_price(day_rows, max_hour):
    eligible = [price for stamp, price in day_rows if stamp.hour <= max_hour]
    return eligible[-1] if eligible else None


def _overnight_return(hourly_by_day, as_of_day, target_day):
    prev_rows = hourly_by_day.get(as_of_day) or []
    target_rows = hourly_by_day.get(target_day) or []
    anchor = _completed_price(prev_rows, 15)
    snap = _completed_price(target_rows, 8)
    if anchor is None or snap is None:
        return None
    value = snap / anchor - 1.0
    if not math.isfinite(value) or abs(value) > 0.25:
        return None
    return float(value)


def _daily_value(series, day):
    value = series.get(day)
    if value is None:
        return None
    value = float(value)
    return value if math.isfinite(value) and value > 0 else None


def _feature_rows(prices, dates, trace, hourly, daily):
    prices = np.asarray(prices, float)
    hourly_day = {symbol: _by_day(rows) for symbol, rows in hourly.items()}
    vix = daily["^VIX"]
    tnx = daily["^TNX"]
    rows, meta = [], []
    for item in trace:
        t = int(item["t"])
        if t < 5 or t + 1 >= len(dates):
            rows.append([np.nan] * 10)
            meta.append(None)
            continue
        as_of, target = dates[t], dates[t + 1]
        futures = []
        for symbol in FUTURES:
            value = _overnight_return(hourly_day[symbol], as_of, target)
            if value is None:
                futures = []
                break
            futures.append(value)
        if not futures:
            rows.append([np.nan] * 10)
            meta.append(None)
            continue
        previous_day = dates[t - 1]
        v0, v1 = _daily_value(vix, as_of), _daily_value(vix, previous_day)
        y0, y1 = _daily_value(tnx, as_of), _daily_value(tnx, previous_day)
        if None in (v0, v1, y0, y1):
            rows.append([np.nan] * 10)
            meta.append(None)
            continue
        rows.append(
            futures
            + [
                math.log(v0),
                v0 / v1 - 1.0,
                y0,
                y0 - y1,
                prices[t] / prices[t - 1] - 1.0,
                prices[t] / prices[t - 5] - 1.0,
            ]
        )
        meta.append({"as_of": as_of, "target": target})
    return np.asarray(rows, float), meta


def _predict(x, outcomes, previous, config):
    """Causal rolling ridge residual forecast on feature-complete rows."""
    window, ridge, cap = config
    outcomes = np.asarray(outcomes, float)
    previous = np.asarray(previous, float)
    pred = previous.copy()
    adjusted = np.zeros(len(outcomes), dtype=bool)
    for j in range(len(outcomes)):
        if not np.all(np.isfinite(x[j])):
            continue
        idx = np.arange(0, j)
        idx = idx[np.all(np.isfinite(x[idx]), axis=1)]
        if len(idx) < MIN_TRAIN:
            continue
        idx = idx[-window:]
        if len(idx) < MIN_TRAIN:
            continue
        train = x[idx]
        mean = train.mean(axis=0)
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
        z = (train - mean) / sd
        residual = outcomes[idx] - previous[idx]
        beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)
        adjustment = float(np.clip(((x[j] - mean) / sd) @ beta, -cap, cap))
        pred[j] = float(np.clip(previous[j] + adjustment, 0.35, 0.70))
        adjusted[j] = True
    return pred, adjusted


def _brier(probabilities, outcomes):
    probabilities = np.asarray(probabilities, float)
    outcomes = np.asarray(outcomes, float)
    return float(np.mean((probabilities - outcomes) ** 2))


def _gain(previous, candidate, outcomes, idx):
    idx = np.asarray(idx, int)
    return _brier(previous[idx], outcomes[idx]) - _brier(candidate[idx], outcomes[idx])


def _three_blocks(indices):
    return [block for block in np.array_split(np.asarray(indices, int), 3) if len(block)]


def evaluate(prices, dates, target_date, hourly, daily):
    trace = _served_trace(prices, dates, target_date)
    previous = np.asarray([float(row["probability"]) for row in trace], float)
    outcomes = np.asarray([float(row["outcome"]) for row in trace], float)
    x, meta = _feature_rows(prices, dates, trace, hourly, daily)
    complete = np.where(np.all(np.isfinite(x), axis=1))[0]
    if len(complete) < HOLDOUT + MIN_TRAIN + 60:
        return {
            "selected": None,
            "reason": "aligned pre-open history too short",
            "complete_rows": int(len(complete)),
        }
    test_idx = complete[-HOLDOUT:]
    split_position = int(test_idx[0])
    dev_idx = complete[complete < split_position]
    if len(dev_idx) < MIN_TRAIN + 60:
        return {
            "selected": None,
            "reason": "development history too short",
            "complete_rows": int(len(complete)),
        }
    stable = []
    for config in CONFIGS:
        pred, adjusted = _predict(x, outcomes, previous, config)
        usable_dev = dev_idx[adjusted[dev_idx]]
        if len(usable_dev) < 90:
            continue
        gains = [_gain(previous, pred, outcomes, usable_dev)]
        gains += [
            _gain(previous, pred, outcomes, block)
            for block in _three_blocks(usable_dev)
        ]
        if min(gains) > 0.00025:
            stable.append(
                (_brier(pred[usable_dev], outcomes[usable_dev]), config, pred, adjusted, gains)
            )
    if not stable:
        return {
            "selected": None,
            "reason": "no stable development winner",
            "complete_rows": int(len(complete)),
            "development_rows": int(len(dev_idx)),
            "holdout_rows": int(len(test_idx)),
        }
    _, config, pred, adjusted, dev_gains = min(stable, key=lambda row: row[0])
    usable_test = test_idx[adjusted[test_idx]]
    if len(usable_test) != len(test_idx):
        return {
            "selected": {"window": config[0], "ridge": config[1], "cap": config[2]},
            "reason": "selected model lacks full holdout coverage",
            "holdout_rows": int(len(usable_test)),
        }
    halves = np.array_split(usable_test, 2)
    test_gains = [_gain(previous, pred, outcomes, usable_test)] + [
        _gain(previous, pred, outcomes, half) for half in halves
    ]
    passed = min(test_gains) > 0.0
    latest = int(complete[-1])
    return {
        "selected": {"window": config[0], "ridge": config[1], "cap": config[2]},
        "complete_rows": int(len(complete)),
        "development_rows": int(len(dev_idx)),
        "holdout_rows": int(len(usable_test)),
        "development_gain_all": float(dev_gains[0]),
        "development_gain_block1": float(dev_gains[1]),
        "development_gain_block2": float(dev_gains[2]),
        "development_gain_block3": float(dev_gains[3]),
        "previous_holdout_brier": _brier(previous[usable_test], outcomes[usable_test]),
        "candidate_holdout_brier": _brier(pred[usable_test], outcomes[usable_test]),
        "holdout_gain_all": float(test_gains[0]),
        "holdout_gain_first": float(test_gains[1]),
        "holdout_gain_second": float(test_gains[2]),
        "holdout_passed": bool(passed),
        "latest_feature_date": meta[latest]["target"] if meta[latest] else None,
        "reference_model": REFERENCE_MODEL,
    }
