"""KOSPI extended-hours continuity patch.

Preferred source remains EWY + USD/KRW from extended_session_probability.
When that market is not producing a fresh trade (for example Korea Monday
pre-open before US cash/ETF trading resumes), use fresh ES/NQ futures anchored
at the last completed KOSPI cash close.  This is never labelled as a KOSPI cash
print: it is a conservative linked estimate only.
"""
from __future__ import annotations

import math
import time

import numpy as np

import extended_session_probability as esp
import monitor
import production_fixed

_ORIGINAL = esp._kospi_proxy_signal


def _futures_fallback(now: float):
    current, previous, _, _, _, cash_ts, market_state = production_fixed._naver_kospi_quote()
    if market_state == "REGULAR":
        raise ValueError("KOSPI 정규장 진행 중")
    if min(current, previous) <= 0:
        raise ValueError("KOSPI 기준가 이상")

    moves = []
    latest_ts = 0
    used = []
    for proxy in ("ES=F", "NQ=F"):
        try:
            ratio, _, anchor, _, proxy_ts = monitor.proxy_ratio_from_cash_close(proxy, int(cash_ts))
            if not esp._fresh(int(proxy_ts or 0), now, 60):
                continue
            if not math.isfinite(ratio) or ratio <= 0 or abs(ratio - 1.0) > 0.10:
                continue
            # Use only the incremental move since the completed Korea cash close.
            moves.append(ratio - 1.0)
            latest_ts = max(latest_ts, int(proxy_ts))
            used.append(proxy)
        except Exception:
            continue

    if not moves:
        raise ValueError("KOSPI 글로벌선물 연동값 대기")

    # ES/NQ are a weaker proxy for KOSPI than EWY+FX.  Compress the raw move
    # before it reaches the already-bounded KOSPI probability overlay.
    raw = float(np.mean(moves))
    incremental = float(np.clip(raw * 0.65, -0.035, 0.035))
    return {
        "cash_close": current,
        "move": incremental,
        "estimated_price": current * (1.0 + incremental),
        "source": f"KOSPI 글로벌선물 연동 추정 · {'/'.join(used)}",
        "session": "GLOBAL_FUTURES_PROXY",
        "data_ts": latest_ts,
        "proxy_strength": "conservative",
    }


def _patched(now: float):
    try:
        return _ORIGINAL(now)
    except Exception as preferred_error:
        try:
            return _futures_fallback(now)
        except Exception:
            raise preferred_error


esp._kospi_proxy_signal = _patched
print("KOSPI extended-session futures fallback active", flush=True)
