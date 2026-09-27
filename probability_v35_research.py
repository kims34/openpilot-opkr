"""Research-only ridge residual next-close model with untouched holdout.

Configurations are selected using only the first 756 days of the 1008-session
audit. The final 252 sessions are never used for configuration selection and
are reported as an untouched holdout.
"""
import numpy as np

import probability_model as core
import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS = [
    (window, ridge, cap)
    for window in (504, 756, 1008)
    for ridge in (10.0, 30.0, 100.0, 300.0)
    for cap in (0.03, 0.05, 0.08)
]


def features(prices):
    p = np.asarray(prices, dtype=float)
    n = len(p)
    r = np.zeros(n)
    r[1:] = p[1:] / p[:-1] - 1.0
    x = np.full((n, 5), np.nan)
    for t in range(60, n):
        x[t, 0] = r[t]
        x[t, 1] = p[t] / p[t-5] - 1.0
        x[t, 2] = p[t] / p[t-20] - 1.0
        x[t, 3] = np.std(r[t-19:t+1], ddof=1)
        x[t, 4] = p[t] / np.max(p[t-59:t+1]) - 1.0
    return x


def previous_served(prices, dates, target_date):
    a = v33.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    if a.get('calibration_gate_passed'):
        return np.array([float(z['probability']) for z in a['audit_trace']])
    b = v32.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    return np.array([float(z['probability']) for z in b['audit_trace']])


def ridge_series(prices, dates, config):
    p = np.asarray(prices, dtype=float)
    n = len(p)
    y, candidates = core._candidate_probabilities(p, dates)
    base = np.asarray(candidates['fixed'], dtype=float)
    x = features(p)
    audit_start = max(core.MIN_TRAIN + core.POLICY_WINDOW, n - 1 - core.AUDIT_DAYS)
    window, ridge, cap = config
    preds = []
    for t in range(audit_start, n - 1):
        start = max(60, t - window)
        idx = np.arange(start, t)
        valid = np.all(np.isfinite(x[idx]), axis=1) & np.isfinite(base[idx])
        idx = idx[valid]
        if len(idx) < 252 or not np.all(np.isfinite(x[t])) or not np.isfinite(base[t]):
            preds.append(float(base[t]))
            continue
        train = x[idx]
        mean = train.mean(axis=0)
        sd = train.std(axis=0, ddof=1)
        sd = np.maximum(sd, np.array([0.003, 0.01, 0.02, 0.003, 0.02]))
        z = (train - mean) / sd
        target = y[idx] - base[idx]
        gram = z.T @ z + ridge * np.eye(z.shape[1])
        beta = np.linalg.solve(gram, z.T @ target)
        live_z = (x[t] - mean) / sd
        adjustment = float(np.clip(live_z @ beta, -cap, cap))
        preds.append(float(np.clip(base[t] + adjustment, 0.35, 0.70)))
    outcomes = np.asarray(y[audit_start:n-1], dtype=float)
    return np.asarray(preds), outcomes, audit_start


def brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def evaluate(prices, dates, target_date):
    prev = previous_served(prices, dates, target_date)
    first_preds, outcomes, audit_start = ridge_series(prices, dates, CONFIGS[0])
    if len(prev) != len(outcomes):
        raise ValueError('audit alignment mismatch')
    split = len(outcomes) - 252
    dev_y, test_y = outcomes[:split], outcomes[split:]
    prev_dev, prev_test = prev[:split], prev[split:]

    candidates = []
    for cfg in CONFIGS:
        preds, y, _ = ridge_series(prices, dates, cfg)
        dev = preds[:split]
        mid = len(dev) // 2
        gains = (
            brier(prev_dev, dev_y) - brier(dev, dev_y),
            brier(prev_dev[:mid], dev_y[:mid]) - brier(dev[:mid], dev_y[:mid]),
            brier(prev_dev[mid:], dev_y[mid:]) - brier(dev[mid:], dev_y[mid:]),
        )
        if min(gains) > 0:
            candidates.append((brier(dev, dev_y), cfg, preds, gains))

    if not candidates:
        return {'selected': None, 'reason': 'no stable development winner'}
    _, cfg, preds, dev_gains = min(candidates, key=lambda z: z[0])
    test = preds[split:]
    half = len(test) // 2
    test_gains = (
        brier(prev_test, test_y) - brier(test, test_y),
        brier(prev_test[:half], test_y[:half]) - brier(test[:half], test_y[:half]),
        brier(prev_test[half:], test_y[half:]) - brier(test[half:], test_y[half:]),
    )
    return {
        'selected': {'window': cfg[0], 'ridge': cfg[1], 'cap': cfg[2]},
        'dev_gain_all': dev_gains[0], 'dev_gain_first': dev_gains[1], 'dev_gain_second': dev_gains[2],
        'test_brier': brier(test, test_y), 'previous_test_brier': brier(prev_test, test_y),
        'test_gain_all': test_gains[0], 'test_gain_first': test_gains[1], 'test_gain_second': test_gains[2],
        'holdout_passed': min(test_gains) > 0,
        'audit_start_index': audit_start,
    }
