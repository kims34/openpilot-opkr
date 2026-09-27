"""IndexAlert next-close probability model 3.3.

3.3 keeps the validated causal 3.2 policy as its safety floor and adds a
past-only probability calibration layer.  Calibration is allowed to change the
served probability only when it lowers Brier loss versus 3.2 over the full
1,008-session audit *and* in both chronological halves.  Otherwise 3.2 is
served unchanged.

The calibration itself is causal: for each historical forecast date it chooses
an alpha using only earlier, already-known outcomes.  Alpha shrinks the raw
adaptive candidate toward that date's causal base rise rate.
"""
from datetime import date
import numpy as np

import probability_model as core
import probability_model_v31_runtime as v32

MODEL_VERSION = "3.3-calibration-gated"
CALIBRATION_ALPHAS = (0.0, 0.25, 0.50, 0.75, 1.0)
CALIBRATION_WINDOW = 504
CALIBRATION_MIN_HALF = 60


def _prepare(prices, dates=None, target_date=None):
    p = np.asarray(prices, dtype=float)
    if len(p) < core.MIN_TRAIN + 1 or not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError("invalid/insufficient price history")
    n = len(p)
    y, candidates = core._candidate_probabilities(p, dates)
    current_t = n - 1

    # Historical weekday candidates already use each forecast's actual t+1
    # date.  Only the live row lacks t+1, so use the exchange-calendar target.
    if target_date and dates is not None:
        weekdays = core._weekday_codes(n, dates)
        target_weekday = date.fromisoformat(str(target_date)).weekday()
        mask = np.zeros(n - 1, dtype=bool)
        mask[:current_t] = (weekdays[1:current_t + 1] == target_weekday)
        cond = core._weighted_rate(y, current_t, core.BASE_HALF_LIFE, mask)
        fixed = float(candidates["fixed"][current_t])
        candidates["weekday"][current_t] = fixed if cond is None else 0.75 * fixed + 0.25 * cond
    return p, y, candidates


def _raw_policy_series(y, candidates, n):
    raw = np.full(n, np.nan)
    base = np.asarray(candidates["fixed"], dtype=float).copy()
    strategy = ["fixed"] * n
    for t in range(300, n):
        s = core._causal_strategy(y, candidates, t)
        q = float(candidates[s][t])
        b = float(base[t])
        if np.isfinite(q) and np.isfinite(b):
            raw[t] = q
            strategy[t] = s
    return raw, base, strategy


def _choose_alpha(raw, base, y, t):
    """Choose shrinkage using only forecasts/outcomes strictly before t."""
    start = max(300, t - CALIBRATION_WINDOW)
    idx = np.arange(start, t)
    valid = np.isfinite(raw[idx]) & np.isfinite(base[idx])
    idx = idx[valid]
    if len(idx) < 2 * CALIBRATION_MIN_HALF:
        return 0.0

    mid = len(idx) // 2
    halves = (idx[:mid], idx[mid:])
    base_loss_all = (base[idx] - y[idx]) ** 2
    best_alpha = 0.0
    best_loss = float(base_loss_all.mean())

    for alpha in CALIBRATION_ALPHAS[1:]:
        q = base + alpha * (raw - base)
        # Stability gate: candidate must beat base independently in both
        # chronological halves.  This prevents one lucky regime dominating.
        stable = True
        for h in halves:
            if len(h) < CALIBRATION_MIN_HALF:
                stable = False
                break
            base_loss = (base[h] - y[h]) ** 2
            cand_loss = (q[h] - y[h]) ** 2
            if float(base_loss.mean() - cand_loss.mean()) <= 0.0:
                stable = False
                break
        if not stable:
            continue
        loss = float(np.mean((q[idx] - y[idx]) ** 2))
        if loss < best_loss - 1e-12:
            best_loss = loss
            best_alpha = float(alpha)
    return best_alpha


def _brier_parts(probabilities, outcomes):
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if len(p) != len(y) or len(p) < 2:
        raise ValueError("audit mismatch")
    losses = (p - y) ** 2
    mid = len(losses) // 2
    return (
        float(losses.mean()),
        float(losses[:mid].mean()),
        float(losses[mid:].mean()),
    )


def estimate_prices(prices, include_trace=False, dates=None, target_date=None):
    p, y, candidates = _prepare(prices, dates, target_date)
    n = len(p)
    raw, base, raw_strategy = _raw_policy_series(y, candidates, n)
    audit_start = max(core.MIN_TRAIN + core.POLICY_WINDOW, n - 1 - core.AUDIT_DAYS)

    audit = []
    positions = []
    alphas = []
    strategies = []
    for t in range(audit_start, n - 1):
        alpha = _choose_alpha(raw, base, y, t)
        probability = float(base[t] + alpha * (raw[t] - base[t]))
        audit.append((probability, float(base[t]), float(y[t])))
        positions.append(t)
        alphas.append(alpha)
        strategies.append(raw_strategy[t])

    current_t = n - 1
    current_alpha = _choose_alpha(raw, base, y, current_t)
    raw_current = float(raw[current_t])
    base_current = float(base[current_t])
    calibrated_current = float(base_current + current_alpha * (raw_current - base_current))

    calibrated_stats = core.summarize_audit(audit, calibrated_current)
    new_probs = [row[0] for row in audit]
    outcomes = [row[2] for row in audit]
    new_brier, new_first, new_second = _brier_parts(new_probs, outcomes)

    # 3.2 remains the safety floor.  Compare against exactly the same price
    # history and only promote the new calibrated output if it is better on the
    # overall audit and on both chronological halves.
    previous = v32.estimate_prices(
        prices, include_trace=True, dates=dates, target_date=target_date
    )
    prev_trace = previous.get("audit_trace") or []
    prev_probs = [float(row["probability"]) for row in prev_trace]
    prev_outcomes = [float(row["outcome"]) for row in prev_trace]
    if len(prev_probs) != len(new_probs):
        raise ValueError("3.2/3.3 audit alignment mismatch")
    prev_brier, prev_first, prev_second = _brier_parts(prev_probs, prev_outcomes)

    gate_passed = (
        current_alpha > 0.0
        and new_brier < prev_brier - 1e-12
        and new_first <= prev_first + 1e-12
        and new_second <= prev_second + 1e-12
        and float(calibrated_stats.get("backtest_skill") or 0.0) > 0.0
    )

    if gate_passed:
        result = dict(calibrated_stats)
        served_probability = calibrated_current
        served_strategy = raw_strategy[current_t]
        reliability = "3.3 보정 검증 통과"
        fallback_reason = None
        validation_choice = "3.3_calibrated"
    else:
        result = {k: v for k, v in previous.items() if k != "audit_trace"}
        served_probability = float(previous["probability"]) / 100.0
        served_strategy = str(previous.get("current_strategy") or raw_strategy[current_t])
        reliability = "3.2 안전모드 유지"
        fallback_reason = "3.3 보정이 전체·전반부·후반부 검증을 모두 이기지 못해 3.2 결과 유지"
        validation_choice = "3.2_safe_fallback"

    result.update(
        probability=served_probability * 100.0,
        base_rate=base_current * 100.0,
        candidate_probability=raw_current * 100.0,
        calibration_candidate_probability=calibrated_current * 100.0,
        calibration_alpha=current_alpha,
        calibration_gate_passed=gate_passed,
        previous_model_probability=float(previous["probability"]),
        previous_model_version=str(previous.get("model_version") or "3.2-live-guardrails"),
        calibration_audit_brier=new_brier,
        previous_audit_brier=prev_brier,
        calibration_first_half_brier=new_first,
        previous_first_half_brier=prev_first,
        calibration_second_half_brier=new_second,
        previous_second_half_brier=prev_second,
        fallback_to_previous=not gate_passed,
        fallback_reason=fallback_reason,
        verified_advantage=gate_passed,
        current_strategy=served_strategy,
        validation_choice=validation_choice,
        model_version=MODEL_VERSION,
        reliability=reliability,
        price_basis="close_excluding_dividends",
        as_of_index=n - 1,
        audit_start_index=positions[0],
        audit_end_index=positions[-1] + 1,
        method=(
            "3.2 인과 적응형 확률 + 과거 504거래일 보정 축소계수 선택 + "
            "전체/전반부/후반부 Brier 동시 개선 시에만 3.3 승격"
        ),
        calibration_strategy_counts={
            str(a): alphas.count(a) for a in CALIBRATION_ALPHAS
        },
        nonzero_signal_days=sum(a > 0.0 for a in alphas),
    )

    if include_trace:
        result["audit_trace"] = [
            dict(
                t=t,
                probability=float(probability),
                base=float(base_i),
                outcome=float(outcome),
                alpha=float(alpha),
                strategy=strategy,
            )
            for t, (probability, base_i, outcome), alpha, strategy
            in zip(positions, audit, alphas, strategies)
        ]
    return result
