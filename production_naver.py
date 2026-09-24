import html
import math
import re
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import monitor
import production
import production_fixed

app = production_fixed.app
_original_evaluate = monitor.evaluate

NAVER_API = "https://stock.naver.com/api/securityFe/api/index/KPI100/basic"
NAVER_LEGACY = "https://finance.naver.com/sise/sise_index.naver?code=KPI100"
NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Referer": "https://finance.naver.com/",
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.8,*/*;q=0.7",
}


def _num(value):
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").replace("+", "").strip()
        return float(text)
    except Exception:
        return None


def _pick(obj, *keys):
    for key in keys:
        if key in obj and obj.get(key) not in (None, ""):
            return obj.get(key)
    return None


def _naver_api_quote():
    r = requests.get(NAVER_API, headers={**NAVER_HEADERS, "Referer": "https://stock.naver.com/", "Accept": "application/json,*/*;q=0.8"}, timeout=8)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and isinstance(data.get("result"), dict):
        data = data["result"]
    if not isinstance(data, dict):
        raise RuntimeError("unexpected Naver API payload")

    value = _num(_pick(data, "closePrice", "nowPrice", "currentPrice"))
    ratio = _num(_pick(data, "fluctuationsRatio", "changeRate"))
    change_abs = _num(_pick(data, "compareToPreviousClosePrice", "changePrice"))
    if value is None or value <= 0:
        raise RuntimeError("Naver KPI100 price unavailable")

    ratio = ratio or 0.0
    sign = -1.0 if ratio < 0 else (1.0 if ratio > 0 else 0.0)
    day_change = (change_abs or 0.0) * sign
    previous_close = value - day_change if value - day_change > 0 else value

    high52 = _num(_pick(data, "highest52WeekPrice", "highest52WeekPriceValue", "fiftyTwoWeekHigh"))
    high52_date = _pick(data, "highest52WeekDate", "highest52WeekDateTime")
    traded_at = _pick(data, "localTradedAt", "tradedAt", "updatedAt")
    ts = int(time.time())
    if traded_at:
        try:
            dt = datetime.fromisoformat(str(traded_at).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
            ts = int(dt.timestamp())
        except Exception:
            pass

    print("kospi100 Naver API", {"value": value, "change": day_change, "ratio": ratio, "high52": high52}, flush=True)
    return value, previous_close, day_change, ratio, high52, high52_date, ts, "네이버 증권 API · KPI100"


def _decode_naver(content: bytes):
    for encoding in ("euc-kr", "cp949", "utf-8"):
        try:
            return content.decode(encoding)
        except Exception:
            pass
    return content.decode("utf-8", errors="replace")


def _naver_legacy_quote():
    r = requests.get(NAVER_LEGACY, headers=NAVER_HEADERS, timeout=8)
    r.raise_for_status()
    raw = _decode_naver(r.content)

    # Naver Finance's live index page exposes the live value in #now_value.
    m = re.search(r'id=["\']now_value["\'][^>]*>\s*([0-9,]+(?:\.[0-9]+)?)', raw, re.I | re.S)
    if not m:
        raise RuntimeError("Naver legacy #now_value unavailable")
    value = _num(m.group(1))
    if value is None or value <= 0:
        raise RuntimeError("Naver legacy KPI100 price unavailable")

    # #change_value_and_rate contains the absolute change and 상승/하락 state.
    pos = raw.find('id="change_value_and_rate"')
    if pos < 0:
        pos = raw.find("id='change_value_and_rate'")
    snippet = raw[pos:pos + 1800] if pos >= 0 else ""
    plain = html.unescape(re.sub(r"(?s)<[^>]+>", " ", snippet))
    plain = re.sub(r"\s+", " ", plain)
    nums = re.findall(r"[0-9][0-9,]*(?:\.[0-9]+)?", plain)
    change_abs = _num(nums[0]) if nums else 0.0

    lowered = snippet.lower()
    if "하락" in plain or "ico_down" in lowered or "minus" in lowered:
        sign = -1.0
    elif "상승" in plain or "ico_up" in lowered or "plus" in lowered:
        sign = 1.0
    else:
        sign = 0.0
    day_change = (change_abs or 0.0) * sign
    previous_close = value - day_change if value - day_change > 0 else value
    ratio = (value / previous_close - 1.0) * 100.0 if previous_close > 0 else 0.0

    # 52-week high is optional here; ATH cross-check has its own safe floor.
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)
    high52 = None
    mh = re.search(r"52주최고\s*([0-9,]+(?:\.[0-9]+)?)", text)
    if mh:
        high52 = _num(mh.group(1))

    print("kospi100 Naver legacy", {"value": value, "change": day_change, "ratio": ratio, "high52": high52}, flush=True)
    return value, previous_close, day_change, ratio, high52, None, int(time.time()), "네이버 증권 실시간 · KPI100"


def _naver_quote():
    try:
        return _naver_legacy_quote()
    except Exception as exc:
        print("kospi100 Naver legacy failed", type(exc).__name__, str(exc), flush=True)
    try:
        return _naver_api_quote()
    except Exception as exc:
        print("kospi100 Naver API failed", type(exc).__name__, str(exc), flush=True)
        raise


def _date_to_ts(value):
    if not value:
        return 0
    s = str(value).strip().replace(".", "-").replace("/", "-")
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            dt = datetime.strptime(s[:10] if fmt == "%Y-%m-%d" else s[:8], fmt).replace(tzinfo=ZoneInfo("Asia/Seoul"))
            return int(dt.timestamp())
        except Exception:
            pass
    return 0


def _evaluate(index_id: str):
    if index_id != "kospi100":
        return _original_evaluate(index_id)

    try:
        value, previous_close, day_change, day_change_percent, naver_high52, naver_high52_date, value_ts, source = _naver_quote()
        ath, ath_ts = production_fixed._kospi100_ath()
        if naver_high52 and naver_high52 > ath:
            ath = naver_high52
            ath_ts = _date_to_ts(naver_high52_date)
        if value > ath:
            ath = value
            ath_ts = value_ts
        drawdown = (value / ath - 1.0) * 100.0
        tz = ZoneInfo("Asia/Seoul")
        ath_date = datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(tz).date().isoformat() if ath_ts else None
        now = datetime.now(tz)
        market_state = "REGULAR" if now.weekday() < 5 and ((9 <= now.hour < 15) or (now.hour == 15 and now.minute <= 30)) else "CLOSED"

        monitor.save_state(index_id, ath, value, value, source)
        production.EXTRA_STATE[index_id] = {
            "previous_close": previous_close,
            "day_change": day_change,
            "day_change_percent": day_change_percent,
            "ath_date": ath_date,
            "ath_days": production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None,
            "drawdown": drawdown,
            "market_state": market_state,
            "value_ts": value_ts,
        }
        result = {
            "id": index_id,
            "name": monitor.RULES[index_id]["name"],
            "value": value,
            "cash": value,
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
    except Exception as exc:
        print("kospi100 Naver fallback to Yahoo", type(exc).__name__, str(exc), flush=True)
        return _original_evaluate(index_id)


monitor.evaluate = _evaluate
