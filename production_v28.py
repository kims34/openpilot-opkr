"""IndexAlert production v3.0: Naver KPI100 + verified ATH safety floor.

Current/previous/day change come from Naver's realtime KPI100 polling API on
every market poll.  Slow historical peak cross-checks are intentionally run at
most once per Seoul calendar day; retrying known-failing history endpoints every
60 seconds adds latency without improving the displayed index.  A publicly
cross-checked 52-week high remains a minimum peak when history is unavailable.
"""
from __future__ import annotations

import math
import threading
from datetime import datetime, timezone

import monitor
import production
import production_v27

app = production_v27.app
SEOUL = production_v27.SEOUL
_base_init_db = monitor.init_db

# Public KOSPI100 sources cross-checked on 2026-09-28 show a 52-week high of
# 11,932.83. Because an all-time high cannot be below a 52-week high, this is a
# safe lower bound, never a ceiling. Any verified higher historical value wins.
KPI100_VERIFIED_PEAK_FLOOR = 11932.83
_HISTORY_CACHE = {
    "day": None,
    "ath": KPI100_VERIFIED_PEAK_FLOOR,
    "ts": 0,
    "basis": "verified-52w-floor",
}
_HISTORY_LOCK = threading.Lock()


def _init_db_v28():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-verified-peak-floor-v28'").fetchone():
            # Remove the false 8,7xx peak that could have been persisted by the
            # prior Yahoo-only fallback. KOSPI100 is display-only, so no alert
            # state is sacrificed.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-verified-peak-floor-v28')")


monitor.init_db = _init_db_v28


def _daily_historical_peak():
    """Return the best verified historical peak, refreshing once per Seoul day."""
    day = datetime.now(SEOUL).date().isoformat()
    with _HISTORY_LOCK:
        if _HISTORY_CACHE["day"] == day:
            return (
                float(_HISTORY_CACHE["ath"]),
                int(_HISTORY_CACHE["ts"] or 0),
                str(_HISTORY_CACHE["basis"]),
            )

        ath = KPI100_VERIFIED_PEAK_FLOOR
        ath_ts = 0
        basis = "verified-52w-floor"

        # Naver is first choice for Korean-index history. A failure is cached for
        # the rest of the day instead of hitting the same 400 endpoint each minute.
        try:
            naver_ath, naver_ts = production_v27._naver_history_ath()
            if math.isfinite(naver_ath) and naver_ath >= ath:
                ath = float(naver_ath)
                ath_ts = int(naver_ts or 0)
                basis = "naver-history"
        except Exception as exc:
            print("KPI100 Naver history unavailable; daily verified floor retained", type(exc).__name__, flush=True)

        # Secondary long-history source may only RAISE the peak and is also
        # attempted once per day. It never supplies the realtime/current quote.
        try:
            hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
            if math.isfinite(hist_ath) and hist_ath > ath:
                ath = float(hist_ath)
                ath_ts = int(hist_ts or 0)
                basis = "historical-crosscheck"
        except Exception as exc:
            print("KPI100 secondary history unavailable; daily cache retained", type(exc).__name__, flush=True)

        _HISTORY_CACHE.update(day=day, ath=ath, ts=ath_ts, basis=basis)
        print("KPI100 daily ATH crosscheck", dict(_HISTORY_CACHE), flush=True)
        return ath, ath_ts, basis


def _evaluate_kpi100_v28(index_id):
    # Realtime quote and prior-close change are always Naver KPI100.
    current, previous, change, rate, day_high, _, ts, state = production_v27._polling_kpi100_fixed()
    stored = monitor.get_state(index_id)
    old_ath = float(stored[0]) if stored and stored[0] else 0.0

    historical_ath, historical_ts, historical_basis = _daily_historical_peak()
    ath = max(old_ath, current, day_high, KPI100_VERIFIED_PEAK_FLOOR, historical_ath)
    ath_ts = historical_ts if historical_ath >= ath and historical_ts else 0
    ath_basis = historical_basis if historical_ath >= ath else "persisted-or-live"

    # A new live high always supersedes the cached history immediately.
    if day_high > max(old_ath, historical_ath, KPI100_VERIFIED_PEAK_FLOOR):
        ath = day_high
        ath_ts = ts
        ath_basis = "new-live-high"

    dd = (current / ath - 1.0) * 100.0 if ath > 0 else None
    ath_date = (
        datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(SEOUL).date().isoformat()
        if ath_ts else None
    )
    source = "KOSPI100 실시간/전일대비 · 네이버 증권 KPI100 · 최고가 교차검증"
    monitor.save_state(index_id, ath, current, current, source)
    production.EXTRA_STATE[index_id] = {
        "previous_close": previous,
        "day_change": change,
        "day_change_percent": rate,
        "ath_date": ath_date,
        "ath_days": production._days_since(ath_ts, "Asia/Seoul") if ath_ts else None,
        "drawdown": dd,
        "market_state": state,
        "value_ts": ts,
        "extended_display": False,
        "extended_estimate": False,
        "actual_extended_trade": False,
        "ath_basis": ath_basis,
        "quote_provider": "Naver Finance KPI100",
        "history_crosscheck_day": _HISTORY_CACHE["day"],
    }
    result = {
        "id": index_id,
        "name": "KOSPI 100",
        "value": current,
        "cash": current,
        "ath": ath,
        "drawdown": dd,
        "source": source,
        "market_state": state,
        "cash_ts": ts,
        "value_ts": ts,
        **production.EXTRA_STATE[index_id],
    }
    print("KPI100 v28 final", result, flush=True)
    return result


# production_v24 owns the dynamic evaluator used by monitor/scheduler/routes.
production_v24 = production_v27.production_v24
production_v24._evaluate_kospi100 = _evaluate_kpi100_v28
