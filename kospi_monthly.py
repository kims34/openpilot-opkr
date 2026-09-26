"""KOSPI one-month probability analysis.

Current KOSPI display quotes come from Naver in production_fixed.  This module
uses ten years of completed KOSPI daily history for the statistical 21-session
analysis, aligned to Asia/Seoul, and reconciles the latest completed close with
Naver when available.
"""
import math
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import one_month_distribution
import one_month_probability
import production_fixed

SYMBOL = "^KS11"
INDEX_ID = "kospi100"  # legacy wire id; visible label is KOSPI only
SEOUL = ZoneInfo("Asia/Seoul")
CACHE_SECONDS = 15 * 60
CACHE = {"updated": 0.0, "item": {}}
LOCK = threading.Lock()


def _history_rows():
    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}",
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert/2.9"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json().get("chart", {})
    if payload.get("error"):
        raise RuntimeError("KOSPI history provider error")
    result = (payload.get("result") or [None])[0]
    if not result:
        raise RuntimeError("KOSPI history unavailable")
    timestamps = result.get("timestamp") or []
    closes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    if len(timestamps) != len(closes):
        raise RuntimeError("KOSPI history length mismatch")

    by_day = {}
    for ts, price in zip(timestamps, closes):
        if price is None:
            continue
        p = float(price)
        if not math.isfinite(p) or p <= 0:
            continue
        day = datetime.fromtimestamp(int(ts), timezone.utc).astimezone(SEOUL).date().isoformat()
        by_day[day] = p

    # Naver is authoritative for the visible current KOSPI card.  When the
    # latest Naver trading day is complete, use that same close as the final
    # observation so the probability card and index card share one anchor.
    try:
        current, previous, change, ratio, high, value_ts, market_state = production_fixed._naver_kospi_quote()
        naver_day = datetime.fromtimestamp(int(value_ts), timezone.utc).astimezone(SEOUL).date().isoformat()
        if market_state == "CLOSED" and current > 0:
            by_day[naver_day] = float(current)
        elif market_state == "REGULAR":
            # Never feed an unfinished intraday close into the monthly model.
            by_day.pop(naver_day, None)
    except Exception as exc:
        print("kospi monthly Naver reconciliation failed", type(exc).__name__, flush=True)

    rows = sorted(by_day.items())
    if len(rows) < 1100:
        raise RuntimeError("KOSPI monthly history insufficient")
    if any(abs(b / a - 1.0) > 0.40 for (_, a), (_, b) in zip(rows, rows[1:])):
        raise RuntimeError("KOSPI history discontinuity")
    return rows


def estimate():
    rows = _history_rows()
    try:
        ohlc = one_month_probability.fetch_ohlc(SYMBOL, rows, "Asia/Seoul")
        month = one_month_probability.estimate(rows, ohlc)
    except Exception as exc:
        print("kospi monthly OHLC fallback", type(exc).__name__, flush=True)
        month = one_month_probability.estimate(rows)

    month.update(one_month_distribution.estimate(rows))
    month.update(
        index_id=INDEX_ID,
        name="KOSPI",
        symbol=SYMBOL,
        source="KOSPI 최근 10년 일봉 · 현재 종가 네이버 증권 교차확인",
    )
    print(
        "kospi one-month probability ready",
        {
            "as_of": month.get("as_of"),
            "up10": month.get("up_10_probability"),
            "down10": month.get("down_10_probability"),
            "top3": month.get("terminal_return_top3"),
            "basis": month.get("price_basis"),
        },
        flush=True,
    )
    return month


def refresh(force=False):
    if not LOCK.acquire(blocking=False):
        return dict(CACHE)
    try:
        if not force and CACHE["item"] and time.time() - CACHE["updated"] < CACHE_SECONDS:
            return dict(CACHE)
        try:
            item = estimate()
        except Exception as exc:
            print("kospi one-month probability unavailable", type(exc).__name__, str(exc), flush=True)
            previous = CACHE.get("item") or {}
            item = dict(previous) if previous else {"error": "KOSPI 1개월 분석 계산 중"}
        CACHE.update(item=item, updated=time.time())
        return dict(CACHE)
    finally:
        LOCK.release()


def get_all():
    if not CACHE["item"]:
        refresh(True)
    elif time.time() - CACHE["updated"] >= CACHE_SECONDS:
        threading.Thread(target=refresh, daemon=True).start()
    return {"items": {INDEX_ID: CACHE["item"]}, "updated_at": CACHE["updated"]}
