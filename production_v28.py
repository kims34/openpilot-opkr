"""IndexAlert production v3.0: verified KPI100 ATH safety floor.

Current/previous/day change remain Naver realtime KPI100.  Historical Naver data
is preferred when available.  If Naver history is temporarily unavailable, a
publicly cross-checked 52-week high is used as a *minimum* peak so the displayed
ATH can never fall below a known recent high.  Its date is intentionally left
unknown rather than fabricated.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import monitor
import production
import production_v27

app = production_v27.app
SEOUL = production_v27.SEOUL
_base_init_db = monitor.init_db

# Public KOSPI100 sources cross-checked on 2026-09-28 show a 52-week high of
# 11,932.83.  Because an all-time high cannot be below a 52-week high, this is a
# safe lower bound, never a ceiling.  Any verified higher historical value wins.
KPI100_VERIFIED_PEAK_FLOOR = 11932.83


def _init_db_v28():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi100-verified-peak-floor-v28'").fetchone():
            # Remove the false 8,7xx peak that could have been persisted by the
            # prior Yahoo-only fallback.  KOSPI100 is display-only, so no alert
            # state is sacrificed.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi100-verified-peak-floor-v28')")


monitor.init_db = _init_db_v28


def _evaluate_kpi100_v28(index_id):
    current, previous, change, rate, day_high, _, ts, state = production_v27._polling_kpi100_fixed()
    stored = monitor.get_state(index_id)
    old_ath = float(stored[0]) if stored and stored[0] else 0.0

    ath = max(old_ath, current, day_high, KPI100_VERIFIED_PEAK_FLOOR)
    ath_ts = 0
    ath_basis = "verified-52w-floor"

    # Prefer Naver's own historical maximum when the endpoint is available.
    try:
        naver_ath, naver_ts = production_v27._naver_history_ath()
        if math.isfinite(naver_ath) and naver_ath >= ath:
            ath = float(naver_ath)
            ath_ts = int(naver_ts or 0)
            ath_basis = "naver-history"
    except Exception as exc:
        print("KPI100 Naver history unavailable; verified floor retained", type(exc).__name__, flush=True)

    # Secondary long-history cross-check may only RAISE the known peak; it may
    # never lower the Naver/current/verified floor.
    try:
        hist_ath, hist_ts = production._history_ath("KOSPI100.KS")
        if math.isfinite(hist_ath) and hist_ath > ath:
            ath = float(hist_ath)
            ath_ts = int(hist_ts or 0)
            ath_basis = "historical-crosscheck"
    except Exception as exc:
        print("KPI100 secondary history unavailable", type(exc).__name__, flush=True)

    if day_high > ath:
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
