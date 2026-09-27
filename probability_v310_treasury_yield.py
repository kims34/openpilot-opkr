"""Research-only v3.10 Treasury-yield residual probability model.

Uses only Treasury-yield information known by the prior completed U.S. session
close. It challenges the guarded pre-open forecast and is promoted only if it
wins stable chronological development slices and the untouched final 252
sessions. Production is not changed by this module.
"""
import numpy as np

import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS = [
    (window, ridge, cap)
    for window in (504, 756, 1008)
    for ridge in (30.0, 100.0, 300.0, 1000.0, 3000.0)
    for cap in (0.01, 0.02, 0.03)
]


def _previous_trace(prices, dates, target_date):
    out33 = v33.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    if out33.get('calibration_gate_passed'):
        return out33['audit_trace']
    return v32.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)['audit_trace']


def _ret(p):
    p = np.asarray(p, float)
    r = np.zeros(len(p))
    r[1:] = p[1:] / p[:-1] - 1.0
    return r


def _diff(p):
    p = np.asarray(p, float)
    d = np.zeros(len(p))
    d[1:] = p[1:] - p[:-1]
    return d


def _feature_matrix(target, aligned):
    target = np.asarray(target, float)
    tnx = np.asarray(aligned['^TNX'][1], float)  # 10Y yield, percentage points*10 convention in Yahoo
    fvx = np.asarray(aligned['^FVX'][1], float)  # 5Y yield
    irx = np.asarray(aligned['^IRX'][1], float)  # 13-week bill yield

    rt = _ret(target)
    d10 = _diff(tnx)
    d5 = _diff(fvx)
    d3m = _diff(irx)
    n = len(target)
    x = np.full((n, 15), np.nan)
    for t in range(20, n):
        # Absolute yield levels.
        x[t, 0] = tnx[t]
        x[t, 1] = fvx[t]
        x[t, 2] = irx[t]
        # Prior-session daily yield changes.
        x[t, 3] = d10[t]
        x[t, 4] = d5[t]
        x[t, 5] = d3m[t]
        # Multi-day rate impulse.
        x[t, 6] = tnx[t] - tnx[t-5]
        x[t, 7] = fvx[t] - fvx[t-5]
        x[t, 8] = irx[t] - irx[t-5]
        # Curve shape / steepening information.
        x[t, 9] = tnx[t] - fvx[t]
        x[t, 10] = tnx[t] - irx[t]
        x[t, 11] = (tnx[t] - irx[t]) - (tnx[t-5] - irx[t-5])
        # Interaction with equity state: same yield shock can matter differently
        # after an up/down day or in a short trend.
        x[t, 12] = rt[t]
        x[t, 13] = target[t] / target[t-5] - 1.0
        x[t, 14] = d10[t] * rt[t]
    return x


def _ridge_predictions(x, outcomes, previous, config):
    window, ridge, cap = config
    preds = np.asarray(previous, float).copy()
    for j in range(len(outcomes)):
        if j < 252 or not np.all(np.isfinite(x[j])):
            continue
        start = max(0, j-window)
        idx = np.arange(start, j)
        valid = np.all(np.isfinite(x[idx]), axis=1) & np.isfinite(previous[idx])
        idx = idx[valid]
        if len(idx) < 252:
            continue
        train = x[idx]
        mean = train.mean(axis=0)
        sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
        z = (train-mean)/sd
        residual = outcomes[idx] - previous[idx]
        beta = np.linalg.solve(z.T@z + ridge*np.eye(z.shape[1]), z.T@residual)
        adj = float(np.clip(((x[j]-mean)/sd) @ beta, -cap, cap))
        preds[j] = float(np.clip(previous[j] + adj, 0.35, 0.70))
    return preds


def _brier(p, y):
    return float(np.mean((np.asarray(p)-np.asarray(y))**2))


def evaluate(aligned, target_symbol, target_date):
    dates, target = aligned[target_symbol]
    trace = _previous_trace(target, dates, target_date)
    positions = np.asarray([int(row['t']) for row in trace])
    previous = np.asarray([float(row['probability']) for row in trace], float)
    outcomes = np.asarray([float(row['outcome']) for row in trace], float)
    x = _feature_matrix(target, aligned)[positions]

    if len(outcomes) < 1008:
        raise ValueError(f'audit too short: {len(outcomes)}')
    split = len(outcomes)-252
    dev_y, test_y = outcomes[:split], outcomes[split:]
    prev_dev, prev_test = previous[:split], previous[split:]

    stable=[]
    for cfg in CONFIGS:
        pred=_ridge_predictions(x,outcomes,previous,cfg)
        dev=pred[:split]
        mid=len(dev)//2
        gains=(
            _brier(prev_dev,dev_y)-_brier(dev,dev_y),
            _brier(prev_dev[:mid],dev_y[:mid])-_brier(dev[:mid],dev_y[:mid]),
            _brier(prev_dev[mid:],dev_y[mid:])-_brier(dev[mid:],dev_y[mid:]),
        )
        if min(gains)>0:
            stable.append((_brier(dev,dev_y),cfg,pred,gains))
    if not stable:
        return {'selected':None,'reason':'no stable development winner'}

    _,cfg,pred,dev_gains=min(stable,key=lambda row:row[0])
    test=pred[split:]
    mid=len(test)//2
    test_gains=(
        _brier(prev_test,test_y)-_brier(test,test_y),
        _brier(prev_test[:mid],test_y[:mid])-_brier(test[:mid],test_y[:mid]),
        _brier(prev_test[mid:],test_y[mid:])-_brier(test[mid:],test_y[mid:]),
    )
    return {
        'selected':{'window':cfg[0],'ridge':cfg[1],'cap':cfg[2]},
        'dev_gain_all':dev_gains[0],
        'dev_gain_first':dev_gains[1],
        'dev_gain_second':dev_gains[2],
        'previous_test_brier':_brier(prev_test,test_y),
        'test_brier':_brier(test,test_y),
        'test_gain_all':test_gains[0],
        'test_gain_first':test_gains[1],
        'test_gain_second':test_gains[2],
        'holdout_passed':min(test_gains)>0,
        'holdout_count':len(test_y),
    }
