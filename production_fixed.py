import html as html_lib
import math
import re
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import monitor
import production

# Preserve the hardened production app/routes and only replace KOSPI100 handling.
app = production.app
_original_init_db = monitor.init_db

# Verified 52-week high seen on Naver/KRX-derived public data in 2026.
# This is a safety floor for ATH, never a ceiling.
KOSPI100_VERIFIED_ATH_FLOOR = 11932.83
NAVER_KOSPI100_URL = "https://finance.naver.com/sise/sise_index.naver?code=KPI100"
NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}


def _init_db_with_kospi_ath_fix():
    _original_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-naver-primary-v4'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-naver-primary-v4')")


monitor.init_db = _init_db_with_kospi_ath_fix
_original_evaluate = monitor.evaluate


def _clean_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _number(raw: str):
    m = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", raw or "")
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except Exception:
        return None


def _naver_kospi100_quote():
    r = monitor.requests.get(NAVER_KOSPI100_URL, headers=NAVER_HEADERS, timeout=15)
    r.raise_for_status()
    # Naver Finance legacy pages are commonly served as euc-kr/cp949.
    if not r.encoding or r.encoding.lower() in {"iso-8859-1", "ascii"}:
        r.encoding = "euc-kr"
    page = r.text

    m = re.search(r'id=["\']now_value["\'][^>]*>(.*?)</', page, re.I | re.S)
    if not m:
        raise RuntimeError("naver KOSPI100 now_value missing")
    current = _number(_clean_text(m.group(1)))
    if not current or current <= 0:
        raise RuntimeError("naver KOSPI100 current invalid")

    # Read a bounded chunk around change_value_and_rate. Its child span carries
    # the absolute move and direction text (상승/하락). Derive previous close so
    # current, absolute change, and percentage stay internally consistent.
    change = 0.0
    cm = re.search(r'id=["\']change_value_and_rate["\']', page, re.I)
    if cm:
        chunk = _clean_text(page[cm.start():cm.start() + 900])
        raw_change = _number(chunk)
        if raw_change is not None:
            if "하락" in chunk:
                change = -abs(raw_change)
            elif "상승" in chunk:
                change = abs(raw_change)
            else:
                change = raw_change
    previous_close = current - change
    if previous_close <= 0:
        previous_close = current
        change = 0.0
    change_pct = (current / previous_close - 1.0) * 100.0 if previous_close > 0 else 0.0

    flat = _clean_text(page)
    high52 = None
    hm = re.search(r"52주최고\s*([0-9][0-9,]*(?:\.\d+)?)", flat)
    if hm:
        high52 = _number(hm.group(1))

    # Naver's page is KRX/Koscom-fed. Timestamp the successful fetch rather
    # than inventing an exchange print timestamp.
    now_ts = int(time.time())
    print("kospi100 naver quote", {
        "current": current,
        "previous_close": previous_close,
        "day_change": change,
        "day_change_percent": change_pct,
        "high52": high52,
    }, flush=True)
    return current, previous_close, change, change_pct, high52, now_ts


def _history_candidates(symbol: str, naver_high52=None):
    candidates = [(KOSPI100_VERIFIED_ATH_FLOOR, 0, "verified-52w-floor")]
    if naver_high52 and math.isfinite(float(naver_high52)) and float(naver_high52) > 0:
        candidates.append((float(naver_high52), 0, "naver-52w"))

    try:
        value, ts = production._history_ath(symbol)
        if math.isfinite(value) and value > 0:
            candidates.append((float(value), int(ts or 0), "yahoo-max"))
    except Exception as exc:
        print("kospi100 production history failed", type(exc).__name__, flush=True)

    try:
        result = monitor.yahoo_result(symbol, "1y", "1d", False)
        timestamps = result.get("timestamp") or []
        highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
        best = 0.0
        best_ts = 0
        for ts, high in zip(timestamps, highs):
            if high is None:
                continue
            h = float(high)
            if math.isfinite(h) and h > 0 and h >= best:
                best = h
                best_ts = int(ts)
        if best > 0:
            candidates.append((best, best_ts, "yahoo-1y"))
    except Exception as exc:
        print("kospi100 1y crosscheck failed", type(exc).__name__, flush=True)
    return candidates


def _kospi100_ath(naver_high52=None):
    candidates = _history_candidates("KOSPI100.KS", naver_high52)
    best_value, best_ts, source = max(candidates, key=lambda x: x[0])
    print("kospi100 ATH crosscheck", {"ath": best_value, "ts": best_ts, "source": source, "candidates": candidates}, flush=True)
    return best_value, best_ts


def _evaluate(index_id: str):
    if index_id != "kospi100":
        return _original_evaluate(index_id)

    rule = monitor.RULES[index_id]
    source = "네이버 증권 KPI100 · KRX/Koscom"
    market_state = "REGULAR"
    try:
        value, previous_close, day_change, day_change_percent, high52, value_ts = _naver_kospi100_quote()
    except Exception as exc:
        print("kospi100 naver quote failed", type(exc).__name__, str(exc), flush=True)
        # Fallback only. Yahoo's Korean index can be delayed or mapped
        # inconsistently, so make the fallback explicit in the source label.
        cash_result = monitor.yahoo_result(rule["cash"], prepost=False)
        points = monitor.series(cash_result)
        if not points:
            raise RuntimeError("no KOSPI100 prices")
        value_ts, value = points[-1]
        meta = cash_result.get("meta", {})
        previous_close = production._previous_close(meta, value)
        day_change = value - previous_close
        day_change_percent = (value / previous_close - 1.0) * 100.0 if previous_close > 0 else 0.0
        high52 = None
        market_state = monitor.session_state(meta)
        source = "Yahoo KOSPI100 보조 조회"

    ath, ath_ts = _kospi100_ath(high52)
    ath = max(ath, value)
    if ath == value and not ath_ts:
        ath_ts = value_ts

    if not math.isfinite(ath) or ath <= 0 or not math.isfinite(value) or value <= 0:
        raise RuntimeError("invalid KOSPI100 data")

    drawdown = (value / ath - 1.0) * 100.0
    tz = ZoneInfo("Asia/Seoul")
    ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat() if ath_ts else None

    monitor.save_state(index_id, ath, value, value, source)
    production.EXTRA_STATE[index_id] = {
        "previous_close": previous_close,
        "day_change": day_change,
        "day_change_percent": day_change_percent,
        "ath_date": ath_date,
        "ath_days": production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None,
        "drawdown": drawdown,
        "market_state": market_state,
        "value_ts": value_ts,
    }
    return {
        "id": index_id,
        "name": rule["name"],
        "value": value,
        "cash": value,
        "ath": ath,
        "drawdown": drawdown,
        "source": source,
        "market_state": market_state,
        "cash_ts": value_ts,
        "value_ts": value_ts,
        **production.EXTRA_STATE[index_id],
    }


monitor.evaluate = _evaluate
