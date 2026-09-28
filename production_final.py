import math
import re
from datetime import datetime, time as dt_time, timezone
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

import monitor
import production
import production_fixed

# Keep all existing hardened routes, FCM, laggard TOP10 and prediction features.
app = production_fixed.app
_original_init_db = monitor.init_db
_original_evaluate = monitor.evaluate

# Make the U.S. price basis explicit. The symbol used for current prices is the
# ETF itself in every session; futures are not used anywhere in this wrapper.
for index_id, ticker in (("sp500", "SPY"), ("ndx", "QQQ"), ("djdiv", "SCHD")):
    rule = monitor.RULES[index_id]
    rule["cash"] = ticker
    rule["proxy"] = ticker
    rule["regular_label"] = f"{ticker} ETF 정규장 실제 체결가"
    rule["proxy_label"] = f"{ticker} ETF 프리/애프터 실제 체결가"
    rule["extended"] = True

# Restore the fourth card to the KOSPI 100 requested by the user. The historical
# internal id remains kospi100 so already-installed clients do not break.
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

NAVER_KOSPI100_URL = "https://finance.naver.com/sise/sise_index.naver?code=KPI100"
NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}
SEOUL = ZoneInfo("Asia/Seoul")


def _init_db_final():
    _original_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-naver-kpi100-v7'").fetchone():
            # The same id was temporarily used for the KOSPI composite. Clear only
            # that display-only state so KOSPI100 can establish a clean basis.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-naver-kpi100-v7')")


monitor.init_db = _init_db_final


def _number(text):
    if text is None:
        return None
    match = re.search(r"[+-]?\d[\d,]*(?:\.\d+)?", str(text).replace("−", "-"))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except Exception:
        return None


def _naver_rows(soup):
    rows = {}
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if not cells:
            continue
        key = re.sub(r"\s+", "", cells[0])
        if key:
            rows[key] = cells
    return rows


def _cell_number(rows, key):
    cells = rows.get(key) or []
    if len(cells) >= 2:
        return _number(cells[1])
    if cells:
        return _number(" ".join(cells))
    return None


def _naver_kospi100_quote():
    r = monitor.requests.get(NAVER_KOSPI100_URL, headers=NAVER_HEADERS, timeout=12)
    r.raise_for_status()
    # Legacy Naver Finance pages are EUC-KR/CP949 in some responses.
    if not r.encoding or r.encoding.lower() in {"iso-8859-1", "ascii"}:
        r.encoding = r.apparent_encoding or "euc-kr"
    soup = BeautifulSoup(r.text, "html.parser")
    rows = _naver_rows(soup)

    current = _cell_number(rows, "코스피100")
    if current is None:
        tag = soup.find(id="now_value")
        current = _number(tag.get_text(" ", strip=True) if tag else None)
    if current is None or current <= 0:
        raise RuntimeError("Naver KOSPI100 current unavailable")

    ratio_text = " ".join(rows.get("등락률") or [])
    ratio = _number(ratio_text)
    if ratio is None:
        ratio = 0.0
    # Preserve the explicit sign from the page when present.
    if "-" in ratio_text or "하락" in ratio_text:
        ratio = -abs(ratio)
    elif "+" in ratio_text or "상승" in ratio_text:
        ratio = abs(ratio)

    change_text = " ".join(rows.get("전일대비") or [])
    change_mag = _number(change_text)
    if change_mag is None:
        change_mag = 0.0
    if ratio < 0 or "하락" in change_text:
        change = -abs(change_mag)
    elif ratio > 0 or "상승" in change_text:
        change = abs(change_mag)
    else:
        change = change_mag

    previous = current - change
    if previous <= 0:
        previous = current / (1.0 + ratio / 100.0) if abs(ratio) < 99.0 else current
        change = current - previous

    day_high = _cell_number(rows, "장중최고") or current
    high_52w = _cell_number(rows, "52주최고")

    page_text = soup.get_text(" ", strip=True)
    date_match = re.search(r"(20\d{2})[.\-/](\d{2})[.\-/](\d{2})", page_text)
    trade_date = None
    if date_match:
        try:
            trade_date = datetime(
                int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)), tzinfo=SEOUL
            ).date()
        except Exception:
            trade_date = None

    now = datetime.now(SEOUL)
    is_today = trade_date == now.date() if trade_date else False
    regular = is_today and now.weekday() < 5 and dt_time(9, 0) <= now.time() <= dt_time(15, 30)
    market_state = "REGULAR" if regular else "CLOSED"
    if regular:
        value_ts = int(now.timestamp())
    elif trade_date:
        value_ts = int(datetime.combine(trade_date, dt_time(15, 30), tzinfo=SEOUL).timestamp())
    else:
        value_ts = int(now.timestamp())

    print(
        "kospi100 naver quote",
        {
            "current": current,
            "previous": previous,
            "change": change,
            "ratio": ratio,
            "day_high": day_high,
            "high_52w": high_52w,
            "trade_date": str(trade_date) if trade_date else None,
            "market_state": market_state,
        },
        flush=True,
    )
    return current, previous, change, ratio, day_high, high_52w, value_ts, market_state


def _evaluate_kospi100(index_id: str):
    current, previous, change, ratio, day_high, high_52w, value_ts, market_state = _naver_kospi100_quote()
    state = monitor.get_state(index_id)
    old_ath = float(state[0]) if state and state[0] else 0.0

    # Naver's live KOSPI100 page is authoritative for the current quote and its
    # published 52-week high. Persist the maximum so a rolling 52-week window can
    # never make our tracked peak move downward.
    ath = max(old_ath, current, day_high, float(high_52w or 0.0))
    ath_ts = 0

    # Yahoo is only a secondary historical cross-check. It can raise the peak if
    # it returns a credible higher KOSPI100 high, but it never supplies current price.
    try:
        hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
        if math.isfinite(hist_ath) and hist_ath > ath:
            ath = float(hist_ath)
            ath_ts = int(hist_ts or 0)
    except Exception as exc:
        print("kospi100 yahoo history fallback unavailable", type(exc).__name__, flush=True)

    if day_high >= ath:
        ath = day_high
        ath_ts = value_ts

    drawdown = (current / ath - 1.0) * 100.0 if ath > 0 else None
    ath_date = (
        datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(SEOUL).date().isoformat()
        if ath_ts
        else None
    )
    source = "KOSPI100 현재/전일대비 · 네이버 증권 (KPI100)"
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
        "name": "KOSPI 100",
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


def _evaluate(index_id: str):
    if index_id == "kospi100":
        return _evaluate_kospi100(index_id)
    return _original_evaluate(index_id)


monitor.evaluate = _evaluate
