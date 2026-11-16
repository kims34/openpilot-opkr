"""Exploratory public-history VIX/10Y pilot. NOT as-issued/PIT trading evidence.

Yahoo historical series may be revised, late or not historically available at
the stamped time. Times here are explicitly retrospective analysis cutoffs,
NOT authenticated publication timestamps. No 2026 live model deployment.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, time as clock, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import numpy as np
import requests

import next_day_probability as market
import probability_model as core
from research_v35_macro_overlay import evaluate, EvidenceError

NY = ZoneInfo("America/New_York")
USER_AGENT = {"User-Agent": "Mozilla/5.0 IndexAlert research-only"}
SYMBOLS = ("SPY", "QQQ")
MACRO_SYMBOLS = {"vix": "^VIX", "us10y": "^TNX"}


def _stamp(day, hour, minute):
    return datetime.combine(datetime.fromisoformat(day).date(), clock(hour, minute), tzinfo=NY).isoformat()


def public_daily(symbol):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + quote(symbol, safe="")
    response = requests.get(
        url, params={"range": "10y", "interval": "1d", "includePrePost": "false"},
        headers=USER_AGENT, timeout=25)
    response.raise_for_status()
    result = (response.json().get("chart") or {}).get("result") or []
    if len(result) != 1:
        raise EvidenceError("public historical provider returned no single usable series")
    data = result[0]
    days = {}
    timestamps = data.get("timestamp") or []
    closes = (((data.get("indicators") or {}).get("quote") or [{}])[0].get("close") or [])
    if len(timestamps) != len(closes):
        raise EvidenceError("macro history timestamps/closes mismatch")
    for timestamp, price in zip(timestamps, closes):
        if price is None:
            continue
        day = datetime.fromtimestamp(int(timestamp), NY).date().isoformat()
        value = float(price)
        if not np.isfinite(value) or day in days:
            raise EvidenceError("nonfinite/duplicated daily macro record")
        days[day] = value
    return days


def build_rows(prices, macros):
    """Causally generated base-rate comparator, NOT original 3.3 issued forecasts."""
    dates = [d for d, _ in prices]
    p = np.asarray([v for _, v in prices], dtype=float)
    y, candidates = core._candidate_probabilities(p, dates)
    base = candidates["fixed"]
    start = max(core.MIN_TRAIN + core.POLICY_WINDOW, len(prices) - 1 - core.AUDIT_DAYS)
    rows = []
    missing_vix = 0
    missing_yield = 0
    for t in range(start, len(prices) - 1):
        as_of = dates[t]
        target = dates[t + 1]
        if as_of not in macros["vix"]:
            missing_vix += 1
            continue
        observed = {}
        for name in MACRO_SYMBOLS:
            value = macros[name].get(as_of)
            if value is None:
                if name == "us10y":
                    missing_yield += 1
                continue
            observed[name] = {
                "value": value, "session": as_of,
                # Deliberately an analysis convention, not vintage proof.
                "published_at": _stamp(as_of, 17, 15),
                "source_quality": "public_backfill",
            }
        rows.append({
            "as_of": as_of, "target_date": target,
            "prediction_at": _stamp(as_of, 17, 30),
            "baseline_issued_at": _stamp(as_of, 17, 0),
            "target_close_at": _stamp(target, 17, 0),
            "outcome_known_at": _stamp(target, 17, 15),
            "outcome": int(y[t]),
            "baseline_probability": float(base[t]),
            "features": observed,
        })
    return rows, {"missing_vix_dates": missing_vix, "missing_us10y_dates": missing_yield,
                  "complete_vix_rows": len(rows)}


def pilot():
    macros = {}
    source_errors = {}
    for name, symbol in MACRO_SYMBOLS.items():
        try:
            macros[name] = public_daily(symbol)
        except (ValueError, requests.RequestException, EvidenceError) as exc:
            if name == "vix":
                raise EvidenceError("VIX source unavailable: " + type(exc).__name__) from exc
            macros[name] = {}
            source_errors[name] = type(exc).__name__
    summary = {}
    for symbol in SYMBOLS:
        prices, meta = market.fetch_history(symbol, time.time())
        rows, coverage = build_rows(prices, macros)
        if len(rows) < 756:
            summary[symbol] = {"status": "BLOCKED_INSUFFICIENT_ALIGNED_HISTORY", **coverage}
            continue
        outcome = evaluate(rows)
        outcome["public_provisional"] = True
        outcome["reference"] = "causal_fixed_rate_not_exact_live_v3.3"
        outcome["provider"] = "Yahoo backfilled public history, no original vintage verification"
        outcome["analysis_cutoff_is_not_authenticated_published_at"] = True
        outcome["source_errors"] = source_errors
        outcome["aligned_input_sha256"] = hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        outcome["coverage"] = coverage
        summary[symbol] = outcome
    return summary


def main():
    try:
        result = pilot()
        print("V35_PUBLIC_EXPLORATORY", json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (EvidenceError, ValueError, requests.RequestException) as exc:
        print("V35_PUBLIC_BLOCKED", json.dumps({"error_type": type(exc).__name__,
            "detail": str(exc)[:200], "production_admission": "BLOCKED",
            "results_not_verified": True}, ensure_ascii=False))
        sys.exit(2)


if __name__ == "__main__":
    main()
