"""IndexAlert production v3.2: align the fourth card with KOSPI composite.

The Android client already labels the legacy wire id ``kospi100`` as KOSPI.
Older server revisions still returned Naver KPI100 for that id, which made the
card title and value refer to different indices.  This module keeps the wire id
for backward compatibility but sources the actual KOSPI composite from Naver's
realtime SERVICE_INDEX:KOSPI feed.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import execution_evidence_ledger
import monitor
import production
import production_v27
import production_v29
import push_health

app = production_v29.app
SEOUL = production_v27.SEOUL
production_v24 = production_v27.production_v24
_base_init_db = monitor.init_db

# Wire id is retained so installed apps need no APK update.
monitor.RULES["kospi100"] = {
    "name": "KOSPI",
    "cash": "^KS11",
    "proxy": None,
    "levels": [],
    "regular_label": "KOSPI · 네이버 증권",
    "proxy_label": "KOSPI · 네이버 증권",
    "extended": False,
    "timezone": "Asia/Seoul",
}


def _init_db_v30():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi-composite-naver-v30'").fetchone():
            # Previous revisions stored KOSPI100 (8,xxx/11,xxx) under this wire id.
            # Those values must never seed KOSPI composite ATH/state.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi-composite-naver-v30')")


monitor.init_db = _init_db_v30


def _naver_kospi_realtime():
    data, url = production_v27.production_v26._polling_data("KOSPI")
    if not data:
        raise RuntimeError("Naver KOSPI realtime unavailable")

    current = production_v27._poll_hundredth(data.get("nv"))
    change = production_v27._poll_hundredth(data.get("cv"))
    previous = production_v27._poll_hundredth(data.get("sv"))
    day_high = production_v27._poll_hundredth(data.get("hv"))
    rate = production_v27._decimal(data.get("cr"))
    if current is None or current <= 0:
        raise RuntimeError("Naver KOSPI realtime current invalid")

    rf = str(data.get("rf") or "")
    change = float(change or 0.0)
    rate = float(rate or 0.0)
    if rf == "5":
        change, rate = -abs(change), -abs(rate)
    elif rf == "2":
        change, rate = abs(change), abs(rate)

    if previous is None or previous <= 0:
        previous = current - change
    if previous <= 0:
        previous = current / (1.0 + rate / 100.0) if abs(rate) < 99 else current
        change = current - previous
    if day_high is None or day_high <= 0:
        day_high = current

    ms = str(data.get("ms") or "").upper()
    state = "REGULAR" if ms in {"OPEN", "OPENED", "REGULAR"} else "CLOSED"
    ts = int(datetime.now(SEOUL).timestamp())
    print(
        "KOSPI naver realtime",
        {
            "current": current,
            "previous": previous,
            "change": change,
            "rate": rate,
            "day_high": day_high,
            "market_status": ms,
            "rf": rf,
            "url": url,
        },
        flush=True,
    )
    return current, previous, change, rate, day_high, ts, state


def _evaluate_kospi(index_id: str):
    current, previous, change, rate, day_high, ts, state = _naver_kospi_realtime()
    stored = monitor.get_state(index_id)
    old_ath = float(stored[0]) if stored and stored[0] else 0.0
    ath = max(old_ath, current, day_high)
    ath_ts = 0

    # KOSPI historical peak/date is refreshed from the long-history series.
    # Realtime current/previous/day change always come from Naver.
    try:
        hist_ath, hist_ts = production._history_ath("^KS11")
        if math.isfinite(hist_ath) and hist_ath > ath:
            ath = float(hist_ath)
            ath_ts = int(hist_ts or 0)
        elif math.isfinite(hist_ath) and abs(float(hist_ath) - ath) / max(ath, 1.0) < 0.002:
            ath_ts = int(hist_ts or 0)
    except Exception as exc:
        print("KOSPI historical ATH crosscheck unavailable", type(exc).__name__, flush=True)

    if day_high >= ath:
        ath = day_high
        ath_ts = ts

    dd = (current / ath - 1.0) * 100.0 if ath > 0 else None
    ath_date = (
        datetime.fromtimestamp(ath_ts, tz=timezone.utc).astimezone(SEOUL).date().isoformat()
        if ath_ts else None
    )
    source = "KOSPI 실시간/전일대비 · 네이버 증권"
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
        "quote_provider": "Naver Finance KOSPI",
    }
    result = {
        "id": index_id,
        "name": "KOSPI",
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
    print("KOSPI v30 final", result, flush=True)
    return result


# v24 owns the dynamic fourth-card evaluator used throughout the later stack.
production_v24._evaluate_kospi100 = _evaluate_kospi

# Protected, immutable operational ledger for future empirical fill/latency/
# markout evidence.  This does not alter served recommendations or promotion.
execution_evidence_ledger.attach(app)

# Sanitized aggregate push-health endpoint. No FCM token or device payload is
# returned; this is operational observability only.
push_health.attach(app)
