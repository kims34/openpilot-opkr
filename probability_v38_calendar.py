"""Research-only v3.8 calendar/seasonality residual model.

Only calendar information known in advance is used. No price after the forecast
close enters any feature. Production probabilities are never changed here.
"""
from datetime import date
import math
import numpy as np

import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS = [
    (window, ridge, cap)
    for window in (504, 756, 1008)
    for ridge in (30.0, 100.0, 300.0, 1000.0)
    for cap in (0.01, 0.02, 0.03)
]


def _previous_trace(prices, dates, target_date):
    out33 = v33.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    if out33.get('calibration_gate_passed'):
        return out33['audit_trace']
    return v32.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)['audit_trace']


def _calendar_matrix(dates):
    ds = [date.fromisoformat(d) for d in dates]
    n = len(ds)
    x = np.zeros((n, 11), float)
    month_positions = {}
    for i, d in enumerate(ds):
        month_positions.setdefault((d.year, d.month), []).append(i)
    first3 = set()
    last3 = set()
    first1 = set()
    last1 = set()
    for idxs in month_positions.values():
        first3.update(idxs[:3])
        last3.update(idxs[-3:])
        first1.add(idxs[0])
        last1.add(idxs[-1])

    for i, d in enumerate(ds):
        # Smooth weekday/month seasonality rather than dozens of sparse dummies.
        x[i, 0] = math.sin(2 * math.pi * d.weekday() / 5.0)
        x[i, 1] = math.cos(2 * math.pi * d.weekday() / 5.0)
        x[i, 2] = math.sin(2 * math.pi * (d.month - 1) / 12.0)
        x[i, 3] = math.cos(2 * math.pi * (d.month - 1) / 12.0)
        x[i, 4] = 1.0 if i in first3 else 0.0
        x[i, 5] = 1.0 if i in last3 else 0.0
        x[i, 6] = 1.0 if i in first1 else 0.0
        x[i, 7] = 1.0 if i in last1 else 0.0
        # Quarter-end / year-end context.
        x[i, 8] = 1.0 if d.month in (3, 6, 9, 12) and i in last3 else 0.0
        x[i, 9] = 1.0 if d.month == 12 and i in last3 else 0.0
        # Calendar gap until next trading session (weekend/holiday), known ex ante.
        if i + 1 < n:
            gap = (ds[i+1] - d).days
            x[i, 10] = min(gap, 5) / 5.0
    return x


def _ridge_predictions(x, outcomes, previous, config):
    window, ridge, cap = config
    preds = np.asarray(previous, float).copy()
    for j in range(len(outcomes)):
        if j < 252:
            continue
        start = max(0, j - window)
        idx = np.arange(start, j)
        if len(idx) < 252:
            continue
        train = x[idx]
        mean = train.mean(axis=0)
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
        z = (train - mean) / sd
        residual = outcomes[idx] - previous[idx]
        beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)
        adj = float(np.clip(((x[j] - mean) / sd) @ beta, -cap, cap))
        preds[j] = float(np.clip(previous[j] + adj, 0.35, 0.70))
    return preds


def _brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def evaluate(prices, dates, target_date):
    trace = _previous_trace(prices, dates, target_date)
    positions = np.asarray([int(row['t']) for row in trace])
    previous = np.asarray([float(row['probability']) for row in trace], float)
    outcomes = np.asarray([float(row['outcome']) for row in trace], float)
    x = _calendar_matrix(dates)[positions]
    if len(outcomes) < 1008:
        raise ValueError(f'audit too short: {len(outcomes)}')

    split = len(outcomes) - 252
    dev_y, test_y = outcomes[:split], outcomes[split:]
    prev_dev, prev_test = previous[:split], previous[split:]
    stable = []
    for cfg in CONFIGS:
        pred = _ridge_predictions(x, outcomes, previous, cfg)
        dev = pred[:split]
        mid = len(dev) // 2
        gains = (
            _brier(prev_dev, dev_y) - _brier(dev, dev_y),
            _brier(prev_dev[:mid], dev_y[:mid]) - _brier(dev[:mid], dev_y[:mid]),
            _brier(prev_dev[mid:], dev_y[mid:]) - _brier(dev[mid:], dev_y[mid:]),
        )
        if min(gains) > 0:
            stable.append((_brier(dev, dev_y), cfg, pred, gains))
    if not stable:
        return {'selected': None, 'reason': 'no stable development winner'}

    _, cfg, pred, dev_gains = min(stable, key=lambda row: row[0])
    test = pred[split:]
    mid = len(test) // 2
    test_gains = (
        _brier(prev_test, test_y) - _brier(test, test_y),
        _brier(prev_test[:mid], test_y[:mid]) - _brier(test[:mid], test_y[:mid]),
        _brier(prev_test[mid:], test_y[mid:]) - _brier(test[mid:], test_y[mid:]),
    )
    return {
        'selected': {'window': cfg[0], 'ridge': cfg[1], 'cap': cfg[2]},
        'dev_gain_all': dev_gains[0],
        'dev_gain_first': dev_gains[1],
        'dev_gain_second': dev_gains[2],
        'previous_test_brier': _brier(prev_test, test_y),
        'test_brier': _brier(test, test_y),
        'test_gain_all': test_gains[0],
        'test_gain_first': test_gains[1],
        'test_gain_second': test_gains[2],
        'holdout_passed': min(test_gains) > 0,
        'holdout_count': len(test_y),
    }
