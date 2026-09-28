"""Prospective Brier safety gate for promoted probability overlays.

Historical holdout validation remains the first promotion prerequisite.  This
module adds a second, strictly prospective check after deployment.  It compares
paired Brier losses from the raw candidate and its exact reference probability.

Policy:
- Before MIN_LIVE_N scored forecasts, keep the historically validated candidate
  while collecting live evidence.
- From MIN_LIVE_N onward, keep the candidate only when the full 95% confidence
  interval for mean Brier gain is above zero.
- If live advantage is inconclusive or negative, serve the previous/reference
  probability.  The raw candidate must still be recorded before this gate so it
  continues accumulating evidence and can automatically recover later.

Positive gain = candidate has lower (better) Brier loss.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

MIN_LIVE_N = 30
Z95 = 1.959963984540054
SERVING_POLICY_VERSION = "prospective-brier-ci95-v1"


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
            "policy_version": SERVING_POLICY_VERSION,
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
    elif ci_low is not None and ci_low > 0.0:
        status = "live_confirmed"
        fallback = False
    elif ci_high is not None and ci_high < 0.0:
        status = "fallback_underperforming"
        fallback = True
    else:
        status = "fallback_inconclusive"
        fallback = True

    return {
        "policy_version": SERVING_POLICY_VERSION,
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
    """Expose diagnostics and switch only the served probability.

    The caller must record the raw candidate before calling this function.  This
    guarantees that a fallback candidate remains observable in shadow mode and
    can automatically return if later prospective evidence becomes convincing.
    """
    out = result
    candidate = out.get("probability")
    previous = out.get(previous_key)
    out["live_candidate_probability"] = candidate
    # Preserve any model-internal candidate field already present.
    if "candidate_probability" not in out:
        out["candidate_probability"] = candidate
    out["live_gate_policy_version"] = gate.get("policy_version", SERVING_POLICY_VERSION)
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
        status = str(out.get("status") or "").strip()
        note = "실전 Brier 우위 미확인 · 안전 확률 사용"
        out["status"] = f"{status} · {note}" if status else note
    else:
        out["served_probability"] = candidate
        out["served_from"] = "candidate"
    return out
