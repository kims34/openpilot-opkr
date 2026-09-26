"""Validated 21-session terminal +/-5% probability model.

This answers a different question from the existing one-month +/-10% barrier model:
what is P(close in 21 sessions >= +5%) and P(close in 21 sessions <= -5%)?

It reuses the causal feature set, neighbour de-clustering, Bayesian shrinkage,
chronological tuning split, and untouched walk-forward validation from
one_month_probability.  Analogue estimates are served only when they beat the
unconditional historical baseline on the later validation slice.
"""
import math

import one_month_probability as month

HORIZON = month.HORIZON
THRESHOLD = 0.05
METHOD = "validated-historical-analogs-terminal-5pct-v1"


def _records(prices):
    out = []
    last = len(prices) - HORIZON - 1
    for i in range(month.MIN_FEATURE_INDEX, last + 1):
        terminal_return = prices[i + HORIZON] / prices[i] - 1.0
        if not math.isfinite(terminal_return):
            continue
        out.append((
            i,
            month._features(prices, i),
            int(terminal_return >= THRESHOLD),
            int(terminal_return <= -THRESHOLD),
        ))
    return out


def estimate(rows):
    clean = [(str(d), float(p)) for d, p in rows if float(p) > 0]
    if len(clean) < month.MIN_HISTORY:
        raise ValueError("insufficient history for terminal +/-5% probability")
    prices = [p for _, p in clean]
    records = _records(prices)
    if len(records) < 300:
        raise ValueError("insufficient labelled monthly terminal windows")

    current_features = month._features(prices, len(prices) - 1)
    base_up = month._baseline(records, 2)
    base_down = month._baseline(records, 3)

    k_up, tune_up, test_up = month._choose_and_validate(prices, records, 2)
    k_down, tune_down, test_down = month._choose_and_validate(prices, records, 3)

    analog_up, sample_up, eff_up = month._analog_probability(current_features, records, k_up, 2)
    analog_down, sample_down, eff_down = month._analog_probability(current_features, records, k_down, 3)

    use_analog_up = bool(test_up and test_up["count"] >= 80 and test_up["skill"] > 0.0)
    use_analog_down = bool(test_down and test_down["count"] >= 80 and test_down["skill"] > 0.0)

    served_up = analog_up if use_analog_up else base_up
    served_down = analog_down if use_analog_down else base_down

    return {
        "terminal_5_horizon_sessions": HORIZON,
        "terminal_5_threshold_percent": int(THRESHOLD * 100),
        "terminal_up_5_probability": round(100.0 * served_up, 1),
        "terminal_down_5_probability": round(100.0 * served_down, 1),
        "terminal_5_analog_up_probability": round(100.0 * analog_up, 1),
        "terminal_5_analog_down_probability": round(100.0 * analog_down, 1),
        "terminal_5_baseline_up_probability": round(100.0 * base_up, 1),
        "terminal_5_baseline_down_probability": round(100.0 * base_down, 1),
        "terminal_5_baseline_sample_size": len(records),
        "terminal_5_sample_size": min(sample_up, sample_down),
        "terminal_5_effective_sample_up": round(eff_up, 1),
        "terminal_5_effective_sample_down": round(eff_down, 1),
        "terminal_5_selected_k_up": k_up,
        "terminal_5_selected_k_down": k_down,
        "terminal_5_validation_up": test_up,
        "terminal_5_validation_down": test_down,
        "terminal_5_tuning_up": tune_up,
        "terminal_5_tuning_down": tune_down,
        "terminal_5_selection_up": "analog" if use_analog_up else "baseline",
        "terminal_5_selection_down": "analog" if use_analog_down else "baseline",
        "terminal_5_method": METHOD,
        "terminal_5_as_of": clean[-1][0],
    }
