"""Runtime wiring for the validated 3.1 adaptive probability model."""
import hashlib
import json
import time

import next_day_probability as base
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
        # Store the target date in inference cache so a new exchange session forces
        # recomputation even if the price-history digest is unchanged over a weekend.
        cached_result = dict(result)
        cached_result["target_date"] = meta["target_date"]
        base.INFERENCE_CACHE[symbol] = (digest, cached_result)
    result.update(meta, symbol=symbol, data_digest=digest, computed_at=int(now))
    try:
        result.update(base.record_forecast(symbol, result, rows, now))
    except Exception as exc:
        result.update(prospective_count=0, prospective_error="실시간 검증 기록 일시 중단")
        print("probability ledger unavailable", type(exc).__name__, flush=True)

    # Shadow challengers are recorded prospectively but never replace the served
    # v3.1 probability. Any shadow failure is isolated from the live response.
    try:
        result["shadow_validation"] = probability_shadow.record_shadow_forecasts(
            symbol, result, rows, now
        )
    except Exception as exc:
        print("probability shadow ledger unavailable", type(exc).__name__, flush=True)
    return result


base.estimate = estimate

# refresh() resolves base.estimate and base.MODEL_VERSION dynamically, so all
# existing stale-data handling and prospective recording are retained.
refresh = base.refresh
get_all = base.get_all
