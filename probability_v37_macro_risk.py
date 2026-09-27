"""Research-only v3.7 macro/risk-appetite residual probability model.

The production forecast is never changed by this module. Every feature is based
only on closes known at the forecast-day close. Configuration is selected on
the development slice; the final 252 sessions remain untouched until one final
holdout evaluation.
"""
import numpy as np

import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS = [
    (window, ridge, cap)
    for window in (504, 756)
    for ridge in (100.0, 300.0, 1000.0, 3000.0)
    for cap in (0.01, 0.02, 0.03)
]


def _previous_trace(prices, dates, target_date):
    out33 = v33.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    if out33.get('calibration_gate_passed'):
        trace = out33['audit_trace']
    else:
        trace = v32.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)['audit_trace']
    return trace


def _ret(p):
    p = np.asarray(p, float)
    r = np.zeros(len(p))
    r[1:] = p[1:] / p[:-1] - 1.0
    return r


def _mom(p, t, n):
    return p[t] / p[t-n] - 1.0


def _feature_matrix(target, aligned):
    target = np.asarray(target, float)
    spy = np.asarray(aligned['SPY'][1], float)
    qqq = np.asarray(aligned['QQQ'][1], float)
    schd = np.asarray(aligned['SCHD'][1], float)
    vix = np.asarray(aligned['^VIX'][1], float)
    tlt = np.asarray(aligned['TLT'][1], float)
    hyg = np.asarray(aligned['HYG'][1], float)
    iwm = np.asarray(aligned['IWM'][1], float)
    uup = np.asarray(aligned['UUP'][1], float)
    gld = np.asarray(aligned['GLD'][1], float)

    n = len(target)
    rt = _ret(target)
    rvix = _ret(vix)
    rhyg = _ret(hyg)
    riwm = _ret(iwm)
    rtlt = _ret(tlt)
    ruup = _ret(uup)
    rgld = _ret(gld)
    rsp = _ret(spy)
    rqq = _ret(qqq)
    rsc = _ret(schd)

    # 16 features. They deliberately avoid same-day information after the
    # completed close, macro release timestamps, or revised economic series.
    x = np.full((n, 16), np.nan)
    for t in range(60, n):
        x[t, 0] = np.log(max(vix[t], 1e-6))
        x[t, 1] = rvix[t]
        x[t, 2] = rt[t]
        x[t, 3] = _mom(target, t, 5)
        x[t, 4] = _mom(target, t, 20)
        x[t, 5] = np.std(rt[t-19:t+1], ddof=1)
        x[t, 6] = sum(r[t] > 0 for r in (rsp, rqq, rsc)) / 3.0
        # Credit appetite: high-yield strength versus duration / Treasuries.
        x[t, 7] = rhyg[t]
        x[t, 8] = _mom(hyg, t, 5) - _mom(tlt, t, 5)
        # Small-cap risk appetite versus broad market.
        x[t, 9] = riwm[t]
        x[t, 10] = _mom(iwm, t, 5) - _mom(spy, t, 5)
        # Rates/duration proxy.
        x[t, 11] = rtlt[t]
        x[t, 12] = _mom(tlt, t, 5)
        # Dollar and defensive-gold context.
        x[t, 13] = ruup[t]
        x[t, 14] = _mom(uup, t, 5)
        x[t, 15] = _mom(gld, t, 5)
    return x


def _ridge_predictions(x, outcomes, previous_probs, config):
    window, ridge, cap = config
    m = len(outcomes)
    preds = np.asarray(previous_probs, float).copy()
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
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
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
    dates, target = aligned[target_symbol]
    trace = _previous_trace(target, dates, target_date)
    positions = np.asarray([int(row['t']) for row in trace])
    previous = np.asarray([float(row['probability']) for row in trace], float)
    outcomes = np.asarray([float(row['outcome']) for row in trace], float)
    x = _feature_matrix(target, aligned)[positions]

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
