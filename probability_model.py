"""Causal next-close forecasts; selection windows never score themselves.

The five-feature KNN is retained, but a conservative past-only policy decides
whether its signal should be used. Backtest metrics evaluate that *whole policy*.
No numeric interval for an individual future probability is claimed.
"""
import math
import numpy as np

MODEL_VERSION = "3.0-prequential-close"
MIN_TRAIN = 320
POLICY_WINDOW = 504
AUDIT_DAYS = 1008
ALPHAS = np.array([0.0, 0.25, 0.5, 0.75, 1.0])


def hac_mean_se(values, lag=5):
    """Newey-West standard error of a mean (selection conservatism only)."""
    x = np.asarray(values, dtype=float)
    n = len(x)
    if n < 2:
        return float("inf")
    z = x - x.mean()
    long_var = float(z @ z) / n
    for k in range(1, min(lag, n - 1) + 1):
        long_var += 2 * (1 - k / (lag + 1)) * float(z[k:] @ z[:-k]) / n
    return math.sqrt(max(0.0, long_var) / n)


def choose_alpha(past):
    """Fit on older 2/3, require evidence on newer 1/3; never touch target y."""
    h = np.asarray(past[-POLICY_WINDOW:], dtype=float)
    if len(h) < 252:
        return 0.0
    split = int(len(h) * 2 / 3)
    fit, gate = h[:split], h[split:]
    # Columns are posterior, causal baseline, subsequently observed outcome.
    predicted = fit[:, 1, None] + (fit[:, 0] - fit[:, 1])[:, None] * ALPHAS
    losses = ((predicted - fit[:, 2, None]) ** 2).mean(axis=0)
    alpha = float(ALPHAS[int(np.argmin(losses))])
    if alpha == 0:
        return 0.0
    p = gate[:, 1] + alpha * (gate[:, 0] - gate[:, 1])
    base_losses = (gate[:, 1] - gate[:, 2]) ** 2
    advantage = base_losses - (p - gate[:, 2]) ** 2
    # Fixed, predeclared gate, not tuned on the reported audit results.
    required = max(0.002 * float(base_losses.mean()), 1.645 * hac_mean_se(advantage))
    return alpha if float(advantage.mean()) > required else 0.0


class Model:
    def __init__(self, prices):
        self.prices = np.asarray(prices, dtype=float)
        if len(self.prices) < MIN_TRAIN + 1 or not np.all(np.isfinite(self.prices)) or np.any(self.prices <= 0):
            raise ValueError("invalid/insufficient price history")
        n = len(self.prices)
        p = self.prices
        r = p[1:] / p[:-1] - 1
        self.features = np.zeros((n, 5))
        for i in range(60, n):
            self.features[i] = (r[i - 1], p[i] / p[i - 5] - 1,
                p[i] / p[i - 20] - 1, np.std(r[i - 20:i]),
                p[i] / max(p[i - 59:i + 1]) - 1)

    def core(self, t):
        if t < MIN_TRAIN:
            raise ValueError("training history too short")
        # Last training label is close[t] > close[t-1], known when forecasting t+1.
        f = self.features[60:t]
        y = (self.prices[61:t + 1] > self.prices[60:t]).astype(float)
        scale = np.maximum(np.std(f, axis=0, ddof=1), [0.003, 0.010, 0.020, 0.003, 0.020])
        d2 = np.mean(((f - self.features[t]) / scale) ** 2, axis=1)
        count = min(180, max(80, int(math.sqrt(len(y)) * 2.5)))
        ids = np.argsort(d2, kind="stable")[:count]
        age = (t - np.arange(60, t)) / 252
        w = np.exp(-0.5 * d2[ids]) * 0.5 ** (age[ids] / 4)
        effective = float(w.sum() ** 2 / (w @ w)) if w.sum() else 0.0
        bw = 0.5 ** (age / 5)
        base = float(bw @ y / bw.sum())
        raw = float(w @ y[ids] / w.sum()) if w.sum() else base
        posterior = (raw * effective + base * 80) / (effective + 80)
        # Similarity extrapolation is not evidence: suppress unfamiliar states.
        ood = float(np.mean(d2[ids])) > 5.0 or effective < 40
        return dict(posterior=base if ood else posterior, base=base,
                    effective_n=effective, neighbor_count=count, out_of_domain=ood)


def block_indices(n, rng, repetitions=400, block=20):
    """Moving-block resampling preserves local ordering of daily audit errors."""
    block = min(block, n)
    starts = rng.integers(0, n - block + 1, size=(repetitions, math.ceil(n / block)))
    return (starts[:, :, None] + np.arange(block)).reshape(repetitions, -1)[:, :n]


def summarize_audit(audit, current_probability, seed=1947):
    # Columns: policy prediction, baseline, outcome.
    a = np.asarray(audit, dtype=float)
    if len(a) < 252:
        raise ValueError("independent audit history too short")
    p, base, y = a.T
    loss = (p - y) ** 2
    base_loss = (base - y) ** 2
    mean_base = float(base_loss.mean())
    skill = 1 - float(loss.mean()) / mean_base if mean_base else 0.0
    ids = block_indices(len(a), np.random.default_rng(seed))
    boot_base = base_loss[ids].mean(axis=1)
    boot_skill = 1 - loss[ids].mean(axis=1) / np.maximum(boot_base, 1e-12)
    skill_low, skill_high = np.quantile(boot_skill, [0.025, 0.975])
    # Reliability diagram uses predeclared fixed 10-percentage-point buckets.
    bins = []
    for lower in range(0, 100, 10):
        mask = (p >= lower / 100) & (p < (lower + 10) / 100)
        count = int(mask.sum())
        bins.append(dict(low=lower, high=lower + 10, count=count,
            mean_prediction=float(p[mask].mean()) * 100 if count else None,
            observed_rise_rate=float(y[mask].mean()) * 100 if count else None))
    bucket = min(9, int(current_probability * 10))
    calibration = dict(bins[bucket])
    mask = (p >= bucket / 10) & (p < (bucket + 1) / 10)
    calibration.update(range_low=None, range_high=None)
    # This interval is for a historical bucket's frequency, NOT tomorrow's p.
    if mask.sum() >= 100 and y[mask].sum() >= 5 and (1 - y[mask]).sum() >= 5:
        denominators = mask[ids].sum(axis=1)
        rates = (mask[ids] * y[ids]).sum(axis=1) / np.maximum(denominators, 1)
        valid = rates[denominators >= 30]
        if len(valid) >= 360:
            lo, hi = np.quantile(valid, [0.025, 0.975])
            calibration.update(range_low=float(lo) * 100, range_high=float(hi) * 100)
    ece = sum(b['count'] / len(a) * abs(b['mean_prediction'] - b['observed_rise_rate'])
              for b in bins if b['count'])
    clipped = np.clip(p, 1e-9, 1 - 1e-9)
    return dict(validation_count=len(a), backtest_brier=float(loss.mean()),
        baseline_brier=mean_base, backtest_skill=skill * 100,
        skill_range_low=float(skill_low) * 100, skill_range_high=float(skill_high) * 100,
        log_loss=float(-(y * np.log(clipped) + (1 - y) * np.log(1 - clipped)).mean()),
        calibration_error_pp=ece, calibration=calibration, calibration_bins=bins,
        evidence="과거 개선 관찰" if skill_low > 0 and len(a) >= 504 else "예측 우위 미확인")


def estimate_prices(prices, include_trace=False):
    model = Model(prices)
    n = len(prices)
    # Daily predictions, not a convenient weekday/subsample selected after testing.
    first = max(MIN_TRAIN, n - 1 - AUDIT_DAYS - POLICY_WINDOW)
    history, audit, positions, alphas = [], [], [], []
    for t in range(first, n - 1):
        core = model.core(t)
        if len(history) >= POLICY_WINDOW:
            alpha = choose_alpha(history)
            p = core['base'] + alpha * (core['posterior'] - core['base'])
            audit.append((p, core['base'], float(prices[t + 1] > prices[t])))
            positions.append(t)
            alphas.append(alpha)
        history.append((core['posterior'], core['base'], float(prices[t + 1] > prices[t])))
    core = model.core(n - 1)
    alpha = choose_alpha(history)
    probability = core['base'] + alpha * (core['posterior'] - core['base'])
    result = summarize_audit(audit, probability)
    result.update(probability=probability * 100, base_rate=core['base'] * 100,
        sample_size=round(core['effective_n']), neighbor_count=core['neighbor_count'],
        calibration_alpha=alpha, validation_choice="base" if alpha == 0 else "calibrated",
        model_version=MODEL_VERSION, price_basis="close_excluding_dividends",
        as_of_index=n - 1, audit_start_index=positions[0], audit_end_index=positions[-1] + 1,
        out_of_domain=core['out_of_domain'], range_low=None, range_high=None,
        reliability="과거 검증" if result['evidence']=="과거 개선 관찰" else "제한적",
        method="10년 일별 종가 · 과거 자료로만 모델 선택 · 일별 순차 검증",
        nonzero_signal_days=sum(a > 0 for a in alphas))
    if include_trace:
        result['audit_trace'] = [dict(t=t, probability=p, base=base, outcome=y, alpha=alpha)
            for t,(p,base,y),alpha in zip(positions,audit,alphas)]
    return result
