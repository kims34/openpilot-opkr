"""Retry long-history research using explicit Yahoo period bounds."""
import math
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import one_month_window_research as research

NY = ZoneInfo("America/New_York")


def fetch_period_rows(symbol):
    now = int(time.time())
    attempts = [
        {"period1": 0, "period2": now, "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        {"range": "max", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
    ]
    best_rows = []
    best_jump = None
    diagnostics = []
    for params in attempts:
        r = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            params=params,
            headers={"User-Agent": "Mozilla/5.0 IndexAlert/monthly-window-research-v2"},
            timeout=30,
        )
        diagnostics.append((r.status_code, len(r.content), r.url))
        r.raise_for_status()
        payload = r.json().get("chart", {})
        if payload.get("error"):
            continue
        result = (payload.get("result") or [None])[0]
        if not result or result.get("meta", {}).get("symbol") != symbol:
            continue
        timestamps = result.get("timestamp") or []
        closes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
        by_day = {}
        for ts, close in zip(timestamps, closes):
            if close is None:
                continue
            px = float(close)
            if not math.isfinite(px) or px <= 0:
                continue
            day = datetime.fromtimestamp(int(ts), timezone.utc).astimezone(NY).date().isoformat()
            by_day[day] = px
        rows = sorted(by_day.items())
        if len(rows) > len(best_rows):
            best_rows = rows
            jumps = [abs(rows[i][1] / rows[i - 1][1] - 1.0) for i in range(1, len(rows))]
            best_jump = max(jumps) if jumps else 0.0
    print("HISTORY_FETCH_DIAGNOSTIC", symbol, diagnostics, "points", len(best_rows), flush=True)
    if len(best_rows) < 1100:
        raise RuntimeError(f"history too short points={len(best_rows)}")
    if best_jump is not None and best_jump > 0.40:
        raise RuntimeError(f"unadjusted/discontinuous history max_jump={best_jump:.3f}")
    return best_rows, best_jump or 0.0


research.fetch_max_rows = fetch_period_rows

if __name__ == "__main__":
    research.main()
