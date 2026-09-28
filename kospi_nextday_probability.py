"""Guarded next-session KOSPI probability using completed KRX closes only.

The same causal 3.3 calibration gate used for the US ETF cards is re-fit on
KOSPI's own history.  Nothing is promoted merely because the US model worked:
all audit/Brier decisions are recomputed on ^KS11.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from functools import lru_cache

import exchange_calendars as xcals

import kospi_monthly
import next_day_probability as ledger
from probability_model_v33_runtime import estimate_prices

SYMBOL = "^KS11"
INDEX_ID = "kospi100"
MODEL_VERSION = "3.3-calibration-gated-kospi"
CACHE_SECONDS = 15 * 60
CACHE = {"updated": 0.0, "item": {}}
LOCK = threading.Lock()


@lru_cache(maxsize=2)
def _calendar(year: int):
    return xcals.get_calendar("XKRX", start=f"{year-11}-01-01", end=f"{year+2}-12-31")


def _target_info(as_of: str):
    year = datetime.now(timezone.utc).year
    cal = _calendar(year)
    if not cal.is_session(as_of):
        raise ValueError("KOSPI 완료 거래일 캘린더 불일치")
    target = cal.next_session(as_of)
    target_open = int(cal.session_open(target).timestamp())
    target_close = int(cal.session_close(target).timestamp())
    return target.date().isoformat(), target_open, target_close


def estimate(now: float | None = None):
    now = time.time() if now is None else float(now)
    rows = kospi_monthly._history_rows()
    dates = [d for d, _ in rows]
    prices = [float(p) for _, p in rows]
    if len(prices) < 1100:
        raise ValueError("KOSPI 일봉 이력 부족")

    as_of = dates[-1]
    target_date, target_open, target_close = _target_info(as_of)
    result = estimate_prices(prices, dates=dates, target_date=target_date)
    result["audit_start"] = rows[result.pop("audit_start_index")][0]
    result["audit_end"] = rows[result.pop("audit_end_index")][0]
    result.pop("as_of_index", None)
    result.update(
        index_id=INDEX_ID,
        symbol=SYMBOL,
        name="KOSPI",
        as_of=as_of,
        target_date=target_date,
        target_open=target_open,
        target_close=target_close,
        valid_until=target_close + 15 * 60,
        history_points=len(rows),
        computed_at=int(now),
        data_digest=hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest(),
        model_version=MODEL_VERSION,
        underlying_model_version="3.3-calibration-gated",
        data_quality="completed_close_only",
        price_basis="KOSPI price index close",
    )

    # Keep a prospective ledger exactly like the US cards.  The ledger helper
    # does not depend on the NYSE calendar once target timestamps are supplied.
    try:
        result.update(ledger.record_forecast(SYMBOL, result, rows, now))
    except Exception as exc:
        result.update(prospective_count=0, prospective_error="KOSPI 실시간 검증 기록 일시 중단")
        print("kospi next-day ledger unavailable", type(exc).__name__, flush=True)

    try:
        month_payload = kospi_monthly.get_all()
        month = (month_payload.get("items") or {}).get(INDEX_ID)
        if month and not month.get("error"):
            result["one_month"] = month
    except Exception:
        pass
    return result


def refresh(force: bool = False):
    if not LOCK.acquire(blocking=False):
        return dict(CACHE)
    try:
        if not force and CACHE["item"] and time.time() - CACHE["updated"] < CACHE_SECONDS:
            return dict(CACHE)
        try:
            item = estimate()
        except Exception as exc:
            print("kospi next-day probability unavailable", type(exc).__name__, str(exc), flush=True)
            previous = CACHE.get("item") or {}
            item = dict(previous) if previous else {"symbol": SYMBOL, "error": "KOSPI 다음 거래일 확률 계산 중"}
        CACHE.update(item=item, updated=time.time())
        return dict(CACHE)
    finally:
        LOCK.release()


def get_item():
    if not CACHE["item"]:
        refresh(True)
    elif time.time() - CACHE["updated"] >= CACHE_SECONDS:
        threading.Thread(target=refresh, daemon=True).start()
    return dict(CACHE["item"])
