"""IndexAlert production v2.7: robust Naver KPI100 decoding/parsing."""
from __future__ import annotations

import re
from datetime import datetime, time as dt_time

from bs4 import BeautifulSoup

import monitor
import production_v24

app = production_v24.app
SEOUL = production_v24.SEOUL
NAVER_URL = production_v24.NAVER_URL
HEADERS = production_v24.HEADERS


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


def _pick_text(response):
    candidates = []
    try:
        candidates.append(response.text)
    except Exception:
        pass
    raw = response.content or b""
    for encoding in ("euc-kr", "cp949", "utf-8"):
        try:
            candidates.append(raw.decode(encoding, errors="replace"))
        except Exception:
            pass
    # Prefer the decode that clearly contains the KPI100 quote table.
    for text in candidates:
        if "코스피100" in text and ("장중최고" in text or "52주최고" in text):
            return text
    for text in candidates:
        if "코스피100" in text:
            return text
    return candidates[0] if candidates else ""


def _label_number(page_text, label):
    # BeautifulSoup text has whitespace between table cells. Keep the match tight
    # so a later unrelated number is not accidentally consumed.
    patterns = [
        rf"{re.escape(label)}\s*([+-]?\d[\d,]*(?:\.\d+)?)",
        rf"{re.escape(label)}[^0-9+\-]{{0,50}}([+-]?\d[\d,]*(?:\.\d+)?)",
    ]
    for pattern in patterns:
        m = re.search(pattern, page_text)
        if m:
            return _num(m.group(1))
    return None


def _naver_kpi100_robust():
    r = monitor.requests.get(NAVER_URL, headers=HEADERS, timeout=12)
    r.raise_for_status()
    html = _pick_text(r)
    soup = BeautifulSoup(html, "html.parser")
    rows = production_v24._rows(soup)
    page_text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()

    # 1) structured table / legacy id
    current = production_v24._row_num(rows, "코스피100")
    if current is None:
        node = soup.find(id="now_value")
        current = _num(node.get_text(" ", strip=True) if node else None)

    # 2) text fallback. Limit the search to the quote-table region when possible,
    # because "코스피100" also appears in navigation/menu text.
    quote_text = page_text
    marker = "코스피100 주요시세"
    if marker in page_text:
        quote_text = page_text.split(marker, 1)[1][:1800]
    if current is None:
        current = _label_number(quote_text, "코스피100")

    if current is None or not (100.0 < current < 100000.0):
        print(
            "KPI100 naver parse failed",
            {"status": r.status_code, "bytes": len(r.content or b""), "has_name": "코스피100" in page_text, "sample": quote_text[:180]},
            flush=True,
        )
        raise RuntimeError("Naver KPI100 current unavailable")

    rate_text = " ".join(rows.get("등락률") or [])
    rate = production_v24._row_num(rows, "등락률")
    if rate is None:
        m = re.search(r"등락률\s*([+-]?\d[\d,]*(?:\.\d+)?)\s*%?", quote_text)
        rate = _num(m.group(1)) if m else 0.0
        rate_text = m.group(0) if m else ""
    rate = float(rate or 0.0)
    if "-" in rate_text or "하락" in rate_text:
        rate = -abs(rate)
    elif "+" in rate_text or "상승" in rate_text:
        rate = abs(rate)

    change_text = " ".join(rows.get("전일대비") or [])
    change_mag = production_v24._row_num(rows, "전일대비")
    if change_mag is None:
        m = re.search(r"전일대비(?:\s*(?:상승|하락))?\s*([+-]?\d[\d,]*(?:\.\d+)?)", quote_text)
        change_mag = _num(m.group(1)) if m else 0.0
        change_text = m.group(0) if m else ""
    change_mag = abs(float(change_mag or 0.0))
    if rate < 0 or "하락" in change_text:
        change = -change_mag
    elif rate > 0 or "상승" in change_text:
        change = change_mag
    else:
        change = float(change_mag)

    previous = current - change
    if previous <= 0:
        previous = current / (1.0 + rate / 100.0) if abs(rate) < 99 else current
        change = current - previous

    day_high = production_v24._row_num(rows, "장중최고")
    if day_high is None:
        day_high = _label_number(quote_text, "장중최고")
    day_high = float(day_high or current)

    high_52w = production_v24._row_num(rows, "52주최고")
    if high_52w is None:
        high_52w = _label_number(quote_text, "52주최고")

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
            "decode_ok": True,
        },
        flush=True,
    )
    return current, previous, change, rate, day_high, high_52w, ts, state


# production_v24's evaluator resolves this global dynamically, so replacing it
# here keeps all v24 state/ATH logic while hardening only Naver decoding/parsing.
production_v24._naver_kpi100 = _naver_kpi100_robust
