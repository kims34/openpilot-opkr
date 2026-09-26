"""Causal next-close probability forecasts.

Version 3.1 keeps the older KNN helpers for regression tests, but the production
forecast uses a simpler causal adaptive policy that beat the fixed baseline in
walk-forward research for SPY, QQQ and SCHD.  Every strategy choice is made
using only outcomes already known at the forecast time.
"""
import math
from datetime import date
import numpy as np

MODEL_VERSION = "3.1-causal-adaptive-close"
MIN_TRAIN = 320
POLICY_WINDOW = 504
AUDIT_DAYS = 1008
ALPHAS = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
ADAPTIVE_HALF_LIVES = (126.0, 252.0, 504.0, 756.0, 1260.0, 2520.0)
BASE_HALF_LIFE = 1260.0
CONDITIONAL_HALF_LIFE = 756.0
BETA_PRIOR = 20.0


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
    """Legacy KNN gate retained for regression tests and research comparison."""
    h = np.asarray(past[-POLICY_WINDOW:], dtype=float)
    if len(h) < 252:
        return 0.0
    split = int(len(h) * 2 / 3)
    fit, gate = h[:split], h[split:]
    predicted = fit[:, 1, None] + (fit[:, 0] - fit[:, 1])[:, None] * ALPHAS
    losses = ((predicted - fit[:, 2, None]) ** 2).mean(axis=0)
    alpha = float(ALPHAS[int(np.argmin(losses))])
    if alpha == 0:
        return 0.0
    p = gate[:, 1] + alpha * (gate[:, 0] - gate[:, 1])
    base_losses = (gate[:, 1] - gate[:, 2]) ** 2
    advantage = base_losses - (p - gate[:, 2]) ** 2
    required = max(0.002 * float(base_losses.mean()), 1.645 * hac_mean_se(advantage))
    return alpha if float(advantage.mean()) > required else 0.0


class Model:
    """Legacy five-feature KNN retained for causal-regression tests."""
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
        ood = float(np.mean(d2[ids])) > 5.0 or effective < 40
        return dict(posterior=base if ood else posterior, base=base,
                    effective_n=effective, neighbor_count=count, out_of_domain=ood)


def _weighted_rate(y, t, half_life, mask=None):
    """Past-only rise rate with a small 50/50 beta prior."""
    idx = np.arange(max(0, t - 2520), t)
    if mask is not None:
        idx = idx[mask[idx]]
    if len(idx) < 30:
        return None
    age = t - 1 - idx
    w = 0.5 ** (age / half_life)
    prior_half = BETA_PRIOR / 2
    return float((w @ y[idx] + prior_half) / (w.sum() + BETA_PRIOR))


def _weekday_codes(n, dates=None):
    if dates is None:
        return np.arange(n) % 5
    if len(dates) != n:
        raise ValueError("date/price length mismatch")
    return np.asarray([date.fromisoformat(str(d)).weekday() for d in dates], dtype=int)


def _candidate_probabilities(prices, dates=None):
    p = np.asarray(prices, dtype=float)
    n = len(p)
    y = (p[1:] > p[:-1]).astype(float)
    rets = np.zeros(n)
    rets[1:] = p[1:] / p[:-1] - 1
    weekdays = _weekday_codes(n, dates)

    hl_probs = {hl: np.full(n, np.nan) for hl in ADAPTIVE_HALF_LIVES}
    for hl in ADAPTIVE_HALF_LIVES:
        for t in range(300, n):
            hl_probs[hl][t] = _weighted_rate(y, t, hl)

    out = {name: np.full(n, np.nan) for name in ("fixed", "adaptive_hl", "prev_sign", "weekday")}
    out["fixed"][:] = hl_probs[BASE_HALF_LIFE]

    for t in range(300, n):
        fixed = out["fixed"][t]
        hist = np.arange(max(300, t - POLICY_WINDOW), t)
        best_loss, best_hl = float("inf"), BASE_HALF_LIFE
        for hl in ADAPTIVE_HALF_LIVES:
            q = hl_probs[hl][hist]
            valid = ~np.isnan(q)
            if valid.sum() >= 126:
                loss = float(np.mean((q[valid] - y[hist][valid]) ** 2))
                if loss < best_loss:
                    best_loss, best_hl = loss, hl
        out["adaptive_hl"][t] = hl_probs[best_hl][t]

        sign = rets[t] > 0
        mask = np.zeros(n - 1, dtype=bool)
        mask[1:t] = ((rets[1:t] > 0) == sign)
        cond = _weighted_rate(y, t, CONDITIONAL_HALF_LIFE, mask)
        out["prev_sign"][t] = fixed if cond is None else 0.75 * fixed + 0.25 * cond

        target_weekday = weekdays[t + 1] if t + 1 < n else None
        if target_weekday is None:
            out["weekday"][t] = fixed
        else:
            mask = np.zeros(n - 1, dtype=bool)
            mask[:t] = (weekdays[1:t + 1] == target_weekday)
            cond = _weighted_rate(y, t, BASE_HALF_LIFE, mask)
            out["weekday"][t] = fixed if cond is None else 0.75 * fixed + 0.25 * cond
    return y, out


def _causal_strategy(y, candidates, t):
    """Pick a challenger only if it beat fixed in both halves of the prior window."""
    fixed = candidates["fixed"]
    start = max(300, t - POLICY_WINDOW)
    mid = start + (t - start) // 2
    best_name, best_gain = "fixed", 0.0
    for name in ("adaptive_hl", "prev_sign", "weekday"):
        q = candidates[name]
        if np.isnan(q[t]):
            continue
        gains = []
        ok = True
        for a, b in ((start, mid), (mid, t)):
            idx = np.arange(a, b)
            idx = idx[~np.isnan(q[idx]) & ~np.isnan(fixed[idx])]
            if len(idx) < 60:
                ok = False
                break
            gain = float(np.mean((fixed[idx] - y[idx]) ** 2 - (q[idx] - y[idx]) ** 2))
            gains.append(gain)
        if ok and min(gains) > 0 and sum(gains) > best_gain:
            best_name, best_gain = name, sum(gains)
    return best_name


def block_indices(n, rng, repetitions=400, block=20):
    """Moving-block resampling preserves local ordering of daily audit errors."""
    block = min(block, n)
    starts = rng.integers(0, n - block + 1, size=(repetitions, math.ceil(n / block)))
    return (starts[:, :, None] + np.arange(block)).reshape(repetitions, -1)[:, :n]


def summarize_audit(audit, current_probability, seed=1947):
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


def estimate_prices(prices, include_trace=False, dates=None):
    p = np.asarray(prices, dtype=float)
    if len(p) < MIN_TRAIN + 1 or not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError("invalid/insufficient price history")
    n = len(p)
    y, candidates = _candidate_probabilities(p, dates)
    audit_start = max(MIN_TRAIN + POLICY_WINDOW, n - 1 - AUDIT_DAYS)
    audit, positions, strategies = [], [], []
    for t in range(audit_start, n - 1):
        strategy = _causal_strategy(y, candidates, t)
        probability = float(candidates[strategy][t])
        base = float(candidates["fixed"][t])
        audit.append((probability, base, float(y[t])))
        positions.append(t)
        strategies.append(strategy)

    current_t = n - 1
    current_strategy = _causal_strategy(y, candidates, current_t)
    probability = float(candidates[current_strategy][current_t])
    base = float(candidates["fixed"][current_t])
    result = summarize_audit(audit, probability)
    counts = {name: strategies.count(name) for name in ("fixed", "adaptive_hl", "prev_sign", "weekday")}
    result.update(probability=probability * 100, base_rate=base * 100,
        sample_size=min(n - 1, 2520), neighbor_count=0,
        calibration_alpha=0.0 if current_strategy == "fixed" else 1.0,
        validation_choice="base" if current_strategy == "fixed" else current_strategy,
        current_strategy=current_strategy, strategy_counts=counts,
        model_version=MODEL_VERSION, price_basis="close_excluding_dividends",
        as_of_index=n - 1, audit_start_index=positions[0], audit_end_index=positions[-1] + 1,
        out_of_domain=False, range_low=None, range_high=None,
        reliability="과거 검증" if result['evidence']=="과거 개선 관찰" else "제한적",
        method="10년 일별 종가 · 적응형 기본확률/요일/전일방향 · 과거 성적으로만 선택 · 일별 순차 검증",
        nonzero_signal_days=sum(s != "fixed" for s in strategies))
    if include_trace:
        result['audit_trace'] = [dict(t=t, probability=pred, base=base_i, outcome=outcome,
            alpha=0.0 if strategy == "fixed" else 1.0, strategy=strategy)
            for t, (pred, base_i, outcome), strategy in zip(positions, audit, strategies)]
    return result
