import json
import math
from datetime import datetime, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import monitor
from fastapi import HTTPException

monitor.RULES.update({
    "sp500": {
        "name": "SPY (S&P 500 ETF)",
        "cash": "SPY",
        "proxy": "SPY",
        "levels": [(5,10),(10,15),(15,20),(20,25),(25,15),(30,10),(35,5)],
        "regular_label": "SPY ETF",
        "proxy_label": "SPY ETF 장외거래",
        "extended": True,
        "timezone": "America/New_York",
    },
    "ndx": {
        "name": "QQQ (NASDAQ 100 ETF)",
        "cash": "QQQ",
        "proxy": "QQQ",
        "levels": [(10,10),(15,15),(20,20),(25,20),(30,20),(35,15)],
        "regular_label": "QQQ ETF",
        "proxy_label": "QQQ ETF 장외거래",
        "extended": True,
        "timezone": "America/New_York",
    },
    "djdiv": {
        "name": "SCHD",
        "cash": "SCHD",
        "proxy": "SCHD",
        "levels": [(5,15),(10,20),(15,20),(20,20),(25,15),(30,10)],
        "regular_label": "SCHD ETF",
        "proxy_label": "SCHD ETF 장외거래",
        "extended": True,
        "timezone": "America/New_York",
    },
    "kospi100": {
        "name": "KOSPI 100",
        "cash": "KOSPI100.KS",
        "proxy": None,
        "levels": [],
        "regular_label": "KOSPI 100 지수",
        "proxy_label": "KOSPI 100 지수",
        "extended": False,
        "timezone": "Asia/Seoul",
    },
})

EXTRA_STATE = {}
_original_init_db = monitor.init_db


def _init_db_with_market_migrations():
    _original_init_db()
    with monitor.db() as con:
        ids = ("sp500", "ndx", "djdiv")
        if not con.execute("SELECT 1 FROM migrations WHERE name='etf-basis-v1'").fetchone():
            con.execute("DELETE FROM index_state WHERE id IN (?,?,?)", ids)
            con.execute("DELETE FROM fired WHERE index_id IN (?,?,?)", ids)
            con.execute("DELETE FROM deliveries WHERE index_id IN (?,?,?)", ids)
            con.execute("INSERT INTO migrations(name) VALUES('etf-basis-v1')")
        if not con.execute("SELECT 1 FROM migrations WHERE name='etf-split-ath-v2'").fetchone():
            con.execute("DELETE FROM index_state WHERE id IN (?,?,?)", ids)
            con.execute("DELETE FROM fired WHERE index_id IN (?,?,?)", ids)
            con.execute("DELETE FROM deliveries WHERE index_id IN (?,?,?)", ids)
            con.execute("INSERT INTO migrations(name) VALUES('etf-split-ath-v2')")
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-display-v1'").fetchone():
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-display-v1')")


monitor.init_db = _init_db_with_market_migrations


def _history_ath(symbol: str):
    url = monitor.YAHOO.format(symbol=quote(symbol, safe=""))
    r = monitor.requests.get(
        url,
        params={"range": "max", "interval": "1d", "includePrePost": "false", "events": "splits"},
        headers=monitor.UA,
        timeout=20,
    )
    r.raise_for_status()
    result = (r.json().get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError(f"no Yahoo history for {symbol}")

    timestamps = result.get("timestamp") or []
    highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
    split_events = (result.get("events") or {}).get("splits") or {}
    splits = []
    for ev in split_events.values():
        try:
            ts = int(ev.get("date") or 0)
            num = float(ev.get("numerator") or 0)
            den = float(ev.get("denominator") or 0)
            if num > 0 and den > 0:
                ratio = num / den
            else:
                raw = str(ev.get("splitRatio") or "")
                if ":" in raw:
                    a, b = raw.split(":", 1)
                    ratio = float(a) / float(b)
                else:
                    ratio = float(raw)
            if ts > 0 and ratio > 0:
                splits.append((ts, ratio))
        except Exception:
            continue

    best = 0.0
    best_ts = 0
    for ts, high in zip(timestamps, highs):
        if high is None:
            continue
        h = float(high)
        if not math.isfinite(h) or h <= 0:
            continue
        factor = 1.0
        for split_ts, ratio in splits:
            if split_ts > int(ts):
                factor *= ratio
        adjusted = h / factor
        if adjusted >= best:
            best = adjusted
            best_ts = int(ts)
    if best <= 0:
        raise RuntimeError(f"no ATH history for {symbol}")
    return best, best_ts


def _latest_price(symbol: str):
    result = monitor.yahoo_result(symbol, prepost=True)
    points = monitor.series(result)
    if not points:
        raise RuntimeError(f"no current price for {symbol}")
    return points[-1]


def _recent_high(result, fallback_ts: int, fallback_value: float):
    timestamps = result.get("timestamp") or []
    highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
    best = fallback_value
    best_ts = fallback_ts
    for ts, high in zip(timestamps, highs):
        if high is None:
            continue
        h = float(high)
        if math.isfinite(h) and h >= best:
            best = h
            best_ts = int(ts)
    return best, best_ts


def _previous_close(meta: dict, fallback: float):
    for key in ("regularMarketPreviousClose", "previousClose", "chartPreviousClose"):
        try:
            value = float(meta.get(key) or 0)
            if math.isfinite(value) and value > 0:
                return value
        except Exception:
            pass
    return fallback


def _days_since(ts: int, tz_name: str):
    if not ts:
        return None
    tz = ZoneInfo(tz_name)
    then = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(tz).date()
    return max(0, (datetime.now(tz).date() - then).days)


def _evaluate_market(index_id: str):
    rule = monitor.RULES[index_id]
    cash_result = monitor.yahoo_result(rule["cash"], prepost=False)
    points = monitor.series(cash_result)
    if not points:
        raise RuntimeError("no market prices")

    cash_ts, cash_now = points[-1]
    meta = cash_result.get("meta", {})
    market_state = monitor.session_state(meta)
    previous_close = _previous_close(meta, cash_now)
    recent_high, recent_high_ts = _recent_high(cash_result, cash_ts, cash_now)

    state = monitor.get_state(index_id)
    old_ath = float(state[0]) if state and state[0] else 0.0
    ath = old_ath
    ath_ts = 0
    tz = ZoneInfo(rule["timezone"])
    day = datetime.now(tz).date().isoformat()

    hist_ath = hist_ts = None
    if ath <= 0 or monitor.ATH_REFRESH.get(index_id) != day:
        hist_ath, hist_ts = _history_ath(rule["cash"])
        if hist_ath >= ath:
            ath = hist_ath
            ath_ts = hist_ts
        monitor.ATH_REFRESH[index_id] = day

    if recent_high >= ath:
        ath = recent_high
        ath_ts = recent_high_ts

    if ath_ts == 0:
        if hist_ath is None:
            hist_ath, hist_ts = _history_ath(rule["cash"])
        if abs(float(hist_ath) - ath) / max(ath, 1.0) < 1e-6:
            ath_ts = int(hist_ts)

    if not math.isfinite(ath) or ath <= 0 or not math.isfinite(cash_now) or cash_now <= 0:
        raise RuntimeError("invalid market data")
    if ath > old_ath:
        monitor.clear_fired(index_id)

    value = cash_now
    value_ts = cash_ts
    source = rule["regular_label"]
    if rule.get("extended") and market_state != "REGULAR":
        value_ts, value = _latest_price(rule["cash"])
        source = rule["proxy_label"]
    if not math.isfinite(value) or value <= 0:
        raise RuntimeError("invalid current market value")

    dd = (value / ath - 1.0) * 100.0
    day_change = value - previous_close
    day_change_pct = (value / previous_close - 1.0) * 100.0 if previous_close > 0 else 0.0
    ath_date = None
    if ath_ts:
        ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat()

    if rule["levels"]:
        monitor.enqueue_crossings(index_id, ath, dd, source)
    monitor.save_state(index_id, ath, cash_now, value, source)
    EXTRA_STATE[index_id] = {
        "previous_close": previous_close,
        "day_change": day_change,
        "day_change_percent": day_change_pct,
        "ath_date": ath_date,
        "ath_days": _days_since(ath_ts, rule["timezone"]),
        "drawdown": dd,
        "market_state": market_state,
        "value_ts": value_ts,
    }

    return {
        "id": index_id,
        "name": rule["name"],
        "value": value,
        "cash": cash_now,
        "ath": ath,
        "drawdown": dd,
        "source": source,
        "market_state": market_state,
        "cash_ts": cash_ts,
        "value_ts": value_ts,
        **EXTRA_STATE[index_id],
    }


monitor.evaluate = _evaluate_market
app = monitor.app
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/check", "/register", "/status"}
]


@app.post("/register")
def register(body: monitor.RegisterBody):
    token = body.token.strip()
    if not (20 <= len(token) <= 4096):
        raise HTTPException(400, "invalid token")
    if body.platform != "android":
        raise HTTPException(400, "unsupported platform")
    if body.protocol not in (1, 2):
        raise HTTPException(400, "unsupported protocol")

    settings = body.enabled_levels
    if settings is not None:
        settings = dict(settings)
        # v0.8 and older clients only know the original three monitored assets.
        settings.setdefault("kospi100", [])
        body = monitor.RegisterBody(
            token=body.token,
            platform=body.platform,
            enabled_levels=settings,
            protocol=body.protocol,
        )
    return monitor.register(body)


@app.get("/status")
def status():
    out = []
    for index_id, rule in monitor.RULES.items():
        st = monitor.get_state(index_id)
        extra = EXTRA_STATE.get(index_id, {})
        out.append({
            "id": index_id,
            "name": rule["name"],
            "ath": st[0] if st else None,
            "last_cash": st[1] if st else None,
            "last_value": st[2] if st else None,
            "source": st[3] if st else None,
            "updated_at": st[4] if st else None,
            "fired": sorted(monitor.fired_set(index_id)) if rule["levels"] else [],
            "alerts_enabled": bool(rule["levels"]),
            **extra,
        })
    return {"indices": out}
