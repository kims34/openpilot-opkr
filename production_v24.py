"""IndexAlert production v2.6.

Preserves production_v23's validated U.S. session pipeline:
- regular session: actual SPY/QQQ/SCHD trades
- pre/post: actual ETF extended-hours trades when fresh
- only when the ETF itself is closed: clearly-labelled linked futures estimate

Also restores the fourth display card to KOSPI100 and sources its current quote
from Naver Finance KPI100 instead of the KOSPI composite.
"""
from __future__ import annotations

import math
import re
from datetime import datetime, time as dt_time, timezone
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

import monitor
import production
import production_v23

app = production_v23.app
_base_init_db = monitor.init_db
_base_evaluate = monitor.evaluate
SEOUL = ZoneInfo("Asia/Seoul")

# Make the U.S. fallback labels explicit. production_v23/extended_market_display
# already keeps regular-session prices as actual ETF trades and prefers actual
# ETF pre/post trades before any linked estimate.
for index_id, ticker in (("sp500", "SPY"), ("ndx", "QQQ"), ("djdiv", "SCHD")):
    rule = monitor.RULES[index_id]
    rule["cash"] = ticker
    rule["proxy"] = ticker
    rule["regular_label"] = f"{ticker} ETF 정규장 실제 체결가"
    rule["proxy_label"] = f"{ticker} ETF 프리/애프터 실제 체결가"
    rule["extended"] = True

# Keep the wire id for compatibility, but restore its requested meaning.
monitor.RULES["kospi100"] = {
    "name": "KOSPI 100",
    "cash": "KOSPI100.KS",
    "proxy": None,
    "levels": [],
    "regular_label": "KOSPI100 · 네이버 증권",
    "proxy_label": "KOSPI100 · 네이버 증권",
    "extended": False,
    "timezone": "Asia/Seoul",
}

NAVER_URL = "https://finance.naver.com/sise/sise_index.naver?code=KPI100"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}


def _init_db_v24():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-naver-v24'").fetchone():
            # The legacy id was temporarily reused for the KOSPI composite.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-naver-v24')")


monitor.init_db = _init_db_v24


def _num(text):
    if text is None:
        return None
    m = re.search(r"[+-]?\d[\d,]*(?:\.\d+)?", str(text).replace("−", "-"))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except Exception:
        return None


def _rows(soup):
    out = {}
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if not cells:
            continue
        key = re.sub(r"\s+", "", cells[0])
        if key:
            out[key] = cells
    return out


def _row_num(rows, label):
    cells = rows.get(label) or []
    if len(cells) >= 2:
        return _num(cells[1])
    return _num(" ".join(cells)) if cells else None


def _naver_kpi100():
    r = monitor.requests.get(NAVER_URL, headers=HEADERS, timeout=12)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() in {"iso-8859-1", "ascii"}:
        r.encoding = r.apparent_encoding or "euc-kr"
    soup = BeautifulSoup(r.text, "html.parser")
    rows = _rows(soup)

    current = _row_num(rows, "코스피100")
    if current is None:
        node = soup.find(id="now_value")
        current = _num(node.get_text(" ", strip=True) if node else None)
    if current is None or current <= 0:
        raise RuntimeError("Naver KPI100 current unavailable")

    rate_text = " ".join(rows.get("등락률") or [])
    rate = _num(rate_text) or 0.0
    if "-" in rate_text or "하락" in rate_text:
        rate = -abs(rate)
    elif "+" in rate_text or "상승" in rate_text:
        rate = abs(rate)

    change_text = " ".join(rows.get("전일대비") or [])
    change_mag = _num(change_text) or 0.0
    if rate < 0 or "하락" in change_text:
        change = -abs(change_mag)
    elif rate > 0 or "상승" in change_text:
        change = abs(change_mag)
    else:
        change = change_mag

    previous = current - change
    if previous <= 0:
        previous = current / (1.0 + rate / 100.0) if abs(rate) < 99 else current
        change = current - previous

    day_high = _row_num(rows, "장중최고") or current
    high_52w = _row_num(rows, "52주최고")

    page_text = soup.get_text(" ", strip=True)
    m = re.search(r"(20\d{2})[.\-/](\d{2})[.\-/](\d{2})", page_text)
    trade_date = None
    if m:
        try:
            trade_date = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=SEOUL).date()
        except Exception:
            pass

    now = datetime.now(SEOUL)
    regular = bool(
        trade_date == now.date()
        and now.weekday() < 5
        and dt_time(9, 0) <= now.time() <= dt_time(15, 30)
    )
    state = "REGULAR" if regular else "CLOSED"
    if regular:
        ts = int(now.timestamp())
    elif trade_date:
        ts = int(datetime.combine(trade_date, dt_time(15, 30), tzinfo=SEOUL).timestamp())
    else:
        ts = int(now.timestamp())

    print(
        "KPI100 naver",
        {
            "current": current,
            "previous": previous,
            "change": change,
            "rate": rate,
            "day_high": day_high,
            "high_52w": high_52w,
            "date": str(trade_date) if trade_date else None,
            "state": state,
        },
        flush=True,
    )
    return current, previous, change, rate, day_high, high_52w, ts, state


def _evaluate_kospi100(index_id):
    current, previous, change, rate, day_high, high_52w, ts, state = _naver_kpi100()
    stored = monitor.get_state(index_id)
    old_ath = float(stored[0]) if stored and stored[0] else 0.0
    ath = max(old_ath, current, day_high, float(high_52w or 0.0))
    ath_ts = 0

    # Naver is primary for current/previous/day range. Yahoo is only a secondary
    # historical cross-check and can never lower the Naver/tracked peak.
    try:
        hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
        if math.isfinite(hist_ath) and hist_ath > ath:
            ath = float(hist_ath)
            ath_ts = int(hist_ts or 0)
    except Exception as exc:
        print("KPI100 Yahoo history crosscheck unavailable", type(exc).__name__, flush=True)

    if day_high >= ath:
        ath = day_high
        ath_ts = ts

    dd = (current / ath - 1.0) * 100.0 if ath > 0 else None
    ath_date = (
        datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(SEOUL).date().isoformat()
        if ath_ts else None
    )
    source = "KOSPI100 현재/전일대비 · 네이버 증권 KPI100"
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
    return {
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


def _evaluate(index_id):
    if index_id == "kospi100":
        # Deliberately bypass v23's KOSPI-composite overnight proxy. The user
        # requested KOSPI100 as a display-only actual index card, not an estimate.
        return _evaluate_kospi100(index_id)
    return _base_evaluate(index_id)


monitor.evaluate = _evaluate
