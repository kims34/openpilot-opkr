"""Research-only v3.12 pre-open futures/context challenger.

Forecast timing
---------------
This challenger is evaluated at 09:05 America/New_York on the *target* U.S.
trading day.  It may use only completed 60-minute bars whose timestamps are at
or before 08:00 ET (the 08:00-09:00 bar), plus information from the previous
completed cash session.  The target remains:

    close(target_session) > close(previous_completed_session)

The production next-session probability is NOT changed by this module.  A
configuration is eligible for promotion only if it beats the currently served
3.3/3.2 forecast on development chronology blocks and on an untouched final
126-session holdout overall and in both halves.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import math

import numpy as np

import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

MODEL_VERSION = "3.12-futures-preopen-research"
HOLDOUT = 126
MIN_TRAIN = 126

# Deliberately compact grid.  Hyperparameters are selected only on development
# data; the final HOLDOUT rows are never consulted during selection.
CONFIGS = [
    (window, ridge, cap)
    for window in (126, 252, 378)
    for ridge in (30.0, 100.0, 300.0, 1000.0)
    for cap in (0.02, 0.03, 0.05)
]

FUTURES = ("ES=F", "NQ=F", "CL=F", "DX-Y.NYB")


def _served_trace(prices, dates, target_date):
    """Return exactly the guarded probability that production would serve."""
    candidate = v33.estimate_prices(
        prices, include_trace=True, dates=dates, target_date=target_date
    )
    if candidate.get("calibration_gate_passed"):
        return candidate["audit_trace"]
    return v32.estimate_prices(
        prices, include_trace=True, dates=dates, target_date=target_date
    )["audit_trace"]


def _by_day(hourly_rows):
    """hourly_rows: iterable[(aware datetime, close)] -> date -> sorted rows."""
    out = defaultdict(list)
    for stamp, close in hourly_rows:
        if close is None or not math.isfinite(float(close)) or float(close) <= 0:
            continue
        out[stamp.date().isoformat()].append((stamp, float(close)))
    for rows in out.values():
        rows.sort(key=lambda item: item[0])
    return dict(out)


def _completed_price(day_rows, max_hour):
    """Price of the last completed 1h bar with bar-start <= max_hour ET."""
    eligible = [price for stamp, price in day_rows if stamp.hour <= max_hour]
    return eligible[-1] if eligible else None


def _overnight_return(hourly_by_day, as_of_day, target_day):
    """16:00 cash-close aligned anchor -> 09:00 target-day completed futures bar.

    Yahoo 1h timestamps are bar starts.  The 15:00 ET bar is complete by
    16:00; the 08:00 ET bar is complete by 09:00.  Runtime availability is
    therefore delayed until 09:05 ET.
    """
    prev_rows = hourly_by_day.get(as_of_day) or []
    target_rows = hourly_by_day.get(target_day) or []
    anchor = _completed_price(prev_rows, 15)
    snap = _completed_price(target_rows, 8)
    if anchor is None or snap is None:
        return None
    r = snap / anchor - 1.0
    if not math.isfinite(r) or abs(r) > 0.25:
        return None
    return float(r)


def _daily_value(series, day):
    value = series.get(day)
    if value is None:
        return None
    value = float(value)
    return value if math.isfinite(value) and value > 0 else None


def _feature_rows(prices, dates, trace, hourly, daily):
    """Build timing-safe feature matrix in trace order.

    Features:
      ES/NQ/WTI/Dollar overnight moves known by 09:05 ET,
      previous-close VIX level/change, 10Y level/change,
      target ETF previous 1d and 5d momentum.
    """
    p = np.asarray(prices, float)
    hourly_day = {symbol: _by_day(rows) for symbol, rows in hourly.items()}
    vix = daily["^VIX"]
    tnx = daily["^TNX"]

    rows = []
    meta = []
    date_to_index = {d: i for i, d in enumerate(dates)}
    for item in trace:
        t = int(item["t"])
        if t < 5 or t + 1 >= len(dates):
            rows.append([np.nan] * 10)
            meta.append(None)
            continue
        as_of = dates[t]
        target = dates[t + 1]
        fut = []
        ok = True
        for symbol in FUTURES:
            value = _overnight_return(hourly_day[symbol], as_of, target)
            if value is None:
                ok = False
                break
            fut.append(value)
        if not ok:
            rows.append([np.nan] * 10)
            meta.append(None)
            continue

        v0 = _daily_value(vix, as_of)
        y0 = _daily_value(tnx, as_of)
        prev_i = t - 1
        prev_day = dates[prev_i]
        v1 = _daily_value(vix, prev_day)
        y1 = _daily_value(tnx, prev_day)
        if None in (v0, v1, y0, y1):
            rows.append([np.nan] * 10)
            meta.append(None)
            continue

        ret1 = p[t] / p[t - 1] - 1.0
        mom5 = p[t] / p[t - 5] - 1.0
        feature = fut + [
            math.log(v0),
            v0 / v1 - 1.0,
            y0,
            y0 - y1,
            ret1,
            mom5,
        ]
        rows.append(feature)
        meta.append({"as_of": as_of, "target": target})
    return np.asarray(rows, float), meta


def _predict(x, outcomes, previous, config):
    window, ridge, cap = config
    outcomes = np.asarray(outcomes, float)
    previous = np.asarray(previous, float)
    pred = previous.copy()
    adjusted = np.zeros(len(outcomes), dtype=bool)

    for j in range(len(outcomes)):
        if not np.all(np.isfinite(x[j])):
            continue
        lo = max(0, j - window)
        idx = np.arange(lo, j)
        idx = idx[np.all(np.isfinite(x[idx]), axis=1)]
        if len(idx) < MIN_TRAIN:
            continue
        train = x[idx]
        mu = train.mean(axis=0)
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
        z = (train - mu) / sd
        residual = outcomes[idx] - previous[idx]
        beta = np.linalg.solve(
            z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual
        )
        adjustment = float(np.clip(((x[j] - mu) / sd) @ beta, -cap, cap))
        pred[j] = float(np.clip(previous[j] + adjustment, 0.35, 0.70))
        adjusted[j] = True
    return pred, adjusted


def _brier(p, y):
    p = np.asarray(p, float)
    y = np.asarray(y, float)
    return float(np.mean((p - y) ** 2))


def _gain(previous, candidate, outcomes, idx):
    idx = np.asarray(idx, int)
    return _brier(previous[idx], outcomes[idx]) - _brier(candidate[idx], outcomes[idx])


def _three_blocks(indices):
    parts = np.array_split(np.asarray(indices, int), 3)
    return [p for p in parts if len(p)]


def evaluate(prices, dates, target_date, hourly, daily):
    trace = _served_trace(prices, dates, target_date)
    previous = np.asarray([float(r["probability"]) for r in trace], float)
    outcomes = np.asarray([float(r["outcome"]) for r in trace], float)
    x, meta = _feature_rows(prices, dates, trace, hourly, daily)

    complete = np.where(np.all(np.isfinite(x), axis=1))[0]
    if len(complete) < HOLDOUT + MIN_TRAIN + 60:
        return {
            "selected": None,
            "reason": "aligned pre-open history too short",
            "complete_rows": int(len(complete)),
        }

    # Holdout is the latest 126 *feature-complete* forecasts.  It is never used
    # to select a configuration.
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
        gains += [_gain(previous, pred, outcomes, block) for block in _three_blocks(usable_dev)]
        # Pre-register a meaningful floor, not merely > 0, to reduce selection
        # noise across the small 2-year intraday sample.
        if min(gains) > 0.00025:
            stable.append((_brier(pred[usable_dev], outcomes[usable_dev]), config, pred, adjusted, gains))

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
    if len(usable_test) < 90:
        return {
            "selected": {"window": config[0], "ridge": config[1], "cap": config[2]},
            "reason": "insufficient adjusted holdout rows",
            "holdout_rows": int(len(usable_test)),
        }

    halves = np.array_split(usable_test, 2)
    test_gains = [_gain(previous, pred, outcomes, usable_test)] + [
        _gain(previous, pred, outcomes, h) for h in halves
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
    }
