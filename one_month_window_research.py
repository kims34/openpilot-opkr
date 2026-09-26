"""Offline research: can a longer history window improve the six-bin model?

This never changes production probabilities. It compares a 10-year-like
2520-session reference with 5y, 15y and all-history candidates. Window, k and
blend weight are chosen only on the earlier tuning slice. Promotion is reported
only if the chosen candidate beats the 10y reference on the untouched test
slice AND both chronological halves of that test slice.
"""
import json
import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import one_month_calibrated as calibrated
import one_month_distribution as dist
import one_month_probability as month

SYMBOLS = ("SPY", "QQQ", "SCHD")
WINDOWS = (1260, 2520, 3780, None)
REFERENCE_WINDOW = 2520
NY = ZoneInfo("America/New_York")


def fetch_max_rows(symbol):
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range": "max", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert/monthly-window-research"},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json().get("chart", {})
    if payload.get("error"):
        raise RuntimeError(f"provider error: {payload['error']}")
    result = (payload.get("result") or [None])[0]
    if not result or result.get("meta", {}).get("symbol") != symbol:
        raise RuntimeError("symbol mismatch")
    timestamps = result.get("timestamp") or []
    closes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    by_day = {}
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        px = float(close)
        if not math.isfinite(px) or px <= 0:
            continue
        day = datetime.fromtimestamp(int(ts), timezone.utc).astimezone(NY).date().isoformat()
        by_day[day] = px
    rows = sorted(by_day.items())
    if len(rows) < 1100:
        raise RuntimeError("history too short")
    jumps = [abs(rows[i][1] / rows[i - 1][1] - 1.0) for i in range(1, len(rows))]
    max_jump = max(jumps) if jumps else 0.0
    if max_jump > 0.40:
        raise RuntimeError(f"unadjusted/discontinuous history max_jump={max_jump:.3f}")
    return rows, max_jump


def training_slice(records, target, window):
    end = target - dist.HORIZON - 1
    start = -10**18 if window is None else target - int(window)
    return [r for r in records if start <= r[0] <= end]


def score_grid(prices, records, window, k, targets):
    record_by_index = {r[0]: r for r in records}
    sums = {w: [0.0, 0.0, 0] for w in calibrated.BLEND_WEIGHTS}
    for target in targets:
        training = training_slice(records, target, window)
        if len(training) < 300:
            continue
        actual = record_by_index.get(target)
        if actual is None:
            continue
        baseline = dist._six_baseline_distribution(training)
        analogue, _, _ = dist._six_analog_distribution(month._features(prices, target), training, k)
        actual_index = dist._six_class_index(actual[3])
        base_loss = dist._multiclass_brier(baseline, actual_index)
        for weight in calibrated.BLEND_WEIGHTS:
            pred = [calibrated._blend(b, a, weight) for b, a in zip(baseline, analogue)]
            slot = sums[weight]
            slot[0] += dist._multiclass_brier(pred, actual_index)
            slot[1] += base_loss
            slot[2] += 1
    out = {}
    for weight, (model_sum, base_sum, count) in sums.items():
        if count:
            mb = model_sum / count
            bb = base_sum / count
            out[weight] = {
                "count": count,
                "model_brier": mb,
                "baseline_brier": bb,
                "skill": (1.0 - mb / bb) * 100.0 if bb > 0 else 0.0,
            }
    return out


def choose_candidate(prices, records, targets, windows):
    candidates = []
    for window in windows:
        for k in dist.K_CANDIDATES:
            grid = score_grid(prices, records, window, k, targets)
            for weight, result in grid.items():
                # Conservative tie-breaking: less analogue weight, then shorter
                # finite history before all-history.
                window_order = 10**9 if window is None else window
                candidates.append((result["model_brier"], weight, window_order, k, window, result))
    if not candidates:
        raise RuntimeError("no candidate")
    _, weight, _, k, window, tune = min(candidates, key=lambda x: (x[0], x[1], x[2], x[3]))
    return {"window": window, "k": k, "weight": weight, "tune": tune}


def evaluate_candidate(prices, records, candidate, targets):
    return score_grid(prices, records, candidate["window"], candidate["k"], targets).get(candidate["weight"])


def compact(metric):
    if not metric:
        return None
    return {
        "n": metric["count"],
        "brier": round(metric["model_brier"], 6),
        "baseline": round(metric["baseline_brier"], 6),
        "skill": round(metric["skill"], 3),
    }


def research_symbol(symbol):
    rows, max_jump = fetch_max_rows(symbol)
    prices = [p for _, p in rows]
    records = dist._records(prices)
    eligible = [
        r[0] for r in records
        if r[0] >= max(dist.MIN_FEATURE_INDEX + 300 + dist.HORIZON, len(prices) - dist.VALIDATION_DAYS - dist.HORIZON)
    ]
    if len(eligible) < 120:
        raise RuntimeError("not enough validation targets")
    split = max(60, int(len(eligible) * dist.TUNE_FRACTION))
    tune_targets, test_targets = eligible[:split], eligible[split:]
    half = len(test_targets) // 2
    first_targets, second_targets = test_targets[:half], test_targets[half:]

    chosen = choose_candidate(prices, records, tune_targets, WINDOWS)
    reference = choose_candidate(prices, records, tune_targets, (REFERENCE_WINDOW,))

    chosen_test = evaluate_candidate(prices, records, chosen, test_targets)
    reference_test = evaluate_candidate(prices, records, reference, test_targets)
    chosen_first = evaluate_candidate(prices, records, chosen, first_targets)
    reference_first = evaluate_candidate(prices, records, reference, first_targets)
    chosen_second = evaluate_candidate(prices, records, chosen, second_targets)
    reference_second = evaluate_candidate(prices, records, reference, second_targets)

    def better(a, b):
        return bool(a and b and a["model_brier"] < b["model_brier"])

    relative_gain = None
    if chosen_test and reference_test and reference_test["model_brier"] > 0:
        relative_gain = (1.0 - chosen_test["model_brier"] / reference_test["model_brier"]) * 100.0
    promote = bool(
        chosen["window"] != REFERENCE_WINDOW
        and relative_gain is not None and relative_gain >= 0.5
        and better(chosen_test, reference_test)
        and better(chosen_first, reference_first)
        and better(chosen_second, reference_second)
    )
    return {
        "symbol": symbol,
        "points": len(rows),
        "first_date": rows[0][0],
        "last_date": rows[-1][0],
        "max_abs_daily_jump_pct": round(max_jump * 100.0, 2),
        "chosen": {"window": chosen["window"], "k": chosen["k"], "weight": chosen["weight"], "tune": compact(chosen["tune"]), "test": compact(chosen_test), "first_half": compact(chosen_first), "second_half": compact(chosen_second)},
        "reference_10y": {"window": reference["window"], "k": reference["k"], "weight": reference["weight"], "tune": compact(reference["tune"]), "test": compact(reference_test), "first_half": compact(reference_first), "second_half": compact(reference_second)},
        "relative_test_brier_gain_vs_10y_pct": None if relative_gain is None else round(relative_gain, 3),
        "promote_longer_window": promote,
    }


def main():
    results = []
    for symbol in SYMBOLS:
        try:
            item = research_symbol(symbol)
        except Exception as exc:
            item = {"symbol": symbol, "error": f"{type(exc).__name__}: {exc}"}
        results.append(item)
        print("MONTHLY_HISTORY_RESEARCH", json.dumps(item, ensure_ascii=False, sort_keys=True), flush=True)
    print("MONTHLY_HISTORY_RESEARCH_SUMMARY", json.dumps(results, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
