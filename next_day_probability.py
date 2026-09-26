"""Validated daily-close forecasts and an append-only prospective score ledger."""
import hashlib
import json
import math
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import pandas as pd
import requests
from probability_model import MODEL_VERSION, estimate_prices

SYMBOLS = {"sp500": "SPY", "ndx": "QQQ", "djdiv": "SCHD"}
CACHE_SECONDS = 15 * 60
CACHE = {"updated": 0.0, "items": {}}
INFERENCE_CACHE = {}
LOCK = threading.Lock()
NY = ZoneInfo("America/New_York")
CLOSE_GRACE_SECONDS = 15 * 60
DB_PATH = os.getenv("INDEXALERT_DB", "/tmp/indexalert.db")


@lru_cache(maxsize=2)
def calendar(year):
    return xcals.get_calendar("XNYS", start=f"{year-11}-01-01", end=f"{year+2}-12-31")


def completed_session_info(now=None):
    """Return the latest exchange session whose close is safely complete."""
    now = time.time() if now is None else now
    cal = calendar(datetime.fromtimestamp(now, timezone.utc).year)
    schedule = cal.schedule
    completed = schedule[schedule['close'] <= pd.Timestamp(now - CLOSE_GRACE_SECONDS, unit='s', tz='UTC')]
    if completed.empty:
        raise ValueError('완료된 거래일 없음')
    expected_last = completed.index[-1].date().isoformat()
    target = cal.next_session(expected_last)
    return cal, expected_last, target


def parse_history(result, now=None):
    now = time.time() if now is None else now
    cal, expected_last, target = completed_session_info(now)
    timestamps = result.get('timestamp') or []
    closes = (result.get('indicators', {}).get('quote') or [{}])[0].get('close') or []
    if len(timestamps) != len(closes):
        raise ValueError('가격·날짜 개수 불일치')
    rows, seen = [], set()
    for ts, price in zip(timestamps, closes):
        day = datetime.fromtimestamp(int(ts), timezone.utc).astimezone(NY).date().isoformat()
        # Never use today's unfinished daily bar or any future-dated vendor bar.
        if day > expected_last:
            continue
        if day in seen:
            raise ValueError('중복 거래일')
        seen.add(day)
        if not cal.is_session(day):
            raise ValueError('거래일 아닌 가격')
        if price is None or not math.isfinite(float(price)) or float(price) <= 0:
            raise ValueError('누락·비정상 종가')
        rows.append((day, float(price)))
    if len(rows) < 1100 or rows != sorted(rows):
        raise ValueError('거래일 이력 부족 또는 순서 오류')
    if not rows or rows[-1][0] != expected_last:
        raise ValueError('최신 완료 종가 지연')
    expected = [d.date().isoformat() for d in cal.sessions_in_range(rows[0][0], expected_last)]
    if [day for day,_ in rows] != expected:
        raise ValueError('최신 종가 지연 또는 중간 거래일 누락')
    if any(abs(b/a - 1) > 0.40 for (_,a),(_,b) in zip(rows,rows[1:])):
        raise ValueError('가격 단위·분할 조정 확인 필요')
    return rows, dict(
        as_of=expected_last,
        target_date=target.date().isoformat(),
        target_open=int(cal.session_open(target).timestamp()),
        target_close=int(cal.session_close(target).timestamp()),
        valid_until=int(cal.session_close(target).timestamp()) + CLOSE_GRACE_SECONDS,
        history_points=len(rows),
        latest_completed_session=expected_last,
        data_quality='completed_close_only',
        incomplete_session_excluded=True,
    )


def fetch_history(symbol, now=None):
    response = requests.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',
        params={'range':'10y','interval':'1d','includePrePost':'false','events':'div,splits'},
        headers={'User-Agent':'Mozilla/5.0 IndexAlert/3.2'},timeout=20)
    response.raise_for_status()
    payload = response.json().get('chart',{})
    if payload.get('error'):
        raise ValueError('시세 공급자 오류')
    result = (payload.get('result') or [None])[0]
    if not result or result.get('meta',{}).get('symbol') != symbol:
        raise ValueError('종목 데이터 불일치')
    return parse_history(result, now)


def _prospective_metrics(scores):
    if not scores:
        return dict(
            prospective_count=0,
            prospective_brier=None,
            prospective_baseline_brier=None,
            prospective_skill=None,
            prospective_direction_accuracy=None,
            prospective_mean_probability=None,
            prospective_observed_rise_rate=None,
            prospective_status='수집 중',
        )
    n = len(scores)
    model_brier = sum((p-y)**2 for p,b,y in scores) / n
    base_brier = sum((b-y)**2 for p,b,y in scores) / n
    skill = (1 - model_brier / base_brier) * 100 if base_brier > 0 else None
    direction_accuracy = sum(int((p >= 0.5) == bool(y)) for p,b,y in scores) / n * 100
    mean_probability = sum(p for p,b,y in scores) / n * 100
    observed = sum(y for p,b,y in scores) / n * 100
    status = '수집 중' if n < 20 else ('초기 실시간 검증' if n < 60 else '누적 실시간 검증')
    return dict(
        prospective_count=n,
        prospective_brier=model_brier,
        prospective_baseline_brier=base_brier,
        prospective_skill=skill,
        prospective_direction_accuracy=direction_accuracy,
        prospective_mean_probability=mean_probability,
        prospective_observed_rise_rate=observed,
        prospective_status=status,
    )


def record_forecast(symbol, result, rows, now):
    """Record first pre-open forecast immutably, then score it after the target close."""
    with sqlite3.connect(DB_PATH, timeout=10) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS probability_forecasts(
            model TEXT,symbol TEXT,as_of TEXT,target TEXT,p REAL,base REAL,
            created REAL,outcome INTEGER,scored_at REAL,
            PRIMARY KEY(model,symbol,as_of))''')
        prices = dict(rows)
        pending = con.execute(
            'SELECT model,as_of,target FROM probability_forecasts WHERE symbol=? AND outcome IS NULL',
            (symbol,)
        ).fetchall()
        for model,as_of,target in pending:
            if as_of in prices and target in prices:
                con.execute(
                    'UPDATE probability_forecasts SET outcome=?,scored_at=? WHERE model=? AND symbol=? AND as_of=? AND outcome IS NULL',
                    (int(prices[target] > prices[as_of]),now,model,symbol,as_of)
                )
        # Only the first forecast made before target open is preserved.
        if now < result['target_open']:
            con.execute('INSERT OR IGNORE INTO probability_forecasts VALUES(?,?,?,?,?,?,?,NULL,NULL)',
                (MODEL_VERSION,symbol,result['as_of'],result['target_date'],result['probability']/100,result['base_rate']/100,now))
        scores = con.execute(
            'SELECT p,base,outcome FROM probability_forecasts WHERE model=? AND symbol=? AND outcome IS NOT NULL ORDER BY target',
            (MODEL_VERSION,symbol)
        ).fetchall()
        last_scored = con.execute(
            'SELECT MAX(target) FROM probability_forecasts WHERE model=? AND symbol=? AND outcome IS NOT NULL',
            (MODEL_VERSION,symbol)
        ).fetchone()[0]
    metrics = _prospective_metrics(scores)
    metrics['prospective_last_scored_target'] = last_scored
    return metrics


def estimate(symbol, now=None):
    now = time.time() if now is None else now
    rows, meta = fetch_history(symbol, now)
    digest = hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
    cached = INFERENCE_CACHE.get(symbol)
    if cached and cached[0] == digest:
        result = dict(cached[1])
    else:
        result = estimate_prices([p for _,p in rows], dates=[d for d,_ in rows])
        result['audit_start'] = rows[result.pop('audit_start_index')][0]
        result['audit_end'] = rows[result.pop('audit_end_index')][0]
        result.pop('as_of_index')
        INFERENCE_CACHE[symbol] = (digest,dict(result))
    result.update(meta,symbol=symbol,data_digest=digest,computed_at=int(now))
    try:
        result.update(record_forecast(symbol,result,rows,now))
    except Exception as exc:
        result.update(prospective_count=0,prospective_error='실시간 검증 기록 일시 중단')
        print('probability ledger unavailable',type(exc).__name__,flush=True)
    return result


def _cache_still_matches_completed_session(value, now):
    if value.get('valid_until',0) <= now or 'probability' not in value:
        return False
    try:
        _, expected_last, _ = completed_session_info(now)
    except Exception:
        return False
    return value.get('as_of') == expected_last


def refresh(force=False):
    if not LOCK.acquire(blocking=False):
        return dict(CACHE,model_version=MODEL_VERSION)
    try:
        if not force and CACHE['items'] and time.time() - CACHE['updated'] < CACHE_SECONDS:
            return dict(CACHE,model_version=MODEL_VERSION)
        items = {}
        for index_id,symbol in SYMBOLS.items():
            try:
                items[index_id] = estimate(symbol)
            except Exception as exc:
                now = time.time()
                previous = CACHE['items'].get(index_id,{})
                if _cache_still_matches_completed_session(previous, now):
                    items[index_id] = dict(previous,cached=True,cache_reason='공급자 일시 오류 · 동일 완료 거래일 검증값 유지')
                else:
                    items[index_id] = dict(symbol=symbol,error='완료된 최신 종가 데이터 확인 중')
                print('probability unavailable',symbol,type(exc).__name__,flush=True)
        CACHE.update(items=items,updated=time.time())
        print('probability audit ready',MODEL_VERSION,{k:(v.get('probability'),v.get('backtest_skill'),v.get('validation_choice'),v.get('fallback_to_base')) for k,v in items.items()},flush=True)
        return dict(CACHE,model_version=MODEL_VERSION)
    finally:
        LOCK.release()


def get_all():
    now = time.time()
    if now - CACHE['updated'] >= CACHE_SECONDS:
        threading.Thread(target=refresh,daemon=True).start()
    items = {}
    for index_id,symbol in SYMBOLS.items():
        value = CACHE['items'].get(index_id,{})
        items[index_id] = value if _cache_still_matches_completed_session(value, now) else dict(symbol=symbol,error='최신 검증값 계산 중')
    return dict(items=items,updated_at=CACHE['updated'],model_version=MODEL_VERSION)
