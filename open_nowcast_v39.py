"""Timing-safe v3.9 after-open nowcast for SPY/QQQ/SCHD.

This module NEVER replaces the pre-open next-session forecast. It adds a
separate probability only after the target NYSE session has opened and the
vendor's daily opening price is available. The target remains:
    close(target) > close(previous completed session)

Research-selected hyperparameters were chosen on the development sample and
passed an untouched final-252-session holdout plus price-basis integrity tests.
"""
import json
import math
import sqlite3
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

import next_day_probability as base
import probability_v39_open_nowcast as research

MODEL_VERSION = "3.9-open-nowcast"
OPEN_GRACE_SECONDS = 5 * 60
NY = ZoneInfo("America/New_York")
CONFIG_BY_SYMBOL = {
    "SPY": (504, 100.0, 0.15),
    "QQQ": (756, 100.0, 0.15),
    "SCHD": (252, 100.0, 0.15),
}
CACHE = {}
LOCK = threading.Lock()


def _daily_ohlc(symbol):
    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert/3.9-runtime"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json().get("chart", {})
    if payload.get("error"):
        raise ValueError("시세 공급자 오류")
    result = (payload.get("result") or [None])[0]
    if not result or result.get("meta", {}).get("symbol") != symbol:
        raise ValueError("종목 데이터 불일치")
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    opens = quote.get("open") or []
    closes = quote.get("close") or []
    rows = {}
    for ts, op, cl in zip(timestamps, opens, closes):
        day = datetime.fromtimestamp(int(ts), timezone.utc).astimezone(NY).date().isoformat()
        if op is None or float(op) <= 0:
            continue
        rows[day] = {
            "open": float(op),
            # Current target close may be incomplete; it is stored but never
            # read by the nowcast calculation for that target.
            "close": float(cl) if cl is not None and float(cl) > 0 else None,
        }
    return rows


def _historical_features(opens, closes, positions):
    return research._features(opens, closes, positions)


def _live_feature(target_open, closes):
    closes = np.asarray(closes, float)
    if len(closes) < 6:
        raise ValueError("종가 이력 부족")
    prior = closes[-1]
    gap = target_open / prior - 1.0
    prev1 = prior / closes[-2] - 1.0
    mom5 = prior / closes[-6] - 1.0
    return np.asarray([gap, abs(gap), 1.0 if gap > 0 else 0.0, prev1, mom5, gap * prev1], float)


def _fit_live(opens, closes, dates, target_date, target_open, preopen_probability, config):
    trace = research._previous_trace(closes, dates, target_date)
    positions = np.asarray([int(row["t"]) for row in trace])
    previous = np.asarray([float(row["probability"]) for row in trace], float)
    outcomes = np.asarray([float(row["outcome"]) for row in trace], float)
    x = _historical_features(opens, closes, positions)

    window, ridge, cap = config
    idx = np.arange(max(0, len(outcomes) - window), len(outcomes))
    valid = np.all(np.isfinite(x[idx]), axis=1) & np.isfinite(previous[idx]) & np.isfinite(outcomes[idx])
    idx = idx[valid]
    if len(idx) < 126:
        raise ValueError("개장후 모델 학습표본 부족")

    train = x[idx]
    mean = train.mean(axis=0)
    sd = np.maximum(train.std(axis=0, ddof=1), 1e-6)
    z = (train - mean) / sd
    residual = outcomes[idx] - previous[idx]
    beta = np.linalg.solve(z.T @ z + ridge * np.eye(z.shape[1]), z.T @ residual)

    live = _live_feature(target_open, closes)
    gap = float(live[0])
    if abs(gap) > 0.15:
        raise ValueError("비정상 시가 갭 · 분할/단위 확인 필요")
    adj = float(np.clip(((live - mean) / sd) @ beta, -cap, cap))
    p0 = float(preopen_probability) / 100.0
    p = float(np.clip(p0 + adj, 0.05, 0.95))
    return {
        "probability": round(p * 100.0, 1),
        "preopen_probability": round(p0 * 100.0, 1),
        "adjustment_pp": round(adj * 100.0, 1),
        "opening_gap_percent": round(gap * 100.0, 2),
        "training_count": int(len(idx)),
    }


def _score_and_record(symbol, item, result, completed_rows, now):
    """Freeze the first post-open nowcast and score only after a later completed close."""
    with sqlite3.connect(base.DB_PATH, timeout=10) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS open_nowcast_forecasts(
            model TEXT, symbol TEXT, as_of TEXT, target TEXT,
            probability REAL, preopen_probability REAL, opening_gap REAL,
            created REAL, outcome INTEGER, scored_at REAL,
            PRIMARY KEY(model,symbol,target))''')
        prices = dict(completed_rows)
        pending = con.execute(
            "SELECT target,as_of FROM open_nowcast_forecasts WHERE model=? AND symbol=? AND outcome IS NULL",
            (MODEL_VERSION, symbol),
        ).fetchall()
        for target, as_of in pending:
            if target in prices and as_of in prices:
                con.execute(
                    "UPDATE open_nowcast_forecasts SET outcome=?,scored_at=? WHERE model=? AND symbol=? AND target=? AND outcome IS NULL",
                    (int(prices[target] > prices[as_of]), now, MODEL_VERSION, symbol, target),
                )
        if result.get("available"):
            con.execute(
                "INSERT OR IGNORE INTO open_nowcast_forecasts VALUES(?,?,?,?,?,?,?,?,NULL,NULL)",
                (
                    MODEL_VERSION, symbol, item["as_of"], item["target_date"],
                    result["probability"] / 100.0, result["preopen_probability"] / 100.0,
                    result["opening_gap_percent"] / 100.0, now,
                ),
            )
        scores = con.execute(
            "SELECT probability,preopen_probability,outcome FROM open_nowcast_forecasts WHERE model=? AND symbol=? AND outcome IS NOT NULL ORDER BY target",
            (MODEL_VERSION, symbol),
        ).fetchall()
    if scores:
        brier = sum((p-y)**2 for p,b,y in scores) / len(scores)
        pre_brier = sum((b-y)**2 for p,b,y in scores) / len(scores)
        result["prospective_count"] = len(scores)
        result["prospective_brier"] = brier
        result["prospective_preopen_brier"] = pre_brier
        result["prospective_gain"] = pre_brier - brier
    else:
        result["prospective_count"] = 0
    return result


def estimate(symbol, item, now=None):
    now = time.time() if now is None else now
    target_open_ts = int(item.get("target_open") or 0)
    target_close_ts = int(item.get("target_close") or 0)
    target_date = item.get("target_date")
    if not target_open_ts or not target_close_ts or not target_date:
        return {"available": False, "status": "거래일 정보 확인 중", "model_version": MODEL_VERSION}
    available_from = target_open_ts + OPEN_GRACE_SECONDS
    if now < available_from:
        return {
            "available": False,
            "status": "개장 후 5분부터 제공",
            "model_version": MODEL_VERSION,
            "available_from": available_from,
            "target_date": target_date,
        }
    if now >= target_close_ts:
        return {
            "available": False,
            "status": "정규장 종료 · 결과 확정 대기",
            "model_version": MODEL_VERSION,
            "target_date": target_date,
        }

    key = (symbol, target_date, item.get("data_digest"))
    cached = CACHE.get(key)
    if cached:
        return dict(cached)

    completed_rows, meta = base.fetch_history(symbol, now)
    if meta["target_date"] != target_date:
        raise ValueError("타깃 거래일 불일치")
    dates = [d for d, _ in completed_rows]
    closes = [p for _, p in completed_rows]
    ohlc = _daily_ohlc(symbol)
    if target_date not in ohlc:
        return {
            "available": False,
            "status": "당일 공식 시가 확인 중",
            "model_version": MODEL_VERSION,
            "available_from": available_from,
            "target_date": target_date,
        }

    # Historical opens and validated closes must align on the same price basis.
    hist_dates = [d for d in dates if d in ohlc and ohlc[d].get("close") is not None]
    if hist_dates != dates:
        raise ValueError("개장후 모델 OHLC 거래일 누락")
    opens = [ohlc[d]["open"] for d in dates]
    raw_closes = [ohlc[d]["close"] for d in dates]
    max_basis_error = max(abs(r/c - 1.0) for r, c in zip(raw_closes, closes))
    if max_basis_error > 0.002:
        raise ValueError("개장후 모델 가격기준 불일치")

    config = CONFIG_BY_SYMBOL[symbol]
    fitted = _fit_live(
        opens, closes, dates, target_date, ohlc[target_date]["open"], item["probability"], config
    )
    result = {
        "available": True,
        "status": "개장후 시가 반영",
        "model_version": MODEL_VERSION,
        "target_date": target_date,
        "as_of": item.get("as_of"),
        "computed_at": int(now),
        "available_from": available_from,
        "target_close": target_close_ts,
        "price_basis_check": "passed",
        **fitted,
    }
    try:
        result = _score_and_record(symbol, item, result, completed_rows, now)
    except Exception as exc:
        result["prospective_error"] = "개장후 실시간 검증 기록 일시 중단"
        print("open nowcast ledger unavailable", symbol, type(exc).__name__, flush=True)
    CACHE[key] = dict(result)
    return result


def enrich(payload, now=None):
    now = time.time() if now is None else now
    out = dict(payload)
    items = {}
    for index_id, item0 in (payload.get("items") or {}).items():
        item = dict(item0)
        symbol = item.get("symbol") or base.SYMBOLS.get(index_id)
        if item.get("error") or symbol not in CONFIG_BY_SYMBOL:
            item["after_open"] = {"available": False, "status": "기본 확률 계산 중", "model_version": MODEL_VERSION}
        else:
            try:
                item["after_open"] = estimate(symbol, item, now)
            except Exception as exc:
                item["after_open"] = {"available": False, "status": "개장후 확률 데이터 확인 중", "model_version": MODEL_VERSION}
                print("open nowcast unavailable", symbol, type(exc).__name__, str(exc), flush=True)
        items[index_id] = item
    out["items"] = items
    out["after_open_model_version"] = MODEL_VERSION
    return out
