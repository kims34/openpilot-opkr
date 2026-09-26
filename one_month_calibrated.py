"""Conservative blended 21-session probability models.

The existing one-month models make a hard choice between the unconditional
historical baseline and a historical-analogue estimate. This module replaces
that discontinuous choice with a small, pre-declared blend grid. The blend and
analogue-neighbour count are tuned only on an earlier chronological slice and
are allowed into production only when they beat the baseline on the untouched
test slice *and* on both halves of that test slice.

No future labels are used in feature selection, tuning, validation or live
inference. If the guardrail fails, the served probability is the baseline.
"""
import math

import one_month_distribution as distribution
import one_month_probability as barrier

BLEND_WEIGHTS = (0.0, 0.25, 0.50, 0.75, 1.0)
MIN_TEST_COUNT = 80
MIN_HALF_COUNT = 30
BARRIER_METHOD = "validated-historical-analogs-barrier-touch-v3-blended"
DISTRIBUTION_METHOD = "validated-historical-analogs-terminal-return-v2-blended"
SIX_METHOD = "validated-historical-analogs-terminal-return-six-bins-v2-blended"


def _blend(base, analogue, weight):
    return (1.0 - weight) * base + weight * analogue


def _selection(weight, passed):
    if not passed or weight <= 0.0:
        return "baseline"
    if weight >= 0.999:
        return "analog"
    # Keep the legacy Android parser compatible while exposing the exact blend
    # weight in separate payload fields. The UI already describes the estimate
    # as a validated combination of similar regimes and the long-run baseline.
    return "analog"


def _validation_targets(prices_len, records, min_feature_index, horizon, validation_days, tune_fraction):
    eligible = [
        r[0]
        for r in records
        if r[0] >= max(min_feature_index + 300 + horizon, prices_len - validation_days - horizon)
    ]
    if len(eligible) < 120:
        return [], []
    split = max(60, int(len(eligible) * tune_fraction))
    return eligible[:split], eligible[split:]


def _score_binary_grid(prices, records, k, outcome_pos, targets):
    record_by_index = {r[0]: r for r in records}
    sums = {w: [0.0, 0.0, 0] for w in BLEND_WEIGHTS}
    for t in targets:
        training = [r for r in records if r[0] <= t - barrier.HORIZON - 1]
        if len(training) < 300:
            continue
        actual = record_by_index.get(t)
        if actual is None:
            continue
        base = barrier._baseline(training, outcome_pos)
        analogue, _, _ = barrier._analog_probability(barrier._features(prices, t), training, k, outcome_pos)
        y = actual[outcome_pos]
        base_loss = (base - y) ** 2
        for weight in BLEND_WEIGHTS:
            pred = _blend(base, analogue, weight)
            slot = sums[weight]
            slot[0] += (pred - y) ** 2
            slot[1] += base_loss
            slot[2] += 1
    out = {}
    for weight, (model_sum, base_sum, count) in sums.items():
        if not count:
            continue
        model_brier = model_sum / count
        baseline_brier = base_sum / count
        skill = (1.0 - model_brier / baseline_brier) * 100.0 if baseline_brier > 0 else 0.0
        out[weight] = {
            "count": count,
            "model_brier": model_brier,
            "baseline_brier": baseline_brier,
            "skill": skill,
        }
    return out


def _score_multiclass_grid(prices, records, k, targets, six=False):
    record_by_index = {r[0]: r for r in records}
    sums = {w: [0.0, 0.0, 0] for w in BLEND_WEIGHTS}
    for t in targets:
        training = [r for r in records if r[0] <= t - distribution.HORIZON - 1]
        if len(training) < 300:
            continue
        actual = record_by_index.get(t)
        if actual is None:
            continue
        features = barrier._features(prices, t)
        if six:
            base = distribution._six_baseline_distribution(training)
            analogue, _, _ = distribution._six_analog_distribution(features, training, k)
            actual_index = distribution._six_class_index(actual[3])
        else:
            base = distribution._baseline_distribution(training)
            analogue, _, _ = distribution._analog_distribution(features, training, k)
            actual_index = actual[2]
        base_loss = distribution._multiclass_brier(base, actual_index)
        for weight in BLEND_WEIGHTS:
            pred = [_blend(b, a, weight) for b, a in zip(base, analogue)]
            slot = sums[weight]
            slot[0] += distribution._multiclass_brier(pred, actual_index)
            slot[1] += base_loss
            slot[2] += 1
    out = {}
    for weight, (model_sum, base_sum, count) in sums.items():
        if not count:
            continue
        model_brier = model_sum / count
        baseline_brier = base_sum / count
        skill = (1.0 - model_brier / baseline_brier) * 100.0 if baseline_brier > 0 else 0.0
        out[weight] = {
            "count": count,
            "model_brier": model_brier,
            "baseline_brier": baseline_brier,
            "skill": skill,
        }
    return out


def _half_guardrail(score_fn, prices, records, k, weight, test_targets, *score_args):
    if len(test_targets) < 2:
        return None, None, False
    split = len(test_targets) // 2
    first_targets = test_targets[:split]
    second_targets = test_targets[split:]
    first = score_fn(prices, records, k, *score_args, first_targets).get(weight)
    second = score_fn(prices, records, k, *score_args, second_targets).get(weight)
    passed = bool(
        first and second
        and first["count"] >= MIN_HALF_COUNT
        and second["count"] >= MIN_HALF_COUNT
        and first["skill"] > 0.0
        and second["skill"] > 0.0
    )
    return first, second, passed


def _choose_binary(prices, records, outcome_pos):
    tune_targets, test_targets = _validation_targets(
        len(prices), records, barrier.MIN_FEATURE_INDEX, barrier.HORIZON,
        barrier.VALIDATION_DAYS, barrier.TUNE_FRACTION,
    )
    if not tune_targets or not test_targets:
        return barrier.K_CANDIDATES[1], 0.0, None, None, None, None, False

    candidates = []
    for k in barrier.K_CANDIDATES:
        grid = _score_binary_grid(prices, records, k, outcome_pos, tune_targets)
        for weight, result in grid.items():
            candidates.append((result["model_brier"], weight, k, result))
    if not candidates:
        return barrier.K_CANDIDATES[1], 0.0, None, None, None, None, False

    # On equal loss prefer the more conservative (smaller analogue weight).
    _, weight, k, tune = min(candidates, key=lambda x: (x[0], x[1], x[2]))
    test = _score_binary_grid(prices, records, k, outcome_pos, test_targets).get(weight)
    first, second, halves_pass = _half_guardrail(
        _score_binary_grid, prices, records, k, weight, test_targets, outcome_pos,
    )
    passed = bool(
        weight > 0.0
        and test and test["count"] >= MIN_TEST_COUNT
        and test["skill"] > 0.0
        and halves_pass
    )
    return k, weight if passed else 0.0, tune, test, first, second, passed


def _score_multiclass_adapter(prices, records, k, six, targets):
    return _score_multiclass_grid(prices, records, k, targets, six=six)


def _choose_multiclass(prices, records, six=False):
    tune_targets, test_targets = _validation_targets(
        len(prices), records, distribution.MIN_FEATURE_INDEX, distribution.HORIZON,
        distribution.VALIDATION_DAYS, distribution.TUNE_FRACTION,
    )
    if not tune_targets or not test_targets:
        return distribution.K_CANDIDATES[1], 0.0, None, None, None, None, False

    candidates = []
    for k in distribution.K_CANDIDATES:
        grid = _score_multiclass_grid(prices, records, k, tune_targets, six=six)
        for weight, result in grid.items():
            candidates.append((result["model_brier"], weight, k, result))
    if not candidates:
        return distribution.K_CANDIDATES[1], 0.0, None, None, None, None, False

    _, weight, k, tune = min(candidates, key=lambda x: (x[0], x[1], x[2]))
    test = _score_multiclass_grid(prices, records, k, test_targets, six=six).get(weight)
    first, second, halves_pass = _half_guardrail(
        _score_multiclass_adapter, prices, records, k, weight, test_targets, six,
    )
    passed = bool(
        weight > 0.0
        and test and test["count"] >= MIN_TEST_COUNT
        and test["skill"] > 0.0
        and halves_pass
    )
    return k, weight if passed else 0.0, tune, test, first, second, passed


def estimate_probability(rows, ohlc_rows=None):
    clean = [(str(d), float(p)) for d, p in rows if float(p) > 0]
    if len(clean) < barrier.MIN_HISTORY:
        raise ValueError("insufficient history for one-month probability")
    dates = [d for d, _ in clean]
    prices = [p for _, p in clean]

    if ohlc_rows and len(ohlc_rows) == len(clean):
        high_map = {str(d): float(h) for d, h, l, c in ohlc_rows}
        low_map = {str(d): float(l) for d, h, l, c in ohlc_rows}
        highs = [max(prices[i], high_map.get(dates[i], prices[i])) for i in range(len(prices))]
        lows = [min(prices[i], low_map.get(dates[i], prices[i])) for i in range(len(prices))]
        price_basis = "daily_high_low"
    else:
        highs = list(prices)
        lows = list(prices)
        price_basis = "daily_close"

    records = barrier._records(prices, highs, lows)
    if len(records) < 300:
        raise ValueError("insufficient labelled monthly windows")
    current_features = barrier._features(prices, len(prices) - 1)
    base_up = barrier._baseline(records, 2)
    base_down = barrier._baseline(records, 3)

    ku, wu, tune_up, test_up, first_up, second_up, pass_up = _choose_binary(prices, records, 2)
    kd, wd, tune_down, test_down, first_down, second_down, pass_down = _choose_binary(prices, records, 3)
    analog_up, sample_up, eff_up = barrier._analog_probability(current_features, records, ku, 2)
    analog_down, sample_down, eff_down = barrier._analog_probability(current_features, records, kd, 3)
    served_up = _blend(base_up, analog_up, wu) if pass_up else base_up
    served_down = _blend(base_down, analog_down, wd) if pass_down else base_down

    f = current_features
    return {
        "horizon_sessions": barrier.HORIZON,
        "threshold_percent": int(barrier.THRESHOLD * 100),
        "price_basis": price_basis,
        "up_10_probability": round(100.0 * served_up, 1),
        "down_10_probability": round(100.0 * served_down, 1),
        "analog_up_10_probability": round(100.0 * analog_up, 1),
        "analog_down_10_probability": round(100.0 * analog_down, 1),
        "baseline_sample_size": len(records),
        "baseline_up_10_probability": round(100.0 * base_up, 1),
        "baseline_down_10_probability": round(100.0 * base_down, 1),
        "sample_size": min(sample_up, sample_down),
        "effective_sample_up": round(eff_up, 1),
        "effective_sample_down": round(eff_down, 1),
        "selected_k_up": ku,
        "selected_k_down": kd,
        "blend_weight_up": round(wu, 2),
        "blend_weight_down": round(wd, 2),
        "validation_up": test_up,
        "validation_down": test_down,
        "validation_up_first_half": first_up,
        "validation_up_second_half": second_up,
        "validation_down_first_half": first_down,
        "validation_down_second_half": second_down,
        "tuning_up": tune_up,
        "tuning_down": tune_down,
        "selection_up": _selection(wu, pass_up),
        "selection_down": _selection(wd, pass_down),
        "trend_regime": "up" if f[1] >= 0 else "down",
        "volatility_regime": "high" if f[3] >= 0.20 else "low",
        "annualized_volatility": round(100.0 * f[3], 1),
        "features": {
            "return_5d": round(100.0 * f[0], 2),
            "return_21d": round(100.0 * f[1], 2),
            "return_63d": round(100.0 * f[2], 2),
            "drawdown_252d": round(100.0 * f[4], 2),
            "ma50_gap": round(100.0 * f[5], 2),
            "ma200_gap": round(100.0 * f[6], 2),
        },
        "prior_strength": int(barrier.PRIOR_STRENGTH),
        "method": BARRIER_METHOD,
        "as_of": clean[-1][0],
    }


def estimate_distribution(rows):
    clean = [(str(d), float(p)) for d, p in rows if float(p) > 0]
    if len(clean) < barrier.MIN_HISTORY:
        raise ValueError("insufficient history for terminal-return distribution")
    prices = [p for _, p in clean]
    records = distribution._records(prices)
    if len(records) < 300:
        raise ValueError("insufficient labelled monthly return windows")
    current_features = barrier._features(prices, len(prices) - 1)

    # Fine 2 percentage-point distribution retained for backwards-compatible
    # metadata/top-3 consumers.
    base = distribution._baseline_distribution(records)
    k, weight, tune, test, first, second, passed = _choose_multiclass(prices, records, six=False)
    analogue, sample_size, effective_n = distribution._analog_distribution(current_features, records, k)
    served = [_blend(b, a, weight) for b, a in zip(base, analogue)] if passed else base
    mode_index = max(range(distribution.BIN_COUNT), key=lambda i: served[i])
    low, high = distribution._bin_bounds(mode_index)
    midpoint = None if low is None or high is None else (low + high) / 2.0
    if midpoint is None:
        direction = "down" if high is not None and high <= 0 else "up"
    elif midpoint > 0.005:
        direction = "up"
    elif midpoint < -0.005:
        direction = "down"
    else:
        direction = "flat"
    top = sorted(range(distribution.BIN_COUNT), key=lambda i: served[i], reverse=True)[:3]

    six_base = distribution._six_baseline_distribution(records)
    sk, sw, six_tune, six_test, six_first, six_second, six_pass = _choose_multiclass(prices, records, six=True)
    six_analogue, six_sample_size, six_effective_n = distribution._six_analog_distribution(current_features, records, sk)
    six_served = [_blend(b, a, sw) for b, a in zip(six_base, six_analogue)] if six_pass else six_base
    six_percentages = distribution._round_percentages_to_100(six_served)

    return {
        "terminal_return_mode_label": distribution._bin_label(mode_index),
        "terminal_return_mode_probability": round(100.0 * served[mode_index], 1),
        "terminal_return_mode_low": None if low is None else round(100.0 * low, 1),
        "terminal_return_mode_high": None if high is None else round(100.0 * high, 1),
        "terminal_return_mode_midpoint": None if midpoint is None else round(100.0 * midpoint, 1),
        "terminal_return_mode_direction": direction,
        "terminal_return_bin_width_percent": int(round(distribution.BIN_WIDTH * 100)),
        "terminal_return_selection": _selection(weight, passed),
        "terminal_return_blend_weight": round(weight, 2),
        "terminal_return_sample_size": sample_size,
        "terminal_return_effective_sample": round(effective_n, 1),
        "terminal_return_baseline_sample_size": len(records),
        "terminal_return_validation": test,
        "terminal_return_validation_first_half": first,
        "terminal_return_validation_second_half": second,
        "terminal_return_tuning": tune,
        "terminal_return_selected_k": k,
        "terminal_return_method": DISTRIBUTION_METHOD,
        "terminal_return_top3": [
            {"label": distribution._bin_label(i), "probability": round(100.0 * served[i], 1)}
            for i in top
        ],
        "terminal_return_six_bins": [
            {
                "key": distribution.SIX_BUCKETS[i][0],
                "label": distribution.SIX_BUCKETS[i][1],
                "probability": six_percentages[i],
            }
            for i in range(distribution.SIX_COUNT)
        ],
        "terminal_return_six_total_probability": round(sum(six_percentages), 1),
        "terminal_return_six_selection": _selection(sw, six_pass),
        "terminal_return_six_blend_weight": round(sw, 2),
        "terminal_return_six_sample_size": six_sample_size,
        "terminal_return_six_effective_sample": round(six_effective_n, 1),
        "terminal_return_six_baseline_sample_size": len(records),
        "terminal_return_six_validation": six_test,
        "terminal_return_six_validation_first_half": six_first,
        "terminal_return_six_validation_second_half": six_second,
        "terminal_return_six_tuning": six_tune,
        "terminal_return_six_selected_k": sk,
        "terminal_return_six_method": SIX_METHOD,
    }
