"""Runtime wiring for the validated 3.1 adaptive probability model."""
import hashlib
import json
import time

import next_day_probability as base
import one_month_distribution
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

    try:
        ohlc = one_month_probability.fetch_ohlc(symbol, rows)
        result["one_month"] = one_month_probability.estimate(rows, ohlc)
    except Exception as exc:
        try:
            result["one_month"] = one_month_probability.estimate(rows)
        except Exception:
            result["one_month"] = {"error": "1개월 +/-10% 확률 계산 일시 중단"}
        print("one-month probability OHLC fallback", type(exc).__name__, flush=True)

    month = result.get("one_month") or {}
    if not month.get("error"):
        try:
            month.update(one_month_distribution.estimate(rows))
        except Exception as exc:
            print("one-month terminal distribution unavailable", type(exc).__name__, str(exc), flush=True)

        print(
            "one-month probability ready",
            symbol,
            {
                "up10": month.get("up_10_probability"),
                "down10": month.get("down_10_probability"),
                "mode": month.get("terminal_return_mode_label"),
                "mode_probability": month.get("terminal_return_mode_probability"),
                "mode_selection": month.get("terminal_return_selection"),
                "mode_skill": (month.get("terminal_return_validation") or {}).get("skill"),
                "basis": month.get("price_basis"),
                "selection_up": month.get("selection_up"),
                "selection_down": month.get("selection_down"),
                "skill_up": (month.get("validation_up") or {}).get("skill"),
                "skill_down": (month.get("validation_down") or {}).get("skill"),
                "features": month.get("features"),
            },
            flush=True,
        )

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
