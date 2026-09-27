"""IndexAlert next-close probability model 3.4.

Adds five causal market-state challengers to the validated 3.3 stack:
1) previous-day return magnitude, 2) two-day sign pattern, 3) 20-session trend,
4) distance from the prior 60-session high, and 5) 20-session volatility regime.

Every conditional estimate is built only from outcomes known before the forecast
being made. 3.4 is served only when it beats the *actually served* 3.3 safety
floor on the full 1,008-session audit and both chronological halves. Otherwise
3.3 is returned unchanged.
"""
import numpy as np

import probability_model as core
import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

MODEL_VERSION = "3.4-feature-gated"
FEATURE_BLEND = 0.20
FEATURE_HALF_LIFE = 756.0
MIN_IMPROVEMENT = 1e-5
FEATURE_NAMES = ("ret_strength", "two_day", "trend20", "drawdown60", "vol20_regime")


def _bucket_return(x):
    if x <= -0.01:
        return 0
    if x < 0.0:
        return 1
    if x < 0.01:
        return 2
    return 3


def _states(prices):
    p = np.asarray(prices, dtype=float)
    n = len(p)
    r = np.zeros(n)
    r[1:] = p[1:] / p[:-1] - 1.0

    ret_strength = np.full(n, -1, dtype=int)
    two_day = np.full(n, -1, dtype=int)
    trend20 = np.full(n, -1, dtype=int)
    drawdown60 = np.full(n, -1, dtype=int)
    vol20_regime = np.full(n, -1, dtype=int)
    vols = np.full(n, np.nan)

    for t in range(20, n):
        vols[t] = float(np.std(r[t-19:t+1], ddof=1))
        ret_strength[t] = _bucket_return(r[t])
        if t >= 2:
            two_day[t] = (1 if r[t-1] > 0 else 0) * 2 + (1 if r[t] > 0 else 0)
        trend20[t] = 1 if p[t] >= p[t-20] else 0
        if t >= 59:
            peak = float(np.max(p[t-59:t+1]))
            dd = p[t] / peak - 1.0
            drawdown60[t] = 0 if dd <= -0.08 else 1 if dd <= -0.03 else 2
        hist = vols[max(20, t-252):t]
        hist = hist[np.isfinite(hist)]
        if len(hist) >= 60 and np.isfinite(vols[t]):
            vol20_regime[t] = 1 if vols[t] > float(np.median(hist)) else 0

    return {
        "ret_strength": ret_strength,
        "two_day": two_day,
        "trend20": trend20,
        "drawdown60": drawdown60,
        "vol20_regime": vol20_regime,
    }


def _candidate_probabilities(prices, dates=None):
    p = np.asarray(prices, dtype=float)
    n = len(p)
    y, base_candidates = core._candidate_probabilities(p, dates)
    fixed = np.asarray(base_candidates["fixed"], dtype=float)
    states = _states(p)
    out = {name: np.full(n, np.nan) for name in FEATURE_NAMES}

    for t in range(320, n):
        b = float(fixed[t])
        if not np.isfinite(b):
            continue
        for name in FEATURE_NAMES:
            state = int(states[name][t])
            if state < 0:
                out[name][t] = b
                continue
            mask = np.zeros(n - 1, dtype=bool)
            hist_states = states[name][:t]
            valid = np.arange(t)
            chosen = valid[hist_states == state]
            chosen = chosen[chosen < n - 1]
            mask[chosen] = True
            cond = core._weighted_rate(y, t, FEATURE_HALF_LIFE, mask)
            out[name][t] = b if cond is None else (1.0 - FEATURE_BLEND) * b + FEATURE_BLEND * float(cond)
    return y, fixed, out


def _choose_strategy(y, fixed, candidates, t):
    start = max(320, t - core.POLICY_WINDOW)
    mid = start + (t - start) // 2
    best = "fixed"
    best_gain = 0.0
    for name in FEATURE_NAMES:
        q = candidates[name]
        if not np.isfinite(q[t]):
            continue
        half_gains = []
        stable = True
        for a, b in ((start, mid), (mid, t)):
            idx = np.arange(a, b)
            idx = idx[np.isfinite(q[idx]) & np.isfinite(fixed[idx])]
            if len(idx) < 60:
                stable = False
                break
            gain = float(np.mean((fixed[idx] - y[idx]) ** 2 - (q[idx] - y[idx]) ** 2))
            if gain <= 0.0:
                stable = False
                break
            half_gains.append(gain)
        if stable:
            gain = sum(half_gains)
            if gain > best_gain:
                best = name
                best_gain = gain
    return best


def _brier_parts(probs, outcomes):
    p = np.asarray(probs, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    losses = (p - y) ** 2
    mid = len(losses) // 2
    return float(losses.mean()), float(losses[:mid].mean()), float(losses[mid:].mean())


def _served_previous(prices, dates=None, target_date=None):
    prev33 = v33.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    if prev33.get("calibration_gate_passed"):
        return prev33, prev33.get("audit_trace") or []
    prev32 = v32.estimate_prices(prices, include_trace=True, dates=dates, target_date=target_date)
    return prev33, prev32.get("audit_trace") or []


def estimate_prices(prices, include_trace=False, dates=None, target_date=None):
    p = np.asarray(prices, dtype=float)
    if len(p) < core.MIN_TRAIN + 1 or not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError("invalid/insufficient price history")
    n = len(p)
    y, fixed, candidates = _candidate_probabilities(p, dates)
    audit_start = max(core.MIN_TRAIN + core.POLICY_WINDOW, n - 1 - core.AUDIT_DAYS)

    audit, positions, strategies = [], [], []
    for t in range(audit_start, n - 1):
        strategy = _choose_strategy(y, fixed, candidates, t)
        q = float(fixed[t] if strategy == "fixed" else candidates[strategy][t])
        audit.append((q, float(fixed[t]), float(y[t])))
        positions.append(t)
        strategies.append(strategy)

    current_t = n - 1
    current_strategy = _choose_strategy(y, fixed, candidates, current_t)
    candidate_current = float(fixed[current_t] if current_strategy == "fixed" else candidates[current_strategy][current_t])
    stats = core.summarize_audit(audit, candidate_current)
    new_probs = [x[0] for x in audit]
    outcomes = [x[2] for x in audit]
    new_brier, new_first, new_second = _brier_parts(new_probs, outcomes)

    previous, prev_trace = _served_previous(prices, dates, target_date)
    prev_probs = [float(x["probability"]) for x in prev_trace]
    prev_outcomes = [float(x["outcome"]) for x in prev_trace]
    if len(prev_probs) != len(new_probs):
        raise ValueError("3.3/3.4 audit alignment mismatch")
    prev_brier, prev_first, prev_second = _brier_parts(prev_probs, prev_outcomes)

    gate_passed = (
        current_strategy != "fixed"
        and new_brier < prev_brier - MIN_IMPROVEMENT
        and new_first <= prev_first + 1e-12
        and new_second <= prev_second + 1e-12
        and float(stats.get("backtest_skill") or 0.0) > 0.0
        and float(stats.get("skill_range_low") or 0.0) > 0.0
    )

    if gate_passed:
        result = dict(stats)
        served = candidate_current
        reliability = "3.4 다중신호 검증 통과"
        fallback_reason = None
        validation_choice = current_strategy
    else:
        result = {k: v for k, v in previous.items() if k != "audit_trace"}
        served = float(previous["probability"]) / 100.0
        reliability = "3.3 안전모드 유지"
        fallback_reason = "3.4가 전체·전반부·후반부 Brier 및 신뢰구간 검증을 모두 통과하지 못해 3.3 결과 유지"
        validation_choice = "3.3_safe_fallback"

    result.update(
        probability=served * 100.0,
        model_version=MODEL_VERSION,
        feature_candidate_probability=candidate_current * 100.0,
        feature_strategy=current_strategy,
        feature_gate_passed=gate_passed,
        feature_audit_brier=new_brier,
        previous_audit_brier=prev_brier,
        feature_first_half_brier=new_first,
        previous_first_half_brier=prev_first,
        feature_second_half_brier=new_second,
        previous_second_half_brier=prev_second,
        fallback_to_previous=not gate_passed,
        fallback_reason=fallback_reason,
        validation_choice=validation_choice,
        reliability=reliability,
        current_strategy=current_strategy if gate_passed else str(previous.get("current_strategy") or "fixed"),
        method=("3.3 안전모드 + 전일수익률강도/2일패턴/20일추세/60일고점이격/20일변동성 인과 후보 + "
                "전체·시간순 양분 Brier와 bootstrap skill 하한 동시 개선 시에만 3.4 승격"),
        feature_strategy_counts={name: strategies.count(name) for name in ("fixed",) + FEATURE_NAMES},
        audit_start_index=positions[0],
        audit_end_index=positions[-1] + 1,
        as_of_index=n - 1,
    )
    if include_trace:
        result["audit_trace"] = [
            dict(t=t, probability=float(q), base=float(b), outcome=float(o), strategy=s)
            for t, (q, b, o), s in zip(positions, audit, strategies)
        ]
    return result
