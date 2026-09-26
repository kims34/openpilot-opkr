import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import history_routes
import monitor
import production
import production_fixed
import production_v14

app = production_v14.app
_base_init_db = monitor.init_db
_base_evaluate = monitor.evaluate

NAVER_KPI100_BASIC = "https://m.stock.naver.com/api/index/KPI100/basic"
NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36",
    "Referer": "https://m.stock.naver.com/",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
}
# Verified from Naver's KOSPI100 page. This is a seed/floor, never a ceiling.
KPI100_VERIFIED_52W_HIGH = 11932.83

monitor.RULES["kospi100"] = {
    "name": "KOSPI 100",
    "cash": "KOSPI100.KS",
    "proxy": None,
    "levels": [],
    "regular_label": "KOSPI 100 · 네이버 증권",
    "proxy_label": "KOSPI 100 · 네이버 증권",
    "extended": False,
    "timezone": "Asia/Seoul",
}


def _init_db():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kpi100-mobile-v8'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kpi100-mobile-v8')")


monitor.init_db = _init_db


def _num(v):
    if v is None:
        return None
    try:
        x = float(str(v).replace(",", "").replace("%", "").strip())
        return x if math.isfinite(x) else None
    except Exception:
        return None


def _direction(data):
    d = data.get("compareToPreviousPrice") or {}
    code = str(d.get("code") or "")
    text = str(d.get("name") or d.get("text") or d.get("nameKor") or "")
    if code in {"4", "5"} or "하락" in text or "FALL" in text.upper():
        return -1
    if code in {"1", "2"} or "상승" in text or "RISE" in text.upper():
        return 1
    return 0


def _find_52w_high(obj):
    wanted = {
        "fiftytwoweekhigh", "fiftytwoweekhighprice", "high52w", "high52wprice",
        "week52high", "week52highprice", "yearhigh", "yearhighprice",
    }
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = "".join(ch for ch in str(k).lower() if ch.isalnum())
            if key in wanted:
                n = _num(v)
                if n and n > 0:
                    return n
        for v in obj.values():
            n = _find_52w_high(v)
            if n:
                return n
    elif isinstance(obj, list):
        for v in obj:
            n = _find_52w_high(v)
            if n:
                return n
    return None


def _parse_ts(raw):
    if raw:
        try:
            return int(datetime.fromisoformat(str(raw).replace("Z", "+00:00")).timestamp())
        except Exception:
            pass
    return int(datetime.now(ZoneInfo("Asia/Seoul")).timestamp())


def naver_kpi100_quote():
    r = monitor.requests.get(NAVER_KPI100_BASIC, headers=NAVER_HEADERS, timeout=12)
    r.raise_for_status()
    data = r.json()
    current = _num(data.get("closePrice") or data.get("closePriceRaw"))
    if current is None or current <= 0:
        raise RuntimeError("Naver KPI100 mobile current unavailable")

    sign = _direction(data)
    change_raw = _num(data.get("compareToPreviousClosePrice") or data.get("compareToPreviousClosePriceRaw")) or 0.0
    ratio_raw = _num(data.get("fluctuationsRatio") or data.get("fluctuationsRatioRaw")) or 0.0
    if sign < 0:
        change = -abs(change_raw)
        ratio = -abs(ratio_raw)
    elif sign > 0:
        change = abs(change_raw)
        ratio = abs(ratio_raw)
    else:
        ratio = ratio_raw
        change = -abs(change_raw) if ratio < 0 else abs(change_raw)

    previous = current - change
    if previous <= 0:
        previous = current
        change = 0.0
        ratio = 0.0

    day_high = _num(data.get("highPrice") or data.get("highPriceRaw")) or current
    high52 = _find_52w_high(data) or KPI100_VERIFIED_52W_HIGH
    value_ts = _parse_ts(data.get("localTradedAt") or data.get("tradeTime") or data.get("date"))
    status = str(data.get("marketStatus") or data.get("marketStatusType") or "").upper()
    market_state = "REGULAR" if "OPEN" in status or "REGULAR" in status else "CLOSED"

    print("kpi100 mobile naver quote", {
        "current": current, "previous": previous, "change": change, "ratio": ratio,
        "day_high": day_high, "high52": high52, "status": status,
    }, flush=True)
    return current, previous, change, ratio, day_high, high52, value_ts, market_state


def naver_kpi100_history_quote():
    current, previous, change, ratio, day_high, _high52, value_ts, state = naver_kpi100_quote()
    return current, previous, change, ratio, day_high, value_ts, state


def _evaluate_kpi100(index_id):
    source = "KOSPI 100 현재/등락 · 네이버 모바일"
    try:
        current, previous, change, ratio, day_high, high52, value_ts, market_state = naver_kpi100_quote()
    except Exception as exc:
        print("kpi100 mobile Naver failed -> previous fallback", type(exc).__name__, str(exc)[:160], flush=True)
        return _base_evaluate(index_id)

    state = monitor.get_state(index_id)
    old_ath = float(state[0]) if state and state[0] else 0.0
    ath = max(old_ath, current, day_high, high52 or 0.0)
    ath_ts = 0

    # Yahoo is only allowed to increase the ATH; it can never lower the Naver seed.
    try:
        hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
        if math.isfinite(hist_ath) and hist_ath > ath:
            ath = float(hist_ath)
            ath_ts = int(hist_ts or 0)
        elif abs(float(hist_ath) - ath) / max(ath, 1.0) < 0.002:
            ath_ts = int(hist_ts or 0)
    except Exception:
        pass

    if day_high >= ath - 1e-9 and day_high > old_ath and day_high >= (high52 or 0.0) - 1e-9:
        ath_ts = value_ts

    drawdown = (current / ath - 1.0) * 100.0
    tz = ZoneInfo("Asia/Seoul")
    ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat() if ath_ts else None
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
    result = {
        "id": index_id, "name": "KOSPI 100", "value": current, "cash": current,
        "ath": ath, "drawdown": drawdown, "source": source,
        "market_state": market_state, "cash_ts": value_ts, "value_ts": value_ts,
        **production.EXTRA_STATE[index_id],
    }
    print("check", result, flush=True)
    return result


def _evaluate(index_id):
    if index_id == "kospi100":
        return _evaluate_kpi100(index_id)
    return _base_evaluate(index_id)


monitor.evaluate = _evaluate

# Replace the history route so KOSPI100 history no longer uses KOSPI (^KS11).
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/history/{index_id}"
]
history_routes.attach(
    app,
    monitor,
    naver_kpi100_history_quote,
    production_fixed._naver_usdkrw_quote,
)
