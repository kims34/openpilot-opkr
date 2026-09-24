import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException


def attach(app, monitor, naver_kospi_quote, naver_usdkrw_quote):
    symbols = {
        "sp500": ("SPY", "America/New_York"),
        "ndx": ("QQQ", "America/New_York"),
        "djdiv": ("SCHD", "America/New_York"),
        "kospi100": ("^KS11", "Asia/Seoul"),
        "usdkrw": ("KRW=X", "Asia/Seoul"),
    }

    def local_day(ts: int, tz_name: str):
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).astimezone(ZoneInfo(tz_name)).date()

    @app.get("/history/{index_id}")
    def one_month_daily_history(index_id: str):
        if index_id not in symbols:
            raise HTTPException(404, "unknown market")

        symbol, tz_name = symbols[index_id]
        try:
            result = monitor.yahoo_result(symbol, "1mo", "1d", False)
        except Exception as exc:
            raise HTTPException(502, f"history unavailable: {type(exc).__name__}")

        timestamps = result.get("timestamp") or []
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        closes = quote.get("close", []) or []
        highs = quote.get("high", []) or []
        lows = quote.get("low", []) or []

        daily = []
        month_high = None
        month_high_ts = 0
        month_low = None
        month_low_ts = 0

        for ts, close, high, low in zip(timestamps, closes, highs, lows):
            if close is None:
                continue
            try:
                t = int(ts)
                c = float(close)
                h = float(high) if high is not None else c
                l = float(low) if low is not None else c
            except Exception:
                continue
            if c <= 0 or h <= 0 or l <= 0:
                continue
            daily.append((t, c))
            if month_high is None or h > month_high:
                month_high = h
                month_high_ts = t
            if month_low is None or l < month_low:
                month_low = l
                month_low_ts = t

        if not daily:
            raise HTTPException(502, "history unavailable")

        current_ts, current = daily[-1]
        source = "Yahoo 최근 1개월 일봉"

        try:
            if index_id == "kospi100":
                current, _, _, _, _, current_ts, _ = naver_kospi_quote()
                source = "KOSPI 최근 1개월 일봉 + 네이버 증권 최신값"
            elif index_id == "usdkrw":
                current, _, _, _, current_ts, _ = naver_usdkrw_quote()
                source = "USD/KRW 최근 1개월 일봉 + 네이버 증권 최신값"
            else:
                current, _, _, current_ts = monitor.current(symbol)
                source = f"{symbol} 최근 1개월 일봉 + 최신 거래값"
        except Exception as exc:
            print("history latest-value patch failed", index_id, type(exc).__name__, flush=True)

        try:
            current = float(current)
            current_ts = int(current_ts)
        except Exception:
            current_ts, current = daily[-1]

        # Keep exactly one close/current value per market day so the chart remains
        # a true daily chart even when the latest value comes from intraday data.
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

        # The latest live value may exceed today's regular-session high/low.
        if month_high is None or current > month_high:
            month_high = current
            month_high_ts = current_ts
        if month_low is None or current < month_low:
            month_low = current
            month_low_ts = current_ts

        if len(daily) < 2 or month_high is None or month_low is None:
            raise HTTPException(502, "not enough history")

        from_high_pct = (current / month_high - 1.0) * 100.0 if month_high > 0 else 0.0
        return {
            "id": index_id,
            "period": "1mo",
            "interval": "1d",
            "source": source,
            "points": [{"ts": ts, "value": value} for ts, value in daily],
            "min": month_low,
            "min_ts": month_low_ts,
            "max": month_high,
            "max_ts": month_high_ts,
            "current": current,
            "current_ts": current_ts,
            "from_high_percent": from_high_pct,
            "generated_at": int(time.time()),
        }
