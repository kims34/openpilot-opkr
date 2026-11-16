"""Isolated 21-session +/-10% barrier-touch research. NEVER a live serving model.

Scores both signs independently; both events can occur in one path.
Exact OHLC coverage is mandatory: missing highs/lows are NEVER imputed with closes.
Public backfilled implied-vol history is research-only, not original PIT proof.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from typing import Mapping

import numpy as np

HORIZON = 21
THRESHOLD = 0.10
HISTORY = 252
BLOCK = 5
PATHS = 1024
DEV_DAYS = 252
TEST_DAYS = 126
EMBARGO = 21
WEIGHTS = (0.25, 0.5, 0.75, 1.0)
EXPECTED_MACRO = {"SPY": "VIX", "QQQ": "VXN"}


class SourceQualityError(ValueError):
    pass


def _number(value, label):
    if isinstance(value, bool):
        raise SourceQualityError(label + ": nonnumeric boolean")
    try:
        v = float(value)
    except (ValueError, TypeError) as e:
        raise SourceQualityError(label + ": not numeric") from e
    if not math.isfinite(v):
        raise SourceQualityError(label + ": non-finite value")
    return v


def validate_ohlc(close_rows, ohlc_rows):
    """One-to-one sessions and unadjusted OHLC consistency; never close-impute."""
    if not close_rows or not ohlc_rows or len(close_rows) != len(ohlc_rows):
        raise SourceQualityError("missing OHLC session(s): refuse close substitution")
    dates, prices, highs, lows = [], [], [], []
    for i, (ref, bar) in enumerate(zip(close_rows, ohlc_rows)):
        if len(ref) != 2 or len(bar) != 4:
            raise SourceQualityError("invalid OHLC schema")
        d, anchor = str(ref[0]), _number(ref[1], "anchor")
        bd, high, low, vendor_close = str(bar[0]), *(
            _number(v, "OHLC") for v in bar[1:]
        )
        try:
            date.fromisoformat(d)
            date.fromisoformat(bd)
        except ValueError as e:
            raise SourceQualityError("invalid session date") from e
        if d != bd or (i and d <= dates[-1]):
            raise SourceQualityError("misordered, missing or duplicate OHLC date")
        if anchor <= 0 or vendor_close <= 0 or low <= 0 or high < low:
            raise SourceQualityError("invalid OHLC price")
        if abs(vendor_close / anchor - 1.0) > 0.001:
            raise SourceQualityError("close data not aligned (split/adjustment?)")
        if high + 1e-8 < max(anchor, vendor_close) or low - 1e-8 > min(anchor, vendor_close):
            raise SourceQualityError("inconsistent high/low vs close")
        dates.append(d)
        prices.append(anchor)
        highs.append(high)
        lows.append(low)
    return dates, np.asarray(prices), np.asarray(highs), np.asarray(lows)


def touch_label(prices, highs, lows, t):
    if t + HORIZON >= len(prices):
        raise SourceQualityError("barrier label needs 21 completed future sessions")
    anchor = prices[t]
    return np.array([
        float(np.any(highs[t + 1:t + HORIZON + 1] >= anchor * (1 + THRESHOLD))),
        float(np.any(lows[t + 1:t + HORIZON + 1] <= anchor * (1 - THRESHOLD))),
    ])


def asof_baseline(prices, highs, lows, t):
    """Fully matured past-event frequencies, not the deployed analogue model."""
    eligible = range(HISTORY, t - HORIZON + 1)
    if t - HORIZON + 1 - HISTORY < HISTORY:
        raise SourceQualityError("too few known past 21-day outcomes")
    labels = np.stack([touch_label(prices, highs, lows, i) for i in eligible])
    return (labels.sum(axis=0) + 2.0) / (len(labels) + 4.0)


def simulate_touch(prices, t, implied_vol_pct, seed, paths=PATHS):
    """Circular block-resampled empirical shocks, scaled to quoted annual IV.

    No future returns, and no artificial assertion that IV equals realized vol.
    Monte Carlo approximates paths, not a fitted predictive probability.
    """
    iv = _number(implied_vol_pct, "implied volatility")
    if not 5 <= iv <= 150:
        raise SourceQualityError("invalid implied-vol annual percentage")
    if t < HISTORY:
        raise SourceQualityError("insufficient prior log-return history")
    rets = np.diff(np.log(prices[t - HISTORY:t + 1]))
    sd = float(np.std(rets, ddof=1))
    if not np.isfinite(sd) or sd < 1e-6:
        raise SourceQualityError("unusable historical volatility")
    standardized = (rets - rets.mean()) / sd
    rng = np.random.default_rng(int(seed))
    # Resample 5-day contiguous blocks, preserving some return clustering.
    block_starts = rng.integers(0, len(standardized) - BLOCK + 1,
                                size=(paths, math.ceil(HORIZON / BLOCK)))
    offsets = np.arange(BLOCK)
    shocks = standardized[block_starts[:, :, None] + offsets].reshape(paths, -1)[:, :HORIZON]
    annual_iv = iv / 100.0
    daily_sigma = annual_iv / np.sqrt(252.0)
    # Return-location shrinkage is frozen, not tuned on holdout.
    drift = float(np.clip(rets.mean() * 0.25, -0.002, 0.002))
    paths_log_return = np.cumsum(drift + daily_sigma * shocks, axis=1)
    up = (paths_log_return >= math.log(1 + THRESHOLD)).any(axis=1)
    down = (paths_log_return <= math.log(1 - THRESHOLD)).any(axis=1)
    return np.array([float(np.mean(up)), float(np.mean(down))])


def _brier(pred, actual):
    return np.mean((np.asarray(pred) - np.asarray(actual)) ** 2, axis=0)


def _gains(baseline, candidate, outcome):
    a = _brier(baseline, outcome)
    b = _brier(candidate, outcome)
    return {"baseline_up": float(a[0]), "baseline_down": float(a[1]),
            "candidate_up": float(b[0]), "candidate_down": float(b[1]),
            "gain_up": float(a[0]-b[0]), "gain_down": float(a[1]-b[1]),
            "gain_combined": float(np.mean(a - b))}


def evaluate(symbol, close_rows, ohlc_rows, implied_by_day: Mapping,
             *, paths=PATHS):
    """Select on development only, reserve test with 21-session label embargo."""
    if symbol not in EXPECTED_MACRO:
        raise SourceQualityError("SPY/VIX or QQQ/VXN only")
    dates, prices, highs, lows = validate_ohlc(close_rows, ohlc_rows)
    n = len(dates)
    final_target = n - HORIZON
    test_start = final_target - TEST_DAYS
    dev_end = test_start - EMBARGO
    dev_start = dev_end - DEV_DAYS
    if dev_start < HISTORY + HORIZON + HISTORY or paths < 32:
        raise SourceQualityError("insufficient independent temporal history")
    targets = list(range(dev_start, dev_end)) + list(range(test_start, final_target))
    if any(dates[t] not in implied_by_day for t in targets):
        raise SourceQualityError("missing as-of implied-vol session: reject evaluation")
    meta = {"iv_symbol": EXPECTED_MACRO[symbol], "symbol": symbol,
            "train_history": HISTORY, "horizon": HORIZON,
            "development_n": DEV_DAYS, "reserved_test_n": TEST_DAYS,
            "embargo_sessions": EMBARGO, "source_quality": "PUBLIC_BACKFILL_NO_PIT_PROOF",
            "independent_as_published_iv_verified": False,
            "reference": "causal-matured-rolling-frequency-NOT-deployed-v3.3",
            "production_admission": "BLOCKED", "app_changed": False,
            "order_authorization": False}
    # Precompute each fully matured label once; prefixes never incorporate a
    # label beyond t-HORIZON for any forecast t.
    labels = np.stack([touch_label(prices, highs, lows, i) for i in range(final_target)])
    label_prefix = np.concatenate((np.zeros((1, 2)), np.cumsum(labels, axis=0)), axis=0)
    base, mc, actual = [], [], []
    for t in targets:
        known_end = t - HORIZON + 1
        known_count = known_end - HISTORY
        if known_count < HISTORY:
            raise SourceQualityError("too few matured labels")
        actual.append(labels[t])
        base.append((label_prefix[known_end] - label_prefix[HISTORY] + 2.0)
                    / (known_count + 4.0))
        mc.append(simulate_touch(prices, t, implied_by_day[dates[t]],
                                 seed=20261116 + t, paths=paths))
    base, mc, actual = np.array(base), np.array(mc), np.array(actual)
    if not all(np.isfinite(v).all() for v in (base, mc, actual)):
        raise SourceQualityError("invalid predicted probability or labels")
    dev_base, test_base = base[:DEV_DAYS], base[DEV_DAYS:]
    dev_mc, test_mc = mc[:DEV_DAYS], mc[DEV_DAYS:]
    dev_y, test_y = actual[:DEV_DAYS], actual[DEV_DAYS:]
    candidates = []
    for w in WEIGHTS:
        forecast = (1.0 - w) * dev_base + w * dev_mc
        whole = _gains(dev_base, forecast, dev_y)
        first = _gains(dev_base[:DEV_DAYS // 2], forecast[:DEV_DAYS // 2], dev_y[:DEV_DAYS // 2])
        second = _gains(dev_base[DEV_DAYS // 2:], forecast[DEV_DAYS // 2:], dev_y[DEV_DAYS // 2:])
        candidates.append({"weight": w, "dev": whole, "first": first, "second": second})
    qualified = [v for v in candidates if v["dev"]["gain_combined"] > 0.000001
                 and v["dev"]["gain_up"] >= 0.0 and v["dev"]["gain_down"] >= 0.0
                 and v["first"]["gain_combined"] > 0.0 and v["second"]["gain_combined"] > 0.0]
    qualified.sort(key=lambda x: (-x["dev"]["gain_combined"], x["weight"]))
    result = {**meta, "development": candidates, "selected_weight": None,
              "reserved_test_scored": False}
    if not qualified:
        result["decision"] = "NO_DEVELOPMENT_WINNER;_HOLDOUT_NOT_TOUCHED"
        return result
    best = qualified[0]
    weight = best["weight"]
    challenger = (1.0 - weight) * test_base + weight * test_mc
    score = _gains(test_base, challenger, test_y)
    # Dependence-aware uncertainty: 21-session moving-block bootstrap.
    daily_diff = ((test_base - test_y) ** 2 - (challenger - test_y) ** 2).mean(axis=1)
    rng = np.random.default_rng(20261116)
    gains = []
    for _ in range(600):
        blocks = rng.integers(0, TEST_DAYS - HORIZON + 1,
                              size=math.ceil(TEST_DAYS / HORIZON))
        ids = (blocks[:, None] + np.arange(HORIZON)).reshape(-1)[:TEST_DAYS]
        gains.append(float(np.mean(daily_diff[ids])))
    lo, hi = np.quantile(gains, (0.025, 0.975))
    passed = (score["gain_combined"] > 0.0
              and score["gain_up"] > 0.0 and score["gain_down"] > 0.0
              and float(lo) > 0.0)
    result.update(
        selected_weight=weight, reserved_test_scored=True,
        reserved_test={**score, "block_bootstrap_ci95_gain": [float(lo), float(hi)],
                       "improved_both_sides": score["gain_up"] > 0 and score["gain_down"] > 0,
                       "research_gate_passed": bool(passed)},
        decision=("RESEARCH_ONLY_INDEPENDENT_PIT_AND_PROSPECTIVE_REQUIRED"
                  if passed else "HOLDOUT_FAILED_NO_PROMOTION"))
    return result


def digest(records):
    return hashlib.sha256(json.dumps(records, sort_keys=True,
                              ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
