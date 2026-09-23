import json, os, sqlite3, threading, time
from contextlib import contextmanager
from datetime import datetime, timezone

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import firebase_admin
from firebase_admin import credentials, messaging

DB_PATH = os.getenv("INDEXALERT_DB", "/tmp/indexalert.db")
POLL_SECONDS = max(60, int(os.getenv("MARKET_POLL_SECONDS", "60")))
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
UA = {"User-Agent": "Mozilla/5.0 IndexAlert/1.0"}
LOCK = threading.Lock()

RULES = {
    "sp500": {
        "name": "S&P 500", "cash": "^GSPC", "proxy": "ES=F",
        "levels": [(5,10),(10,15),(15,20),(20,25),(25,15),(30,10),(35,5)],
        "proxy_label": "장외시장 연동 추정치",
    },
    "ndx": {
        "name": "NASDAQ 100", "cash": "^NDX", "proxy": "NQ=F",
        "levels": [(10,10),(15,15),(20,20),(25,20),(30,20),(35,15)],
        "proxy_label": "장외시장 연동 추정치",
    },
    "djdiv": {
        "name": "SCHD 기준지수", "cash": os.getenv("DJUSDIV_SYMBOL", "^DJUSDIV"), "proxy": "SCHD",
        "levels": [(5,15),(10,20),(15,20),(20,20),(25,15),(30,10)],
        "proxy_label": "SCHD ETF 프록시 연동 추정치",
    },
}

app = FastAPI(title="IndexAlert Monitor", version="1.1")
scheduler = BackgroundScheduler(timezone="UTC")

class RegisterBody(BaseModel):
    token: str
    platform: str = "android"

@contextmanager
def db():
    con = sqlite3.connect(DB_PATH, timeout=30)
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS devices(
            token TEXT PRIMARY KEY, platform TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS index_state(
            id TEXT PRIMARY KEY, ath REAL NOT NULL DEFAULT 0, last_cash REAL NOT NULL DEFAULT 0,
            last_value REAL NOT NULL DEFAULT 0, source TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS fired(
            index_id TEXT NOT NULL, threshold INTEGER NOT NULL,
            PRIMARY KEY(index_id, threshold)
        );
        """)

def init_firebase() -> bool:
    if firebase_admin._apps:
        return True
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        return False
    try:
        firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
        return True
    except Exception as exc:
        print("firebase init failed:", exc, flush=True)
        return False

def yahoo_result(symbol: str, range_: str = "5d", interval: str = "5m", prepost: bool = True):
    from urllib.parse import quote
    url = YAHOO.format(symbol=quote(symbol, safe=""))
    r = requests.get(
        url,
        params={"range": range_, "interval": interval, "includePrePost": str(prepost).lower()},
        headers=UA,
        timeout=15,
    )
    r.raise_for_status()
    result = r.json().get("chart", {}).get("result")
    if not result:
        raise RuntimeError(f"no Yahoo result for {symbol}")
    return result[0]

def series(result):
    timestamps = result.get("timestamp") or []
    closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", []) or []
    return [(int(ts), float(cl)) for ts, cl in zip(timestamps, closes) if cl is not None]

def session_state(meta: dict) -> str:
    regular = (meta.get("currentTradingPeriod") or {}).get("regular") or {}
    start = int(regular.get("start") or 0)
    end = int(regular.get("end") or 0)
    now = int(time.time())
    if start and end and start <= now < end:
        return "REGULAR"
    pre = (meta.get("currentTradingPeriod") or {}).get("pre") or {}
    post = (meta.get("currentTradingPeriod") or {}).get("post") or {}
    if int(pre.get("start") or 0) <= now < int(pre.get("end") or 0):
        return "PRE"
    if int(post.get("start") or 0) <= now < int(post.get("end") or 0):
        return "POST"
    return "CLOSED"

def current(symbol: str):
    result = yahoo_result(symbol)
    meta = result.get("meta", {})
    points = series(result)
    if not points:
        raise RuntimeError(f"no current price for {symbol}")
    last_ts, last = points[-1]
    prev = float(meta.get("previousClose") or meta.get("chartPreviousClose") or last)
    return last, prev, session_state(meta), last_ts

def proxy_ratio_from_cash_close(symbol: str, cash_close_ts: int):
    result = yahoo_result(symbol)
    points = series(result)
    if not points:
        raise RuntimeError(f"no proxy data for {symbol}")
    latest_ts, latest = points[-1]
    # Anchor the proxy to the last available proxy bar at or immediately before
    # the cash index's own last regular-session timestamp. This removes the
    # futures price-level basis and avoids Yahoo chartPreviousClose range artifacts.
    anchors = [(ts, value) for ts, value in points if ts <= cash_close_ts + 300]
    if anchors:
        anchor_ts, anchor = anchors[-1]
        if cash_close_ts - anchor_ts <= 60 * 60 * 8 and anchor > 0:
            return latest / anchor, latest, anchor, anchor_ts, latest_ts
    meta = result.get("meta", {})
    anchor = float(meta.get("previousClose") or 0)
    if anchor <= 0:
        raise RuntimeError(f"no proxy anchor for {symbol}")
    return latest / anchor, latest, anchor, 0, latest_ts

def historical_ath(symbol: str) -> float:
    result = yahoo_result(symbol, "max", "1d", False)
    highs = result.get("indicators", {}).get("quote", [{}])[0].get("high", []) or []
    vals = [float(x) for x in highs if x is not None]
    if not vals:
        raise RuntimeError(f"no ATH history for {symbol}")
    return max(vals)

def get_state(index_id: str):
    with db() as con:
        return con.execute(
            "SELECT ath,last_cash,last_value,source,updated_at FROM index_state WHERE id=?",
            (index_id,),
        ).fetchone()

def save_state(index_id: str, ath: float, last_cash: float, value: float, source: str):
    now = datetime.now(timezone.utc).isoformat()
    with db() as con:
        con.execute("""INSERT INTO index_state(id,ath,last_cash,last_value,source,updated_at)
          VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET ath=excluded.ath,last_cash=excluded.last_cash,
          last_value=excluded.last_value,source=excluded.source,updated_at=excluded.updated_at""",
          (index_id, ath, last_cash, value, source, now))

def clear_fired(index_id: str):
    with db() as con:
        con.execute("DELETE FROM fired WHERE index_id=?", (index_id,))

def fired_set(index_id: str):
    with db() as con:
        return {int(r[0]) for r in con.execute("SELECT threshold FROM fired WHERE index_id=?", (index_id,)).fetchall()}

def mark_fired(index_id: str, thresholds):
    with db() as con:
        con.executemany(
            "INSERT OR IGNORE INTO fired(index_id,threshold) VALUES(?,?)",
            [(index_id, int(t)) for t in thresholds],
        )

def send_push(title: str, body: str, data: dict):
    if not init_firebase():
        print("FCM not configured:", title, body, flush=True)
        return 0
    with db() as con:
        tokens = [r[0] for r in con.execute("SELECT token FROM devices").fetchall()]
    sent, dead = 0, []
    for token in tokens:
        try:
            messaging.send(messaging.Message(
                token=token,
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in data.items()},
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(channel_id="index_alerts"),
                ),
            ))
            sent += 1
        except Exception as exc:
            msg = str(exc).lower()
            if "registration-token-not-registered" in msg or "not found" in msg:
                dead.append(token)
            print("FCM send failed:", exc, flush=True)
    if dead:
        with db() as con:
            con.executemany("DELETE FROM devices WHERE token=?", [(x,) for x in dead])
    return sent

def evaluate(index_id: str):
    rule = RULES[index_id]
    cash_now, _, market_state, cash_ts = current(rule["cash"])
    state = get_state(index_id)
    ath = float(state[0]) if state and state[0] else 0.0
    if ath <= 0:
        ath = historical_ath(rule["cash"])

    value = cash_now
    source = "현물지수"
    proxy_debug = None
    if market_state != "REGULAR":
        ratio, p_now, p_anchor, p_anchor_ts, p_latest_ts = proxy_ratio_from_cash_close(rule["proxy"], cash_ts)
        value = cash_now * ratio
        source = rule["proxy_label"]
        proxy_debug = {
            "ratio": ratio, "proxy_now": p_now, "proxy_anchor": p_anchor,
            "proxy_anchor_ts": p_anchor_ts, "proxy_latest_ts": p_latest_ts,
        }

    # Only an official cash-index print may establish/reset ATH.
    if market_state == "REGULAR" and cash_now > ath:
        ath = cash_now
        clear_fired(index_id)

    dd = (value / ath - 1.0) * 100.0 if ath else 0.0
    already = fired_set(index_id)
    crossed = [(thr, pct) for thr, pct in rule["levels"] if dd <= -thr and thr not in already]
    if crossed:
        mark_fired(index_id, [x[0] for x in crossed])
        thr, pct = max(crossed, key=lambda x: x[0])
        next_level = next((x for x in rule["levels"] if x[0] > thr), None)
        title = f"{rule['name']} -{thr}% 매수구간 진입"
        body = f"ATH 대비 {dd:.2f}% · 이번 단계 {pct}% · {source}"
        if next_level:
            body += f" · 다음 -{next_level[0]}%"
        send_push(title, body, {
            "index_id": index_id, "drawdown": f"{dd:.4f}",
            "threshold": thr, "allocation": pct, "source": source,
        })

    save_state(index_id, ath, cash_now, value, source)
    out = {
        "id": index_id, "name": rule["name"], "value": value, "cash": cash_now,
        "ath": ath, "drawdown": dd, "source": source, "market_state": market_state,
        "cash_ts": cash_ts,
    }
    if proxy_debug:
        out["proxy"] = proxy_debug
    return out

def check_all():
    if not LOCK.acquire(blocking=False):
        return
    try:
        for index_id in RULES:
            try:
                print("check", evaluate(index_id), flush=True)
            except Exception as exc:
                print("check failed", index_id, exc, flush=True)
    finally:
        LOCK.release()

@app.on_event("startup")
def startup():
    init_db()
    init_firebase()
    if not scheduler.running:
        scheduler.add_job(check_all, "interval", seconds=POLL_SECONDS, id="market-check", max_instances=1, coalesce=True)
        scheduler.start()
    threading.Thread(target=check_all, daemon=True).start()

@app.get("/health")
def health():
    return {
        "ok": True,
        "firebase": bool(firebase_admin._apps),
        "poll_seconds": POLL_SECONDS,
        "version": "1.1",
        "time": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/register")
def register(body: RegisterBody):
    token = body.token.strip()
    if len(token) < 20:
        raise HTTPException(400, "invalid token")
    with db() as con:
        con.execute(
            "INSERT INTO devices(token,platform,updated_at) VALUES(?,?,?) ON CONFLICT(token) DO UPDATE SET platform=excluded.platform,updated_at=excluded.updated_at",
            (token, body.platform, datetime.now(timezone.utc).isoformat()),
        )
    return {"ok": True}

@app.get("/status")
def status():
    out = []
    for index_id, rule in RULES.items():
        st = get_state(index_id)
        out.append({
            "id": index_id,
            "name": rule["name"],
            "ath": st[0] if st else None,
            "last_cash": st[1] if st else None,
            "last_value": st[2] if st else None,
            "source": st[3] if st else None,
            "updated_at": st[4] if st else None,
            "fired": sorted(fired_set(index_id)),
        })
    return {"indices": out}

@app.post("/check")
def check():
    check_all()
    return status()
