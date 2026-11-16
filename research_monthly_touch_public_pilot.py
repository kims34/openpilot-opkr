"""Public-history SPY/VIX and QQQ/VXN pilot: NOT genuine historical PIT evidence.

The available Yahoo daily bars are retrospective and can be revised; their
historical first-publication timestamps are not authenticated. This tool makes
no live model/alert/broker changes and never persists fetched price history.
"""
import json
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

import next_day_probability as market
import research_monthly_touch_v1 as research

NY = ZoneInfo("America/New_York")
SYMBOLS = {"SPY": "^VIX", "QQQ": "^VXN"}


def raw_daily(symbol):
    response = requests.get(
        "https://query1.finance.yahoo.com/v8/finance/chart/" + quote(symbol, safe=""),
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert Research/1.0"}, timeout=30)
    response.raise_for_status()
    data = response.json().get("chart", {})
    if data.get("error") or len(data.get("result") or []) != 1:
        raise research.SourceQualityError("vendor returned no unambiguous daily history")
    item = data["result"][0]
    stamps = item.get("timestamp") or []
    quote_data = ((item.get("indicators") or {}).get("quote") or [None])[0]
    if quote_data is None:
        raise research.SourceQualityError("missing vendor OHLC")
    fields = [quote_data.get(name) or [] for name in ("high", "low", "close")]
    if not len(stamps) == len(fields[0]) == len(fields[1]) == len(fields[2]):
        raise research.SourceQualityError("vendor daily OHLC schema length mismatch")
    out = {}
    missing = []
    for t, high, low, close in zip(stamps, *fields):
        day = datetime.fromtimestamp(int(t), timezone.utc).astimezone(NY).date().isoformat()
        if day in out or day in missing:
            raise research.SourceQualityError("duplicate source trading session")
        if any(z is None for z in (high, low, close)):
            missing.append(day)
            continue
        out[day] = (float(high), float(low), float(close))
    return out, missing


def run():
    result = {}
    for symbol, iv_symbol in SYMBOLS.items():
        try:
            close_rows, metadata = market.fetch_history(symbol, time.time())
            ohlc_map, absent = raw_daily(symbol)
            # Never replace absent day highs/lows with daily closing prices.
            ohlc = [(d, *ohlc_map[d]) for d, _ in close_rows if d in ohlc_map]
            if len(ohlc) != len(close_rows):
                raise research.SourceQualityError(
                    "missing instrument OHLC; absent=" + str(len(close_rows) - len(ohlc))
                    + ", empty_vendordays=" + str(len(absent)))
            macro, macro_absent = raw_daily(iv_symbol)
            iv = {d: z[2] for d, z in macro.items()}
            evaluated = research.evaluate(symbol, close_rows, ohlc, iv)
            evaluated["source"] = "Yahoo Finance historical daily backfill; not as-issued"
            evaluated["historical_publication_times_authenticated"] = False
            evaluated["completed_session"] = metadata["as_of"]
            evaluated["instrument_input_sha256"] = research.digest(ohlc)
            evaluated["iv_input_sha256"] = research.digest(sorted(iv.items()))
            evaluated["missing_vendor_iv_bars"] = len(macro_absent)
            result[symbol] = evaluated
        except (ValueError, requests.RequestException, research.SourceQualityError) as exc:
            result[symbol] = {
                "status": "BLOCKED_SOURCE_OR_HISTORY",
                "error_type": type(exc).__name__,
                "reason": str(exc)[:240],
                "production_admission": "BLOCKED", "app_changed": False,
                "historical_accuracy_improvement_proven": False,
            }
    print("MONTHLY_TOUCH_RESEARCH_RESULT", json.dumps(result, ensure_ascii=False, sort_keys=True))
    if any(v.get("status") == "BLOCKED_SOURCE_OR_HISTORY" for v in result.values()):
        print("MONTHLY_TOUCH_WARNING insufficient data for some symbols", file=sys.stderr)


if __name__ == "__main__":
    run()
