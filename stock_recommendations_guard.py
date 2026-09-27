"""Production guardrails for the individual-stock probability screener.

The constituent sources occasionally contain fund/security tickers from page
metadata. A stock recommendation must be an actual equity, so validate Yahoo's
instrument type while fetching the same 10-year history used by the model.
The v3.1 cache is invalidated once so stale ETF candidates cannot survive an
upgrade through the persistent Railway volume.
"""
import math
import requests

import monitor
import stock_recommendations as screener

CACHE_SCHEMA = "equity-only-v1"
_original_init_db = screener.init_db


def _guarded_init_db():
    _original_init_db()
    with monitor.db() as con:
        row = con.execute(
            "SELECT value FROM stock_recommendation_meta WHERE key='cache_schema'"
        ).fetchone()
        if not row or row[0] != CACHE_SCHEMA:
            con.execute("DELETE FROM stock_recommendation_cache")
            con.execute("DELETE FROM stock_recommendation_meta")
            con.execute(
                "INSERT INTO stock_recommendation_meta(key,value) VALUES('cache_schema',?)",
                (CACHE_SCHEMA,),
            )
            print("stock recommendation cache invalidated", CACHE_SCHEMA, flush=True)


def _completed_equity_history(symbol, now=None):
    ys = screener._yahoo_symbol(symbol)
    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ys}",
        params={
            "range": "10y",
            "interval": "1d",
            "includePrePost": "false",
            "events": "splits",
        },
        headers=screener.UA,
        timeout=20,
    )
    response.raise_for_status()
    chart = response.json().get("chart", {})
    if chart.get("error"):
        raise ValueError("vendor error")
    result = (chart.get("result") or [None])[0]
    if not result:
        raise ValueError("history unavailable")

    meta = result.get("meta", {})
    instrument = str(meta.get("instrumentType") or "").upper().strip()
    if instrument != "EQUITY":
        raise ValueError(f"non-equity instrument: {instrument or 'unknown'}")

    rows, session_meta = screener.base.parse_history(result, now)
    if len(rows) < 320:
        raise ValueError("insufficient completed equity history")
    if any(not math.isfinite(float(price)) or float(price) <= 0 for _, price in rows):
        raise ValueError("invalid equity history")
    return rows, session_meta


screener.init_db = _guarded_init_db
screener._completed_history = _completed_equity_history
