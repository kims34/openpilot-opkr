"""Runtime wiring for IndexAlert probability model 3.3.

The frozen 3.3 candidate and its shadow challengers are always recorded
prospectively before the serving safety gate is applied.  After 30 scored live
sessions, the candidate is served only while its paired Brier advantage over
the fixed baseline is confirmed by the prospective 95% CI.  Otherwise the
public probability falls back to the baseline while all raw candidates keep
accumulating unbiased shadow evidence for possible automatic recovery.
"""
import hashlib
import json
import sqlite3
import time

import next_day_probability as base
import one_month_calibrated
import one_month_probability
import probability_live_gate
import probability_milestone
import probability_shadow
from probability_model_v33_runtime import MODEL_VERSION, estimate_prices

base.MODEL_VERSION = MODEL_VERSION


def _live_rows(symbol):
    with sqlite3.connect(base.DB_PATH, timeout=10) as con:
        return con.execute(
            "SELECT p,base,outcome FROM probability_forecasts "
            "WHERE model=? AND symbol=? AND outcome IS NOT NULL ORDER BY target",
            (MODEL_VERSION, symbol),
        ).fetchall()


def estimate(symbol, now=None):
    now = time.time() if now is None else now
    rows, meta = base.fetch_history(symbol, now)
    digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    cached = base.INFERENCE_CACHE.get(symbol)
    if cached and cached[0] == digest and cached[1].get("target_date") == meta["target_date"]:
        result = dict(cached[1])
    else:
        result = estimate_prices(
            [p for _, p in rows],
            dates=[d for d, _ in rows],
            target_date=meta["target_date"],
        )
        result["audit_start"] = rows[result.pop("audit_start_index")][0]
        result["audit_end"] = rows[result.pop("audit_end_index")][0]
        result.pop("as_of_index")
        cached_result = dict(result)
        cached_result["target_date"] = meta["target_date"]
        base.INFERENCE_CACHE[symbol] = (digest, cached_result)
    result.update(meta, symbol=symbol, data_digest=digest, computed_at=int(now))

    try:
        ohlc = one_month_probability.fetch_ohlc(symbol, rows)
        result["one_month"] = one_month_calibrated.estimate_probability(rows, ohlc)
    except Exception as exc:
        try:
            result["one_month"] = one_month_calibrated.estimate_probability(rows)
        except Exception:
            result["one_month"] = {"error": "1개월 +/-10% 확률 계산 일시 중단"}
        print("one-month probability OHLC fallback", type(exc).__name__, flush=True)

    month = result.get("one_month") or {}
    if not month.get("error"):
        try:
            month.update(one_month_calibrated.estimate_distribution(rows))
        except Exception as exc:
            print("one-month terminal distribution unavailable", type(exc).__name__, str(exc), flush=True)

    # Freeze and score the RAW historically-approved production candidate first.
    try:
        result.update(base.record_forecast(symbol, result, rows, now))
    except Exception as exc:
        result.update(prospective_count=0, prospective_error="실시간 검증 기록 일시 중단")
        print("probability ledger unavailable", type(exc).__name__, flush=True)

    # Shadow challengers MUST also see the raw candidate, never a served fallback.
    # This keeps the future-only comparison unbiased and preserves the ability to
    # recover automatically if prospective evidence later becomes convincing.
    try:
        result["shadow_validation"] = probability_shadow.record_shadow_forecasts(
            symbol, result, rows, now
        )
    except Exception as exc:
        print("probability shadow ledger unavailable", type(exc).__name__, flush=True)

    # Serving policy is deliberately last among forecast-recording steps.
    try:
        verdict = probability_live_gate.evaluate(_live_rows(symbol))
        result = probability_live_gate.apply(result, verdict, "base_rate")
    except Exception as exc:
        # A ledger/read failure must never invent a replacement probability.
        # Keep the already historically-validated candidate and expose the issue.
        result["live_gate_status"] = "temporarily_unavailable"
        result["live_gate_policy_version"] = probability_live_gate.SERVING_POLICY_VERSION
        result["live_gate_error"] = "실전 Brier 안전장치 상태 확인 중"
        print("next-day live gate unavailable", symbol, type(exc).__name__, flush=True)

    try:
        result["milestone_60"] = probability_milestone.maybe_notify(
            base.DB_PATH, MODEL_VERSION, now
        )
    except Exception as exc:
        result["milestone_60"] = {"ready": False, "error": "검증 알림 상태 확인 중"}
        print("probability milestone unavailable", type(exc).__name__, flush=True)
    return result


base.estimate = estimate
refresh = base.refresh
get_all = base.get_all
