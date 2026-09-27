"""Prospective safety gate for promoted probability overlays.

Historical holdout validation remains the promotion prerequisite. This module
adds a second, strictly prospective check after deployment. It compares paired
Brier losses from the candidate and its exact reference model. A promoted
candidate is only auto-disabled when live evidence is sufficiently strong that
the whole 95% CI for mean Brier gain is below zero.

Positive gain = candidate has lower (better) Brier loss.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

MIN_LIVE_N = 30
Z95 = 1.959963984540054


def evaluate(scores: Iterable[Sequence[float]], min_n: int = MIN_LIVE_N) -> dict:
    rows = []
    for row in scores:
        if len(row) < 3:
            continue
        try:
            candidate, previous, outcome = map(float, row[:3])
        except (TypeError, ValueError):
            continue
        if not all(math.isfinite(v) for v in (candidate, previous, outcome)):
            continue
        if not (0.0 <= candidate <= 1.0 and 0.0 <= previous <= 1.0 and outcome in (0.0, 1.0)):
            continue
        rows.append((candidate, previous, outcome))

    n = len(rows)
    if not rows:
        return {
            "status": "historical_only",
            "n": 0,
            "min_n": int(min_n),
            "candidate_brier": None,
            "previous_brier": None,
            "mean_gain": None,
            "ci_low": None,
            "ci_high": None,
            "fallback": False,
        }

    candidate_brier = sum((p - y) ** 2 for p, _, y in rows) / n
    previous_brier = sum((b - y) ** 2 for _, b, y in rows) / n
    gains = [(b - y) ** 2 - (p - y) ** 2 for p, b, y in rows]
    mean_gain = sum(gains) / n

    if n > 1:
        variance = sum((g - mean_gain) ** 2 for g in gains) / (n - 1)
        se = math.sqrt(max(variance, 0.0) / n)
    else:
        se = float("inf")

    if math.isfinite(se):
        ci_low = mean_gain - Z95 * se
        ci_high = mean_gain + Z95 * se
    else:
        ci_low = None
        ci_high = None

    if n < int(min_n):
        status = "historical_only"
        fallback = False
    elif ci_high is not None and ci_high < 0.0:
        status = "fallback_previous"
        fallback = True
    elif ci_low is not None and ci_low > 0.0:
        status = "live_confirmed"
        fallback = False
    else:
        status = "live_inconclusive"
        fallback = False

    return {
        "status": status,
        "n": n,
        "min_n": int(min_n),
        "candidate_brier": candidate_brier,
        "previous_brier": previous_brier,
        "mean_gain": mean_gain,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "fallback": fallback,
    }


def apply(result: dict, gate: dict, previous_key: str) -> dict:
    """Expose candidate diagnostics and switch only the served probability.

    The caller must record the raw candidate before calling this function so a
    fallback candidate keeps accumulating prospective evidence in shadow mode.
    """
    out = result
    candidate = out.get("probability")
    previous = out.get(previous_key)
    out["candidate_probability"] = candidate
    out["live_gate_status"] = gate.get("status")
    out["live_gate_n"] = gate.get("n", 0)
    out["live_gate_min_n"] = gate.get("min_n", MIN_LIVE_N)
    out["live_gate_gain"] = gate.get("mean_gain")
    out["live_gate_ci_low"] = gate.get("ci_low")
    out["live_gate_ci_high"] = gate.get("ci_high")
    out["live_candidate_brier"] = gate.get("candidate_brier")
    out["live_previous_brier"] = gate.get("previous_brier")

    if gate.get("fallback") and previous is not None:
        out["probability"] = previous
        out["served_probability"] = previous
        out["served_from"] = "previous_stage"
        out["status"] = str(out.get("status") or "") + " · 실전 성능 저하 감지, 이전 단계 확률 사용"
    else:
        out["served_probability"] = candidate
        out["served_from"] = "candidate"
    return out
