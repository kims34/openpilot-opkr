"""Validated 21-session terminal-return distribution for IndexAlert.

This complements the +/-10% barrier-touch model.  A continuous future return
cannot have a meaningful probability at one exact percentage, so returns are
binned in 2 percentage-point intervals.  We report the most probable bin.

The analogue model is causal and is served only when it beats an unconditional
historical distribution on a later untouched walk-forward validation slice.
Otherwise the unconditional distribution is used.
"""
import math
import statistics

import one_month_probability as month

HORIZON = month.HORIZON
MIN_FEATURE_INDEX = month.MIN_FEATURE_INDEX
VALIDATION_DAYS = month.VALIDATION_DAYS
TUNE_FRACTION = month.TUNE_FRACTION
K_CANDIDATES = month.K_CANDIDATES
PRIOR_STRENGTH = month.PRIOR_STRENGTH

BIN_WIDTH = 0.02
MIN_EDGE = -0.20
MAX_EDGE = 0.20
METHOD = "validated-historical-analogs-terminal-return-v1"

# Interior edges: -20%, -18%, ..., +20%.  Bin 0 is below -20%, the last
# bin is +20% or above, and all interior bins have 2pp width.
EDGES = tuple(MIN_EDGE + i * BIN_WIDTH for i in range(int(round((MAX_EDGE - MIN_EDGE) / BIN_WIDTH)) + 1))
BIN_COUNT = len(EDGES) + 1


def _bin_index(value):
    if value < EDGES[0]:
        return 0
    for i in range(len(EDGES) - 1):
        if EDGES[i] <= value < EDGES[i + 1]:
            return i + 1
    if value < EDGES[-1]:
        return len(EDGES) - 1
    return len(EDGES)


def _bin_bounds(index):
    if index <= 0:
        return None, EDGES[0]
    if index >= len(EDGES):
        return EDGES[-1], None
    return EDGES[index - 1], EDGES[index]


def _bin_label(index):
    low, high = _bin_bounds(index)
    if low is None:
        return f"{high * 100:.0f}% 미만"
    if high is None:
        return f"+{low * 100:.0f}% 이상"
    def fmt(x):
        v = x * 100.0
        return f"{v:+.0f}%"
    return f"{fmt(low)} ~ {fmt(high)}"


def _records(prices):
    out = []
    last = len(prices) - HORIZON - 1
    for i in range(MIN_FEATURE_INDEX, last + 1):
        terminal_return = prices[i + HORIZON] / prices[i] - 1.0
        if not math.isfinite(terminal_return):
            continue
        out.append((i, month._features(prices, i), _bin_index(terminal_return), terminal_return))
    return out


def _baseline_distribution(records):
    counts = [0.0] * BIN_COUNT
    for record in records:
        counts[record[2]] += 1.0
    total = sum(counts)
    if total <= 0:
        return [1.0 / BIN_COUNT] * BIN_COUNT
    return [c / total for c in counts]


def _analog_distribution(target_features, training, k):
    baseline = _baseline_distribution(training)
    ranked = sorted((month._distance(target_features, r[1]), r) for r in training)
    selected = []
    selected_indices = []
    for distance, record in ranked:
        idx = record[0]
        if any(abs(idx - old) < 3 for old in selected_indices):
            continue
        selected.append((distance, record))
        selected_indices.append(idx)
        if len(selected) >= k:
            break
    if not selected:
        return baseline, 0, 0.0

    distances = [d for d, _ in selected]
    bandwidth = max(statistics.median(distances), 0.35)
    weights = [math.exp(-0.5 * (d / bandwidth) ** 2) for d in distances]
    weight_sum = sum(weights)
    weighted_counts = [0.0] * BIN_COUNT
    for weight, (_, record) in zip(weights, selected):
        weighted_counts[record[2]] += weight
    denom = weight_sum + PRIOR_STRENGTH
    probabilities = [
        (weighted_counts[i] + PRIOR_STRENGTH * baseline[i]) / denom
        for i in range(BIN_COUNT)
    ]
    effective_n = (weight_sum * weight_sum / sum(w * w for w in weights)) if weights else 0.0
    return probabilities, len(selected), effective_n


def _multiclass_brier(probabilities, actual_index):
    return sum((p - (1.0 if i == actual_index else 0.0)) ** 2 for i, p in enumerate(probabilities))


def _walk_forward(prices, records, k, targets):
    model_scores = []
    base_scores = []
    record_by_index = {r[0]: r for r in records}
    for t in targets:
        training = [r for r in records if r[0] <= t - HORIZON - 1]
        if len(training) < 300:
            continue
        actual = record_by_index.get(t)
        if actual is None:
            continue
        baseline = _baseline_distribution(training)
        model_probs, _, _ = _analog_distribution(month._features(prices, t), training, k)
        model_scores.append(_multiclass_brier(model_probs, actual[2]))
        base_scores.append(_multiclass_brier(baseline, actual[2]))
    if not model_scores:
        return None
    model_brier = sum(model_scores) / len(model_scores)
    baseline_brier = sum(base_scores) / len(base_scores)
    skill = (1.0 - model_brier / baseline_brier) * 100.0 if baseline_brier > 0 else 0.0
    return {
        "count": len(model_scores),
        "model_brier": model_brier,
        "baseline_brier": baseline_brier,
        "skill": skill,
    }


def _choose_and_validate(prices, records):
    eligible = [
        r[0] for r in records
        if r[0] >= max(MIN_FEATURE_INDEX + 300 + HORIZON, len(prices) - VALIDATION_DAYS - HORIZON)
    ]
    if len(eligible) < 120:
        return K_CANDIDATES[1], None, None
    split = max(60, int(len(eligible) * TUNE_FRACTION))
    tune_targets = eligible[:split]
    test_targets = eligible[split:]
    tuning = []
    for k in K_CANDIDATES:
        result = _walk_forward(prices, records, k, tune_targets)
        if result:
            tuning.append((result["model_brier"], k, result))
    if not tuning:
        return K_CANDIDATES[1], None, None
    _, best_k, tune = min(tuning, key=lambda x: x[0])
    test = _walk_forward(prices, records, best_k, test_targets)
    return best_k, tune, test


def estimate(rows):
    clean = [(str(d), float(p)) for d, p in rows if float(p) > 0]
    if len(clean) < month.MIN_HISTORY:
        raise ValueError("insufficient history for terminal-return distribution")
    prices = [p for _, p in clean]
    records = _records(prices)
    if len(records) < 300:
        raise ValueError("insufficient labelled monthly return windows")

    current_features = month._features(prices, len(prices) - 1)
    baseline = _baseline_distribution(records)
    k, tune, test = _choose_and_validate(prices, records)
    analog, sample_size, effective_n = _analog_distribution(current_features, records, k)
    use_analog = bool(test and test["count"] >= 80 and test["skill"] > 0.0)
    served = analog if use_analog else baseline

    mode_index = max(range(BIN_COUNT), key=lambda i: served[i])
    low, high = _bin_bounds(mode_index)
    midpoint = None if low is None or high is None else (low + high) / 2.0
    if midpoint is None:
        direction = "down" if high is not None and high <= 0 else "up"
    elif midpoint > 0.005:
        direction = "up"
    elif midpoint < -0.005:
        direction = "down"
    else:
        direction = "flat"

    top = sorted(range(BIN_COUNT), key=lambda i: served[i], reverse=True)[:3]
    return {
        "terminal_return_mode_label": _bin_label(mode_index),
        "terminal_return_mode_probability": round(100.0 * served[mode_index], 1),
        "terminal_return_mode_low": None if low is None else round(100.0 * low, 1),
        "terminal_return_mode_high": None if high is None else round(100.0 * high, 1),
        "terminal_return_mode_midpoint": None if midpoint is None else round(100.0 * midpoint, 1),
        "terminal_return_mode_direction": direction,
        "terminal_return_bin_width_percent": int(round(BIN_WIDTH * 100)),
        "terminal_return_selection": "analog" if use_analog else "baseline",
        "terminal_return_sample_size": sample_size,
        "terminal_return_effective_sample": round(effective_n, 1),
        "terminal_return_baseline_sample_size": len(records),
        "terminal_return_validation": test,
        "terminal_return_tuning": tune,
        "terminal_return_selected_k": k,
        "terminal_return_method": METHOD,
        "terminal_return_top3": [
            {"label": _bin_label(i), "probability": round(100.0 * served[i], 1)}
            for i in top
        ],
    }
