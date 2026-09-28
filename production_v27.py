"""IndexAlert production v2.9: corrected Naver KPI100 scaling + Naver history ATH."""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone

import monitor
import production
import production_v26

app = production_v26.app
SEOUL = production_v26.SEOUL

NAVER_STOCK_BASE = "https://stock.naver.com"
NAVER_NEW_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://stock.naver.com/domestic/index/KPI100/price",
    "Accept": "application/json,text/plain,*/*",
}

_base_init_db = monitor.init_db


def _init_db_v27():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-naver-history-v27'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-naver-history-v27')")


monitor.init_db = _init_db_v27


def _poll_hundredth(value):
    if value is None:
        return None
    try:
        # Naver SERVICE_INDEX numeric price fields are integer hundredths.
        return float(str(value).replace(",", "")) / 100.0
    except Exception:
        return None


def _decimal(value):
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except Exception:
        return None


def _polling_kpi100_fixed():
    data, url = production_v26._polling_data("KPI100")
    if not data:
        raise RuntimeError("Naver KPI100 realtime unavailable")

    current = _poll_hundredth(data.get("nv"))
    change = _poll_hundredth(data.get("cv"))
    rate = _decimal(data.get("cr"))
    day_high = _poll_hundredth(data.get("hv"))
    if current is None or current <= 0:
        raise RuntimeError("Naver KPI100 realtime current invalid")

    rf = str(data.get("rf") or "")
    change = float(change or 0.0)
    rate = float(rate or 0.0)
    if rf == "5":
        change, rate = -abs(change), -abs(rate)
    elif rf == "2":
        change, rate = abs(change), abs(rate)

    previous = current - change
    if previous <= 0:
        previous = current / (1.0 + rate / 100.0) if abs(rate) < 99 else current
        change = current - previous
    if day_high is None or day_high <= 0:
        day_high = current

    ms = str(data.get("ms") or "").upper()
    state = "REGULAR" if ms in {"OPEN", "OPENED", "REGULAR"} else "CLOSED"
    ts = int(datetime.now(SEOUL).timestamp())
    print(
        "KPI100 naver realtime",
        {
            "current": current,
            "previous": previous,
            "change": change,
            "rate": rate,
            "day_high": day_high,
            "market_status": ms,
            "rf": rf,
            "url": url,
        },
        flush=True,
    )
    return current, previous, change, rate, day_high, None, ts, state


def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk(value)


def _price_from_record(record, keys):
    for key in keys:
        if key not in record:
            continue
        value = record.get(key)
        x = _decimal(value)
        if x is None:
            continue
        # New stock.naver JSON usually uses formatted decimals. If a numeric
        # integer is obviously hundredth-scaled, normalize it conservatively.
        if isinstance(value, (int, float)) and abs(x) >= 100000:
            x /= 100.0
        return x
    return None


def _date_from_record(record):
    for key in ("localDate", "businessDay", "tradeDate", "date", "localTradedAt"):
        raw = str(record.get(key) or "")
        m = re.search(r"(20\d{2})[-./]?(\d{2})[-./]?(\d{2})", raw)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=SEOUL)
            except Exception:
                pass
    return None


def _naver_history_ath():
    candidates = []
    endpoints = [
        (f"{NAVER_STOCK_BASE}/api/securityFe/api/index/KPI100/price", {"page": 1, "pageSize": 500}),
        ("https://m.stock.naver.com/front-api/stock/domestic/index/price/list", {"code": "KPI100", "page": 1, "pageSize": 500}),
    ]
    for url, params in endpoints:
        try:
            r = monitor.requests.get(url, params=params, headers=NAVER_NEW_HEADERS, timeout=15)
            print("KPI100 history source", r.status_code, r.url, len(r.content or b""), flush=True)
            r.raise_for_status()
            root = r.json()
            count = 0
            for rec in _walk(root):
                high = _price_from_record(rec, ("highPrice", "high", "hv", "highestPrice"))
                close = _price_from_record(rec, ("closePrice", "close", "nv"))
                value = high if high is not None and high > 0 else close
                if value is None or not math.isfinite(value) or value <= 0:
                    continue
                date = _date_from_record(rec)
                candidates.append((float(value), int(date.timestamp()) if date else 0, r.url))
                count += 1
            print("KPI100 history parsed", count, flush=True)
            if count >= 20:
                break
        except Exception as exc:
            print("KPI100 history source failed", type(exc).__name__, url, flush=True)

    # New Naver basic endpoint may expose a 52-week high even when paginated
    # history is truncated. Include any recognizable high-like field.
    try:
        url = f"{NAVER_STOCK_BASE}/api/securityFe/api/index/KPI100/basic"
        r = monitor.requests.get(url, headers=NAVER_NEW_HEADERS, timeout=12)
        print("KPI100 basic source", r.status_code, len(r.content or b""), flush=True)
        r.raise_for_status()
        for rec in _walk(r.json()):
            for key in (
                "highestPriceOf52Weeks", "highPriceOf52Weeks", "fiftyTwoWeekHigh",
                "highestPrice52Weeks", "yearHighPrice", "high52WeekPrice",
            ):
                if key in rec:
                    value = _price_from_record(rec, (key,))
                    if value and value > 0:
                        candidates.append((float(value), 0, url + "#52w"))
    except Exception as exc:
        print("KPI100 basic source failed", type(exc).__name__, flush=True)

    if not candidates:
        raise RuntimeError("Naver KPI100 history unavailable")
    best = max(candidates, key=lambda x: x[0])
    print("KPI100 Naver ATH", {"ath": best[0], "ts": best[1], "source": best[2], "candidates": len(candidates)}, flush=True)
    return best[0], best[1]


def _evaluate_kpi100(index_id):
    current, previous, change, rate, day_high, _, ts, state = _polling_kpi100_fixed()
    stored = monitor.get_state(index_id)
    old_ath = float(stored[0]) if stored and stored[0] else 0.0
    ath = max(old_ath, current, day_high)
    ath_ts = 0

    try:
        naver_ath, naver_ts = _naver_history_ath()
        if naver_ath > ath:
            ath, ath_ts = float(naver_ath), int(naver_ts or 0)
    except Exception as exc:
        print("KPI100 Naver ATH unavailable", type(exc).__name__, flush=True)
        # Historical Yahoo is a fallback only; current quote never comes from it.
        try:
            hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
            if math.isfinite(hist_ath) and hist_ath > ath:
                ath, ath_ts = float(hist_ath), int(hist_ts or 0)
        except Exception:
            pass

    if day_high >= ath:
        ath, ath_ts = day_high, ts

    dd = (current / ath - 1.0) * 100.0 if ath > 0 else None
    ath_date = (
        datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(SEOUL).date().isoformat()
        if ath_ts else None
    )
    source = "KOSPI100 실시간/전일대비 · 네이버 증권 KPI100"
    monitor.save_state(index_id, ath, current, current, source)
    production.EXTRA_STATE[index_id] = {
        "previous_close": previous,
        "day_change": change,
        "day_change_percent": rate,
        "ath_date": ath_date,
        "ath_days": production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None,
        "drawdown": dd,
        "market_state": state,
        "value_ts": ts,
        "extended_display": False,
        "extended_estimate": False,
        "actual_extended_trade": False,
    }
    result = {
        "id": index_id,
        "name": "KOSPI 100",
        "value": current,
        "cash": current,
        "ath": ath,
        "drawdown": dd,
        "source": source,
        "market_state": state,
        "cash_ts": ts,
        "value_ts": ts,
        **production.EXTRA_STATE[index_id],
    }
    print("KPI100 final check", result, flush=True)
    return result


# Patch the dynamic evaluator used by the established scheduler/routes.
production_v24 = production_v26.production_v24
production_v24._evaluate_kospi100 = _evaluate_kpi100
