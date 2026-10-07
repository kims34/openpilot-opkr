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
from numbers import Real
from typing import Iterable, Sequence

MIN_LIVE_N = 30
Z95 = 1.959963984540054
SERVING_POLICY_VERSION = "prospective-brier-ci95-v1"


class ProbabilityLiveGateError(ValueError):
    pass


def _score_value(value, field):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ProbabilityLiveGateError(f"{field} must be an original finite number")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ProbabilityLiveGateError(f"{field} must be finite")
    return parsed


def _probability(value, field):
    parsed = _score_value(value, field)
    if not 0.0 <= parsed <= 1.0:
        raise ProbabilityLiveGateError(f"{field} must be between 0 and 1")
    return parsed


def evaluate(scores: Iterable[Sequence[float]], min_n: int = MIN_LIVE_N) -> dict:
    if type(min_n) is not int or min_n <= 0:
        raise ProbabilityLiveGateError("min_n must be an exact positive integer")
    if scores is None or isinstance(scores, (str, bytes)):
        raise ProbabilityLiveGateError("scores must be an iterable of 3-field rows")
    rows = []
    try:
        iterator = iter(scores)
    except TypeError:
        raise ProbabilityLiveGateError("scores must be an iterable of 3-field rows") from None
    for index, row in enumerate(iterator):
        if isinstance(row, (str, bytes)) or not isinstance(row, Sequence) or len(row) != 3:
            raise ProbabilityLiveGateError(f"score row {index} must contain exactly 3 fields")
        candidate = _probability(row[0], f"score row {index} candidate")
        previous = _probability(row[1], f"score row {index} previous")
        outcome = _score_value(row[2], f"score row {index} outcome")
        if outcome not in (0.0, 1.0):
            raise ProbabilityLiveGateError(f"score row {index} outcome must be 0 or 1")
        rows.append((candidate, previous, outcome))

    n = len(rows)
    if not rows:
        return {
            "policy_version": SERVING_POLICY_VERSION,
            "status": "historical_only",
            "n": 0,
            "min_n": min_n,
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

    if n < min_n:
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
        "min_n": min_n,
        "candidate_brier": candidate_brier,
        "previous_brier": previous_brier,
        "mean_gain": mean_gain,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "fallback": fallback,
        "score_rows_structurally_valid": True,
        "independent_live_provenance_verified": False,
        "status_scope": "PROSPECTIVE_SCORE_ONLY",
    }


_ALLOWED_STATUSES = frozenset({
    "historical_only", "live_confirmed",
    "fallback_underperforming", "fallback_inconclusive",
})
_REQUIRED_GATE_FIELDS = frozenset({
    "policy_version", "status", "n", "min_n", "candidate_brier",
    "previous_brier", "mean_gain", "ci_low", "ci_high", "fallback",
    "score_rows_structurally_valid", "independent_live_provenance_verified",
    "status_scope",
})


def _validate_gate_result(gate: dict) -> None:
    if type(gate) is not dict or set(gate) != _REQUIRED_GATE_FIELDS:
        raise ProbabilityLiveGateError("gate result must be the canonical evaluator output")
    if gate["policy_version"] != SERVING_POLICY_VERSION:
        raise ProbabilityLiveGateError("gate policy version mismatch")
    if gate["status"] not in _ALLOWED_STATUSES:
        raise ProbabilityLiveGateError("gate status invalid")
    if type(gate["n"]) is not int or gate["n"] < 0:
        raise ProbabilityLiveGateError("gate n must be a nonnegative integer")
    if type(gate["min_n"]) is not int or gate["min_n"] <= 0:
        raise ProbabilityLiveGateError("gate min_n must be a positive integer")
    if type(gate["fallback"]) is not bool:
        raise ProbabilityLiveGateError("gate fallback must be boolean")
    if gate["score_rows_structurally_valid"] is not True:
        raise ProbabilityLiveGateError("gate rows are not structurally valid")
    if gate["independent_live_provenance_verified"] is not False:
        raise ProbabilityLiveGateError("probability gate cannot self-verify LIVE provenance")
    if gate["status_scope"] != "PROSPECTIVE_SCORE_ONLY":
        raise ProbabilityLiveGateError("gate status scope invalid")
    numeric = ("candidate_brier", "previous_brier", "mean_gain", "ci_low", "ci_high")
    for field in numeric:
        value = gate[field]
        if value is not None:
            _score_value(value, f"gate {field}")

    status, n, min_n = gate["status"], gate["n"], gate["min_n"]
    if status == "historical_only":
        if not n < min_n or gate["fallback"] is not False:
            raise ProbabilityLiveGateError("historical-only gate state inconsistent")
    elif status == "live_confirmed":
        if n < min_n or gate["fallback"] is not False or gate["ci_low"] is None or gate["ci_low"] <= 0:
            raise ProbabilityLiveGateError("confirmed gate state inconsistent")
    elif status == "fallback_underperforming":
        if n < min_n or gate["fallback"] is not True or gate["ci_high"] is None or gate["ci_high"] >= 0:
            raise ProbabilityLiveGateError("underperforming gate state inconsistent")
    elif status == "fallback_inconclusive":
        if n < min_n or gate["fallback"] is not True:
            raise ProbabilityLiveGateError("inconclusive gate state inconsistent")
        if gate["ci_low"] is not None and gate["ci_low"] > 0:
            raise ProbabilityLiveGateError("inconclusive gate contradicts positive lower bound")
        if gate["ci_high"] is not None and gate["ci_high"] < 0:
            raise ProbabilityLiveGateError("inconclusive gate contradicts negative upper bound")


def _display_probability(value, field):
    parsed = _score_value(value, field)
    if not 0.0 <= parsed <= 100.0:
        raise ProbabilityLiveGateError(f"{field} must be between 0 and 100")
    return value


def fail_safe_to_previous(result: dict, previous_key: str, *, error_code: str) -> dict:
    """Serve only the already-available reference probability after gate failure."""
    if type(result) is not dict or not isinstance(previous_key, str) or not previous_key:
        raise ProbabilityLiveGateError("invalid probability fallback input")
    if not isinstance(error_code, str) or not error_code.strip():
        raise ProbabilityLiveGateError("error_code must be non-empty")
    previous = result.get(previous_key)
    _display_probability(previous, previous_key)
    candidate = result.get("probability")
    if candidate is not None:
        _display_probability(candidate, "probability")
    out = result
    out["live_candidate_probability"] = candidate
    if "candidate_probability" not in out:
        out["candidate_probability"] = candidate
    out["probability"] = previous
    out["served_probability"] = previous
    out["served_from"] = "previous_stage"
    out["live_gate_status"] = "fallback_gate_unavailable"
    out["live_gate_error_code"] = error_code.strip()
    out["live_gate_independent_provenance_verified"] = False
    status = str(out.get("status") or "").strip()
    note = "실시간 검증 게이트 확인 불가 · 안전 확률 사용"
    out["status"] = f"{status} · {note}" if status else note
    return out


def apply(result: dict, gate: dict, previous_key: str) -> dict:
    """Expose diagnostics and switch only the served probability.

    The caller must record the raw candidate before calling this function.  This
    guarantees that a fallback candidate remains observable in shadow mode and
    can automatically return if later prospective evidence becomes convincing.
    """
    if type(result) is not dict or not isinstance(previous_key, str) or not previous_key:
        raise ProbabilityLiveGateError("invalid probability gate input")
    _validate_gate_result(gate)
    out = result
    candidate = out.get("probability")
    previous = out.get(previous_key)
    _display_probability(candidate, "probability")
    if previous is not None:
        _display_probability(previous, previous_key)
    if gate["fallback"] and previous is None:
        raise ProbabilityLiveGateError("fallback reference probability is unavailable")
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
    out["live_gate_independent_provenance_verified"] = False
    out["live_gate_status_scope"] = "PROSPECTIVE_SCORE_ONLY"

    if gate["fallback"]:
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
