"""Research-only v3.9 after-open nowcast.

This is deliberately a separate forecast timing from the pre-open/next-session
probability. For target session t+1 it uses only the official opening price of
t+1 plus information known through close t, then predicts whether close t+1
will finish above close t. It must never be used before the target session opens.
"""
import numpy as np

import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS = [
    (window, ridge, cap)
    for window in (252, 504, 756)
    for ridge in (10.0, 30.0, 100.0, 300.0, 1000.0)
    for cap in (0.05, 0.10, 0.15)
]


def _previous_trace(closes, dates, target_date):
    out33 = v33.estimate_prices(closes, include_trace=True, dates=dates, target_date=target_date)
    if out33.get('calibration_gate_passed'):
        return out33['audit_trace']
    return v32.estimate_prices(closes, include_trace=True, dates=dates, target_date=target_date)['audit_trace']


def _features(opens, closes, positions):
    opens = np.asarray(opens, float)
    closes = np.asarray(closes, float)
    x = np.full((len(positions), 6), np.nan)
    for j, t in enumerate(positions):
        t = int(t)
        if t < 5 or t + 1 >= len(closes):
            continue
        gap = opens[t+1] / closes[t] - 1.0
        prev1 = closes[t] / closes[t-1] - 1.0
        mom5 = closes[t] / closes[t-5] - 1.0
        x[j, 0] = gap
        x[j, 1] = abs(gap)
        x[j, 2] = 1.0 if gap > 0 else 0.0
        x[j, 3] = prev1
        x[j, 4] = mom5
        # Interaction: a positive gap after a negative prior day can behave
        # differently from continuation. Still fully known at the open.
        x[j, 5] = gap * prev1
    return x


def _ridge_predictions(x, outcomes, previous, config):
    window, ridge, cap = config
    preds = np.asarray(previous, float).copy()
    for j in range(len(outcomes)):
        if j < 126 or not np.all(np.isfinite(x[j])):
            continue
        start = max(0, j - window)
        idx = np.arange(start, j)
        valid = np.all(np.isfinite(x[idx]), axis=1)
        idx = idx[valid]
        if len(idx) < 126:
            continue
        train = x[idx]
        mean = train.mean(axis=0)
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
        z = (train - mean) / sd
        residual = outcomes[idx] - previous[idx]
        beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)
        adj = float(np.clip(((x[j] - mean) / sd) @ beta, -cap, cap))
        preds[j] = float(np.clip(previous[j] + adj, 0.05, 0.95))
    return preds


def _brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def evaluate(opens, closes, dates, target_date):
    trace = _previous_trace(closes, dates, target_date)
    positions = np.asarray([int(row['t']) for row in trace])
    previous = np.asarray([float(row['probability']) for row in trace], float)
    outcomes = np.asarray([float(row['outcome']) for row in trace], float)
    x = _features(opens, closes, positions)
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
