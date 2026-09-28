"""Pure market-session basis helpers for IndexAlert."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def regular_close_basis(points, current_ts: int, market_state: str, tz_name: str):
    """Return (close, YYYY-MM-DD) for the last completed regular session.

    ``points`` must contain regular-session price samples only. During a regular
    session the current local market day is still incomplete, so the basis is
    the most recent earlier market day. Outside regular hours the newest
    completed regular day is the basis (same day for post-market, prior day for
    pre-market/weekends/holidays).
    """
    tz = ZoneInfo(tz_name)
    by_day = {}
    for ts, value in points or []:
        try:
            t = int(ts)
            v = float(value)
        except Exception:
            continue
        if t <= 0 or not math.isfinite(v) or v <= 0:
            continue
        day = datetime.fromtimestamp(t, timezone.utc).astimezone(tz).date()
        previous = by_day.get(day)
        if previous is None or t >= previous[0]:
            by_day[day] = (t, v)

    if not by_day:
        return None, None

    try:
        current_day = datetime.fromtimestamp(int(current_ts), timezone.utc).astimezone(tz).date()
    except Exception:
        current_day = max(by_day)

    state = str(market_state or "").upper()
    if state == "REGULAR":
        eligible = [day for day in by_day if day < current_day]
    else:
        eligible = [day for day in by_day if day <= current_day]

    if not eligible:
        return None, None

    basis_day = max(eligible)
    return float(by_day[basis_day][1]), basis_day.isoformat()
