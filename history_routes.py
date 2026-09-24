import time
from fastapi import HTTPException


def attach(app, monitor, naver_kospi_quote, naver_usdkrw_quote):
    symbols = {
        "sp500": ("SPY", True),
        "ndx": ("QQQ", True),
        "djdiv": ("SCHD", True),
        "kospi100": ("^KS11", False),
        "usdkrw": ("KRW=X", False),
    }

    @app.get("/history/{index_id}")
    def one_week_history(index_id: str):
        if index_id not in symbols:
            raise HTTPException(404, "unknown market")

        symbol, prepost = symbols[index_id]
        try:
            result = monitor.yahoo_result(symbol, "1mo", "1h", prepost)
            points = monitor.series(result)
        except Exception as exc:
            raise HTTPException(502, f"history unavailable: {type(exc).__name__}")

        if not points:
            raise HTTPException(502, "history unavailable")

        latest_ts = int(points[-1][0])
        cutoff = latest_ts - 7 * 24 * 60 * 60
        filtered = [(int(ts), float(value)) for ts, value in points if int(ts) >= cutoff and value > 0]

        source = "Yahoo 1시간봉"
        try:
            if index_id == "kospi100":
                current, _, _, _, _, ts, _ = naver_kospi_quote()
                filtered = [(t, v) for t, v in filtered if t < int(ts)]
                filtered.append((int(ts), float(current)))
                source = "KOSPI 과거 1시간봉 + 네이버 증권 최신값"
            elif index_id == "usdkrw":
                current, _, _, _, ts, _ = naver_usdkrw_quote()
                filtered = [(t, v) for t, v in filtered if t < int(ts)]
                filtered.append((int(ts), float(current)))
                source = "USD/KRW 과거 1시간봉 + 네이버 증권 최신값"
        except Exception as exc:
            print("history latest-value patch failed", index_id, type(exc).__name__, flush=True)

        if len(filtered) < 2:
            raise HTTPException(502, "not enough history")

        values = [v for _, v in filtered]
        first = values[0]
        last = values[-1]
        change_pct = (last / first - 1.0) * 100.0 if first > 0 else 0.0
        return {
            "id": index_id,
            "period": "1w",
            "source": source,
            "points": [{"ts": ts, "value": value} for ts, value in filtered],
            "min": min(values),
            "max": max(values),
            "start": first,
            "end": last,
            "change_percent": change_pct,
            "generated_at": int(time.time()),
        }
