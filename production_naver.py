import math
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

import monitor
import production
import production_fixed

app = production_fixed.app
_base_init_db = monitor.init_db
_base_evaluate = monitor.evaluate

NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://finance.naver.com/sise/",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
}
# Kept for production_naver_state compatibility. That module's old KOSPI-only
# market-state patch is skipped once this module returns name=KOSPI 100.
NAVER_POLLING = production_fixed.NAVER_KOSPI_URL
NAVER_KPI100_URL = "https://finance.naver.com/sise/sise_index.naver?code=KPI100"

# The Android app has always used the historical internal id 'kospi100'. A
# previous server revision accidentally mapped that id to the KOSPI composite.
# Restore the intended KOSPI100 meaning without changing the client protocol.
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


def _init_db_with_kpi100_fix():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kpi100-naver-v7'").fetchone():
            # The persisted row may contain KOSPI-composite values from the
            # accidental mapping, so it must not seed KOSPI100 ATH/state.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kpi100-naver-v7')")


monitor.init_db = _init_db_with_kpi100_fix


def _num(raw):
    if raw is None:
        return None
    text = re.sub(r"[^0-9+\-.,]", "", str(raw)).replace(",", "").strip()
    if not text or text in {"+", "-", "."}:
        return None
    try:
        value = float(text)
        return value if math.isfinite(value) else None
    except Exception:
        return None


def _label_value(soup, label):
    node = soup.find(string=lambda s: s and s.strip() == label)
    if node is None:
        return None
    cell = node.find_parent(["th", "td"])
    if cell is None:
        return None
    sibling = cell.find_next_sibling("td")
    if sibling is None:
        return None
    return _num(sibling.get_text(" ", strip=True))


def _naver_kpi100_quote():
    r = monitor.requests.get(NAVER_KPI100_URL, headers=NAVER_HEADERS, timeout=12)
    r.raise_for_status()
    # Naver's legacy finance pages are CP949/EUC-KR unless a charset is declared.
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = "euc-kr"
    soup = BeautifulSoup(r.text, "html.parser")

    current_node = soup.select_one("#now_value")
    current = _num(current_node.get_text(" ", strip=True) if current_node else None)
    if current is None or current <= 0:
        raise RuntimeError("Naver KPI100 current unavailable")

    change = _label_value(soup, "전일대비") or 0.0
    ratio = _label_value(soup, "등락률")
    if ratio is None:
        # Some Naver layouts keep the percentage in a sibling element rather
        # than the table cell. Search visible text as a structural fallback.
        text = soup.get_text(" ", strip=True)
        m = re.search(r"등락률\s*([+\-]?[0-9.,]+)\s*%", text)
        ratio = _num(m.group(1)) if m else 0.0

    # 전일대비 often renders as an unsigned number plus an up/down icon. The
    # percentage is signed, so use it as the authoritative direction.
    ratio = ratio or 0.0
    change = -abs(change) if ratio < 0 else abs(change)
    previous = current - change
    if previous <= 0:
        previous = current
        change = 0.0
        ratio = 0.0

    day_high = _label_value(soup, "장중최고") or current
    high52 = _label_value(soup, "52주최고")

    text = soup.get_text(" ", strip=True)
    date_match = re.search(r"(20\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})\s*(?:장마감|기준)?", text)
    if date_match:
        traded_at = datetime(
            int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)),
            15, 30, tzinfo=ZoneInfo("Asia/Seoul")
        )
    else:
        traded_at = datetime.now(ZoneInfo("Asia/Seoul"))
    value_ts = int(traded_at.timestamp())

    now = datetime.now(ZoneInfo("Asia/Seoul"))
    market_state = "REGULAR" if now.weekday() < 5 and 9 <= now.hour < 16 else "CLOSED"
    print(
        "kpi100 naver quote",
        {
            "current": current,
            "previous": previous,
            "change": change,
            "ratio": ratio,
            "day_high": day_high,
            "high52": high52,
            "date": traded_at.date().isoformat(),
        },
        flush=True,
    )
    return current, previous, change, ratio, day_high, high52, value_ts, market_state


def _naver_kpi100_history_quote():
    current, previous, change, ratio, day_high, _high52, value_ts, market_state = _naver_kpi100_quote()
    return current, previous, change, ratio, day_high, value_ts, market_state


def _yahoo_kpi100_fallback():
    result = monitor.yahoo_result("KOSPI100.KS", "5d", "5m", False)
    points = monitor.series(result)
    if not points:
        raise RuntimeError("KOSPI100 Yahoo fallback unavailable")
    value_ts, current = points[-1]
    meta = result.get("meta", {})
    previous = production._previous_close(meta, current)
    change = current - previous
    ratio = (current / previous - 1.0) * 100.0 if previous > 0 else 0.0
    day_high, _ = production._recent_high(result, value_ts, current)
    return current, previous, change, ratio, day_high, None, value_ts, monitor.session_state(meta)


def _evaluate_kpi100(index_id):
    source = "KOSPI 100 현재/등락 · 네이버 증권"
    try:
        current, previous, change, ratio, day_high, high52, value_ts, market_state = _naver_kpi100_quote()
    except Exception as exc:
        print("kpi100 Naver failed -> Yahoo fallback", type(exc).__name__, str(exc)[:120], flush=True)
        current, previous, change, ratio, day_high, high52, value_ts, market_state = _yahoo_kpi100_fallback()
        source = "KOSPI 100 · Yahoo 보조 조회"

    state = monitor.get_state(index_id)
    old_ath = float(state[0]) if state and state[0] else 0.0

    # Seed ATH with Naver's live 52-week high and never let a rolling window
    # lower a previously observed ATH. Yahoo max history is used only when it
    # supplies a higher value; truncated Yahoo history can never reduce ATH.
    ath = max(old_ath, current, day_high, high52 or 0.0)
    ath_ts = 0
    try:
        hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
        if math.isfinite(hist_ath) and hist_ath > ath:
            ath = float(hist_ath)
            ath_ts = int(hist_ts or 0)
        elif abs(float(hist_ath) - ath) / max(ath, 1.0) < 0.002:
            ath_ts = int(hist_ts or 0)
    except Exception as exc:
        print("kpi100 historical ATH fallback failed", type(exc).__name__, flush=True)

    if day_high >= ath - 1e-9 and day_high > old_ath and (high52 is None or day_high >= high52 - 1e-9):
        ath_ts = value_ts

    drawdown = (current / ath - 1.0) * 100.0 if ath > 0 else None
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
    print("check", result, flush=True)
    return result


def _evaluate(index_id):
    if index_id == "kospi100":
        return _evaluate_kpi100(index_id)
    return _base_evaluate(index_id)


monitor.evaluate = _evaluate
