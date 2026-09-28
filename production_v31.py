"""IndexAlert production v3.1: align day-change basis and chart snapshots.

This runtime keeps the existing market/probability stack intact, then verifies
U.S. ETF day change against the last *completed* regular session. It also binds
/status and /history responses to the same market snapshot so the Android card
and daily-dot chart cannot quietly mix values from different refreshes.
"""
from __future__ import annotations

import hashlib
import math
import time

from fastapi import HTTPException

import market_basis
import monitor
import production
import production_v30

app = production_v30.app
US_SYMBOLS = {"sp500": "SPY", "ndx": "QQQ", "djdiv": "SCHD"}
PRICE_TIMEZONES = {
    "sp500": "America/New_York",
    "ndx": "America/New_York",
    "djdiv": "America/New_York",
    "kospi100": "Asia/Seoul",
    "usdkrw": "Asia/Seoul",
}

_base_evaluate = monitor.evaluate


def _snapshot_id(index_id: str) -> str:
    state = monitor.get_state(index_id)
    extra = dict(production.EXTRA_STATE.get(index_id) or {})
    value = None
    if state:
        try:
            value = float(state[2] or 0)
        except Exception:
            value = None
    previous = extra.get("previous_close")
    basis_date = str(extra.get("previous_close_date") or "")
    value_ts = int(extra.get("value_ts") or 0)
    source = str(state[3] if state and len(state) > 3 else "")
    raw = f"{index_id}|{value_ts}|{value!r}|{previous!r}|{basis_date}|{source}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _align_us_basis(index_id: str, out: dict):
    symbol = US_SYMBOLS[index_id]
    extra = dict(production.EXTRA_STATE.get(index_id) or {})
    try:
        result = monitor.yahoo_result(symbol, "5d", "5m", False)
        points = monitor.series(result)
        value_ts = int(out.get("value_ts") or extra.get("value_ts") or time.time())
        previous, previous_date = market_basis.regular_close_basis(
            points,
            value_ts,
            str(out.get("market_state") or extra.get("market_state") or ""),
            "America/New_York",
        )
        current = float(out.get("value") or 0)
        if (
            previous is None
            or previous <= 0
            or not math.isfinite(previous)
            or current <= 0
            or not math.isfinite(current)
        ):
            raise RuntimeError("no verified completed-session basis")
        change = current - previous
        percent = (current / previous - 1.0) * 100.0
        extra.update(
            previous_close=previous,
            previous_close_date=previous_date,
            day_change=change,
            day_change_percent=percent,
            basis_verified=True,
        )
        production.EXTRA_STATE[index_id] = extra
        out.update(
            previous_close=previous,
            previous_close_date=previous_date,
            day_change=change,
            day_change_percent=percent,
            basis_verified=True,
        )
        print(
            "aligned regular-close basis",
            {
                "id": index_id,
                "current": current,
                "previous_close": previous,
                "previous_close_date": previous_date,
                "day_change": change,
                "day_change_percent": percent,
            },
            flush=True,
        )
    except Exception as exc:
        # Never display a stale/wrong day-change basis. The Android v4.3 client
        # will show a temporary verification state rather than contradictory data.
        extra.update(
            previous_close=None,
            previous_close_date=None,
            day_change=None,
            day_change_percent=None,
            basis_verified=False,
        )
        production.EXTRA_STATE[index_id] = extra
        out.update(
            previous_close=None,
            previous_close_date=None,
            day_change=None,
            day_change_percent=None,
            basis_verified=False,
        )
        print("US previous-close verification unavailable", index_id, type(exc).__name__, flush=True)
    return out


def _evaluate(index_id: str):
    out = _base_evaluate(index_id)
    if index_id in US_SYMBOLS:
        out = _align_us_basis(index_id, out)
    snapshot = _snapshot_id(index_id)
    extra = dict(production.EXTRA_STATE.get(index_id) or {})
    extra["snapshot_id"] = snapshot
    production.EXTRA_STATE[index_id] = extra
    out["snapshot_id"] = snapshot
    return out


monitor.evaluate = _evaluate


# Preserve the established route logic, adding snapshot metadata only.
_old_status = next(
    (route.endpoint for route in app.router.routes if getattr(route, "path", None) == "/status"),
    None,
)
_old_history = next(
    (route.endpoint for route in app.router.routes if getattr(route, "path", None) == "/history/{index_id}"),
    None,
)
if _old_status is None or _old_history is None:
    raise RuntimeError("required market routes not installed")

app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "path", None) not in {"/status", "/history/{index_id}"}
]


@app.get("/status")
def status_v31():
    payload = _old_status()
    indices = payload.get("indices", []) if isinstance(payload, dict) else []
    for row in indices:
        index_id = str(row.get("id") or "")
        extra = dict(production.EXTRA_STATE.get(index_id) or {})
        row["previous_close_date"] = extra.get("previous_close_date")
        row["basis_verified"] = extra.get("basis_verified")
        row["snapshot_id"] = _snapshot_id(index_id)
    return payload


@app.get("/history/{index_id}")
def history_v31(index_id: str, snapshot_id: str = ""):
    if index_id not in PRICE_TIMEZONES:
        raise HTTPException(404, "unknown market")

    before = _snapshot_id(index_id)
    if snapshot_id and snapshot_id != before:
        raise HTTPException(409, "market snapshot changed; refresh")

    payload = _old_history(index_id)
    after = _snapshot_id(index_id)
    if snapshot_id and snapshot_id != after:
        raise HTTPException(409, "market snapshot changed during chart load; refresh")

    if isinstance(payload, dict):
        payload["price_timezone"] = PRICE_TIMEZONES[index_id]
        payload["snapshot_id"] = after
        extra = dict(production.EXTRA_STATE.get(index_id) or {})
        payload["previous_close"] = extra.get("previous_close")
        payload["previous_close_date"] = extra.get("previous_close_date")
    return payload
