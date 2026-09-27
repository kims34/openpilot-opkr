"""Timing-safe v4.0 first-hour nowcast for SPY/QQQ/SCHD.

The model is an incremental correction on top of the validated v3.9 after-open
probability.  It is deliberately unavailable until 65 minutes after the NYSE
regular open (10:35 ET on a normal session), so an incomplete first-hour bar
can never leak into the estimate.
"""
from __future__ import annotations

import sqlite3
import threading
import time

import numpy as np

import next_day_probability as base
import probability_v40_firsthour as model

MODEL_VERSION = "4.0-first-hour"
FIRST_HOUR_GRACE_SECONDS = 65 * 60
CACHE = {}
SHARED_CACHE = {"target_date": None, "data": None}
LOCK = threading.Lock()


def _shared_first_hour(target_date):
    with LOCK:
        if SHARED_CACHE.get("target_date") == target_date and SHARED_CACHE.get("data"):
            return SHARED_CACHE["data"]
        data = {s: model.first_hour(s) for s in ("SPY", "QQQ", "SCHD", "^VIX")}
        SHARED_CACHE.update(target_date=target_date, data=data)
        return data


def _fit_live(symbol, completed_rows, meta, shared, prior_probability):
    daily = model.daily_ohlcv(symbol)
    dates, closes, positions, outcomes, p39 = model.v39_series(symbol, completed_rows, meta, daily)
    target = meta["target_date"]

    # Re-run the exact validated feature builder with one extra unlabeled live
    # target.  This preserves the research-time rolling-volume construction.
    dates_plus = list(dates) + [target]
    closes_plus = np.append(closes, closes[-1])  # target close is never read
    live_t = len(dates) - 1
    positions_plus = np.append(positions, live_t)
    rows = model.hour_features(
        dates_plus,
        closes_plus,
        positions_plus,
        shared[symbol],
        shared["SPY"],
        shared["QQQ"],
        shared["^VIX"],
    )
    live_j = len(positions)
    live_rows = [row for row in rows if row[0] == live_j and row[2] == target]
    if len(live_rows) != 1:
        raise ValueError("첫 1시간 완성봉 확인 중")
    live = live_rows[0][3]

    historical = [row for row in rows if row[0] < live_j]
    window, ridge, cap = model.FROZEN_CONFIG[symbol]
    historical = historical[-window:]
    if len(historical) < model.MIN_TRAIN:
        raise ValueError("첫 1시간 모델 학습표본 부족")

    source_idx = np.asarray([row[0] for row in historical], int)
    train = np.vstack([row[3] for row in historical])
    y = outcomes[source_idx]
    prior_hist = p39[source_idx]
    if not (np.all(np.isfinite(train)) and np.all(np.isfinite(y)) and np.all(np.isfinite(prior_hist))):
        raise ValueError("첫 1시간 학습자료 이상")

    mean = train.mean(axis=0)
    sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
    z = (train - mean) / sd
    residual = y - prior_hist
    beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)
    adjustment = float(np.clip(((live - mean) / sd) @ beta, -cap, cap))

    p0 = float(prior_probability) / 100.0
    p = float(np.clip(p0 + adjustment, 0.05, 0.95))
    own_bar = shared[symbol][target]
    return {
        "probability": round(p * 100.0, 1),
        "previous_probability": round(p0 * 100.0, 1),
        "adjustment_pp": round(adjustment * 100.0, 1),
        "first_hour_return_percent": round((own_bar[3] / own_bar[0] - 1.0) * 100.0, 2),
        "from_previous_close_percent": round((own_bar[3] / closes[-1] - 1.0) * 100.0, 2),
        "training_count": int(len(historical)),
        "frozen_config": {"window": window, "ridge": ridge, "cap_pp": cap * 100.0},
    }


def _score_and_record(symbol, item, result, completed_rows, now):
    with sqlite3.connect(base.DB_PATH, timeout=10) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS firsthour_nowcast_forecasts(
            model TEXT, symbol TEXT, as_of TEXT, target TEXT,
            probability REAL, previous_probability REAL, created REAL,
            outcome INTEGER, scored_at REAL,
            PRIMARY KEY(model,symbol,target))''')
        prices = dict(completed_rows)
        pending = con.execute(
            "SELECT target,as_of FROM firsthour_nowcast_forecasts WHERE model=? AND symbol=? AND outcome IS NULL",
            (MODEL_VERSION, symbol),
        ).fetchall()
        for target, as_of in pending:
            if target in prices and as_of in prices:
                con.execute(
                    "UPDATE firsthour_nowcast_forecasts SET outcome=?,scored_at=? WHERE model=? AND symbol=? AND target=? AND outcome IS NULL",
                    (int(prices[target] > prices[as_of]), now, MODEL_VERSION, symbol, target),
                )
        if result.get("available"):
            con.execute(
                "INSERT OR IGNORE INTO firsthour_nowcast_forecasts VALUES(?,?,?,?,?,?,?,NULL,NULL)",
                (
                    MODEL_VERSION,
                    symbol,
                    item.get("as_of"),
                    item.get("target_date"),
                    result["probability"] / 100.0,
                    result["previous_probability"] / 100.0,
                    now,
                ),
            )
        scores = con.execute(
            "SELECT probability,previous_probability,outcome FROM firsthour_nowcast_forecasts WHERE model=? AND symbol=? AND outcome IS NOT NULL ORDER BY target",
            (MODEL_VERSION, symbol),
        ).fetchall()
    result["prospective_count"] = len(scores)
    if scores:
        result["prospective_brier"] = sum((p-y)**2 for p,b,y in scores) / len(scores)
        result["prospective_previous_brier"] = sum((b-y)**2 for p,b,y in scores) / len(scores)
        result["prospective_gain"] = result["prospective_previous_brier"] - result["prospective_brier"]
    return result


def estimate(symbol, item, now=None):
    now = time.time() if now is None else now
    target_open = int(item.get("target_open") or 0)
    target_close = int(item.get("target_close") or 0)
    target_date = item.get("target_date")
    after_open = item.get("after_open") or {}
    available_from = target_open + FIRST_HOUR_GRACE_SECONDS if target_open else 0

    base_wait = {
        "available": False,
        "model_version": MODEL_VERSION,
        "target_date": target_date,
        "available_from": available_from or None,
        "timing": "미국 정규장 첫 1시간 마감 후 5분(통상 10:35 ET)부터 업데이트",
    }
    if not target_open or not target_close or not target_date:
        return dict(base_wait, status="거래일 정보 확인 중")
    if now < available_from:
        return dict(base_wait, status="첫 1시간 마감 대기")
    if now >= target_close:
        return dict(base_wait, status="정규장 종료 · 결과 확정 대기")
    if not after_open.get("available") or after_open.get("probability") is None:
        return dict(base_wait, status="개장후 기준 확률 확인 중")

    key = (symbol, target_date, item.get("data_digest"), after_open.get("probability"))
    if key in CACHE:
        return dict(CACHE[key])

    completed_rows, meta = base.fetch_history(symbol, now)
    if meta.get("target_date") != target_date:
        raise ValueError("첫 1시간 타깃 거래일 불일치")
    shared = _shared_first_hour(target_date)
    if any(target_date not in shared[s] for s in (symbol, "SPY", "QQQ", "^VIX")):
        return dict(base_wait, status="첫 1시간 완성봉 수신 대기")

    fitted = _fit_live(symbol, completed_rows, meta, shared, after_open["probability"])
    result = {
        "available": True,
        "status": "첫 1시간 시장정보 반영",
        "model_version": MODEL_VERSION,
        "target_date": target_date,
        "as_of": item.get("as_of"),
        "computed_at": int(now),
        "available_from": available_from,
        "target_close": target_close,
        "timing": "미국 정규장 첫 1시간 마감 후 5분부터 업데이트",
        "validation": "126거래일 최종 홀드아웃 + 21일 6블록 + 이동블록 부트스트랩 통과",
        **fitted,
    }
    try:
        result = _score_and_record(symbol, item, result, completed_rows, now)
    except Exception as exc:
        result["prospective_error"] = "첫 1시간 실시간 검증 기록 일시 중단"
        print("first-hour ledger unavailable", symbol, type(exc).__name__, flush=True)
    CACHE[key] = dict(result)
    return result


def enrich(payload, now=None):
    now = time.time() if now is None else now
    out = dict(payload)
    items = {}
    for index_id, item0 in (payload.get("items") or {}).items():
        item = dict(item0)
        symbol = item.get("symbol") or base.SYMBOLS.get(index_id)
        if item.get("error") or symbol not in model.FROZEN_CONFIG:
            item["first_hour"] = {
                "available": False,
                "status": "기본 확률 계산 중",
                "model_version": MODEL_VERSION,
            }
        else:
            try:
                item["first_hour"] = estimate(symbol, item, now)
            except Exception as exc:
                item["first_hour"] = {
                    "available": False,
                    "status": "첫 1시간 확률 데이터 확인 중",
                    "model_version": MODEL_VERSION,
                    "target_date": item.get("target_date"),
                }
                print("first-hour nowcast unavailable", symbol, type(exc).__name__, str(exc), flush=True)
        items[index_id] = item
    out["items"] = items
    out["first_hour_model_version"] = MODEL_VERSION
    return out
