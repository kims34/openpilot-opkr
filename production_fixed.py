import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import monitor
import production
from fastapi import HTTPException

app = production.app
_original_init_db = monitor.init_db
_original_evaluate = monitor.evaluate

NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}
NAVER_KOSPI_URL = "https://polling.finance.naver.com/api/realtime/domestic/index/KOSPI"
NAVER_USDKRW_URL = "https://api.stock.naver.com/marketindex/exchange/FX_USDKRW"

# Keep the historical internal id for backward compatibility with already-installed
# clients, but it now represents the KOSPI composite index, not KOSPI100.
monitor.RULES["kospi100"] = {
    "name": "KOSPI",
    "cash": "^KS11",
    "proxy": None,
    "levels": [],
    "regular_label": "KOSPI · 네이버 증권",
    "proxy_label": "KOSPI · 네이버 증권",
    "extended": False,
    "timezone": "Asia/Seoul",
}
monitor.RULES["usdkrw"] = {
    "name": "USD/KRW 달러 환율",
    "cash": "KRW=X",
    "proxy": None,
    "levels": [],
    "regular_label": "네이버 증권 · 하나은행 고시",
    "proxy_label": "네이버 증권 · 하나은행 고시",
    "extended": False,
    "timezone": "Asia/Seoul",
}


def _init_db_with_naver_market_fix():
    _original_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi-naver-v5'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi-naver-v5')")
        if not con.execute("SELECT 1 FROM migrations WHERE name='usdkrw-display-v1'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='usdkrw'")
            con.execute("DELETE FROM fired WHERE index_id='usdkrw'")
            con.execute("DELETE FROM deliveries WHERE index_id='usdkrw'")
            con.execute("INSERT INTO migrations(name) VALUES('usdkrw-display-v1')")


monitor.init_db = _init_db_with_naver_market_fix


def _num(value):
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except Exception:
        return None


def _signed(value, direction):
    v = _num(value)
    if v is None:
        return 0.0
    name = str(direction or "").upper()
    if "FALL" in name or "하락" in name:
        return -abs(v)
    if "RIS" in name or "상승" in name:
        return abs(v)
    return v


def _iso_ts(raw):
    try:
        return int(datetime.fromisoformat(str(raw)).timestamp())
    except Exception:
        return int(datetime.now(timezone.utc).timestamp())


def _naver_kospi_quote():
    r = monitor.requests.get(NAVER_KOSPI_URL, headers=NAVER_HEADERS, timeout=12)
    r.raise_for_status()
    datas = r.json().get("datas") or []
    if not datas:
        raise RuntimeError("Naver KOSPI quote unavailable")
    d = datas[0]
    current = _num(d.get("closePriceRaw") or d.get("closePrice"))
    if current is None or current <= 0:
        raise RuntimeError("Naver KOSPI current invalid")
    direction = ((d.get("compareToPreviousPrice") or {}).get("name") or
                 (d.get("compareToPreviousPrice") or {}).get("text"))
    change = _signed(d.get("compareToPreviousClosePriceRaw") or d.get("compareToPreviousClosePrice"), direction)
    ratio_raw = _num(d.get("fluctuationsRatioRaw") or d.get("fluctuationsRatio"))
    ratio = _signed(ratio_raw, direction) if ratio_raw is not None else 0.0
    previous = current - change
    if previous <= 0:
        previous = current
        change = 0.0
        ratio = 0.0
    high = _num(d.get("highPriceRaw") or d.get("highPrice")) or current
    ts = _iso_ts(d.get("localTradedAt"))
    market_state = "REGULAR" if str(d.get("marketStatus", "")).upper() == "OPEN" else "CLOSED"
    print("kospi naver quote", {"current": current, "previous": previous, "change": change, "ratio": ratio, "high": high}, flush=True)
    return current, previous, change, ratio, high, ts, market_state


def _evaluate_kospi(index_id: str):
    current, previous, change, ratio, day_high, value_ts, market_state = _naver_kospi_quote()
    tz = ZoneInfo("Asia/Seoul")
    today = datetime.now(tz).date().isoformat()
    state = monitor.get_state(index_id)
    old_ath = float(state[0]) if state and state[0] else 0.0
    ath = old_ath
    ath_ts = 0

    if ath <= 0 or monitor.ATH_REFRESH.get(index_id) != today:
        try:
            hist_ath, hist_ts = production._history_ath("^KS11")
            if hist_ath >= ath:
                ath = float(hist_ath)
                ath_ts = int(hist_ts or 0)
        except Exception as exc:
            print("kospi historical ATH failed", type(exc).__name__, flush=True)
        monitor.ATH_REFRESH[index_id] = today

    if day_high >= ath:
        ath = day_high
        ath_ts = value_ts
    if ath <= 0:
        ath = max(current, day_high)
        ath_ts = value_ts

    # Recover ATH date after restart when the stored ATH is still current.
    if ath_ts == 0:
        try:
            hist_ath, hist_ts = production._history_ath("^KS11")
            if abs(float(hist_ath) - ath) / max(ath, 1.0) < 0.002:
                ath_ts = int(hist_ts or 0)
        except Exception:
            pass

    drawdown = (current / ath - 1.0) * 100.0 if ath > 0 else None
    ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat() if ath_ts else None
    source = "KOSPI 현재/등락 · 네이버 증권"
    monitor.save_state(index_id, ath, current, current, source)
    production.EXTRA_STATE[index_id] = {
        "previous_close": previous,
        "day_change": change,
        "day_change_percent": ratio,
        "ath_date": ath_date,
        "ath_days": production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None,
        "drawdown": drawdown,
        "market_state": market_state,
        "value_ts": value_ts,
    }
    return {
        "id": index_id,
        "name": "KOSPI",
        "value": current,
        "cash": current,
        "ath": ath,
        "drawdown": drawdown,
        "source": source,
        "market_state": market_state,
        "cash_ts": value_ts,
        "value_ts": value_ts,
        **production.EXTRA_STATE[index_id],
    }


def _naver_usdkrw_quote():
    r = monitor.requests.get(NAVER_USDKRW_URL, headers=NAVER_HEADERS, timeout=12)
    r.raise_for_status()
    info = r.json().get("exchangeInfo") or {}
    current = _num(info.get("closePrice"))
    if current is None or current <= 0:
        raise RuntimeError("Naver USD/KRW current invalid")
    direction = ((info.get("fluctuationsType") or {}).get("name") or
                 (info.get("fluctuationsType") or {}).get("text"))
    change = _signed(info.get("fluctuations"), direction)
    ratio = _signed(info.get("fluctuationsRatio"), direction)
    previous = current - change
    if previous <= 0:
        previous = current
        change = 0.0
        ratio = 0.0
    value_ts = _iso_ts(info.get("localTradedAt"))
    market_state = str(info.get("marketStatus") or "").upper() or "UNKNOWN"
    print("usdkrw naver quote", {"current": current, "previous": previous, "change": change, "ratio": ratio}, flush=True)
    return current, previous, change, ratio, value_ts, market_state


def _evaluate_usdkrw(index_id: str):
    current, previous, change, ratio, value_ts, market_state = _naver_usdkrw_quote()
    source = "네이버 증권 · 하나은행 고시"
    now = datetime.now(timezone.utc).isoformat()
    production.EXTRA_STATE[index_id] = {
        "ath": None,
        "last_cash": current,
        "last_value": current,
        "source": source,
        "updated_at": now,
        "previous_close": previous,
        "day_change": change,
        "day_change_percent": ratio,
        "ath_date": None,
        "ath_days": None,
        "drawdown": None,
        "market_state": market_state,
        "value_ts": value_ts,
    }
    return {
        "id": index_id,
        "name": "USD/KRW 달러 환율",
        "value": current,
        "cash": current,
        "ath": None,
        "drawdown": None,
        "source": source,
        "market_state": market_state,
        "cash_ts": value_ts,
        "value_ts": value_ts,
        **production.EXTRA_STATE[index_id],
    }


def _evaluate(index_id: str):
    if index_id == "kospi100":
        return _evaluate_kospi(index_id)
    if index_id == "usdkrw":
        return _evaluate_usdkrw(index_id)
    return _original_evaluate(index_id)


monitor.evaluate = _evaluate

# production.register predates USD/KRW. Replace it so old v1.0 clients and the
# new client both satisfy monitor.register's exact RULES-key validation.
app.router.routes = [route for route in app.router.routes if getattr(route, "path", None) != "/register"]


@app.post("/register")
def register(body: monitor.RegisterBody):
    token = body.token.strip()
    if not (20 <= len(token) <= 4096):
        raise HTTPException(400, "invalid token")
    if body.platform != "android":
        raise HTTPException(400, "unsupported platform")
    if body.protocol not in (1, 2):
        raise HTTPException(400, "unsupported protocol")
    settings = dict(body.enabled_levels or {}) if body.enabled_levels is not None else None
    if settings is not None:
        settings.setdefault("kospi100", [])
        settings.setdefault("usdkrw", [])
        body = monitor.RegisterBody(
            token=body.token,
            platform=body.platform,
            enabled_levels=settings,
            protocol=body.protocol,
        )
    return monitor.register(body)
