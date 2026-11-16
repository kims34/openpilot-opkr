"""Research-only, causally validated next-close macro overlay for IndexAlert.

This module DOES NOT fetch market data, mutate live app/broker state, or enable
trades. Baseline probabilities must be recorded or reconstructed independently
using a causal replay of the exact deployed reference model. Macro sources and
their as-of publication timestamps must be supplied by the caller.

A historical data provider's reconstructed publication timestamp is NOT proof
of original publication vintage. All results remain research-only.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime
from pathlib import Path

import numpy as np

FEATURE_SETS = (
    ("vix",),
    ("vix", "us10y"),
    ("vix", "us10y", "breadth"),
)
FEATURE_RANGES = {"vix": (5.0, 150.0), "us10y": (-3.0, 25.0), "breadth": (0.0, 1.0)}
QUALITY = {"archived_asof", "public_backfill"}
MIN_GAIN = 1e-6


class EvidenceError(ValueError):
    """Malformed, future-dated, or unauthenticated-as-of research evidence."""


def _instant(value, field):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EvidenceError(f"{field}: timezone required")
    return parsed


def _day(value, field):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"invalid {field}") from exc


def _float(value, field, lo, hi):
    if isinstance(value, bool):
        raise EvidenceError(f"{field}: boolean not allowed")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"invalid {field}") from exc
    if not math.isfinite(number) or not lo <= number <= hi:
        raise EvidenceError(f"{field}: out of bounds")
    return number


def validate(records):
    """Reject temporal leakage; report the strength, not proof, of source evidence."""
    if not isinstance(records, list) or not records:
        raise EvidenceError("nonempty records array required")
    seen = set()
    previous_date = None
    backfill = False
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise EvidenceError(f"row {i}: object required")
        day = _day(record.get("as_of"), "as_of")
        target = _day(record.get("target_date"), "target_date")
        if (previous_date is not None and day <= previous_date) or day in seen:
            raise EvidenceError("as_of dates must be strictly increasing")
        previous_date = day
        seen.add(day)
        if target <= day:
            raise EvidenceError("target date must be after as_of")
        issued = _instant(record.get("prediction_at"), "prediction_at")
        baseline_at = _instant(record.get("baseline_issued_at"), "baseline_issued_at")
        if issued.date() < day or baseline_at > issued:
            raise EvidenceError("baseline not available when prediction issued")
        closing = _instant(record.get("target_close_at"), "target_close_at")
        known = _instant(record.get("outcome_known_at"), "outcome_known_at")
        if closing.date() != target or known < closing or closing <= issued:
            raise EvidenceError("invalid outcome availability / target close")
        _float(record.get("baseline_probability"), "baseline_probability", 0, 1)
        outcome = record.get("outcome")
        if type(outcome) is not int or outcome not in (0, 1):
            raise EvidenceError("outcome must be an exact 0 or 1")
        features = record.get("features")
        if not isinstance(features, dict):
            raise EvidenceError("features must be an object")
        for name, measurement in features.items():
            if name not in FEATURE_RANGES or not isinstance(measurement, dict):
                raise EvidenceError("unknown feature or malformed observation")
            _float(measurement.get("value"), name, *FEATURE_RANGES[name])
            if measurement.get("source_quality") not in QUALITY:
                raise EvidenceError(f"{name}: unknown source quality")
            pub = _instant(measurement.get("published_at"), name + " published_at")
            observed = _day(measurement.get("session"), name + " session")
            if pub > issued or observed > day:
                raise EvidenceError(f"{name}: future information at prediction time")
            if measurement["source_quality"] == "public_backfill":
                backfill = True
    return {"source_quality": "PUBLIC_BACKFILL_NO_PIT_PROOF" if backfill else "DECLARED_ARCHIVE_NOT_INDEPENDENTLY_PROVEN",
            "independent_original_vintage_verified": False}


def _as_of_features(record, fields):
    return np.array([float(record["features"][name]["value"]) for name in fields], dtype=float)


def predict_at(records, t, fields, *, window=504, ridge=30.0, cap=0.08, min_train=252):
    """Forecast using only labels demonstrably available before prediction t."""
    if not 0 <= t < len(records):
        raise EvidenceError("invalid forecast position")
    if not fields or any(name not in FEATURE_RANGES for name in fields):
        raise EvidenceError("unknown feature set")
    p0 = float(records[t]["baseline_probability"])
    if any(name not in records[t]["features"] for name in fields):
        raise EvidenceError("current feature missing")
    issue = _instant(records[t]["prediction_at"], "prediction_at")
    pool = [r for r in records[:t]
            if all(name in r["features"] for name in fields)
            and _instant(r["outcome_known_at"], "outcome_known_at") <= issue]
    pool = pool[-window:]
    if len(pool) < min_train:
        return p0
    x = np.stack([_as_of_features(r, fields) for r in pool])
    center = x.mean(axis=0)
    spread = np.maximum(x.std(axis=0, ddof=1), 1e-4)
    z = np.clip((x - center) / spread, -3.0, 3.0)
    residual = np.array([r["outcome"] - r["baseline_probability"] for r in pool], dtype=float)
    penalty = max(float(ridge), 1e-5)
    beta = np.linalg.solve(z.T @ z + penalty * np.eye(z.shape[1]), z.T @ residual)
    current = np.clip((_as_of_features(records[t], fields) - center) / spread, -3.0, 3.0)
    correction = float(np.clip(current @ beta, -cap, cap))
    return float(np.clip(p0 + correction, 0.02, 0.98))


def _brier(probabilities, outcomes):
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if len(p) != len(y) or len(y) == 0:
        raise EvidenceError("empty or misaligned score window")
    return float(np.mean((p - y) ** 2))


def _gains(base, challenger, outcomes):
    n = len(outcomes)
    mid = n // 2
    if mid == 0:
        raise EvidenceError("score window too short")
    return {
        "all": _brier(base, outcomes) - _brier(challenger, outcomes),
        "first_half": _brier(base[:mid], outcomes[:mid]) - _brier(challenger[:mid], outcomes[:mid]),
        "second_half": _brier(base[mid:], outcomes[mid:]) - _brier(challenger[mid:], outcomes[mid:]),
    }


def evaluate(records, *, min_train=252, test_sessions=252, min_dev_half=126):
    """Select on historical development only; report reserved test without promotion.

    The same reserved test cannot be considered untouched for another
    hypothesis selected after seeing this result. No live promotion or orders.
    """
    evidence = validate(records)
    if min_train < 10 or test_sessions < 4 or min_dev_half < 2:
        raise EvidenceError("invalid research split parameters")
    n = len(records)
    split = n - test_sessions
    if split - min_train < 2 * min_dev_half:
        raise EvidenceError("insufficient independent chronological windows")
    base = np.array([float(r["baseline_probability"]) for r in records], dtype=float)
    y = np.array([int(r["outcome"]) for r in records], dtype=float)

    available = [
        fields for fields in FEATURE_SETS
        if all(all(name in r["features"] for name in fields) for r in records)
    ]
    development, scored = [], {}
    for fields in available:
        predicted = base.copy()
        for t in range(min_train, n):
            predicted[t] = predict_at(records, t, fields, min_train=min_train)
        gain = _gains(base[min_train:split], predicted[min_train:split], y[min_train:split])
        key = "+".join(fields)
        scored[key] = (fields, predicted, gain)
        development.append({
            "features": key, "dev_brier": _brier(predicted[min_train:split], y[min_train:split]),
            "dev_gain": gain,
        })

    candidates = [x for x in development
                  if all(v > MIN_GAIN for v in x["dev_gain"].values())]
    candidates.sort(key=lambda x: (x["dev_brier"], x["features"]))
    selected = candidates[0]["features"] if candidates else None
    result = {
        "model": "v3.5-macro-overlay-research-only",
        "source_evidence": evidence,
        "rows": n, "development_count": split - min_train, "reserved_test_count": test_sessions,
        "candidates": development, "selected": selected,
        "production_admission": "BLOCKED",
        "order_authorization": False, "app_changed": False,
    }
    if selected is None:
        result["decision"] = "NO_STABLE_DEVELOPMENT_WINNER"
        return result
    predicted = scored[selected][1]
    gain = _gains(base[split:], predicted[split:], y[split:])
    result["reserved_test"] = {
        "baseline_brier": _brier(base[split:], y[split:]),
        "challenger_brier": _brier(predicted[split:], y[split:]),
        "gain": gain,
        "all_three_splits_improved": all(v > MIN_GAIN for v in gain.values()),
    }
    result["decision"] = "RESEARCH_EVIDENCE_ONLY_REQUIRES_INDEPENDENT_PIT_AND_PROSPECTIVE"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Local JSON with {'records': [...]}; never credentials")
    parser.add_argument("--output", help="Optional metadata-only JSON report destination")
    args = parser.parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = evaluate(raw["records"])
    summary = json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        Path(args.output).write_text(summary + "\n", encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
