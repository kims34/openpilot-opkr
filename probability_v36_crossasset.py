"""Research-only cross-asset/VIX residual probability model.

All features use information available at the completed close on forecast day.
The model predicts only a small residual around the already-served 3.3 safety
forecast. Configuration is selected on the development portion of the 1008-day
audit; the final 252 sessions remain untouched until the final score.
"""
import numpy as np

import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS = [
    (window, ridge, cap)
    for window in (378, 504, 756)
    for ridge in (30.0, 100.0, 300.0, 1000.0)
    for cap in (0.02, 0.03, 0.05)
]


def _previous_trace(prices, dates, target_date):
    out33 = v33.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    if out33.get('calibration_gate_passed'):
        trace = out33['audit_trace']
    else:
        trace = v32.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)['audit_trace']
    return out33, trace


def _feature_matrix(target, spy, qqq, schd, vix):
    target = np.asarray(target, float)
    spy = np.asarray(spy, float)
    qqq = np.asarray(qqq, float)
    schd = np.asarray(schd, float)
    vix = np.asarray(vix, float)
    n = len(target)
    allp = [spy, qqq, schd]
    rets = []
    for p in allp:
        r = np.zeros(n)
        r[1:] = p[1:] / p[:-1] - 1.0
        rets.append(r)
    rt = np.zeros(n)
    rt[1:] = target[1:] / target[:-1] - 1.0
    rv = np.zeros(n)
    rv[1:] = vix[1:] / vix[:-1] - 1.0

    x = np.full((n, 8), np.nan)
    for t in range(60, n):
        # VIX level is log-scaled and later standardized within each fit window.
        x[t, 0] = np.log(max(vix[t], 1e-6))
        x[t, 1] = rv[t]
        x[t, 2] = sum(r[t] > 0 for r in rets) / 3.0
        x[t, 3] = rt[t]
        x[t, 4] = target[t] / target[t-5] - 1.0
        x[t, 5] = target[t] / target[t-20] - 1.0
        x[t, 6] = np.std(rt[t-19:t+1], ddof=1)
        # Relative 20-day momentum versus broad SPY context.
        x[t, 7] = (target[t] / target[t-20]) - (spy[t] / spy[t-20])
    return x


def _ridge_predictions(x, outcomes, previous_probs, config):
    window, ridge, cap = config
    m = len(outcomes)
    preds = np.array(previous_probs, float).copy()
    for j in range(m):
        if j < 252 or not np.all(np.isfinite(x[j])):
            continue
        start = max(0, j - window)
        idx = np.arange(start, j)
        valid = np.all(np.isfinite(x[idx]), axis=1) & np.isfinite(previous_probs[idx])
        idx = idx[valid]
        if len(idx) < 252:
            continue
        train = x[idx]
        mean = train.mean(axis=0)
        sd = train.std(axis=0, ddof=1)
        sd = np.maximum(sd, 1e-6)
        z = (train - mean) / sd
        residual = outcomes[idx] - previous_probs[idx]
        beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)
        live = (x[j] - mean) / sd
        adj = float(np.clip(live @ beta, -cap, cap))
        preds[j] = float(np.clip(previous_probs[j] + adj, 0.35, 0.70))
    return preds


def _brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def evaluate(aligned, target_symbol, target_date):
    """aligned maps symbol -> (dates, prices), all sharing the exact dates."""
    dates, target = aligned[target_symbol]
    _, trace = _previous_trace(target, dates, target_date)
    positions = [int(row['t']) for row in trace]
    prev = np.asarray([float(row['probability']) for row in trace], float)
    outcomes = np.asarray([float(row['outcome']) for row in trace], float)

    spy = aligned['SPY'][1]
    qqq = aligned['QQQ'][1]
    schd = aligned['SCHD'][1]
    vix = aligned['^VIX'][1]
    full_x = _feature_matrix(target, spy, qqq, schd, vix)
    x = full_x[np.asarray(positions)]

    if len(outcomes) < 1008:
        raise ValueError('audit too short')
    split = len(outcomes) - 252
    dev_y, test_y = outcomes[:split], outcomes[split:]
    prev_dev, prev_test = prev[:split], prev[split:]

    stable = []
    for cfg in CONFIGS:
        pred = _ridge_predictions(x, outcomes, prev, cfg)
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
    _, cfg, pred, dev_gains = min(stable, key=lambda z: z[0])
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
        'test_brier': _brier(test, test_y),
        'previous_test_brier': _brier(prev_test, test_y),
        'test_gain_all': test_gains[0],
        'test_gain_first': test_gains[1],
        'test_gain_second': test_gains[2],
        'holdout_passed': min(test_gains) > 0,
        'holdout_count': len(test_y),
    }
