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
    "Referer": "https://stock.naver.com/",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
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
    r = requests.get(NAVER_API, headers=NAVER_HEADERS, timeout=8)
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

    if ratio is None:
        ratio = 0.0
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
    return value, previous_close, day_change, ratio, high52, high52_date, ts, "네이버 증권 · KPI100"


def _naver_legacy_quote():
    headers = dict(NAVER_HEADERS)
    headers["Accept"] = "text/html,application/xhtml+xml"
    r = requests.get(NAVER_LEGACY, headers=headers, timeout=8)
    r.raise_for_status()
    raw = r.text
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", raw)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", text))
    text = re.sub(r"\s+", " ", text)

    def find(pattern):
        m = re.search(pattern, text)
        return _num(m.group(1)) if m else None

    value = find(r"코스피100\s+([0-9,]+(?:\.[0-9]+)?)")
    ratio = find(r"등락률\s*([+\-]?[0-9,]+(?:\.[0-9]+)?)\s*%")
    change_abs = find(r"전일대비(?:\s*(?:상승|하락|보합))?\s*([0-9,]+(?:\.[0-9]+)?)")
    high52 = find(r"52주최고\s*([0-9,]+(?:\.[0-9]+)?)")
    if value is None or value <= 0:
        raise RuntimeError("Naver legacy KPI100 price unavailable")
    ratio = ratio or 0.0
    sign = -1.0 if ratio < 0 else (1.0 if ratio > 0 else 0.0)
    day_change = (change_abs or 0.0) * sign
    previous_close = value - day_change if value - day_change > 0 else value
    print("kospi100 Naver legacy", {"value": value, "change": day_change, "ratio": ratio, "high52": high52}, flush=True)
    return value, previous_close, day_change, ratio, high52, None, int(time.time()), "네이버 증권 · KPI100"


def _naver_quote():
    try:
        return _naver_api_quote()
    except Exception as exc:
        print("kospi100 Naver API failed", type(exc).__name__, flush=True)
    return _naver_legacy_quote()


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

        monitor.save_state(index_id, ath, value, value, source)
        production.EXTRA_STATE[index_id] = {
            "previous_close": previous_close,
            "day_change": day_change,
            "day_change_percent": day_change_percent,
            "ath_date": ath_date,
            "ath_days": production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None,
            "drawdown": drawdown,
            "market_state": "REGULAR" if datetime.now(tz).weekday() < 5 and 9 <= datetime.now(tz).hour < 16 else "CLOSED",
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
            "market_state": production.EXTRA_STATE[index_id]["market_state"],
            "cash_ts": value_ts,
            "value_ts": value_ts,
            **production.EXTRA_STATE[index_id],
        }
        print("check", result, flush=True)
        return result
    except Exception as exc:
        print("kospi100 Naver fallback to Yahoo", type(exc).__name__, flush=True)
        return _original_evaluate(index_id)


monitor.evaluate = _evaluate
