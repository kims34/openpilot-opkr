"""Validated helper functions for the v4.0 first-hour nowcast.

Frozen after the 2026-09-28 research gate.  The live runtime must only call
these helpers after the first regular 60-minute bar is complete.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

import probability_v39_open_nowcast as v39

NY = ZoneInfo("America/New_York")
UA = {"User-Agent": "Mozilla/5.0 IndexAlert/4.0-runtime"}
V39_CONFIG = {
    "SPY": (504, 100.0, 0.15),
    "QQQ": (756, 100.0, 0.15),
    "SCHD": (252, 100.0, 0.15),
}
FROZEN_CONFIG = {
    "SPY": (126, 30.0, 0.08),
    "QQQ": (126, 100.0, 0.08),
    "SCHD": (378, 10.0, 0.08),
}
MIN_TRAIN = 126


def _chart(symbol: str, range_: str, interval: str):
    encoded = requests.utils.quote(symbol, safe="")
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}",
        params={
            "range": range_,
            "interval": interval,
            "includePrePost": "false",
            "events": "div,splits",
        },
        headers=UA,
        timeout=25,
    )
    r.raise_for_status()
    chart = r.json().get("chart", {})
    if chart.get("error"):
        raise RuntimeError(f"vendor error: {symbol}")
    result = (chart.get("result") or [None])[0]
    if not result:
        raise RuntimeError(f"no data: {symbol}")
    return result


def daily_ohlcv(symbol: str):
    result = _chart(symbol, "10y", "1d")
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    out = {}
    for i, stamp in enumerate(result.get("timestamp") or []):
        day = datetime.fromtimestamp(int(stamp), timezone.utc).astimezone(NY).date().isoformat()
        try:
            values = tuple(float((quote.get(k) or [])[i]) for k in ("open", "high", "low", "close", "volume"))
        except Exception:
            continue
        if all(np.isfinite(values)) and min(values[:4]) > 0 and values[4] >= 0:
            out[day] = values
    return out


def first_hour(symbol: str):
    """Earliest regular 60-minute bar for each NYSE session in Yahoo's 2y archive."""
    result = _chart(symbol, "2y", "60m")
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    out = {}
    for i, stamp in enumerate(result.get("timestamp") or []):
        local = datetime.fromtimestamp(int(stamp), timezone.utc).astimezone(NY)
        minute = local.hour * 60 + local.minute
        if not (9 * 60 + 30 <= minute < 10 * 60 + 30):
            continue
        day = local.date().isoformat()
        if day in out:
            continue
        try:
            values = tuple(float((quote.get(k) or [])[i]) for k in ("open", "high", "low", "close", "volume"))
        except Exception:
            continue
        if all(np.isfinite(values)) and min(values[:4]) > 0 and values[4] >= 0:
            out[day] = values
    return out


def v39_series(symbol, completed_rows, meta, daily):
    dates = [d for d, _ in completed_rows]
    closes = np.asarray([p for _, p in completed_rows], float)
    if any(d not in daily for d in dates):
        raise RuntimeError(f"daily OHLC alignment failed: {symbol}")
    opens = np.asarray([daily[d][0] for d in dates], float)
    trace = v39._previous_trace(closes, dates, meta["target_date"])
    positions = np.asarray([int(x["t"]) for x in trace], int)
    previous = np.asarray([float(x["probability"]) for x in trace], float)
    outcomes = np.asarray([float(x["outcome"]) for x in trace], float)
    x = v39._features(opens, closes, positions)
    p39 = v39._ridge_predictions(x, outcomes, previous, V39_CONFIG[symbol])
    return dates, closes, positions, outcomes, p39


def hour_features(dates, closes, positions, own, spy, qqq, vix):
    rows = []
    volumes = []
    for j, t0 in enumerate(positions):
        t = int(t0)
        if t + 1 >= len(dates):
            continue
        target = dates[t + 1]
        if target not in own or target not in spy or target not in qqq or target not in vix:
            continue
        o, h, l, c, vol = own[target]
        so, sh, sl, sc, _ = spy[target]
        qo, qh, ql, qc, _ = qqq[target]
        vo, vh, vl, vc, _ = vix[target]
        prev = float(closes[t])
        if prev <= 0 or min(o, h, l, c, so, sc, qo, qc, vo, vc) <= 0:
            continue
        prior_vol = [x for _, x in volumes[-20:] if x > 0]
        med_vol = float(np.median(prior_vol)) if len(prior_vol) >= 10 else float("nan")
        volume_ratio = math.log(max(vol / med_vol, 1e-6)) if math.isfinite(med_vol) and med_vol > 0 else float("nan")
        close_loc = (c - l) / max(h - l, 1e-12)
        feature = np.asarray([
            o / prev - 1.0,
            c / o - 1.0,
            c / prev - 1.0,
            (h - l) / prev,
            close_loc,
            volume_ratio,
            sc / so - 1.0,
            qc / qo - 1.0,
            math.log(vc),
            vc / vo - 1.0,
        ], float)
        volumes.append((target, vol))
        if not np.all(np.isfinite(feature)):
            continue
        rows.append((j, t, target, feature))
    return rows
