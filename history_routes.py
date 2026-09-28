import math
import time
from datetime import datetime, timedelta, time as dt_time, timezone
from zoneinfo import ZoneInfo

import requests
from fastapi import HTTPException

import fx_basis
import production

NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://stock.naver.com/",
    "Accept": "application/json,text/plain,*/*",
}


def _number(value):
    if value is None:
        return None
    try:
        v = float(str(value).replace(",", "").replace("%", "").strip())
        return v if math.isfinite(v) else None
    except Exception:
        return None


def _date_ts(value, tz_name: str):
    tz = ZoneInfo(tz_name)
    raw = str(value or "").strip()
    if not raw:
        return 0
    try:
        if "T" in raw:
            return int(datetime.fromisoformat(raw).timestamp())
    except Exception:
        pass
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) >= 8:
        try:
            d = datetime.strptime(digits[:8], "%Y%m%d").date()
            return int(datetime.combine(d, dt_time(15, 30), tzinfo=tz).timestamp())
        except Exception:
            pass
    return 0


def _rows_with_price(payload):
    out = []

    def walk(node):
        if isinstance(node, dict):
            close = node.get("closePrice")
            date = node.get("localDate") or node.get("localTradedAt") or node.get("date")
            if close is not None and date is not None:
                out.append(node)
            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(payload)
    return out


def _naver_daily(urls, tz_name: str):
    last_error = None
    for url in urls:
        try:
            r = requests.get(url, headers=NAVER_HEADERS, timeout=15)
            r.raise_for_status()
            rows = _rows_with_price(r.json())
            parsed = {}
            cutoff = datetime.now(ZoneInfo(tz_name)).date() - timedelta(days=32)
            for row in rows:
                ts = _date_ts(row.get("localDate") or row.get("localTradedAt") or row.get("date"), tz_name)
                close = _number(row.get("closePrice"))
                if not ts or close is None or close <= 0:
                    continue
                day = datetime.fromtimestamp(ts, timezone.utc).astimezone(ZoneInfo(tz_name)).date()
                if day < cutoff:
                    continue
                parsed[day.isoformat()] = (ts, close)
            points = sorted(parsed.values(), key=lambda x: x[0])
            if len(points) >= 10:
                return points
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    raise RuntimeError("Naver history unavailable")


def _naver_kospi_history():
    return _naver_daily(
        [
            "https://api.stock.naver.com/chart/domestic/index/KOSPI?periodType=dayCandle",
            "https://m.stock.naver.com/api/index/KOSPI/price?page=1&pageSize=40",
        ],
        "Asia/Seoul",
    )


def _ecos_usdkrw_history():
    closes = fx_basis.fetch_usdkrw_1530_closes(
        requests,
        now=datetime.now(ZoneInfo("Asia/Seoul")),
        lookback_days=42,
        headers=NAVER_HEADERS,
    )
    tz = ZoneInfo("Asia/Seoul")
    cutoff = datetime.now(tz).date() - timedelta(days=32)
    return [
        (int(datetime.combine(day, dt_time(15, 30), tzinfo=tz).timestamp()), float(value))
        for day, value in closes
        if day >= cutoff and value > 0
    ]


def _session_label(index_id: str, market_state: str, source: str, estimated: bool, ts: int):
    state = str(market_state or "").upper()
    src = str(source or "")
    if index_id in {"sp500", "ndx", "djdiv"}:
        if state == "PRE" or "프리마켓" in src:
            return "프리마켓 현재가"
        if state == "REGULAR":
            return "정규장 현재가"
        if state == "POST" or "애프터마켓" in src:
            return "애프터마켓 현재가"
        if estimated or "선물연동" in src or "연동 추정" in src:
            seoul = datetime.fromtimestamp(ts or int(time.time()), timezone.utc).astimezone(ZoneInfo("Asia/Seoul"))
            if seoul.weekday() < 5 and 8 <= seoul.hour < 18:
                return "데이마켓 연동 추정"
            return "휴장시간 선물연동 추정"
        return "최신 거래가"
    if index_id == "kospi100":
        return "코스피 정규장 현재지수" if state == "REGULAR" else "코스피 장마감 지수"
    if index_id == "usdkrw":
        return "실시간 원/달러 환율" if state == "LIVE" else "최근 원/달러 환율"
    return "현재값"


def attach(app, monitor, naver_kospi_quote, naver_usdkrw_quote):
    symbols = {
        "sp500": ("SPY", "America/New_York"),
        "ndx": ("QQQ", "America/New_York"),
        "djdiv": ("SCHD", "America/New_York"),
        # Legacy wire id retained for installed clients; it represents KOSPI.
        "kospi100": ("^KS11", "Asia/Seoul"),
        "usdkrw": ("KRW=X", "Asia/Seoul"),
    }

    def local_day(ts: int, tz_name: str):
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).astimezone(ZoneInfo(tz_name)).date()

    def yahoo_daily(symbol: str):
        result = monitor.yahoo_result(symbol, "1mo", "1d", False)
        timestamps = result.get("timestamp") or []
        closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", []) or []
        out = []
        for ts, close in zip(timestamps, closes):
            try:
                t = int(ts)
                c = float(close)
            except Exception:
                continue
            if c > 0 and math.isfinite(c):
                out.append((t, c))
        return out

    def live_value(index_id: str, symbol: str):
        extra = dict(production.EXTRA_STATE.get(index_id) or {})
        state_row = monitor.get_state(index_id)
        value = None
        source = ""
        if state_row:
            try:
                candidate = float(state_row[2] or 0)
                if math.isfinite(candidate) and candidate > 0:
                    value = candidate
            except Exception:
                pass
            source = str(state_row[3] or "")
        if value is None:
            try:
                candidate = float(extra.get("last_value") or 0)
                if math.isfinite(candidate) and candidate > 0:
                    value = candidate
            except Exception:
                pass
        source = str(extra.get("source") or extra.get("extended_source") or source)
        market_state = str(extra.get("market_state") or "")
        value_ts = int(extra.get("value_ts") or 0)
        estimated = bool(extra.get("extended_estimate") or False)

        if value is None or value <= 0:
            if index_id == "kospi100":
                value, _, _, _, _, value_ts, market_state = naver_kospi_quote()
                source = "KOSPI · 네이버 증권"
                estimated = False
            elif index_id == "usdkrw":
                value, _, market_state, value_ts = monitor.current(symbol)
                source = "USD/KRW · Yahoo Finance 최근 거래가"
                estimated = False
            else:
                value, _, market_state, value_ts = monitor.current(symbol)
                source = f"{symbol} 최신 거래가"
                estimated = False

        if not value_ts:
            value_ts = int(time.time())
        return float(value), int(value_ts), market_state, source, estimated

    @app.get("/history/{index_id}")
    def one_month_daily_history(index_id: str):
        if index_id not in symbols:
            raise HTTPException(404, "unknown market")

        symbol, tz_name = symbols[index_id]
        history_source = ""
        try:
            if index_id == "kospi100":
                daily = _naver_kospi_history()
                history_source = "KOSPI 최근 1개월 · 네이버 증권 일별 시세"
            elif index_id == "usdkrw":
                daily = _ecos_usdkrw_history()
                history_source = "USD/KRW 최근 1개월 · 한국은행 ECOS 15:30 종가"
            else:
                daily = yahoo_daily(symbol)
                history_source = f"{symbol} 최근 1개월 일봉"
        except Exception as exc:
            print("monthly history fallback", index_id, type(exc).__name__, flush=True)
            try:
                daily = yahoo_daily(symbol)
                history_source = f"{symbol} 최근 1개월 일봉 · 보조 소스"
            except Exception as exc2:
                raise HTTPException(502, f"history unavailable: {type(exc2).__name__}")

        if not daily:
            raise HTTPException(502, "history unavailable")

        try:
            current, current_ts, market_state, live_source, estimated = live_value(index_id, symbol)
        except Exception as exc:
            print("history current-value fallback", index_id, type(exc).__name__, flush=True)
            current_ts, current = daily[-1]
            market_state, live_source, estimated = "CLOSED", history_source, False

        # Exactly one plotted value per market day. Today's point is replaced by
        # the latest live/session value; if the live session belongs to a new day,
        # append it as the final point.
        current_day = local_day(current_ts, tz_name)
        replaced = False
        for i in range(len(daily) - 1, -1, -1):
            if local_day(daily[i][0], tz_name) == current_day:
                daily[i] = (current_ts, current)
                replaced = True
                break
        if not replaced:
            daily.append((current_ts, current))
        daily.sort(key=lambda x: x[0])

        # De-duplicate by local market day after sorting, retaining the freshest
        # point for that day.
        by_day = {}
        for ts, value in daily:
            by_day[local_day(ts, tz_name).isoformat()] = (int(ts), float(value))
        daily = sorted(by_day.values(), key=lambda x: x[0])

        if len(daily) < 2:
            raise HTTPException(502, "not enough history")

        low_ts, low_value = min(daily, key=lambda x: x[1])
        high_ts, high_value = max(daily, key=lambda x: x[1])
        from_high_pct = (current / high_value - 1.0) * 100.0 if high_value > 0 else 0.0
        label = _session_label(index_id, market_state, live_source, estimated, current_ts)

        return {
            "id": index_id,
            "period": "1mo",
            "interval": "1d",
            "source": history_source,
            "latest_source": live_source,
            "latest_session": market_state,
            "latest_label": label,
            "latest_estimated": estimated,
            "points": [{"ts": ts, "value": value} for ts, value in daily],
            "min": low_value,
            "min_ts": low_ts,
            "max": high_value,
            "max_ts": high_ts,
            "current": current,
            "current_ts": current_ts,
            "from_high_percent": from_high_pct,
            "generated_at": int(time.time()),
        }
