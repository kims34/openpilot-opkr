"""Validated 09:05 ET pre-open futures overlay for IndexAlert.

This module does not change the immutable daily-close baseline forecast.  It
adds a separate `preopen_futures` object for models that passed v3.12 research
and fixed-config robustness gates.  The overlay becomes available at 09:05 ET
on the target U.S. session and uses only data timestamped no later than 08:00
ET for that target date, together with previous completed-session information.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
import threading
import time
from zoneinfo import ZoneInfo

import numpy as np
import requests

import next_day_probability as base
import probability_v312_futures_preopen as research

MODEL_VERSION = "3.12-preopen-futures"
NY = ZoneInfo("America/New_York")
DECISION_HOUR = 9
DECISION_MINUTE = 5
CACHE_SECONDS = 10 * 60

# Frozen only after the untouched 126-session holdout and six chronological
# robustness blocks passed.  SCHD is intentionally absent: its holdout failed.
CONFIGS = {
    "SPY": (252, 30.0, 0.05),
    "QQQ": (126, 30.0, 0.05),
}
VALIDATION = {
    "SPY": {
        "holdout_count": 126,
        "previous_brier": 0.25003440986273145,
        "candidate_brier": 0.2326575098088509,
        "holdout_gain": 0.017376900053880567,
        "robustness_positive_blocks": 6,
        "robustness_total_blocks": 6,
    },
    "QQQ": {
        "holdout_count": 126,
        "previous_brier": 0.2477197782303951,
        "candidate_brier": 0.2339880819531332,
        "holdout_gain": 0.013731696277261896,
        "robustness_positive_blocks": 6,
        "robustness_total_blocks": 6,
    },
}

DATA_LOCK = threading.Lock()
DATA_CACHE = {"updated": 0.0, "hourly": None, "daily": None}
RESULT_LOCK = threading.Lock()
RESULT_CACHE = {}
UA = {"User-Agent": "Mozilla/5.0 IndexAlert/3.12-preopen"}


def _yahoo(symbol: str, range_: str, interval: str):
    encoded = requests.utils.quote(symbol, safe="")
    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}",
        params={
            "range": range_,
            "interval": interval,
            "includePrePost": "true",
            "events": "div,splits",
        },
        headers=UA,
        timeout=25,
    )
    response.raise_for_status()
    chart = response.json().get("chart", {})
    if chart.get("error"):
        raise ValueError("선물 데이터 공급자 오류")
    result = (chart.get("result") or [None])[0]
    if not result:
        raise ValueError("선물 데이터 없음")
    timestamps = result.get("timestamp") or []
    closes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    if len(timestamps) != len(closes):
        raise ValueError("선물 가격·시각 개수 불일치")
    rows = []
    for stamp, close in zip(timestamps, closes):
        if close is None:
            continue
        close = float(close)
        if math.isfinite(close) and close > 0:
            rows.append((int(stamp), close))
    return rows


def _market_data(now: float):
    with DATA_LOCK:
        if (
            DATA_CACHE["hourly"] is not None
            and DATA_CACHE["daily"] is not None
            and now - DATA_CACHE["updated"] < CACHE_SECONDS
        ):
            return DATA_CACHE["hourly"], DATA_CACHE["daily"]

        daily = {}
        for symbol in ("^VIX", "^TNX"):
            values = {}
            for stamp, close in _yahoo(symbol, "5y", "1d"):
                day = datetime.fromtimestamp(stamp, timezone.utc).astimezone(NY).date().isoformat()
                values[day] = close
            daily[symbol] = values

        hourly = {}
        for symbol in research.FUTURES:
            hourly[symbol] = [
                (datetime.fromtimestamp(stamp, timezone.utc).astimezone(NY), close)
                for stamp, close in _yahoo(symbol, "2y", "1h")
            ]

        DATA_CACHE.update(updated=now, hourly=hourly, daily=daily)
        return hourly, daily


def _decision_time(target_date: str) -> datetime:
    return datetime.fromisoformat(target_date).replace(
        tzinfo=NY, hour=DECISION_HOUR, minute=DECISION_MINUTE, second=0, microsecond=0
    )


def _live_feature(prices, dates, as_of, target_date, hourly, daily):
    if len(prices) < 6 or not dates or dates[-1] != as_of:
        raise ValueError("완료 종가 정렬 오류")
    by_day = {symbol: research._by_day(rows) for symbol, rows in hourly.items()}
    futures = []
    for symbol in research.FUTURES:
        value = research._overnight_return(by_day[symbol], as_of, target_date)
        if value is None:
            raise ValueError(f"{symbol} 09:05 전 데이터 미완료")
        futures.append(value)

    previous_day = dates[-2]
    v0 = research._daily_value(daily["^VIX"], as_of)
    v1 = research._daily_value(daily["^VIX"], previous_day)
    y0 = research._daily_value(daily["^TNX"], as_of)
    y1 = research._daily_value(daily["^TNX"], previous_day)
    if None in (v0, v1, y0, y1):
        raise ValueError("VIX/10년물 완료값 미확인")

    p = np.asarray(prices, dtype=float)
    vector = np.asarray(
        futures
        + [
            math.log(v0),
            v0 / v1 - 1.0,
            y0,
            y0 - y1,
            p[-1] / p[-2] - 1.0,
            p[-1] / p[-6] - 1.0,
        ],
        dtype=float,
    )
    if vector.shape != (10,) or not np.all(np.isfinite(vector)):
        raise ValueError("선물 특징값 비정상")
    return vector


def _fit_live(symbol, baseline_probability, rows, meta, hourly, daily):
    dates = [day for day, _ in rows]
    prices = [price for _, price in rows]
    trace = research._served_trace(prices, dates, meta["target_date"])
    previous = np.asarray([float(row["probability"]) for row in trace], dtype=float)
    outcomes = np.asarray([float(row["outcome"]) for row in trace], dtype=float)
    x, _ = research._feature_rows(prices, dates, trace, hourly, daily)

    config = CONFIGS[symbol]
    window, ridge, cap = config
    complete = np.where(np.all(np.isfinite(x), axis=1))[0]
    if len(complete) < research.MIN_TRAIN:
        raise ValueError("선물 학습표본 부족")
    idx = complete[-window:]
    if len(idx) < research.MIN_TRAIN:
        raise ValueError("선물 학습창 부족")

    train = x[idx]
    mean = train.mean(axis=0)
    sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
    z = (train - mean) / sd
    residual = outcomes[idx] - previous[idx]
    beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)

    live = _live_feature(
        prices, dates, meta["as_of"], meta["target_date"], hourly, daily
    )
    raw_adjustment = float(((live - mean) / sd) @ beta)
    adjustment = float(np.clip(raw_adjustment, -cap, cap))
    baseline = float(baseline_probability) / 100.0
    probability = float(np.clip(baseline + adjustment, 0.35, 0.70))

    feature_names = (
        "sp500_futures",
        "nasdaq100_futures",
        "wti_futures",
        "dollar_index",
        "vix_level_log",
        "vix_change",
        "us10y_level",
        "us10y_change",
        "etf_1d_momentum",
        "etf_5d_momentum",
    )
    features = {name: float(value) for name, value in zip(feature_names, live)}
    # Human-readable percentages for the return-like components.
    for name in (
        "sp500_futures",
        "nasdaq100_futures",
        "wti_futures",
        "dollar_index",
        "vix_change",
        "etf_1d_momentum",
        "etf_5d_momentum",
    ):
        features[f"{name}_percent"] = features[name] * 100.0

    return {
        "available": True,
        "status": "선물·VIX·미국 10년물 반영 완료",
        "model_version": MODEL_VERSION,
        "probability": probability * 100.0,
        "baseline_probability": float(baseline_probability),
        "adjustment_pp": (probability - baseline) * 100.0,
        "raw_adjustment_pp": raw_adjustment * 100.0,
        "as_of": meta["as_of"],
        "target_date": meta["target_date"],
        "decision_time_et": "09:05",
        "training_count": int(len(idx)),
        "config": {"window": window, "ridge": ridge, "cap_pp": cap * 100.0},
        "features": features,
        "validation": dict(VALIDATION[symbol]),
        "method": (
            "09:05 ET 이전 완료 선물(ES/NQ/WTI/달러) + 전일 VIX/미국10년물 + "
            "ETF 1·5일 모멘텀의 과거오차 ridge 보정"
        ),
        "price_basis": "target_close_vs_previous_close",
    }


def _unavailable(symbol, item, status):
    return {
        "available": False,
        "status": status,
        "model_version": MODEL_VERSION,
        "probability": None,
        "baseline_probability": item.get("probability"),
        "adjustment_pp": None,
        "as_of": item.get("as_of"),
        "target_date": item.get("target_date"),
        "decision_time_et": "09:05",
        "validation": dict(VALIDATION.get(symbol, {})),
    }


def estimate(symbol: str, item: dict, now: float | None = None):
    now = time.time() if now is None else float(now)
    if symbol not in CONFIGS:
        return _unavailable(symbol, item, "검증 통과 종목 아님 · 기존 확률 유지")
    if item.get("error") or not item.get("target_date") or not item.get("as_of"):
        return _unavailable(symbol, item, "기본 확률 확인 중")
    baseline_probability = item.get("probability")
    if baseline_probability is None or not math.isfinite(float(baseline_probability)):
        return _unavailable(symbol, item, "기본 확률 확인 중")

    decision = _decision_time(str(item["target_date"]))
    now_et = datetime.fromtimestamp(now, timezone.utc).astimezone(NY)
    if now_et < decision:
        return _unavailable(symbol, item, "미 동부 09:05 이후 선물 반영")

    cache_key = (symbol, str(item["as_of"]), str(item["target_date"]), round(float(baseline_probability), 6))
    with RESULT_LOCK:
        cached = RESULT_CACHE.get(cache_key)
        if cached:
            return dict(cached)

    try:
        rows, meta = base.fetch_history(symbol, now)
        if meta["as_of"] != item["as_of"] or meta["target_date"] != item["target_date"]:
            raise ValueError("기본확률과 선물 계산 거래일 불일치")
        hourly, daily = _market_data(now)
        result = _fit_live(symbol, float(baseline_probability), rows, meta, hourly, daily)
    except Exception as exc:
        print("v3.12 preopen unavailable", symbol, type(exc).__name__, str(exc), flush=True)
        return _unavailable(symbol, item, "선물·위험지표 최신값 확인 중")

    with RESULT_LOCK:
        RESULT_CACHE[cache_key] = dict(result)
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
    return result
