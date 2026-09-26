"""Runtime adapter for model 3.1.

The historical audit already knows every next-session date.  For the live
forecast, the target session is supplied by the exchange calendar so the
weekday challenger can use the actual next trading day's weekday (including
holiday-shortened weeks) rather than silently falling back to the base rate.
"""
from datetime import date
import numpy as np
import probability_model as core

MODEL_VERSION = core.MODEL_VERSION


def estimate_prices(prices, include_trace=False, dates=None, target_date=None):
    p = np.asarray(prices, dtype=float)
    if len(p) < core.MIN_TRAIN + 1 or not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError("invalid/insufficient price history")
    n = len(p)
    y, candidates = core._candidate_probabilities(p, dates)
    current_t = n - 1

    # Only the live forecast lacks a t+1 row.  Fill its weekday candidate from
    # the exchange-calendar target date. Historical candidates remain untouched.
    if target_date and dates is not None:
        weekdays = core._weekday_codes(n, dates)
        target_weekday = date.fromisoformat(str(target_date)).weekday()
        mask = np.zeros(n - 1, dtype=bool)
        mask[:current_t] = (weekdays[1:current_t + 1] == target_weekday)
        cond = core._weighted_rate(y, current_t, core.BASE_HALF_LIFE, mask)
        fixed = float(candidates["fixed"][current_t])
        candidates["weekday"][current_t] = fixed if cond is None else 0.75 * fixed + 0.25 * cond

    audit_start = max(core.MIN_TRAIN + core.POLICY_WINDOW, n - 1 - core.AUDIT_DAYS)
    audit, positions, strategies = [], [], []
    for t in range(audit_start, n - 1):
        strategy = core._causal_strategy(y, candidates, t)
        probability = float(candidates[strategy][t])
        base = float(candidates["fixed"][t])
        audit.append((probability, base, float(y[t])))
        positions.append(t)
        strategies.append(strategy)

    current_strategy = core._causal_strategy(y, candidates, current_t)
    probability = float(candidates[current_strategy][current_t])
    base = float(candidates["fixed"][current_t])
    result = core.summarize_audit(audit, probability)
    counts = {name: strategies.count(name) for name in ("fixed", "adaptive_hl", "prev_sign", "weekday")}
    result.update(
        probability=probability * 100,
        base_rate=base * 100,
        sample_size=min(n - 1, 2520),
        neighbor_count=0,
        calibration_alpha=0.0 if current_strategy == "fixed" else 1.0,
        validation_choice="base" if current_strategy == "fixed" else current_strategy,
        current_strategy=current_strategy,
        strategy_counts=counts,
        model_version=MODEL_VERSION,
        price_basis="close_excluding_dividends",
        as_of_index=n - 1,
        audit_start_index=positions[0],
        audit_end_index=positions[-1] + 1,
        out_of_domain=False,
        range_low=None,
        range_high=None,
        reliability="과거 검증" if result["evidence"] == "과거 개선 관찰" else "제한적",
        method="10년 일별 종가 · 적응형 기본확률/요일/전일방향 · 과거 성적으로만 선택 · 일별 순차 검증",
        nonzero_signal_days=sum(s != "fixed" for s in strategies),
    )
    if include_trace:
        result["audit_trace"] = [
            dict(
                t=t,
                probability=pred,
                base=base_i,
                outcome=outcome,
                alpha=0.0 if strategy == "fixed" else 1.0,
                strategy=strategy,
            )
            for t, (pred, base_i, outcome), strategy in zip(positions, audit, strategies)
        ]
    return result
