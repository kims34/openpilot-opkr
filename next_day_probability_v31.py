"""Runtime wiring for the validated 3.1 adaptive probability model."""
import hashlib
import json
import time

import next_day_probability as base
import one_month_probability
import probability_milestone
import probability_shadow
from probability_model_v31_runtime import MODEL_VERSION, estimate_prices

# Keep all hardened data/calendar/cache/ledger behavior from next_day_probability,
# replacing only the inference function and model-version namespace.
base.MODEL_VERSION = MODEL_VERSION


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

    # Supplemental 21-session threshold-touch probabilities. Use completed
    # daily highs/lows when available so an intraday +/-10% touch counts even
    # when the session later closes back inside the threshold.
    try:
        ohlc = one_month_probability.fetch_ohlc(symbol, rows)
        result["one_month"] = one_month_probability.estimate(rows, ohlc)
    except Exception as exc:
        try:
            # Conservative availability fallback: retain a close-touch estimate
            # rather than removing the entire monthly section when OHLC retrieval
            # is temporarily unavailable. The response tells the client which
            # price basis was used.
            result["one_month"] = one_month_probability.estimate(rows)
        except Exception:
            result["one_month"] = {"error": "1개월 +/-10% 확률 계산 일시 중단"}
        print("one-month probability OHLC fallback", type(exc).__name__, flush=True)

    try:
        result.update(base.record_forecast(symbol, result, rows, now))
    except Exception as exc:
        result.update(prospective_count=0, prospective_error="실시간 검증 기록 일시 중단")
        print("probability ledger unavailable", type(exc).__name__, flush=True)

    try:
        result["shadow_validation"] = probability_shadow.record_shadow_forecasts(
            symbol, result, rows, now
        )
    except Exception as exc:
        print("probability shadow ledger unavailable", type(exc).__name__, flush=True)

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
