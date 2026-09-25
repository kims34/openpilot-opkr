import math
import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

import monitor
import production
import production_naver_state

app = production_naver_state.app
_base_evaluate = monitor.evaluate

INVESTING_USDKRW_URLS = (
    "https://kr.investing.com/currencies/usd-krw",
    "https://www.investing.com/currencies/usd-krw",
)
INVESTING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://kr.investing.com/",
    "Cache-Control": "no-cache",
}


def _loose_num(value):
    if value is None:
        return None
    text = str(value).replace(",", "").replace("\u2212", "-").strip()
    text = re.sub(r"[^0-9+\-.]", "", text)
    if not text or text in {"+", "-", "."}:
        return None
    try:
        value = float(text)
    except Exception:
        return None
    return value if math.isfinite(value) else None


def _text(node):
    return node.get_text(" ", strip=True) if node is not None else None


def _investing_usdkrw_quote():
    errors = []
    for url in INVESTING_USDKRW_URLS:
        try:
            r = monitor.requests.get(url, headers=INVESTING_HEADERS, timeout=12)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            current = _loose_num(_text(soup.select_one('[data-test="instrument-price-last"]')))
            change = _loose_num(_text(soup.select_one('[data-test="instrument-price-change"]')))
            ratio = _loose_num(_text(soup.select_one('[data-test="instrument-price-change-percent"]')))

            if current is None or not (500.0 <= current <= 2500.0):
                raise RuntimeError("Investing USD/KRW current unavailable")

            if change is None and ratio is not None and abs(ratio) < 20:
                previous = current / (1.0 + ratio / 100.0) if abs(1.0 + ratio / 100.0) > 1e-9 else current
                change = current - previous
            elif change is not None:
                previous = current - change
            else:
                raise RuntimeError("Investing USD/KRW change unavailable")

            if previous <= 0 or not math.isfinite(previous):
                raise RuntimeError("Investing USD/KRW previous close invalid")
            if ratio is None:
                ratio = (current / previous - 1.0) * 100.0
            if not math.isfinite(ratio) or abs(ratio) > 20:
                raise RuntimeError("Investing USD/KRW percent invalid")

            value_ts = int(datetime.now(timezone.utc).timestamp())
            print(
                "usdkrw investing quote",
                {"current": current, "previous": previous, "change": change, "ratio": ratio, "url": url},
                flush=True,
            )
            return current, previous, change, ratio, value_ts, "REALTIME", "Investing.com · 실시간 FX"
        except Exception as exc:
            errors.append(f"{url}:{type(exc).__name__}")
    raise RuntimeError("Investing USD/KRW unavailable " + ",".join(errors))


def _yahoo_usdkrw_quote():
    result = monitor.yahoo_result("KRW=X", "5d", "1m", True)
    points = monitor.series(result)
    if not points:
        raise RuntimeError("Yahoo USD/KRW unavailable")
    value_ts, current = points[-1]
    meta = result.get("meta", {})
    previous = None
    for key in ("regularMarketPreviousClose", "previousClose", "chartPreviousClose"):
        try:
            v = float(meta.get(key) or 0)
            if math.isfinite(v) and v > 0:
                previous = v
                break
        except Exception:
            pass
    if current is None or not (500.0 <= float(current) <= 2500.0):
        raise RuntimeError("Yahoo USD/KRW current invalid")
    current = float(current)
    if previous is None or previous <= 0:
        raise RuntimeError("Yahoo USD/KRW previous close invalid")
    change = current - previous
    ratio = (current / previous - 1.0) * 100.0
    if not math.isfinite(ratio) or abs(ratio) > 20:
        raise RuntimeError("Yahoo USD/KRW percent invalid")
    print(
        "usdkrw yahoo quote",
        {"current": current, "previous": previous, "change": change, "ratio": ratio},
        flush=True,
    )
    return current, previous, change, ratio, int(value_ts), "REALTIME", "Yahoo Finance FX · Investing 대체"


def _make_result(index_id, quote):
    current, previous, change, ratio, value_ts, market_state, source = quote
    now = datetime.now(timezone.utc).isoformat()
    production.EXTRA_STATE[index_id] = {
        "ath": None,
        "last_cash": current,
        "last_value": current,
        "source": source,
        "updated_at": now,
        "previous_close": previous,
        "day_change": change,
        "day_change_percent": ratio,
        "ath_date": None,
        "ath_days": None,
        "drawdown": None,
        "market_state": market_state,
        "value_ts": value_ts,
    }
    return {
        "id": index_id,
        "name": "USD/KRW 달러 환율",
        "value": current,
        "cash": current,
        "ath": None,
        "drawdown": None,
        "source": source,
        "market_state": market_state,
        "cash_ts": value_ts,
        "value_ts": value_ts,
        **production.EXTRA_STATE[index_id],
    }


def _evaluate_usdkrw(index_id: str):
    try:
        return _make_result(index_id, _investing_usdkrw_quote())
    except Exception as exc:
        print("usdkrw investing failed -> yahoo fallback", type(exc).__name__, str(exc), flush=True)

    try:
        return _make_result(index_id, _yahoo_usdkrw_quote())
    except Exception as exc:
        print("usdkrw yahoo failed -> naver fallback", type(exc).__name__, str(exc), flush=True)

    result = _base_evaluate(index_id)
    source = "네이버 증권 · 하나은행 고시 (2차 fallback)"
    if index_id in production.EXTRA_STATE:
        production.EXTRA_STATE[index_id]["source"] = source
    result["source"] = source
    return result


def _evaluate(index_id: str):
    if index_id == "usdkrw":
        return _evaluate_usdkrw(index_id)
    return _base_evaluate(index_id)


monitor.evaluate = _evaluate
