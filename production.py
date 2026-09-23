import math
from datetime import datetime, timezone
from urllib.parse import quote

import monitor
from fastapi import HTTPException

# Use the ETFs themselves as the alert basis while preserving the existing
# internal ids so already-installed Android clients and saved settings remain
# compatible.
monitor.RULES.update({
    "sp500": {
        "name": "SPY (S&P 500 ETF)",
        "cash": "SPY",
        "proxy": "SPY",
        "levels": [(5,10),(10,15),(15,20),(20,25),(25,15),(30,10),(35,5)],
        "regular_label": "SPY ETF",
        "proxy_label": "SPY ETF 장외거래",
    },
    "ndx": {
        "name": "QQQ (NASDAQ 100 ETF)",
        "cash": "QQQ",
        "proxy": "QQQ",
        "levels": [(10,10),(15,15),(20,20),(25,20),(30,20),(35,15)],
        "regular_label": "QQQ ETF",
        "proxy_label": "QQQ ETF 장외거래",
    },
    "djdiv": {
        "name": "SCHD",
        "cash": "SCHD",
        "proxy": "SCHD",
        "levels": [(5,15),(10,20),(15,20),(20,20),(25,15),(30,10)],
        "regular_label": "SCHD ETF",
        "proxy_label": "SCHD ETF 장외거래",
    },
})

# One-time migrations from the old index basis and from the first ETF build
# that did not adjust historical prices for stock splits. Device registrations
# and per-level settings are intentionally preserved.
_original_init_db = monitor.init_db

def _init_db_with_etf_migration():
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

monitor.init_db = _init_db_with_etf_migration


def _split_adjusted_historical_ath(symbol: str) -> float:
    url = monitor.YAHOO.format(symbol=quote(symbol, safe=""))
    r = monitor.requests.get(
        url,
        params={
            "range": "max",
            "interval": "1d",
            "includePrePost": "false",
            "events": "splits",
        },
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

    vals = []
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
        vals.append(h / factor)

    if not vals:
        raise RuntimeError(f"no ATH history for {symbol}")
    return max(vals)


def _evaluate_etf(index_id: str):
    rule = monitor.RULES[index_id]
    cash_result = monitor.yahoo_result(rule["cash"], prepost=False)
    points = monitor.series(cash_result)
    if not points:
        raise RuntimeError("no ETF prices")
    cash_ts, cash_now = points[-1]
    market_state = monitor.session_state(cash_result.get("meta", {}))
    highs = cash_result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
    recent_high = max([cash_now] + [float(x) for x in highs if x is not None and math.isfinite(float(x))])

    state = monitor.get_state(index_id)
    ath = float(state[0]) if state and state[0] else 0.0
    old_ath = ath
    day = datetime.now(timezone.utc).date().isoformat()
    if ath <= 0 or monitor.ATH_REFRESH.get(index_id) != day:
        ath = max(ath, _split_adjusted_historical_ath(rule["cash"]))
        monitor.ATH_REFRESH[index_id] = day
    ath = max(ath, recent_high)
    if not math.isfinite(ath) or ath <= 0 or not math.isfinite(cash_now) or cash_now <= 0:
        raise RuntimeError("invalid ETF data")
    if ath > old_ath:
        monitor.clear_fired(index_id)

    value = cash_now
    source = rule["regular_label"]
    proxy_debug = None
    if market_state != "REGULAR":
        ratio, p_now, p_anchor, p_anchor_ts, p_latest_ts = monitor.proxy_ratio_from_cash_close(rule["proxy"], cash_ts)
        value = cash_now * ratio
        source = rule["proxy_label"]
        proxy_debug = {
            "ratio": ratio,
            "proxy_now": p_now,
            "proxy_anchor": p_anchor,
            "proxy_anchor_ts": p_anchor_ts,
            "proxy_latest_ts": p_latest_ts,
        }

    dd = (value / ath - 1.0) * 100.0
    monitor.enqueue_crossings(index_id, ath, dd, source)
    monitor.save_state(index_id, ath, cash_now, value, source)

    out = {
        "id": index_id,
        "name": rule["name"],
        "value": value,
        "cash": cash_now,
        "ath": ath,
        "drawdown": dd,
        "source": source,
        "market_state": market_state,
        "cash_ts": cash_ts,
    }
    if proxy_debug:
        out["proxy"] = proxy_debug
    return out

monitor.evaluate = _evaluate_etf

# Reuse the proven monitor app and background scheduler, but keep operational
# endpoints minimal in production. The manual /check endpoint is intentionally
# not exposed because it can force repeated upstream market-data requests.
app = monitor.app
app.router.routes = [
    route for route in app.router.routes
    if not (getattr(route, "path", None) in {"/check", "/register"})
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
    return monitor.register(body)
