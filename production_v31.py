"""IndexAlert production v3.1: align day-change basis and chart snapshots.

This runtime keeps the existing market/probability stack intact, then verifies
U.S. ETF day change against the last *completed* regular session. USD/KRW uses
an actual live market quote for the current value and the prior Seoul FX market
15:30 close from Bank of Korea ECOS (731Y003/0000003) for day change. It also
binds /status and /history responses to the same market snapshot so the Android
card and daily-dot chart cannot quietly mix values from different refreshes.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException

import fx_basis
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
SEOUL = ZoneInfo("Asia/Seoul")

_base_evaluate = monitor.evaluate


def _runtime_revision() -> str | None:
    revision = os.getenv("INDEXALERT_DEPLOY_TRIGGER", "").strip()
    return revision or None


def _snapshot_id(index_id: str) -> str:
    state = monitor.get_state(index_id)
    extra = dict(production.EXTRA_STATE.get(index_id) or {})
    value = None
    if state:
        try:
            value = float(state[2] or 0)
        except Exception:
            value = None
    if value is None:
        try:
            candidate = float(extra.get("last_value") or 0)
            value = candidate if candidate > 0 else None
        except Exception:
            value = None
    previous = extra.get("previous_close")
    basis_date = str(extra.get("previous_close_date") or "")
    value_ts = int(extra.get("value_ts") or 0)
    source = str(extra.get("source") or (state[3] if state and len(state) > 3 else ""))
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
        # Never display a stale/wrong day-change basis. The Android client will
        # show a temporary verification state rather than contradictory data.
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


def _live_usdkrw_quote() -> tuple[float, int, str]:
    last_error: Exception | None = None
    for range_, interval in (("1d", "1m"), ("5d", "5m")):
        try:
            result = monitor.yahoo_result("KRW=X", range_, interval, True)
            points = monitor.series(result)
            if not points:
                raise RuntimeError("no USD/KRW live points")
            ts, value = points[-1]
            value = float(value)
            if not math.isfinite(value) or value <= 0:
                raise RuntimeError("invalid USD/KRW live value")
            age = max(0, int(time.time()) - int(ts))
            state = "LIVE" if age <= 60 * 30 else "CLOSED"
            return value, int(ts), state
        except Exception as exc:
            last_error = exc
    raise last_error or RuntimeError("USD/KRW live quote unavailable")


def _align_usdkrw(out: dict):
    extra = dict(production.EXTRA_STATE.get("usdkrw") or {})
    try:
        current, value_ts, market_state = _live_usdkrw_quote()
        current_day = datetime.fromtimestamp(value_ts, tz=timezone.utc).astimezone(SEOUL).date()
        closes = fx_basis.fetch_usdkrw_1530_closes(
            monitor.requests,
            now=datetime.fromtimestamp(value_ts, tz=timezone.utc),
            headers=monitor.UA,
        )
        previous, previous_date = fx_basis.prior_business_close(closes, current_day)
        if previous is None or previous <= 0 or not previous_date:
            raise RuntimeError("no verified prior 15:30 close")

        change = current - previous
        percent = (current / previous - 1.0) * 100.0
        source = "USD/KRW 실시간 · Yahoo Finance | 전일 15:30 종가 · 한국은행 ECOS"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Keep the shared state row aligned with the value shown on the card so
        # the history route's last dot uses this exact live quote as well.
        monitor.save_state("usdkrw", 0.0, current, current, source)
        extra.update(
            ath=None,
            last_cash=current,
            last_value=current,
            source=source,
            updated_at=now_iso,
            previous_close=previous,
            previous_close_date=previous_date,
            day_change=change,
            day_change_percent=percent,
            ath_date=None,
            ath_days=None,
            drawdown=None,
            market_state=market_state,
            value_ts=value_ts,
            basis_verified=True,
            quote_provider="Yahoo Finance KRW=X live",
            basis_provider="Bank of Korea ECOS 731Y003/0000003 15:30 close",
        )
        production.EXTRA_STATE["usdkrw"] = extra
        out.update(
            id="usdkrw",
            name="USD/KRW 달러 환율",
            value=current,
            cash=current,
            ath=None,
            drawdown=None,
            source=source,
            market_state=market_state,
            cash_ts=value_ts,
            value_ts=value_ts,
            previous_close=previous,
            previous_close_date=previous_date,
            day_change=change,
            day_change_percent=percent,
            basis_verified=True,
            quote_provider=extra["quote_provider"],
            basis_provider=extra["basis_provider"],
        )
        print(
            "aligned USDKRW live/15:30 basis",
            {
                "current": current,
                "current_ts": value_ts,
                "previous_close": previous,
                "previous_close_date": previous_date,
                "day_change": change,
                "day_change_percent": percent,
                "market_state": market_state,
            },
            flush=True,
        )
    except Exception as exc:
        # Keep the current card from displaying a mathematically valid but
        # definitionally wrong bank-notice percentage if the official 15:30
        # reference cannot be verified.
        extra.update(
            previous_close=None,
            previous_close_date=None,
            day_change=None,
            day_change_percent=None,
            basis_verified=False,
        )
        production.EXTRA_STATE["usdkrw"] = extra
        out.update(
            previous_close=None,
            previous_close_date=None,
            day_change=None,
            day_change_percent=None,
            basis_verified=False,
        )
        print("USD/KRW 15:30 basis verification unavailable", type(exc).__name__, str(exc), flush=True)
    return out


def _evaluate(index_id: str):
    out = _base_evaluate(index_id)
    if index_id in US_SYMBOLS:
        out = _align_us_basis(index_id, out)
    elif index_id == "usdkrw":
        out = _align_usdkrw(out)
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
    if isinstance(payload, dict):
        payload["runtime_revision"] = _runtime_revision()
    indices = payload.get("indices", []) if isinstance(payload, dict) else []
    for row in indices:
        index_id = str(row.get("id") or "")
        extra = dict(production.EXTRA_STATE.get(index_id) or {})
        row["previous_close_date"] = extra.get("previous_close_date")
        row["basis_verified"] = extra.get("basis_verified")
        row["snapshot_id"] = _snapshot_id(index_id)
        if index_id == "usdkrw":
            # Force the status card to use the same live value and basis that
            # were verified by this outer runtime, regardless of older routes.
            for key in (
                "ath", "last_cash", "last_value", "source", "updated_at",
                "previous_close", "day_change", "day_change_percent", "ath_date",
                "ath_days", "drawdown", "market_state", "value_ts",
                "quote_provider", "basis_provider",
            ):
                if key in extra:
                    row[key] = extra.get(key)
            # Older layers may briefly have a Yahoo/provider fallback previous
            # close before the ECOS 15:30 basis is verified. Preserve the live
            # quote if useful, but never expose that fallback as day change.
            row.update(fx_basis.public_basis_fields(extra))
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
        payload["runtime_revision"] = _runtime_revision()
        payload["price_timezone"] = PRICE_TIMEZONES[index_id]
        payload["snapshot_id"] = after
        extra = dict(production.EXTRA_STATE.get(index_id) or {})
        if index_id == "usdkrw":
            public_basis = fx_basis.public_basis_fields(extra)
            payload["previous_close"] = public_basis["previous_close"]
            payload["previous_close_date"] = public_basis["previous_close_date"]
            payload["basis_verified"] = public_basis["basis_verified"]
            payload["basis_provider"] = public_basis["basis_provider"]
            payload["basis_contract"] = public_basis["basis_contract"]
            payload["quote_provider"] = extra.get("quote_provider")
        else:
            payload["previous_close"] = extra.get("previous_close")
            payload["previous_close_date"] = extra.get("previous_close_date")
    return payload


# The build-bound Android registration/receipt contract must survive runtime
# entrypoint drift. Install the same idempotent overlay here as v32 so either
# `production_v31:app` or `production_v32:app` exposes identical push semantics.
import push_build_registration as _push_build_registration
_push_build_registration.attach(app)
