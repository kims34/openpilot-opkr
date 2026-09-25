import math
import re
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

import briefing
import monitor
import production
import production_fixed

app = production_fixed.app

# Keep the legacy id for Android compatibility, but the displayed instrument is
# the KOSPI composite index. Current price/change comes from Naver Finance.
monitor.RULES["kospi100"].update({
    "name": "KOSPI",
    "cash": "^KS11",
    "regular_label": "네이버 증권 KOSPI",
    "proxy_label": "네이버 증권 KOSPI",
    "timezone": "Asia/Seoul",
    "extended": False,
    "levels": [],
})

# Display-only USD/KRW row used by the Android dashboard.
monitor.RULES.setdefault("usdkrw", {
    "name": "USD/KRW 달러 환율",
    "cash": "KRW=X",
    "proxy": None,
    "levels": [],
    "regular_label": "USD/KRW",
    "proxy_label": "USD/KRW",
    "extended": False,
    "timezone": "Asia/Seoul",
})

_previous_init_db = monitor.init_db
_previous_evaluate = monitor.evaluate
KOSPI_ATH_CACHE = {"day": None, "value": 0.0, "ts": 0}


def _init_db_v17():
    _previous_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi-composite-naver-v4'").fetchone():
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi-composite-naver-v4')")


monitor.init_db = _init_db_v17


def _signed_by_rf(value: float, rf) -> float:
    code = str(rf or "")
    if code in {"4", "5"}:
        return -abs(value)
    if code in {"1", "2"}:
        return abs(value)
    return 0.0 if code == "3" else value


def _naver_kospi():
    r = requests.get(
        "https://polling.finance.naver.com/api/realtime",
        params={"query": "SERVICE_INDEX:KOSPI"},
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://finance.naver.com/sise/sise_index.naver?code=KOSPI",
            "Accept": "application/json,text/plain,*/*",
        },
        timeout=10,
    )
    r.raise_for_status()
    payload = r.json()
    areas = (payload.get("result") or {}).get("areas") or []
    data = None
    for area in areas:
        if area.get("name") == "SERVICE_INDEX":
            for row in area.get("datas") or []:
                if row.get("cd") == "KOSPI":
                    data = row
                    break
    if not data:
        raise RuntimeError("Naver KOSPI data unavailable")

    current = float(data.get("nv") or 0) / 100.0
    raw_change = float(data.get("cv") or 0) / 100.0
    change = _signed_by_rf(raw_change, data.get("rf"))
    raw_pct = float(data.get("cr") or 0)
    pct = _signed_by_rf(raw_pct, data.get("rf"))
    previous = current - change
    high = float(data.get("hv") or 0) / 100.0
    low = float(data.get("lv") or 0) / 100.0
    opened = float(data.get("ov") or 0) / 100.0
    timestamp = int(((payload.get("result") or {}).get("time") or int(time.time() * 1000)) / 1000)
    state = str(data.get("ms") or "CLOSE")
    if current <= 0:
        raise RuntimeError("invalid Naver KOSPI value")
    return {
        "value": current,
        "previous_close": previous,
        "day_change": change,
        "day_change_percent": pct,
        "high": high,
        "low": low,
        "open": opened,
        "ts": timestamp,
        "market_state": "REGULAR" if state in {"OPEN", "PREOPEN"} else "CLOSED",
    }


def _naver_52w_high():
    try:
        r = requests.get(
            "https://finance.naver.com/sise/sise_index.naver",
            params={"code": "KOSPI"},
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/"},
            timeout=10,
        )
        r.raise_for_status()
        text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)
        m = re.search(r"52주\s*최고\s*([0-9,]+(?:\.[0-9]+)?)", text)
        if m:
            return float(m.group(1).replace(",", ""))
    except Exception as exc:
        print("naver KOSPI 52w failed", type(exc).__name__, flush=True)
    return 0.0


def _kospi_ath(current: float, session_high: float):
    today = datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
    if KOSPI_ATH_CACHE["day"] == today and KOSPI_ATH_CACHE["value"] > 0:
        return max(KOSPI_ATH_CACHE["value"], current, session_high), KOSPI_ATH_CACHE["ts"]

    candidates = [(current, 0, "current"), (session_high, 0, "naver-session-high")]
    naver_52w = _naver_52w_high()
    if naver_52w > 0:
        candidates.append((naver_52w, 0, "naver-52w"))
    try:
        hist, hist_ts = production._history_ath("^KS11")
        if math.isfinite(hist) and hist > 0:
            candidates.append((float(hist), int(hist_ts or 0), "yahoo-history-crosscheck"))
    except Exception as exc:
        print("KOSPI historical ATH fallback", type(exc).__name__, flush=True)

    best, ts, source = max(candidates, key=lambda x: x[0])
    KOSPI_ATH_CACHE.update({"day": today, "value": best, "ts": ts})
    print("KOSPI ATH crosscheck", {"ath": best, "source": source}, flush=True)
    return best, ts


def _evaluate_v17(index_id: str):
    if index_id != "kospi100":
        return _previous_evaluate(index_id)

    data = _naver_kospi()
    ath, ath_ts = _kospi_ath(data["value"], data["high"])
    ath = max(ath, data["value"])
    drawdown = (data["value"] / ath - 1.0) * 100.0 if ath > 0 else None
    tz = ZoneInfo("Asia/Seoul")
    ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat() if ath_ts else None
    ath_days = production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None

    monitor.save_state(index_id, ath, data["value"], data["value"], "네이버 증권 KOSPI")
    production.EXTRA_STATE[index_id] = {
        "previous_close": data["previous_close"],
        "day_change": data["day_change"],
        "day_change_percent": data["day_change_percent"],
        "ath_date": ath_date,
        "ath_days": ath_days,
        "drawdown": drawdown,
        "market_state": data["market_state"],
        "value_ts": data["ts"],
    }
    result = {
        "id": index_id,
        "name": "KOSPI",
        "value": data["value"],
        "cash": data["value"],
        "ath": ath,
        "drawdown": drawdown,
        "source": "네이버 증권 KOSPI",
        "market_state": data["market_state"],
        "cash_ts": data["ts"],
        "value_ts": data["ts"],
        **production.EXTRA_STATE[index_id],
    }
    print("check", result, flush=True)
    return result


monitor.evaluate = _evaluate_v17

# Replace any older briefing route if this module is reloaded.
app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/briefings"]


@app.get("/briefings")
def market_briefings():
    return briefing.get_all(production.EXTRA_STATE)
