"""Production live wrapper for the validated v3.12 09:05 ET overlay.

Important: v3.12 was researched and validated against the frozen v3.2
next-session baseline.  This wrapper therefore recomputes that exact v3.2
baseline before applying the futures/risk adjustment, even when the outer API
also exposes a later guarded calibration model.  This preserves research/live
parity and prevents the baseline definition from drifting after validation.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
import time

import next_day_probability as base
import probability_model_v31_runtime as v32
import preopen_futures_v312 as core

MODEL_VERSION = "3.12-preopen-futures"
BASELINE_MODEL_VERSION = "3.2-live-guardrails"
CONFIGS = core.CONFIGS
VALIDATION = core.VALIDATION


def _display_baseline(item: dict):
    for key in ("previous_model_probability", "probability"):
        value = item.get(key)
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            return value
    return None


def _unavailable(symbol: str, item: dict, status: str):
    return {
        "available": False,
        "status": status,
        "model_version": MODEL_VERSION,
        "baseline_model_version": BASELINE_MODEL_VERSION,
        "probability": None,
        "baseline_probability": _display_baseline(item),
        "adjustment_pp": None,
        "as_of": item.get("as_of"),
        "target_date": item.get("target_date"),
        "decision_time_et": "09:05",
        "validation": dict(VALIDATION.get(symbol, {})),
    }


def _fit_from_rows(symbol: str, rows, meta: dict, hourly, daily):
    dates = [day for day, _ in rows]
    prices = [price for _, price in rows]
    baseline = v32.estimate_prices(
        prices,
        dates=dates,
        target_date=meta["target_date"],
    )
    baseline_probability = float(baseline["probability"])
    result = core._fit_live(
        symbol,
        baseline_probability,
        rows,
        meta,
        hourly,
        daily,
    )
    result["model_version"] = MODEL_VERSION
    result["baseline_model_version"] = BASELINE_MODEL_VERSION
    result["baseline_probability"] = baseline_probability
    result["reference_model_locked"] = True
    return result


def estimate(symbol: str, item: dict, now: float | None = None):
    now = time.time() if now is None else float(now)
    if symbol not in CONFIGS:
        return _unavailable(symbol, item, "검증 통과 종목 아님 · 기존 확률 유지")
    if item.get("error") or not item.get("target_date") or not item.get("as_of"):
        return _unavailable(symbol, item, "기본 확률 확인 중")

    decision = core._decision_time(str(item["target_date"]))
    now_et = datetime.fromtimestamp(now, timezone.utc).astimezone(core.NY)
    if now_et < decision:
        return _unavailable(symbol, item, "미 동부 09:05 이후 선물 반영")

    cache_key = (symbol, str(item["as_of"]), str(item["target_date"]), BASELINE_MODEL_VERSION)
    with core.RESULT_LOCK:
        cached = core.RESULT_CACHE.get(cache_key)
        if cached:
            return dict(cached)

    try:
        rows, meta = base.fetch_history(symbol, now)
        if meta["as_of"] != item["as_of"] or meta["target_date"] != item["target_date"]:
            raise ValueError("기본확률과 선물 계산 거래일 불일치")
        hourly, daily = core._market_data(now)
        result = _fit_from_rows(symbol, rows, meta, hourly, daily)
    except Exception as exc:
        print("v3.12 preopen unavailable", symbol, type(exc).__name__, str(exc), flush=True)
        return _unavailable(symbol, item, "선물·위험지표 최신값 확인 중")

    with core.RESULT_LOCK:
        core.RESULT_CACHE[cache_key] = dict(result)
    return result


def enrich(payload: dict, now: float | None = None):
    now = time.time() if now is None else float(now)
    result = dict(payload)
    items = {}
    for index_id, symbol in base.SYMBOLS.items():
        item = dict((payload.get("items") or {}).get(index_id) or {})
        item["preopen_futures"] = estimate(symbol, item, now)
        items[index_id] = item
    result["items"] = items
    result["preopen_futures_model"] = MODEL_VERSION
    result["preopen_futures_baseline_model"] = BASELINE_MODEL_VERSION
    return result
